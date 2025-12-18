"""
Predictive Modeling Service.

Training data collection, feature engineering, gradient boosting model, backtesting framework.
"""

import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc

from app.models.trade import Trade
from app.models.company import Company
from app.models.insider import Insider
from app.models.tradesignal_score import TradeSignalScore

logger = logging.getLogger(__name__)


class PredictiveModelingService:
    """Service for predictive modeling and backtesting."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def collect_training_data(
        self, ticker: Optional[str] = None, days_back: int = 365
    ) -> List[Dict[str, Any]]:
        """
        Collect training data for ML model.

        Features:
        - Insider trade patterns
        - Company metrics
        - Market data
        - Historical performance
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)

        # Get trades with company and insider data
        query = (
            select(Trade, Company, Insider)
            .join(Company, Trade.company_id == Company.id)
            .join(Insider, Trade.insider_id == Insider.id)
            .where(Trade.filing_date >= cutoff_date)
        )

        if ticker:
            query = query.where(Company.ticker == ticker.upper())

        result = await self.db.execute(query)
        trades_data = result.all()

        training_samples = []

        for trade, company, insider in trades_data:
            # Extract features
            features = await self._extract_features(trade, company, insider)

            # Get target (future price performance)
            target = await self._calculate_target(trade, company)

            if target is not None:
                training_samples.append({
                    "features": features,
                    "target": target,
                    "trade_id": trade.id,
                    "ticker": company.ticker,
                    "filing_date": trade.filing_date.isoformat(),
                })

        return training_samples

    async def _extract_features(
        self, trade: Trade, company: Company, insider: Insider
    ) -> Dict[str, Any]:
        """Extract features from trade, company, and insider data."""
        # Get recent trading activity for this company
        cutoff_date = trade.filing_date - timedelta(days=90)

        result = await self.db.execute(
            select(
                func.count(Trade.id).label("recent_trade_count"),
                func.sum(
                    func.case((Trade.transaction_type == "BUY", Trade.total_value), else_=0)
                ).label("recent_buy_value"),
                func.sum(
                    func.case((Trade.transaction_type == "SELL", Trade.total_value), else_=0)
                ).label("recent_sell_value"),
            )
            .join(Company, Trade.company_id == Company.id)
            .where(
                Company.ticker == company.ticker,
                Trade.filing_date >= cutoff_date,
                Trade.filing_date < trade.filing_date,
            )
        )
        recent_stats = result.first()

        # Get insider's historical activity
        insider_result = await self.db.execute(
            select(func.count(Trade.id).label("insider_trade_count"))
            .where(
                Trade.insider_id == insider.id,
                Trade.filing_date < trade.filing_date,
            )
        )
        insider_stats = insider_result.first()

        # Get TS Score if available
        ts_score_result = await self.db.execute(
            select(TradeSignalScore)
            .where(TradeSignalScore.ticker == company.ticker)
            .order_by(desc(TradeSignalScore.calculated_at))
            .limit(1)
        )
        ts_score = ts_score_result.scalar_one_or_none()

        features = {
            # Trade features
            "trade_value": float(trade.total_value) if trade.total_value else 0.0,
            "shares": float(trade.shares) if trade.shares else 0.0,
            "transaction_type": 1 if trade.transaction_type == "BUY" else 0,
            "price_per_share": float(trade.price_per_share) if trade.price_per_share else 0.0,

            # Insider features
            "insider_role_ceo": 1 if insider.title and "CEO" in insider.title.upper() else 0,
            "insider_role_cfo": 1 if insider.title and "CFO" in insider.title.upper() else 0,
            "insider_role_director": 1 if insider.title and "DIRECTOR" in insider.title.upper() else 0,
            "insider_trade_count": insider_stats.insider_trade_count or 0,

            # Company activity features
            "recent_trade_count": recent_stats.recent_trade_count or 0,
            "recent_buy_value": float(recent_stats.recent_buy_value or 0),
            "recent_sell_value": float(recent_stats.recent_sell_value or 0),
            "recent_buy_ratio": (
                float(recent_stats.recent_buy_value or 0) /
                max(float(recent_stats.recent_buy_value or 0) + float(recent_stats.recent_sell_value or 0), 1)
            ),

            # TS Score features
            "ts_score": ts_score.score if ts_score else 50.0,
            "ts_badge_excellent": 1 if ts_score and ts_score.badge == "excellent" else 0,
            "ts_badge_strong": 1 if ts_score and ts_score.badge == "strong" else 0,

            # Temporal features
            "day_of_week": trade.filing_date.weekday(),
            "month": trade.filing_date.month,
            "quarter": (trade.filing_date.month - 1) // 3 + 1,
        }

        return features

    async def _calculate_target(
        self, trade: Trade, company: Company, days_forward: int = 30
    ) -> Optional[float]:
        """
        Calculate target variable (future price performance).

        Returns price change percentage after N days, or None if insufficient data.
        """
        # Get price at filing date (would fetch from stock service)
        filing_price = float(trade.price_per_share) if trade.price_per_share else None

        if not filing_price:
            return None

        # Get price N days later (would fetch from stock service)
        # For now, return None as placeholder
        # In production, would fetch historical prices
        future_date = trade.filing_date + timedelta(days=days_forward)

        # Placeholder: would fetch actual price data
        future_price = None

        if future_price:
            return ((future_price - filing_price) / filing_price) * 100

        return None

    async def train_model(
        self, training_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Train gradient boosting model on training data.

        Returns model metrics and serialized model.
        """
        try:
            from sklearn.ensemble import GradientBoostingRegressor
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import mean_squared_error, r2_score
        except ImportError:
            logger.warning("scikit-learn not installed, using placeholder model")
            return {
                "model_type": "placeholder",
                "status": "sklearn_not_available",
                "message": "Install scikit-learn to enable model training",
            }

        if len(training_data) < 100:
            return {
                "status": "insufficient_data",
                "message": f"Need at least 100 samples, got {len(training_data)}",
            }

        # Prepare features and targets
        X = []
        y = []

        for sample in training_data:
            features = sample["features"]
            target = sample["target"]

            if target is not None:
                # Convert features dict to array
                feature_array = [
                    features["trade_value"],
                    features["shares"],
                    features["transaction_type"],
                    features["price_per_share"],
                    features["insider_role_ceo"],
                    features["insider_role_cfo"],
                    features["insider_role_director"],
                    features["insider_trade_count"],
                    features["recent_trade_count"],
                    features["recent_buy_value"],
                    features["recent_sell_value"],
                    features["recent_buy_ratio"],
                    features["ts_score"],
                    features["ts_badge_excellent"],
                    features["ts_badge_strong"],
                    features["day_of_week"],
                    features["month"],
                    features["quarter"],
                ]
                X.append(feature_array)
                y.append(target)

        X = np.array(X)
        y = np.array(y)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Train model
        model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42,
        )
        model.fit(X_train, y_train)

        # Evaluate
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        return {
            "status": "trained",
            "model_type": "gradient_boosting",
            "metrics": {
                "mse": float(mse),
                "rmse": float(np.sqrt(mse)),
                "r2_score": float(r2),
            },
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "feature_importance": dict(
                zip(
                    [
                        "trade_value", "shares", "transaction_type", "price_per_share",
                        "insider_role_ceo", "insider_role_cfo", "insider_role_director",
                        "insider_trade_count", "recent_trade_count", "recent_buy_value",
                        "recent_sell_value", "recent_buy_ratio", "ts_score",
                        "ts_badge_excellent", "ts_badge_strong", "day_of_week",
                        "month", "quarter",
                    ],
                    model.feature_importances_.tolist(),
                )
            ),
        }

    async def backtest_model(
        self, model: Any, test_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Backtest model on historical data.

        Returns backtesting metrics.
        """
        predictions = []
        actuals = []

        for sample in test_data:
            features = sample["features"]
            target = sample["target"]

            if target is not None:
                # Prepare feature array
                feature_array = np.array([[
                    features["trade_value"],
                    features["shares"],
                    features["transaction_type"],
                    features["price_per_share"],
                    features["insider_role_ceo"],
                    features["insider_role_cfo"],
                    features["insider_role_director"],
                    features["insider_trade_count"],
                    features["recent_trade_count"],
                    features["recent_buy_value"],
                    features["recent_sell_value"],
                    features["recent_buy_ratio"],
                    features["ts_score"],
                    features["ts_badge_excellent"],
                    features["ts_badge_strong"],
                    features["day_of_week"],
                    features["month"],
                    features["quarter"],
                ]])

                # Predict
                prediction = model.predict(feature_array)[0]
                predictions.append(prediction)
                actuals.append(target)

        if not predictions:
            return {
                "status": "no_predictions",
                "message": "No valid predictions generated",
            }

        # Calculate metrics
        predictions = np.array(predictions)
        actuals = np.array(actuals)

        mse = np.mean((predictions - actuals) ** 2)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(predictions - actuals))

        # Calculate directional accuracy
        correct_direction = np.sum(
            (predictions > 0) == (actuals > 0)
        ) / len(predictions)

        return {
            "status": "completed",
            "metrics": {
                "mse": float(mse),
                "rmse": float(rmse),
                "mae": float(mae),
                "directional_accuracy": float(correct_direction),
            },
            "samples": len(predictions),
        }

