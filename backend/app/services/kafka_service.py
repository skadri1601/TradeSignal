"""
Kafka Event Streaming Service.

Apache Kafka event streaming, WebSocket server, consumer groups, dead letter queue.
"""

import logging
import json
from typing import Dict, Any, Optional, Callable
from datetime import datetime

logger = logging.getLogger(__name__)


class KafkaService:
    """Service for Kafka event streaming."""

    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        self.bootstrap_servers = bootstrap_servers
        self.producer = None
        self.consumers = {}
        self._initialize_kafka()

    def _initialize_kafka(self):
        """Initialize Kafka producer and consumers."""
        try:
            from kafka import KafkaProducer, KafkaConsumer
            from kafka.errors import KafkaError

            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8") if k else None,
            )
            logger.info(f"Kafka producer initialized: {self.bootstrap_servers}")
        except ImportError:
            logger.warning("kafka-python not installed, using placeholder service")
            self.producer = None
        except Exception as e:
            logger.error(f"Error initializing Kafka: {e}", exc_info=True)
            self.producer = None

    async def publish_event(
        self,
        topic: str,
        event: Dict[str, Any],
        key: Optional[str] = None,
    ) -> bool:
        """
        Publish event to Kafka topic.

        Returns True if successful.
        """
        if not self.producer:
            logger.warning("Kafka producer not available, event not published")
            return False

        try:
            # Add metadata
            event_with_metadata = {
                **event,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "tradesignal-backend",
            }

            future = self.producer.send(topic, value=event_with_metadata, key=key)
            result = future.get(timeout=10)

            logger.debug(f"Event published to {topic}: {result}")
            return True

        except Exception as e:
            logger.error(f"Error publishing event to Kafka: {e}", exc_info=True)
            return False

    def create_consumer(
        self,
        topic: str,
        group_id: str,
        handler: Callable[[Dict[str, Any]], None],
    ) -> Optional[str]:
        """
        Create Kafka consumer for a topic.

        Returns consumer ID.
        """
        try:
            from kafka import KafkaConsumer
            from kafka.errors import KafkaError
            import threading

            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=self.bootstrap_servers,
                group_id=group_id,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                auto_offset_reset="earliest",
                enable_auto_commit=True,
            )

            consumer_id = f"{group_id}_{topic}_{int(datetime.utcnow().timestamp())}"

            def consume_messages():
                try:
                    for message in consumer:
                        try:
                            handler(message.value)
                        except Exception as e:
                            logger.error(
                                f"Error handling message: {e}", exc_info=True
                            )
                            # Send to dead letter queue
                            self._send_to_dlq(topic, message.value, str(e))
                except Exception as e:
                    logger.error(f"Consumer error: {e}", exc_info=True)

            # Start consumer in background thread
            thread = threading.Thread(target=consume_messages, daemon=True)
            thread.start()

            self.consumers[consumer_id] = {
                "consumer": consumer,
                "thread": thread,
                "topic": topic,
                "group_id": group_id,
            }

            logger.info(f"Kafka consumer created: {consumer_id}")
            return consumer_id

        except ImportError:
            logger.warning("kafka-python not installed")
            return None
        except Exception as e:
            logger.error(f"Error creating Kafka consumer: {e}", exc_info=True)
            return None

    def _send_to_dlq(self, topic: str, message: Dict[str, Any], error: str) -> None:
        """Send failed message to dead letter queue."""
        dlq_topic = f"{topic}_dlq"
        dlq_message = {
            **message,
            "original_topic": topic,
            "error": error,
            "failed_at": datetime.utcnow().isoformat(),
        }
        self.publish_event(dlq_topic, dlq_message)

    async def publish_trade_event(self, trade: Dict[str, Any]) -> bool:
        """Publish trade event to Kafka."""
        return await self.publish_event(
            topic="trades",
            event={
                "event_type": "trade_filed",
                "trade": trade,
            },
            key=trade.get("ticker"),
        )

    async def publish_alert_event(self, alert: Dict[str, Any]) -> bool:
        """Publish alert trigger event to Kafka."""
        return await self.publish_event(
            topic="alerts",
            event={
                "event_type": "alert_triggered",
                "alert": alert,
            },
        )

    async def publish_user_event(self, user_id: int, event_type: str, data: Dict[str, Any]) -> bool:
        """Publish user event to Kafka."""
        return await self.publish_event(
            topic="users",
            event={
                "event_type": event_type,
                "user_id": user_id,
                "data": data,
            },
            key=str(user_id),
        )


class WebSocketService:
    """WebSocket service for real-time updates."""

    def __init__(self):
        self.connections = {}

    async def connect(self, websocket, user_id: Optional[int] = None) -> str:
        """Register WebSocket connection."""
        import uuid

        connection_id = str(uuid.uuid4())
        self.connections[connection_id] = {
            "websocket": websocket,
            "user_id": user_id,
            "connected_at": datetime.utcnow(),
        }
        return connection_id

    async def disconnect(self, connection_id: str) -> None:
        """Unregister WebSocket connection."""
        if connection_id in self.connections:
            del self.connections[connection_id]

    async def broadcast(self, message: Dict[str, Any], user_id: Optional[int] = None) -> int:
        """
        Broadcast message to all or specific user connections.

        Returns number of connections notified.
        """
        sent_count = 0

        for connection_id, conn in list(self.connections.items()):
            try:
                if user_id is None or conn["user_id"] == user_id:
                    await conn["websocket"].send_json(message)
                    sent_count += 1
            except Exception as e:
                logger.error(f"Error sending WebSocket message: {e}")
                # Remove dead connection
                await self.disconnect(connection_id)

        return sent_count

    async def send_to_user(self, user_id: int, message: Dict[str, Any]) -> int:
        """Send message to specific user's connections."""
        return await self.broadcast(message, user_id=user_id)

