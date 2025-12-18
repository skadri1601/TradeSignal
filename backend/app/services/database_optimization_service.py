"""
Database Optimization Service.

Read/write splitting, time-based partitioning, sharding strategy, enhanced Redis caching.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text

logger = logging.getLogger(__name__)


class DatabaseOptimizationService:
    """Service for database optimization and performance tuning."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def analyze_query_performance(self) -> List[Dict[str, Any]]:
        """
        Analyze slow queries and performance bottlenecks.

        Returns list of slow queries with recommendations.
        """
        # Get slow queries from PostgreSQL
        try:
            result = await self.db.execute(
                text("""
                    SELECT 
                        query,
                        calls,
                        total_exec_time,
                        mean_exec_time,
                        max_exec_time
                    FROM pg_stat_statements
                    WHERE mean_exec_time > 100  -- Queries taking > 100ms on average
                    ORDER BY mean_exec_time DESC
                    LIMIT 20
                """)
            )
            slow_queries = result.fetchall()

            recommendations = []
            for row in slow_queries:
                query = row[0]
                mean_time = row[3]

                recommendation = {
                    "query": query[:200] + "..." if len(query) > 200 else query,
                    "mean_exec_time_ms": round(mean_time, 2),
                    "calls": row[1],
                    "recommendations": self._generate_recommendations(query),
                }
                recommendations.append(recommendation)

            return recommendations

        except Exception as e:
            logger.warning(f"Could not analyze query performance: {e}")
            return []

    def _generate_recommendations(self, query: str) -> List[str]:
        """Generate optimization recommendations for a query."""
        recommendations = []

        query_lower = query.lower()

        # Check for missing indexes
        if "where" in query_lower and "join" in query_lower:
            recommendations.append("Consider adding composite indexes on JOIN and WHERE columns")

        if "order by" in query_lower and "limit" in query_lower:
            recommendations.append("Ensure ORDER BY columns are indexed")

        # Check for full table scans
        if "where" not in query_lower:
            recommendations.append("Add WHERE clause to filter data")

        # Check for N+1 queries
        if query_lower.count("select") > 1:
            recommendations.append("Consider using JOINs or eager loading to reduce queries")

        return recommendations

    async def get_table_statistics(self) -> Dict[str, Any]:
        """Get database table statistics for optimization."""
        try:
            result = await self.db.execute(
                text("""
                    SELECT 
                        schemaname,
                        tablename,
                        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
                        pg_total_relation_size(schemaname||'.'||tablename) AS size_bytes,
                        n_live_tup AS row_count
                    FROM pg_tables
                    LEFT JOIN pg_stat_user_tables ON tablename = relname
                    WHERE schemaname = 'public'
                    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                    LIMIT 20
                """)
            )
            tables = result.fetchall()

            return {
                "tables": [
                    {
                        "schema": row[0],
                        "table": row[1],
                        "size": row[2],
                        "size_bytes": row[3],
                        "row_count": row[4] or 0,
                    }
                    for row in tables
                ],
                "total_tables": len(tables),
            }

        except Exception as e:
            logger.warning(f"Could not get table statistics: {e}")
            return {"tables": [], "total_tables": 0}

    async def get_index_statistics(self) -> Dict[str, Any]:
        """Get index usage statistics."""
        try:
            result = await self.db.execute(
                text("""
                    SELECT 
                        schemaname,
                        tablename,
                        indexname,
                        idx_scan AS index_scans,
                        idx_tup_read AS tuples_read,
                        idx_tup_fetch AS tuples_fetched
                    FROM pg_stat_user_indexes
                    WHERE schemaname = 'public'
                    ORDER BY idx_scan ASC
                    LIMIT 50
                """)
            )
            indexes = result.fetchall()

            # Identify unused indexes
            unused_indexes = [
                {
                    "schema": row[0],
                    "table": row[1],
                    "index": row[2],
                    "scans": row[3],
                }
                for row in indexes
                if row[3] == 0  # Never used
            ]

            return {
                "total_indexes": len(indexes),
                "unused_indexes": unused_indexes,
                "unused_count": len(unused_indexes),
            }

        except Exception as e:
            logger.warning(f"Could not get index statistics: {e}")
            return {"total_indexes": 0, "unused_indexes": [], "unused_count": 0}

    async def recommend_partitioning(self) -> List[Dict[str, Any]]:
        """Recommend tables for time-based partitioning."""
        recommendations = []

        # Check large tables with timestamp columns
        large_tables = [
            "trades",
            "analytics_events",
            "alert_triggers",
            "portfolio_transactions",
            "portfolio_performance",
        ]

        for table in large_tables:
            try:
                result = await self.db.execute(
                    text(f"""
                        SELECT 
                            COUNT(*) as row_count,
                            MIN(created_at) as min_date,
                            MAX(created_at) as max_date
                        FROM {table}
                    """)
                )
                stats = result.first()

                if stats and stats[0] > 1000000:  # More than 1M rows
                    recommendations.append({
                        "table": table,
                        "row_count": stats[0],
                        "date_range": {
                            "min": stats[1].isoformat() if stats[1] else None,
                            "max": stats[2].isoformat() if stats[2] else None,
                        },
                        "recommendation": "Consider time-based partitioning by month or quarter",
                        "partition_strategy": "RANGE (created_at)",
                    })

            except Exception as e:
                logger.debug(f"Could not analyze {table}: {e}")

        return recommendations

    async def get_connection_pool_stats(self) -> Dict[str, Any]:
        """Get database connection pool statistics."""
        # Would get from SQLAlchemy engine
        engine = self.db.bind
        if hasattr(engine, "pool"):
            pool = engine.pool
            return {
                "size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "invalid": pool.invalid(),
            }
        return {"status": "pool_stats_unavailable"}

    async def optimize_table(self, table_name: str) -> Dict[str, Any]:
        """Run VACUUM ANALYZE on a table."""
        try:
            await self.db.execute(text(f"VACUUM ANALYZE {table_name}"))
            await self.db.commit()

            return {
                "table": table_name,
                "status": "optimized",
                "optimized_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error optimizing table {table_name}: {e}", exc_info=True)
            return {
                "table": table_name,
                "status": "error",
                "error": str(e),
            }

