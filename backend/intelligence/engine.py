"""
CryptoMind AI - Intelligence Engine
The KEY differentiator: Explains WHY signals happen and evaluates probability
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import random
import json

from models.schemas import MarketBehavior


class IntelligenceEngine:
    """
    Intelligence Engine - The brain of CryptoMind AI
    
    This engine:
    1. Analyzes detected signals and generates explanations
    2. Determines market behavior type
    3. Calculates confidence/probability scores
    4. Finds historical analogies
    5. Evaluates smart money activity
    """
    
    def __init__(self):
        # Historical patterns database (in production, this would be in DB)
        self.historical_patterns: List[dict] = self._generate_historical_data()
        
        # Pattern weights for similarity calculation
        self.feature_weights = {
            "price_change": 0.3,
            "volume_ratio": 0.25,
            "market_behavior": 0.2,
            "timeframe": 0.15,
            "exchange": 0.1
        }
    
    def _generate_historical_data(self) -> List[dict]:
        """Generate simulated historical patterns for analogy matching"""
        patterns = []
        symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]
        behaviors = ["accumulation", "distribution", "breakout", "manipulation"]
        outcomes = ["success", "failure", "neutral"]
        
        base_date = datetime.utcnow() - timedelta(days=90)
        
        for i in range(200):
            symbol = random.choice(symbols)
            behavior = random.choice(behaviors)
            outcome = random.choice(outcomes)
            
            # Generate realistic pattern data
            price_change = random.uniform(-15, 15)
            volume_ratio = random.uniform(1.5, 8.0)
            
            # Success more likely with accumulation and high volume
            if behavior == "accumulation" and volume_ratio > 4:
                outcome_weights = [0.7, 0.15, 0.15]
                outcome = random.choices(outcomes, weights=outcome_weights)[0]
            elif behavior == "distribution" and volume_ratio > 4:
                outcome_weights = [0.15, 0.7, 0.15]
                outcome = random.choices(outcomes, weights=outcome_weights)[0]
            
            price_after = price_change * random.uniform(0.5, 1.5) if outcome == "success" else -price_change * 0.5
            
            patterns.append({
                "pattern_id": f"hist_{i:04d}",
                "symbol": symbol,
                "signal_type": random.choice(["pump", "dump", "volume_spike"]),
                "price_change": price_change,
                "volume_ratio": volume_ratio,
                "market_behavior": behavior,
                "outcome": outcome,
                "price_change_after": round(price_after, 2),
                "date": (base_date + timedelta(days=random.randint(0, 90))).isoformat(),
                "timeframe": random.choice(["5m", "15m", "1h"]),
                "features": {
                    "price_change_normalized": price_change / 15,
                    "volume_ratio_normalized": volume_ratio / 8,
                    "behavior_encoded": behaviors.index(behavior) / len(behaviors)
                }
            })
        
        return patterns
    
    async def analyze_signal(self, signal: dict) -> dict:
        """
        Main analysis method - enriches signal with intelligence
        
        Args:
            signal: Raw signal from detector
            
        Returns:
            Enhanced signal with explanations, confidence, and analogies
        """
        # 1. Enhance explanation
        enhanced_explanation = await self._enhance_explanation(signal)
        
        # 2. Calculate refined confidence score
        refined_confidence = await self._calculate_confidence(signal)
        
        # 3. Find historical analogies
        analogies = await self._find_historical_analogies(signal)
        
        # 4. Detect smart money activity
        smart_money_detected = await self._detect_smart_money(signal)
        
        # Build enhanced signal
        enhanced_signal = signal.copy()
        enhanced_signal["explanation"] = enhanced_explanation
        enhanced_signal["confidence_score"] = refined_confidence
        enhanced_signal["historical_analogies"] = analogies
        enhanced_signal["smart_money_activity"] = smart_money_detected
        
        # Add probability assessment
        enhanced_signal["probability_assessment"] = await self._assess_probability(
            signal, refined_confidence, analogies
        )
        
        return enhanced_signal
    
    async def _enhance_explanation(self, signal: dict) -> dict:
        """Enhance the signal explanation with more context"""
        explanation = signal.get("explanation", {}).copy()
        
        # Add contextual insights based on signal type
        signal_type = signal.get("signal_type")
        volume_change = signal.get("volume_change_percent", 0)
        price_change = signal.get("price_change_percent", 0)
        
        additional_insights = []
        
        if signal_type == "pump":
            if volume_change > 500:
                additional_insights.append("Extraordinary volume suggests coordinated buying")
            elif volume_change > 200:
                additional_insights.append("Strong volume confirms genuine buying pressure")
            else:
                additional_insights.append("Moderate volume - watch for confirmation")
            
            if abs(price_change) > 10:
                additional_insights.append("Extreme price movement - high volatility expected")
        
        elif signal_type == "dump":
            if volume_change > 500:
                additional_insights.append("Panic selling detected with massive volume")
            elif volume_change > 200:
                additional_insights.append("Strong selling pressure confirmed by volume")
            else:
                additional_insights.append("Selling pressure - monitor for support levels")
        
        elif signal_type == "volume_spike":
            if price_change > 5:
                additional_insights.append("Volume spike with price increase - bullish")
            elif price_change < -5:
                additional_insights.append("Volume spike with price decrease - bearish")
            else:
                additional_insights.append("Volume spike without price action - accumulation/distribution possible")
        
        elif signal_type == "order_book_wall":
            if "buy wall" in str(explanation.get("reasons", [])).lower():
                additional_insights.append("Large buy orders suggest institutional interest")
            if "sell wall" in str(explanation.get("reasons", [])).lower():
                additional_insights.append("Large sell orders may indicate resistance or manipulation")
        
        # Merge insights
        existing_reasons = explanation.get("reasons", [])
        explanation["reasons"] = existing_reasons + additional_insights
        
        # Add action recommendation
        market_behavior = explanation.get("market_behavior", "normal")
        if market_behavior == "accumulation":
            explanation["recommendation"] = "Consider long position with tight stop-loss"
        elif market_behavior == "distribution":
            explanation["recommendation"] = "Consider short position or take profits"
        elif market_behavior == "breakout":
            explanation["recommendation"] = "Momentum trade opportunity - enter on confirmation"
        else:
            explanation["recommendation"] = "Wait for additional confirmation"
        
        return explanation
    
    async def _calculate_confidence(self, signal: dict) -> float:
        """Calculate refined confidence score"""
        base_confidence = signal.get("confidence_score", 50)
        
        # Adjust based on various factors
        adjustments = 0
        
        # Volume factor
        volume_change = signal.get("volume_change_percent", 0)
        if volume_change > 300:
            adjustments += 10
        elif volume_change > 150:
            adjustments += 5
        
        # Price movement factor
        price_change = abs(signal.get("price_change_percent", 0))
        if 3 <= price_change <= 10:
            adjustments += 5  # Healthy movement
        elif price_change > 15:
            adjustments -= 5  # Might be exhaustion
        
        # Market behavior factor
        behavior = signal.get("explanation", {}).get("market_behavior", "")
        if behavior in ["accumulation", "breakout"]:
            adjustments += 5
        elif behavior == "manipulation":
            adjustments -= 10
        
        # Calculate final confidence (cap at 95 to maintain humility)
        final_confidence = min(95, max(10, base_confidence + adjustments))
        
        return round(final_confidence, 2)
    
    async def _find_historical_analogies(self, signal: dict, limit: int = 3) -> List[dict]:
        """Find similar historical patterns"""
        current_features = {
            "signal_type": signal.get("signal_type"),
            "price_change": signal.get("price_change_percent", 0),
            "volume_ratio": 1 + (signal.get("volume_change_percent", 0) / 100),
            "market_behavior": signal.get("explanation", {}).get("market_behavior", ""),
            "symbol": signal.get("symbol", "")
        }
        
        similarities = []
        
        for pattern in self.historical_patterns:
            # Calculate similarity score
            similarity = self._calculate_similarity(current_features, pattern)
            
            if similarity > 0.5:  # Only consider reasonably similar patterns
                similarities.append({
                    "similarity_score": round(similarity, 2),
                    "outcome": pattern["outcome"],
                    "price_change_after": pattern["price_change_after"],
                    "date": pattern["date"],
                    "symbol": pattern["symbol"],
                    "timeframe": pattern["timeframe"]
                })
        
        # Sort by similarity and return top matches
        similarities.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        return similarities[:limit]
    
    def _calculate_similarity(self, current: dict, historical: dict) -> float:
        """Calculate similarity between current signal and historical pattern"""
        score = 0.0
        
        # Signal type match
        if current["signal_type"] == historical.get("signal_type"):
            score += 0.2
        
        # Price change similarity (normalized)
        price_diff = abs(current["price_change"] - historical.get("price_change", 0))
        price_similarity = max(0, 1 - price_diff / 20)
        score += price_similarity * self.feature_weights["price_change"]
        
        # Volume ratio similarity
        vol_diff = abs(current["volume_ratio"] - historical.get("volume_ratio", 0))
        vol_similarity = max(0, 1 - vol_diff / 5)
        score += vol_similarity * self.feature_weights["volume_ratio"]
        
        # Market behavior match
        if current["market_behavior"] == historical.get("market_behavior"):
            score += self.feature_weights["market_behavior"]
        
        # Symbol match (same asset tends to behave similarly)
        if current["symbol"] == historical.get("symbol"):
            score += self.feature_weights["exchange"]
        
        return min(1.0, score)
    
    async def _detect_smart_money(self, signal: dict) -> bool:
        """Detect potential smart money activity"""
        volume_ratio = 1 + (signal.get("volume_change_percent", 0) / 100)
        behavior = signal.get("explanation", {}).get("market_behavior", "")
        confidence = signal.get("confidence_score", 0)
        
        # Smart money indicators
        indicators = 0
        
        if volume_ratio > 4:
            indicators += 1
        if behavior in ["accumulation", "distribution"]:
            indicators += 1
        if confidence > 70:
            indicators += 1
        if signal.get("explanation", {}).get("large_orders_detected", False):
            indicators += 1
        
        # Smart money detected if multiple indicators present
        return indicators >= 2
    
    async def _assess_probability(self, signal: dict, confidence: float, analogies: List[dict]) -> dict:
        """Assess probability of signal success"""
        # Base probability from confidence
        base_probability = confidence / 100
        
        # Adjust based on historical analogies
        if analogies:
            success_count = sum(1 for a in analogies if a["outcome"] == "success")
            analogy_success_rate = success_count / len(analogies)
            
            # Blend confidence with historical success rate
            blended_probability = (base_probability * 0.6) + (analogy_success_rate * 0.4)
        else:
            blended_probability = base_probability
        
        # Determine outlook
        if blended_probability > 0.7:
            outlook = "bullish" if signal.get("signal_type") in ["pump", "volume_spike"] else "bearish"
        elif blended_probability > 0.5:
            outlook = "neutral_bullish" if signal.get("signal_type") in ["pump", "volume_spike"] else "neutral_bearish"
        else:
            outlook = "uncertain"
        
        return {
            "success_probability": round(blended_probability * 100, 1),
            "outlook": outlook,
            "risk_level": "low" if blended_probability > 0.7 else "medium" if blended_probability > 0.5 else "high",
            "factors": {
                "confidence_factor": round(base_probability * 100, 1),
                "historical_factor": round((sum(a.get("similarity_score", 0) for a in analogies) / max(len(analogies), 1)) * 100, 1) if analogies else 0
            }
        }
