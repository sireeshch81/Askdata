"""
Feature Calculator - Calculates 24 enhanced features for each member
"""
import logging
import pandas as pd
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class FeatureCalculator:
    """Calculates enhanced features for each member"""
    
    def __init__(self, db_connector):
        self.db = db_connector
    
    def calculate_member_features(self, member_id: int) -> Optional[Dict]:
        """Calculate all 24 features for a member"""
        try:
            # Get basic member data
            member_query = """
                SELECT member_id, first_name, last_name, annual_income, 
                       employment_status, member_since, date_of_birth
                FROM members 
                WHERE member_id = %(member_id)s
            """
            member_df = self.db.execute_query(member_query, {'member_id': member_id})
            
            if member_df.empty:
                logger.warning(f"Member {member_id} not found")
                return None
            
            member = member_df.iloc[0]
            
            # Calculate age and tenure
            today = datetime.now()
            birth_date = pd.to_datetime(member['date_of_birth'])
            member_since = pd.to_datetime(member['member_since'])
            age = (today - birth_date).days // 365
            tenure_days = (today - member_since).days
            
            # Get credit card data
            cards_query = """
                SELECT credit_limit, current_balance, apr_rate, card_status
                FROM credit_cards 
                WHERE member_id = %(member_id)s AND card_status = 'active'
            """
            cards_df = self.db.execute_query(cards_query, {'member_id': member_id})
            
            # Credit card metrics
            if not cards_df.empty:
                total_credit_limit = cards_df['credit_limit'].sum()
                total_balance = cards_df['current_balance'].sum()
                avg_apr = cards_df['apr_rate'].mean()
                num_cards = len(cards_df)
                utilization_ratio = total_balance / total_credit_limit if total_credit_limit > 0 else 0
                available_credit = total_credit_limit - total_balance
            else:
                total_credit_limit = 0
                total_balance = 0
                avg_apr = 0.20  # Default APR
                num_cards = 0
                utilization_ratio = 0
                available_credit = 0
            
            # Get payment history
            payment_query = """
                SELECT payment_status, days_late, late_fee, payment_method
                FROM payment_history 
                WHERE member_id = %(member_id)s
                ORDER BY payment_date DESC
                LIMIT 12
            """
            payments_df = self.db.execute_query(payment_query, {'member_id': member_id})
            
            # Payment history metrics
            if not payments_df.empty:
                on_time_payments = (payments_df['payment_status'] == 'on_time').sum()
                on_time_rate = on_time_payments / len(payments_df)
                avg_days_late = payments_df['days_late'].mean()
                total_late_fees = payments_df['late_fee'].sum()
                payment_method_pref = payments_df['payment_method'].mode().iloc[0] if not payments_df['payment_method'].mode().empty else 'online'
            else:
                on_time_rate = 1.0  # Default for new members
                avg_days_late = 0
                total_late_fees = 0
                payment_method_pref = 'online'
            
            # Get financial health metrics
            health_query = """
                SELECT credit_score, debt_to_income_ratio, credit_utilization_ratio,
                       payment_reliability_score, savings_balance, checking_balance,
                       total_debt, health_score, risk_category
                FROM financial_health_metrics 
                WHERE member_id = %(member_id)s
                ORDER BY assessment_date DESC
                LIMIT 1
            """
            health_df = self.db.execute_query(health_query, {'member_id': member_id})
            
            if not health_df.empty:
                health = health_df.iloc[0]
                credit_score = health['credit_score']
                debt_to_income = health['debt_to_income_ratio']
                savings_balance = health['savings_balance']
                checking_balance = health['checking_balance']
                total_debt = health['total_debt']
                health_score = health['health_score']
                risk_category = health['risk_category']
                payment_reliability = health['payment_reliability_score']
            else:
                # Default values for missing health data
                credit_score = 650
                debt_to_income = 0.3
                savings_balance = member['annual_income'] * 0.1
                checking_balance = member['annual_income'] * 0.05
                total_debt = total_balance
                health_score = 75
                risk_category = 'medium'
                payment_reliability = on_time_rate * 100
            
            # Compile all 24 features
            features = {
                # Basic member features (6)
                'member_id': member_id,
                'annual_income': float(member['annual_income']),
                'age': age,
                'member_tenure_days': tenure_days,
                'employment_status': member['employment_status'],
                'member_status': 'active',
                
                # Credit card features (6)
                'total_credit_limit': float(total_credit_limit),
                'total_balance': float(total_balance),
                'utilization_ratio': float(utilization_ratio),
                'num_active_cards': num_cards,
                'avg_apr': float(avg_apr),
                'total_available_credit': float(available_credit),
                
                # Payment history features (4)
                'on_time_payment_rate': float(on_time_rate),
                'avg_days_late': float(avg_days_late),
                'total_late_fees': float(total_late_fees),
                'payment_method_preference': payment_method_pref,
                
                # Financial health features (8)
                'credit_score': int(credit_score),
                'debt_to_income_ratio': float(debt_to_income),
                'payment_reliability_score': float(payment_reliability),
                'savings_balance': float(savings_balance),
                'checking_balance': float(checking_balance),
                'total_debt': float(total_debt),
                'health_score': float(health_score),
                'risk_category': risk_category
            }
            
            return features
            
        except Exception as e:
            logger.error(f"Error calculating features for member {member_id}: {e}")
            return None
