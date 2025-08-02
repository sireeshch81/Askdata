"""
Recommendation Generator - Core recommendation logic
"""
import logging
import pandas as pd
from typing import Dict, List

logger = logging.getLogger(__name__)

class RecommendationGenerator:
    """Generates product recommendations using rule-based logic"""
    
    def __init__(self, db_connector):
        self.db = db_connector
        self.products_df = self._load_products()
    
    def _load_products(self) -> pd.DataFrame:
        """Load all available financial products - USING YOUR EXACT SCHEMA"""
        query = """
            SELECT product_id, product_name, product_type, product_category,
                   minimum_income_required, minimum_credit_score, maximum_debt_to_income,
                   interest_rate, annual_fee, credit_limit_min, credit_limit_max
            FROM financial_products
            WHERE is_active IS NULL OR is_active = 1
        """
        return self.db.execute_query(query)
    
    def generate_recommendations(self, features: Dict, top_n: int = 5) -> List[Dict]:
        """Generate product recommendations for a member"""
        if self.products_df.empty:
            logger.warning("No products available for recommendations")
            return []
        
        recommendations = []
        
        for _, product in self.products_df.iterrows():
            # Check basic eligibility
            eligible = self._check_eligibility(features, product)
            
            # Calculate recommendation score
            score = self._calculate_score(features, product, eligible)
            
            # Generate reasons
            reasons = self._generate_reasons(features, product, eligible)
            
            recommendation = {
                'rank': 0,  # Will be set after sorting
                'product_id': int(product['product_id']),
                'product_name': product['product_name'],
                'product_type': product['product_type'],
                'score': round(float(score), 1),
                'probability': round(min(score / 100.0, 1.0), 3),
                'eligible': eligible,
                'reasons': reasons
            }
            
            recommendations.append(recommendation)
        
        # Sort by score and assign ranks
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        for i, rec in enumerate(recommendations[:top_n]):
            rec['rank'] = i + 1
        
        return recommendations[:top_n]
    
    def _check_eligibility(self, features: Dict, product: pd.Series) -> bool:
        """Check if member is eligible for the product"""
        try:
            # Check minimum credit score
            if pd.notna(product['minimum_credit_score']) and features['credit_score'] < product['minimum_credit_score']:
                return False
            
            # Check minimum income
            if pd.notna(product['minimum_income_required']) and features['annual_income'] < product['minimum_income_required']:
                return False
            
            # Check maximum debt-to-income ratio
            if pd.notna(product['maximum_debt_to_income']) and features['debt_to_income_ratio'] > product['maximum_debt_to_income']:
                return False
            
            return True
        except Exception as e:
            logger.warning(f"Error checking eligibility: {e}")
            return False
    
    def _calculate_score(self, features: Dict, product: pd.Series, eligible: bool) -> float:
        """Calculate recommendation score (0-100)"""
        if not eligible:
            return 0.0
        
        score = 70.0  # Base score for eligible products
        
        # Income factor
        if pd.notna(product['minimum_income_required']) and product['minimum_income_required'] > 0:
            income_ratio = features['annual_income'] / product['minimum_income_required']
            if income_ratio > 2.0:
                score += 15
            elif income_ratio > 1.5:
                score += 10
            elif income_ratio > 1.2:
                score += 5
        
        # Credit score factor
        if pd.notna(product['minimum_credit_score']):
            credit_diff = features['credit_score'] - product['minimum_credit_score']
            if credit_diff > 100:
                score += 15
            elif credit_diff > 50:
                score += 10
            elif credit_diff > 20:
                score += 5
        
        # Utilization factor
        if features['utilization_ratio'] < 0.1:
            score += 10
        elif features['utilization_ratio'] < 0.3:
            score += 5
        elif features['utilization_ratio'] > 0.8:
            score -= 15
        
        # Payment reliability factor
        if features['on_time_payment_rate'] > 0.95:
            score += 10
        elif features['on_time_payment_rate'] > 0.85:
            score += 5
        elif features['on_time_payment_rate'] < 0.7:
            score -= 20
        
        # Risk category factor
        if features['risk_category'] == 'low':
            score += 10
        elif features['risk_category'] == 'high':
            score -= 15
        
        # Health score factor
        if features['health_score'] > 85:
            score += 10
        elif features['health_score'] < 60:
            score -= 10
        
        # Product type specific adjustments
        if product['product_type'] == 'credit_card' and features['num_active_cards'] >= 3:
            score -= 10  # Don't oversell credit cards
        
        return max(0.0, min(100.0, score))
    
    def _generate_reasons(self, features: Dict, product: pd.Series, eligible: bool) -> str:
        """Generate human-readable reasons for the recommendation"""
        if not eligible:
            reasons = []
            if pd.notna(product['minimum_credit_score']) and features['credit_score'] < product['minimum_credit_score']:
                reasons.append(f"Credit score {features['credit_score']} below required {int(product['minimum_credit_score'])}")
            if pd.notna(product['minimum_income_required']) and features['annual_income'] < product['minimum_income_required']:
                reasons.append(f"Income ${features['annual_income']:,.0f} below required ${product['minimum_income_required']:,.0f}")
            if pd.notna(product['maximum_debt_to_income']) and features['debt_to_income_ratio'] > product['maximum_debt_to_income']:
                reasons.append(f"Debt-to-income {features['debt_to_income_ratio']:.1%} above maximum {product['maximum_debt_to_income']:.1%}")
            
            if reasons:
                return "Not eligible: " + "; ".join(reasons)
            else:
                return "Not eligible: Does not meet requirements"
        
        positive_reasons = []
        
        # Credit score reasons
        if features['credit_score'] >= 750:
            positive_reasons.append("excellent credit score")
        elif features['credit_score'] >= 700:
            positive_reasons.append("good credit score")
        
        # Income reasons
        if pd.notna(product['minimum_income_required']) and product['minimum_income_required'] > 0:
            income_ratio = features['annual_income'] / product['minimum_income_required']
            if income_ratio > 2.0:
                positive_reasons.append("high income")
            elif income_ratio > 1.5:
                positive_reasons.append("strong income")
        
        # Utilization reasons
        if features['utilization_ratio'] < 0.2:
            positive_reasons.append("low credit utilization")
        
        # Payment history reasons
        if features['on_time_payment_rate'] > 0.9:
            positive_reasons.append("excellent payment history")
        elif features['on_time_payment_rate'] > 0.8:
            positive_reasons.append("good payment history")
        
        # Risk and health reasons
        if features['risk_category'] == 'low':
            positive_reasons.append("low financial risk")
        
        if not positive_reasons:
            positive_reasons.append("meets all eligibility requirements")
        
        return "; ".join(positive_reasons[:3])  # Limit to top 3 reasons
