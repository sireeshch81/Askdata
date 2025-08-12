import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from .database_connector import DatabaseConnector

logger = logging.getLogger(__name__)

class DWFeatureCalculator:
    """Extract and calculate ML features from Data Warehouse for similarity clustering"""
    
    def __init__(self, db_connector: DatabaseConnector):
        self.db = db_connector
        
    def calculate_customer_features(self, customer_id: str) -> Optional[Dict]:
        """Calculate comprehensive feature vector for a customer from DW"""
        try:
            # Ensure we're connected to DW
            if self.db.current_source != 'dw':
                self.db.connect('dw')
            
            # Get basic customer profile
            profile = self.db.get_dw_customer_profile(customer_id)
            if not profile:
                logger.warning(f"No profile found for customer {customer_id}")
                return None
            
            # Get financial health metrics
            health_metrics = self.db.get_dw_customer_financial_health(customer_id)
            
            # Get credit card information
            credit_cards = self.db.get_dw_customer_credit_cards(customer_id)
            
            # Get payment history (last 12 months)
            payment_history = self.db.get_dw_customer_payment_history(customer_id, 12)
            
            # Calculate feature vector
            features = self._build_feature_vector(
                profile, health_metrics, credit_cards, payment_history
            )
            
            return features
            
        except Exception as e:
            logger.error(f"Error calculating features for customer {customer_id}: {e}")
            return None
    
    def _build_feature_vector(self, 
                             profile: Dict, 
                             health_metrics: Optional[Dict],
                             credit_cards: pd.DataFrame,
                             payment_history: pd.DataFrame) -> Dict:
        """Build comprehensive feature vector for ML clustering"""
        
        features = {
            'customer_id': profile['customer_id'],
            
            # === DEMOGRAPHIC FEATURES ===
            'credit_score': profile.get('credit_score', 0),
            'annual_income': profile.get('annual_income', 0),
            'risk_category_encoded': self._encode_risk_category(profile.get('risk_category', 'unknown')),
            
            # === FINANCIAL HEALTH FEATURES ===
            'health_score': health_metrics.get('health_score', 0) if health_metrics else 0,
            'utilization_ratio': health_metrics.get('utilization_ratio', 0) if health_metrics else 0,
            'debt_to_income_ratio': health_metrics.get('debt_to_income_ratio', 0) if health_metrics else 0,
            'payment_behavior_score': health_metrics.get('payment_behavior_score', 0) if health_metrics else 0,
            'credit_utilization': health_metrics.get('credit_utilization', 0) if health_metrics else 0,
            'savings_rate': health_metrics.get('savings_rate', 0) if health_metrics else 0,
            
            # === CREDIT CARD FEATURES ===
            'total_credit_cards': len(credit_cards),
            'total_credit_limit': credit_cards['credit_limit'].sum() if not credit_cards.empty else 0,
            'total_credit_balance': credit_cards['current_balance'].sum() if not credit_cards.empty else 0,
            'avg_credit_limit': credit_cards['credit_limit'].mean() if not credit_cards.empty else 0,
            'max_credit_limit': credit_cards['credit_limit'].max() if not credit_cards.empty else 0,
            'avg_interest_rate': credit_cards['interest_rate'].mean() if not credit_cards.empty else 0,
            
            # === PAYMENT BEHAVIOR FEATURES ===
            'payment_frequency': len(payment_history),
            'avg_payment_amount': payment_history['payment_amount'].mean() if not payment_history.empty else 0,
            'total_payment_amount': payment_history['payment_amount'].sum() if not payment_history.empty else 0,
            'payment_consistency': self._calculate_payment_consistency(payment_history),
            'payment_trend': self._calculate_payment_trend(payment_history),
            
            # === DERIVED FEATURES ===
            'income_to_credit_ratio': self._safe_divide(profile.get('annual_income', 0), 
                                                      credit_cards['credit_limit'].sum() if not credit_cards.empty else 1),
            'credit_utilization_total': self._safe_divide(credit_cards['current_balance'].sum() if not credit_cards.empty else 0,
                                                        credit_cards['credit_limit'].sum() if not credit_cards.empty else 1),
            'payment_to_income_ratio': self._safe_divide(payment_history['payment_amount'].sum() if not payment_history.empty else 0,
                                                       profile.get('annual_income', 1)),
            
            # === TENURE FEATURES ===
            'customer_tenure_days': self._calculate_tenure_days(profile.get('date_joined')),
            'avg_days_between_payments': self._calculate_avg_payment_interval(payment_history),
            
            # === CATEGORICAL ENCODED FEATURES ===
            'member_status_encoded': self._encode_member_status(profile.get('member_status', 'unknown'))
        }
        
        # Add income bracket features
        features.update(self._get_income_bracket_features(profile.get('annual_income', 0)))
        
        # Add credit score bracket features  
        features.update(self._get_credit_bracket_features(profile.get('credit_score', 0)))
        
        return features
    
    def _encode_risk_category(self, risk_category: str) -> int:
        """Encode risk category as numeric"""
        risk_mapping = {
            'low': 1,
            'medium': 2, 
            'high': 3,
            'unknown': 0
        }
        return risk_mapping.get(risk_category.lower(), 0)
    
    def _encode_member_status(self, status: str) -> int:
        """Encode member status as numeric"""
        status_mapping = {
            'active': 1,
            'inactive': 0,
            'suspended': -1,
            'unknown': 0
        }
        return status_mapping.get(status.lower(), 0)
    
    def _calculate_payment_consistency(self, payment_history: pd.DataFrame) -> float:
        """Calculate payment consistency score (0-1)"""
        if payment_history.empty or len(payment_history) < 2:
            return 0.0
        
        # Calculate coefficient of variation (lower = more consistent)
        amounts = payment_history['payment_amount']
        cv = amounts.std() / amounts.mean() if amounts.mean() > 0 else float('inf')
        
        # Convert to consistency score (0-1, higher = more consistent)
        consistency = max(0, 1 - min(cv, 2) / 2)  # Cap at 2 for normalization
        return round(consistency, 3)
    
    def _calculate_payment_trend(self, payment_history: pd.DataFrame) -> float:
        """Calculate payment trend (positive = increasing, negative = decreasing)"""
        if payment_history.empty or len(payment_history) < 3:
            return 0.0
        
        # Sort by date and calculate trend
        df_sorted = payment_history.sort_values('payment_date')
        amounts = df_sorted['payment_amount'].values
        
        # Simple linear trend calculation
        x = np.arange(len(amounts))
        trend = np.polyfit(x, amounts, 1)[0]  # Slope of linear fit
        
        return round(float(trend), 2)
    


    def _calculate_tenure_days(self, date_joined) -> int:
        """Calculate customer tenure in days - FIXED DATE HANDLING"""
        if not date_joined:
            return 0
    
        # Handle different date types
        if isinstance(date_joined, str):
            try:
                date_joined = datetime.strptime(date_joined, '%Y-%m-%d').date()
            except:
                return 0
        elif hasattr(date_joined, 'date'):
            # Convert datetime to date
            date_joined = date_joined.date()
    
        # Now both are date objects
        return (datetime.now().date() - date_joined).days


    
    def _calculate_avg_payment_interval(self, payment_history: pd.DataFrame) -> float:
        """Calculate average days between payments"""
        if payment_history.empty or len(payment_history) < 2:
            return 0.0
        
        df_sorted = payment_history.sort_values('payment_date')
        dates = pd.to_datetime(df_sorted['payment_date'])
        intervals = dates.diff().dt.days.dropna()
        
        return round(intervals.mean(), 1) if not intervals.empty else 0.0
    
    def _safe_divide(self, numerator: float, denominator: float) -> float:
        """Safe division with zero handling"""
        if denominator == 0 or denominator is None:
            return 0.0
        return round(numerator / denominator, 4)
    
    def _get_income_bracket_features(self, annual_income: float) -> Dict:
        """Get income bracket one-hot encoded features"""
        brackets = {
            'income_under_30k': annual_income < 30000,
            'income_30k_50k': 30000 <= annual_income < 50000,
            'income_50k_75k': 50000 <= annual_income < 75000,
            'income_75k_100k': 75000 <= annual_income < 100000,
            'income_100k_150k': 100000 <= annual_income < 150000,
            'income_over_150k': annual_income >= 150000
        }
        
        return {k: int(v) for k, v in brackets.items()}
    
    def _get_credit_bracket_features(self, credit_score: int) -> Dict:
        """Get credit score bracket one-hot encoded features"""
        brackets = {
            'credit_poor': credit_score < 580,
            'credit_fair': 580 <= credit_score < 670,
            'credit_good': 670 <= credit_score < 740,
            'credit_very_good': 740 <= credit_score < 800,
            'credit_excellent': credit_score >= 800
        }
        
        return {k: int(v) for k, v in brackets.items()}
    
    def calculate_batch_features(self, customer_ids: List[str]) -> pd.DataFrame:
        """Calculate features for a batch of customers"""
        logger.info(f"Calculating features for {len(customer_ids)} customers")
        
        features_list = []
        successful = 0
        
        for i, customer_id in enumerate(customer_ids):
            if i % 100 == 0:  # Progress logging
                logger.info(f"Processing customer {i+1}/{len(customer_ids)}")
            
            features = self.calculate_customer_features(customer_id)
            if features:
                features_list.append(features)
                successful += 1
        
        logger.info(f"Successfully calculated features for {successful}/{len(customer_ids)} customers")
        
        if features_list:
            return pd.DataFrame(features_list)
        else:
            return pd.DataFrame()
    
    def get_feature_names(self) -> List[str]:
        """Get list of all feature names for consistency"""
        return [
            'customer_id', 'credit_score', 'annual_income', 'risk_category_encoded',
            'health_score', 'utilization_ratio', 'debt_to_income_ratio', 
            'payment_behavior_score', 'credit_utilization', 'savings_rate',
            'total_credit_cards', 'total_credit_limit', 'total_credit_balance',
            'avg_credit_limit', 'max_credit_limit', 'avg_interest_rate',
            'payment_frequency', 'avg_payment_amount', 'total_payment_amount',
            'payment_consistency', 'payment_trend', 'income_to_credit_ratio',
            'credit_utilization_total', 'payment_to_income_ratio',
            'customer_tenure_days', 'avg_days_between_payments', 'member_status_encoded',
            'income_under_30k', 'income_30k_50k', 'income_50k_75k', 
            'income_75k_100k', 'income_100k_150k', 'income_over_150k',
            'credit_poor', 'credit_fair', 'credit_good', 'credit_very_good', 'credit_excellent'
        ]
