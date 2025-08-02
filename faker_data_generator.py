"""
Financial Database Data Generator for Windows + VS Code
Generates realistic financial data with proper relational integrity
Run: python generate_financial_data.py
"""

import random
import csv
import os
from datetime import datetime, timedelta

# Simple Faker alternative for Windows compatibility
class SimpleFaker:
    def __init__(self):
        self.first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Robert', 'Lisa', 'James', 'Jennifer', 
                           'William', 'Amanda', 'Richard', 'Ashley', 'Charles', 'Jessica', 'Thomas', 'Michelle', 'Daniel', 'Stephanie',
                           'Matthew', 'Nicole', 'Anthony', 'Elizabeth', 'Mark', 'Helen', 'Donald', 'Deborah', 'Steven', 'Rachel',
                           'Paul', 'Carolyn', 'Andrew', 'Janet', 'Joshua', 'Maria', 'Kenneth', 'Catherine', 'Kevin', 'Frances']
        
        self.last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez',
                          'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin',
                          'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson']
        
        self.cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego',
                      'Dallas', 'San Jose', 'Austin', 'Jacksonville', 'Fort Worth', 'Columbus', 'Charlotte', 'Indianapolis',
                      'San Francisco', 'Seattle', 'Denver', 'Washington', 'Boston', 'Nashville', 'Oklahoma City', 'Las Vegas']
        
        self.states = ['NY', 'CA', 'IL', 'TX', 'AZ', 'PA', 'FL', 'OH', 'NC', 'IN', 'WA', 'CO', 'DC', 'MA', 'TN', 'OK', 'NV']
        
        self.streets = ['Main St', 'Oak Ave', 'Pine Rd', 'Elm St', 'Maple Dr', 'Cedar Ln', 'Park Ave', 'First St', 'Second St',
                       'Washington St', 'Lincoln Ave', 'Jefferson Dr', 'Madison St', 'Adams Ave', 'Jackson St', 'Monroe Dr']
    
    def first_name(self):
        return random.choice(self.first_names)
    
    def last_name(self):
        return random.choice(self.last_names)
    
    def email(self):
        domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'email.com']
        first = self.first_name().lower()
        last = self.last_name().lower()
        domain = random.choice(domains)
        return f"{first}.{last}@{domain}"
    
    def phone_number(self):
        return f"555-{random.randint(1000, 9999)}"
    
    def date_of_birth(self, min_age=18, max_age=80):
        today = datetime.now()
        start_date = today - timedelta(days=max_age * 365)
        end_date = today - timedelta(days=min_age * 365)
        time_between = end_date - start_date
        days_between = time_between.days
        random_days = random.randrange(days_between)
        return (start_date + timedelta(days=random_days)).strftime('%Y-%m-%d')
    
    def address(self):
        number = random.randint(100, 9999)
        street = random.choice(self.streets)
        return f"{number} {street}"
    
    def city(self):
        return random.choice(self.cities)
    
    def state(self):
        return random.choice(self.states)
    
    def zipcode(self):
        return f"{random.randint(10000, 99999)}"
    
    def date_between(self, start_date, end_date):
        # Handle string start_date
        if isinstance(start_date, str):
            if start_date == '-5y':
                start_date = datetime.now() - timedelta(days=5*365)
            elif start_date == '-6m':
                start_date = datetime.now() - timedelta(days=180)
            elif start_date == '-2m':
                start_date = datetime.now() - timedelta(days=60)
            elif start_date == '-1m':
                start_date = datetime.now() - timedelta(days=30)
            elif start_date == 'today':
                start_date = datetime.now()
            else:
                # If it's a date string like '2023-01-15', parse it
                try:
                    start_date = datetime.strptime(start_date, '%Y-%m-%d')
                except:
                    start_date = datetime.now() - timedelta(days=365)
        
        # Handle string end_date
        if isinstance(end_date, str):
            if end_date == 'today':
                end_date = datetime.now()
            elif end_date == '+1m':
                end_date = datetime.now() + timedelta(days=30)
            elif end_date == '+3m':
                end_date = datetime.now() + timedelta(days=90)
            else:
                # If it's a date string, parse it
                try:
                    end_date = datetime.strptime(end_date, '%Y-%m-%d')
                except:
                    end_date = datetime.now()
        
        # Ensure start_date is before end_date
        if start_date > end_date:
            start_date, end_date = end_date, start_date
        
        time_between = end_date - start_date
        days_between = max(1, time_between.days)
        random_days = random.randrange(days_between)
        return (start_date + timedelta(days=random_days)).strftime('%Y-%m-%d')

# Initialize our simple faker
fake = SimpleFaker()
random.seed(42)  # For reproducible results

# Configuration
NUM_MEMBERS = 2000
NUM_PRODUCTS = 50
OUTPUT_DIR = "financial_data"

# Create output directory
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

print("🏦 Starting Financial Database Data Generation...")
print(f"📊 Generating data for {NUM_MEMBERS} members...")
print(f"📁 Output directory: {os.path.abspath(OUTPUT_DIR)}")

# Helper function to write CSV
def write_csv(filename, data, headers):
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)
    print(f"✅ Saved {filename} with {len(data):,} records")
    return filepath

# Helper function for weighted random choice
def weighted_choice(choices, weights):
    total = sum(weights)
    r = random.uniform(0, total)
    upto = 0
    for choice, weight in zip(choices, weights):
        if upto + weight >= r:
            return choice
        upto += weight
    return choices[-1]

# ==========================================
# 1. GENERATE MEMBERS TABLE
# ==========================================
print("\n👥 Generating MEMBERS table...")

members = []
for i in range(1, NUM_MEMBERS + 1):
    # Realistic income distribution
    income_choices = [25000, 45000, 75000, 120000, 200000]
    income_weights = [15, 35, 30, 15, 5]
    income_bracket = weighted_choice(income_choices, income_weights)
    actual_income = income_bracket + random.randint(-5000, 15000)
    actual_income = max(20000, actual_income)  # Minimum income
    
    # Employment status based on income
    if actual_income < 30000:
        emp_choices = ['employed', 'unemployed', 'self_employed']
        emp_weights = [50, 30, 20]
    elif actual_income > 150000:
        emp_choices = ['employed', 'self_employed']
        emp_weights = [80, 20]
    else:
        emp_choices = ['employed', 'self_employed', 'unemployed']
        emp_weights = [85, 12, 3]
    
    emp_status = weighted_choice(emp_choices, emp_weights)
    
    member = {
        'member_id': i,
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'email': f'member{i}@example.com',
        'phone': fake.phone_number(),
        'date_of_birth': fake.date_of_birth(),
        'address': fake.address(),
        'city': fake.city(),
        'state': fake.state(),
        'zip_code': fake.zipcode(),
        'annual_income': round(actual_income, 2),
        'employment_status': emp_status,
        'member_since': fake.date_between('-5y', 'today'),
        'member_status': weighted_choice(['active', 'inactive'], [95, 5])
    }
    members.append(member)

# Save MEMBERS to CSV
members_headers = ['member_id', 'first_name', 'last_name', 'email', 'phone', 'date_of_birth', 
                  'address', 'city', 'state', 'zip_code', 'annual_income', 'employment_status', 
                  'member_since', 'member_status']
write_csv('members.csv', members, members_headers)

# ==========================================
# 2. GENERATE FINANCIAL_PRODUCTS TABLE
# ==========================================
print("\n🏦 Generating FINANCIAL_PRODUCTS table...")

# Predefined realistic products
base_products = [
    {
        'product_id': 1, 'product_name': 'Platinum Rewards Card', 'product_type': 'credit_card', 
        'product_category': 'premium', 'interest_rate': 0.1599, 'credit_limit_min': 10000.00, 
        'credit_limit_max': 50000.00, 'minimum_income_required': 80000.00, 'minimum_credit_score': 750, 
        'maximum_debt_to_income': 0.3000, 'annual_fee': 95.00, 'rewards_program': 'Points & Miles',
        'benefits': 'Airport lounge access, travel insurance', 'eligibility_criteria': 'Excellent credit required'
    },
    {
        'product_id': 2, 'product_name': 'Cashback Plus Card', 'product_type': 'credit_card', 
        'product_category': 'standard', 'interest_rate': 0.1899, 'credit_limit_min': 1000.00, 
        'credit_limit_max': 15000.00, 'minimum_income_required': 40000.00, 'minimum_credit_score': 680, 
        'maximum_debt_to_income': 0.4000, 'annual_fee': 0.00, 'rewards_program': 'Cashback',
        'benefits': '2% cashback on all purchases', 'eligibility_criteria': 'Good credit required'
    },
    {
        'product_id': 3, 'product_name': 'Secured Starter Card', 'product_type': 'credit_card', 
        'product_category': 'secured', 'interest_rate': 0.2199, 'credit_limit_min': 200.00, 
        'credit_limit_max': 5000.00, 'minimum_income_required': 15000.00, 'minimum_credit_score': 500, 
        'maximum_debt_to_income': 0.6000, 'annual_fee': 25.00, 'rewards_program': 'Cashback',
        'benefits': 'Credit building program', 'eligibility_criteria': 'Security deposit required'
    }
]

# Add more products
product_templates = [
    ('Business Gold Card', 'credit_card', 'premium', 0.1399, 15000, 100000, 100000, 780, 0.25, 175),
    ('Student Card', 'credit_card', 'basic', 0.2099, 300, 3000, 0, 600, 0.50, 0),
    ('Travel Rewards Card', 'credit_card', 'premium', 0.1699, 5000, 25000, 60000, 720, 0.35, 69),
    ('Balance Transfer Card', 'credit_card', 'standard', 0.1999, 2000, 20000, 35000, 660, 0.45, 0),
    ('Gas Rewards Card', 'credit_card', 'standard', 0.1849, 1500, 12000, 30000, 640, 0.40, 0),
    ('Personal Loan', 'personal_loan', 'standard', 0.0899, 5000, 50000, 50000, 650, 0.40, 0),
    ('Auto Loan', 'personal_loan', 'standard', 0.0549, 10000, 75000, 40000, 630, 0.45, 0),
    ('Home Equity Loan', 'mortgage', 'standard', 0.0699, 25000, 500000, 75000, 700, 0.35, 0),
    ('High-Yield Savings', 'savings_account', 'premium', 0.0425, 1000, 1000000, 30000, 600, 0.50, 0),
    ('Certificate of Deposit', 'cd', 'standard', 0.0475, 500, 100000, 20000, 580, 0.60, 0)
]

products = base_products.copy()

for i, template in enumerate(product_templates, start=4):
    product = {
        'product_id': i,
        'product_name': template[0],
        'product_type': template[1],
        'product_category': template[2],
        'interest_rate': template[3],
        'credit_limit_min': template[4],
        'credit_limit_max': template[5],
        'minimum_income_required': template[6],
        'minimum_credit_score': template[7],
        'maximum_debt_to_income': template[8],
        'annual_fee': template[9],
        'rewards_program': 'Standard' if template[1] != 'credit_card' else random.choice(['Cashback', 'Points', 'Miles']),
        'benefits': f"Benefits for {template[0]}",
        'eligibility_criteria': f"Standard eligibility for {template[0]}"
    }
    products.append(product)

# Add remaining products to reach NUM_PRODUCTS
while len(products) < NUM_PRODUCTS:
    i = len(products) + 1
    product_types = ['credit_card', 'personal_loan', 'savings_account']
    categories = ['standard', 'premium', 'basic']
    
    product = {
        'product_id': i,
        'product_name': f"Financial Product {i}",
        'product_type': random.choice(product_types),
        'product_category': random.choice(categories),
        'interest_rate': round(random.uniform(0.05, 0.25), 4),
        'credit_limit_min': random.randint(500, 5000),
        'credit_limit_max': random.randint(10000, 100000),
        'minimum_income_required': random.randint(25000, 100000),
        'minimum_credit_score': random.randint(550, 750),
        'maximum_debt_to_income': round(random.uniform(0.3, 0.6), 2),
        'annual_fee': random.choice([0, 25, 50, 95, 150]),
        'rewards_program': random.choice(['None', 'Cashback', 'Points', 'Miles']),
        'benefits': "Standard benefits package",
        'eligibility_criteria': "Standard eligibility requirements"
    }
    products.append(product)

# Save FINANCIAL_PRODUCTS to CSV
products_headers = ['product_id', 'product_name', 'product_type', 'product_category', 'interest_rate',
                   'credit_limit_min', 'credit_limit_max', 'minimum_income_required', 'minimum_credit_score',
                   'maximum_debt_to_income', 'annual_fee', 'rewards_program', 'benefits', 'eligibility_criteria']
write_csv('financial_products.csv', products, products_headers)

# ==========================================
# 3. GENERATE CREDIT_CARDS TABLE
# ==========================================
print("\n💳 Generating CREDIT_CARDS table...")

credit_cards = []
card_id = 1

for member in members:
    # Determine number of cards based on income
    if member['annual_income'] < 30000:
        num_cards = weighted_choice([0, 1], [20, 80])
    elif member['annual_income'] < 60000:
        num_cards = weighted_choice([1, 2], [70, 30])
    elif member['annual_income'] < 100000:
        num_cards = weighted_choice([1, 2, 3], [40, 50, 10])
    else:
        num_cards = weighted_choice([2, 3, 4], [50, 40, 10])
    
    for _ in range(num_cards):
        # Credit limit based on income
        base_limit = member['annual_income'] * random.uniform(0.1, 0.8)
        credit_limit = round(base_limit / 500) * 500  # Round to nearest 500
        credit_limit = max(500, min(credit_limit, 100000))  # Bounds
        
        # Current balance (realistic utilization)
        utilization_choices = [0.0, 0.1, 0.3, 0.5, 0.8, 0.95]
        utilization_weights = [10, 30, 35, 15, 8, 2]
        utilization = weighted_choice(utilization_choices, utilization_weights)
        current_balance = round(credit_limit * utilization, 2)
        
        # Generate realistic card number
        card_type = random.choice(['visa', 'mastercard', 'amex', 'discover'])
        if card_type == 'visa':
            card_number = '4' + ''.join([str(random.randint(0, 9)) for _ in range(15)])
        elif card_type == 'mastercard':
            card_number = '5' + ''.join([str(random.randint(0, 9)) for _ in range(15)])
        elif card_type == 'amex':
            card_number = '3' + ''.join([str(random.randint(0, 9)) for _ in range(14)])
        else:  # discover
            card_number = '6' + ''.join([str(random.randint(0, 9)) for _ in range(15)])
        
        issue_date = fake.date_between(member['member_since'], 'today')
        expiry_year = int(issue_date[:4]) + random.randint(3, 5)
        expiry_date = f"{expiry_year}-{issue_date[5:]}"
        
        card = {
            'card_id': card_id,
            'member_id': member['member_id'],
            'card_number': card_number,
            'card_type': card_type,
            'credit_limit': credit_limit,
            'current_balance': current_balance,
            'apr_rate': round(random.uniform(0.12, 0.25), 4),
            'minimum_payment': round(max(25, current_balance * 0.02), 2),
            'payment_due_date': fake.date_between('today', '+1m'),
            'card_status': weighted_choice(['active', 'blocked', 'expired'], [90, 5, 5]),
            'issue_date': issue_date,
            'expiry_date': expiry_date
        }
        credit_cards.append(card)
        card_id += 1

# Save CREDIT_CARDS to CSV
cards_headers = ['card_id', 'member_id', 'card_number', 'card_type', 'credit_limit', 'current_balance',
                'apr_rate', 'minimum_payment', 'payment_due_date', 'card_status', 'issue_date', 'expiry_date']
write_csv('credit_cards.csv', credit_cards, cards_headers)

# ==========================================
# 4. GENERATE PAYMENT_HISTORY TABLE
# ==========================================
print("\n💰 Generating PAYMENT_HISTORY table...")

payment_history = []
payment_id = 1

# Generate payment history for each card
for card in credit_cards:
    member = next(m for m in members if m['member_id'] == card['member_id'])
    
    # Generate 3-8 payments per card
    num_payments = random.randint(3, 8)
    
    for i in range(num_payments):
        # Payment date in the last 6 months
        payment_date = fake.date_between('-6m', 'today')
        
        # Determine payment behavior based on member profile
        if member['annual_income'] > 80000:
            behavior_choices = ['on_time', 'late']
            behavior_weights = [90, 10]
        elif member['annual_income'] > 40000:
            behavior_choices = ['on_time', 'late', 'partial']
            behavior_weights = [80, 15, 5]
        else:
            behavior_choices = ['on_time', 'late', 'partial', 'missed']
            behavior_weights = [60, 25, 10, 5]
        
        payment_behavior = weighted_choice(behavior_choices, behavior_weights)
        
        # Calculate payment amounts
        statement_balance = random.uniform(card['current_balance'] * 0.5, card['current_balance'] * 1.2)
        minimum_due = max(25, statement_balance * 0.02)
        
        if payment_behavior == 'on_time':
            payment_amount = random.choice([
                minimum_due,  # Minimum payment
                statement_balance * random.uniform(0.3, 0.8),  # Partial payment
                statement_balance  # Full payment
            ])
            days_late = 0
            late_fee = 0.00
        elif payment_behavior == 'late':
            payment_amount = random.uniform(minimum_due, statement_balance)
            days_late = random.randint(1, 30)
            late_fee = 25.00 if days_late > 15 else 0.00
        elif payment_behavior == 'partial':
            payment_amount = random.uniform(minimum_due * 0.5, minimum_due * 0.9)
            days_late = random.randint(0, 10)
            late_fee = 25.00 if days_late > 5 else 0.00
        else:  # missed
            payment_amount = 0.00
            days_late = random.randint(15, 60)
            late_fee = 35.00
        
        payment = {
            'payment_id': payment_id,
            'member_id': card['member_id'],
            'card_id': card['card_id'],
            'payment_date': payment_date,
            'payment_amount': round(payment_amount, 2),
            'minimum_due': round(minimum_due, 2),
            'payment_status': payment_behavior,
            'days_late': days_late,
            'late_fee': late_fee,
            'statement_balance': round(statement_balance, 2),
            'payment_method': random.choice(['auto_pay', 'online', 'phone', 'mail', 'branch'])
        }
        payment_history.append(payment)
        payment_id += 1

# Save PAYMENT_HISTORY to CSV
payment_headers = ['payment_id', 'member_id', 'card_id', 'payment_date', 'payment_amount', 'minimum_due',
                  'payment_status', 'days_late', 'late_fee', 'statement_balance', 'payment_method']
write_csv('payment_history.csv', payment_history, payment_headers)

# ==========================================
# 5. GENERATE FINANCIAL_HEALTH_METRICS TABLE
# ==========================================
print("\n📊 Generating FINANCIAL_HEALTH_METRICS table...")

financial_health_metrics = []

for member in members:
    # Get member's cards and payment history
    member_cards = [c for c in credit_cards if c['member_id'] == member['member_id']]
    member_payments = [p for p in payment_history if p['member_id'] == member['member_id']]
    
    # Calculate metrics
    total_credit_limit = sum(card['credit_limit'] for card in member_cards)
    total_balance = sum(card['current_balance'] for card in member_cards)
    
    # Credit utilization ratio
    credit_utilization = (total_balance / total_credit_limit) if total_credit_limit > 0 else 0
    credit_utilization = min(1.0, credit_utilization)
    
    # Payment reliability score
    if member_payments:
        on_time_payments = sum(1 for p in member_payments if p['payment_status'] == 'on_time')
        payment_reliability = (on_time_payments / len(member_payments)) * 100
    else:
        payment_reliability = 85.0  # Default for new members
    
    # Credit score calculation
    base_score = 650
    
    # Income factor
    if member['annual_income'] > 100000:
        base_score += 100
    elif member['annual_income'] > 60000:
        base_score += 50
    elif member['annual_income'] < 30000:
        base_score -= 50
    
    # Utilization factor
    if credit_utilization < 0.1:
        base_score += 50
    elif credit_utilization < 0.3:
        base_score += 20
    elif credit_utilization > 0.8:
        base_score -= 100
    elif credit_utilization > 0.5:
        base_score -= 50
    
    # Payment reliability factor
    if payment_reliability > 95:
        base_score += 50
    elif payment_reliability > 85:
        base_score += 25
    elif payment_reliability < 70:
        base_score -= 75
    elif payment_reliability < 80:
        base_score -= 40
    
    credit_score = max(300, min(850, base_score + random.randint(-20, 20)))
    
    # Debt to income ratio
    total_debt = total_balance + random.uniform(0, member['annual_income'] * 0.2)
    debt_to_income = total_debt / member['annual_income'] if member['annual_income'] > 0 else 0
    debt_to_income = min(1.0, debt_to_income)
    
    # Calculate overall health score
    health_score = (
        (credit_score / 850) * 40 +  # 40% weight
        ((1 - credit_utilization) * 25) +  # 25% weight
        (payment_reliability / 100 * 20) +  # 20% weight
        ((1 - debt_to_income) * 15)  # 15% weight
    ) * 100
    
    health_score = max(0, min(100, health_score))
    
    # Risk category
    if health_score >= 80:
        risk_category = 'low'
    elif health_score >= 60:
        risk_category = 'medium'
    else:
        risk_category = 'high'
    
    metric = {
        'metric_id': member['member_id'],
        'member_id': member['member_id'],
        'assessment_date': fake.date_between('-1m', 'today'),
        'credit_score': int(credit_score),
        'debt_to_income_ratio': round(debt_to_income, 4),
        'credit_utilization_ratio': round(credit_utilization, 4),
        'payment_reliability_score': round(payment_reliability, 2),
        'savings_balance': round(random.uniform(0, member['annual_income'] * 0.5), 2),
        'checking_balance': round(random.uniform(500, member['annual_income'] * 0.1), 2),
        'total_debt': round(total_debt, 2),
        'number_of_accounts': len(member_cards) + random.randint(1, 3),
        'recent_inquiries': random.randint(0, 5),
        'delinquent_accounts': weighted_choice([0, 1, 2], [85, 12, 3]),
        'health_score': round(health_score, 2),
        'risk_category': risk_category
    }
    financial_health_metrics.append(metric)

# Save FINANCIAL_HEALTH_METRICS to CSV
health_headers = ['metric_id', 'member_id', 'assessment_date', 'credit_score', 'debt_to_income_ratio',
                 'credit_utilization_ratio', 'payment_reliability_score', 'savings_balance', 'checking_balance',
                 'total_debt', 'number_of_accounts', 'recent_inquiries', 'delinquent_accounts', 'health_score', 'risk_category']
write_csv('financial_health_metrics.csv', financial_health_metrics, health_headers)

# ==========================================
# 6. GENERATE PRODUCT_RECOMMENDATIONS TABLE
# ==========================================
print("\n🤖 Generating PRODUCT_RECOMMENDATIONS table...")

product_recommendations = []
recommendation_id = 1

for member in members:
    member_health = next(h for h in financial_health_metrics if h['member_id'] == member['member_id'])
    
    # Generate 1-4 recommendations per member
    num_recommendations = weighted_choice([1, 2, 3, 4], [40, 35, 20, 5])
    
    # Select appropriate products based on member profile
    eligible_products = []
    for product in products:
        # Check eligibility
        if (member['annual_income'] >= product['minimum_income_required'] and
            member_health['credit_score'] >= product['minimum_credit_score'] and
            member_health['debt_to_income_ratio'] <= product['maximum_debt_to_income']):
            eligible_products.append(product)
    
    # If no eligible products, add basic ones
    if not eligible_products:
        eligible_products = [p for p in products if p['product_category'] in ['basic', 'secured']]
    
    # Sample products for recommendations
    recommended_products = random.sample(
        eligible_products, 
        min(num_recommendations, len(eligible_products))
    )
    
    for product in recommended_products:
        # Calculate recommendation score
        base_score = 70
        
        # Income fit
        if member['annual_income'] > product['minimum_income_required'] * 1.5:
            base_score += 15
        elif member['annual_income'] > product['minimum_income_required'] * 1.2:
            base_score += 10
        
        # Credit score fit
        if member_health['credit_score'] > product['minimum_credit_score'] + 50:
            base_score += 15
        elif member_health['credit_score'] > product['minimum_credit_score'] + 20:
            base_score += 10
        
        # Health score bonus
        if member_health['health_score'] > 80:
            base_score += 10
        elif member_health['health_score'] < 50:
            base_score -= 20
        
        recommendation_score = max(0, min(100, base_score + random.randint(-10, 10)))
        
        # Generate recommendation reason
        reasons = []
        if member_health['credit_score'] >= 750:
            reasons.append("excellent credit score")
        elif member_health['credit_score'] >= 680:
            reasons.append("good credit score")
        
        if member['annual_income'] >= 80000:
            reasons.append("high income")
        elif member['annual_income'] >= 50000:
            reasons.append("stable income")
        
        if member_health['credit_utilization_ratio'] < 0.3:
            reasons.append("low credit utilization")
        
        if member_health['payment_reliability_score'] > 90:
            reasons.append("excellent payment history")
        
        recommendation_reason = f"Recommended based on {', '.join(reasons[:2])}" if reasons else "Standard recommendation"
        
        recommendation = {
            'recommendation_id': recommendation_id,
            'member_id': member['member_id'],
            'product_id': product['product_id'],
            'recommendation_date': fake.date_between('-2m', 'today'),
            'recommendation_score': round(recommendation_score, 2),
            'recommendation_reason': recommendation_reason,
            'member_health_score': member_health['health_score'],
            'credit_utilization_at_time': member_health['credit_utilization_ratio'],
            'payment_reliability_at_time': member_health['payment_reliability_score'],
            'recommendation_status': weighted_choice(['pending', 'accepted', 'declined', 'expired'], [40, 25, 25, 10]),
            'expires_at': fake.date_between('today', '+3m')
        }
        product_recommendations.append(recommendation)
        recommendation_id += 1

# Save PRODUCT_RECOMMENDATIONS to CSV
recommendation_headers = ['recommendation_id', 'member_id', 'product_id', 'recommendation_date', 'recommendation_score',
                         'recommendation_reason', 'member_health_score', 'credit_utilization_at_time', 
                         'payment_reliability_at_time', 'recommendation_status', 'expires_at']
write_csv('product_recommendations.csv', product_recommendations, recommendation_headers)

# ==========================================
# SUMMARY AND STATISTICS
# ==========================================
print("\n" + "="*60)
print("🎉 DATA GENERATION COMPLETE!")
print("="*60)
print(f"📁 Output Directory: {os.path.abspath(OUTPUT_DIR)}")
print(f"👥 Members: {len(members):,}")
print(f"💳 Credit Cards: {len(credit_cards):,}")
print(f"💰 Payment Records: {len(payment_history):,}")
print(f"📊 Health Metrics: {len(financial_health_metrics):,}")
print(f"🏦 Financial Products: {len(products):,}")
print(f"🤖 Recommendations: {len(product_recommendations):,}")

print("\n📈 STATISTICS:")
print(f"   • Average cards per member: {len(credit_cards)/len(members):.1f}")
print(f"   • Average payments per card: {len(payment_history)/len(credit_cards):.1f}")
print(f"   • Average recommendations per member: {len(product_recommendations)/len(members):.1f}")

# Risk distribution
risk_counts = {'low': 0, 'medium': 0, 'high': 0}
for metric in financial_health_metrics:
    risk_counts[metric['risk_category']] += 1

print(f"   • Risk Distribution:")
for risk, count in risk_counts.items():
    print(f"     - {risk.title()} Risk: {count:,} members ({count/len(members)*100:.1f}%)")

print("\n📋 FILES CREATED:")
files = [
    "members.csv",
    "credit_cards.csv", 
    "payment_history.csv",
    "financial_health_metrics.csv",
    "financial_products.csv",
    "product_recommendations.csv"
]

for file in files:
    filepath = os.path.join(OUTPUT_DIR, file)
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        print(f"   ✅ {file} ({size:,} bytes)")

print("\n🚀 Ready for review and MySQL import!")
print("💡 Next steps:")
print("   1. Review the CSV files in the 'financial_data' folder")
print("   2. Make any data adjustments in Excel/Google Sheets")
print("   3. Import to MySQL using Workbench's Table Data Import Wizard")
print("   4. Test your AI natural language to SQL queries!")

print(f"\n📍 Files location: {os.path.abspath(OUTPUT_DIR)}")
input("\nPress Enter to exit...")
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta
import csv
import os

# Initialize Faker
fake = Faker()
Faker.seed(42)  # For reproducible results
random.seed(42)

# Configuration
NUM_MEMBERS = 2000
NUM_PRODUCTS = 50
OUTPUT_DIR = "financial_data"

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("🏦 Starting Financial Database Data Generation...")
print(f"📊 Generating data for {NUM_MEMBERS} members...")

# ==========================================
# 1. GENERATE MEMBERS TABLE
# ==========================================
print("\n👥 Generating MEMBERS table...")

members = []
for i in range(1, NUM_MEMBERS + 1):
    # Realistic income distribution
    income_bracket = random.choices(
        [25000, 45000, 75000, 120000, 200000], 
        weights=[15, 35, 30, 15, 5]
    )[0]
    actual_income = income_bracket + random.randint(-5000, 15000)
    actual_income = max(20000, actual_income)  # Minimum income
    
    # Employment status based on income
    if actual_income < 30000:
        emp_status = random.choices(['employed', 'unemployed', 'self_employed'], weights=[50, 30, 20])[0]
    elif actual_income > 150000:
        emp_status = random.choices(['employed', 'self_employed'], weights=[80, 20])[0]
    else:
        emp_status = random.choices(['employed', 'self_employed', 'unemployed'], weights=[85, 12, 3])[0]
    
    member = {
        'member_id': i,
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'email': fake.email(),
        'phone': fake.phone_number()[:15],
        'date_of_birth': fake.date_of_birth(minimum_age=18, maximum_age=80),
        'address': fake.street_address(),
        'city': fake.city(),
        'state': fake.state_abbr(),
        'zip_code': fake.zipcode(),
        'annual_income': round(actual_income, 2),
        'employment_status': emp_status,
        'member_since': fake.date_between(start_date='-5y', end_date='today'),
        'member_status': random.choices(['active', 'inactive'], weights=[95, 5])[0]
    }
    members.append(member)

# Save MEMBERS to CSV
members_df = pd.DataFrame(members)
members_df.to_csv(f"{OUTPUT_DIR}/members.csv", index=False)
print(f"✅ Generated {len(members)} members")

# ==========================================
# 2. GENERATE FINANCIAL_PRODUCTS TABLE
# ==========================================
print("\n🏦 Generating FINANCIAL_PRODUCTS table...")

products = [
    # Credit Cards
    {
        'product_id': 1, 'product_name': 'Platinum Rewards Card', 'product_type': 'credit_card', 
        'product_category': 'premium', 'interest_rate': 0.1599, 'credit_limit_min': 10000.00, 
        'credit_limit_max': 50000.00, 'minimum_income_required': 80000.00, 'minimum_credit_score': 750, 
        'maximum_debt_to_income': 0.3000, 'annual_fee': 95.00, 'rewards_program': 'Points & Miles',
        'benefits': 'Airport lounge access, travel insurance', 'eligibility_criteria': 'Excellent credit required'
    },
    {
        'product_id': 2, 'product_name': 'Cashback Plus Card', 'product_type': 'credit_card', 
        'product_category': 'standard', 'interest_rate': 0.1899, 'credit_limit_min': 1000.00, 
        'credit_limit_max': 15000.00, 'minimum_income_required': 40000.00, 'minimum_credit_score': 680, 
        'maximum_debt_to_income': 0.4000, 'annual_fee': 0.00, 'rewards_program': 'Cashback',
        'benefits': '2% cashback on all purchases', 'eligibility_criteria': 'Good credit required'
    },
    {
        'product_id': 3, 'product_name': 'Secured Starter Card', 'product_type': 'credit_card', 
        'product_category': 'secured', 'interest_rate': 0.2199, 'credit_limit_min': 200.00, 
        'credit_limit_max': 5000.00, 'minimum_income_required': 15000.00, 'minimum_credit_score': 500, 
        'maximum_debt_to_income': 0.6000, 'annual_fee': 25.00, 'rewards_program': 'Cashback',
        'benefits': 'Credit building program', 'eligibility_criteria': 'Security deposit required'
    }
]

# Generate more products programmatically
product_templates = [
    ('Business Gold Card', 'credit_card', 'premium', 0.1399, 15000, 100000, 100000, 780, 0.25, 175),
    ('Student Card', 'credit_card', 'basic', 0.2099, 300, 3000, 0, 600, 0.50, 0),
    ('Travel Rewards Card', 'credit_card', 'premium', 0.1699, 5000, 25000, 60000, 720, 0.35, 69),
    ('Balance Transfer Card', 'credit_card', 'standard', 0.1999, 2000, 20000, 35000, 660, 0.45, 0),
    ('Gas Rewards Card', 'credit_card', 'standard', 0.1849, 1500, 12000, 30000, 640, 0.40, 0),
    ('Personal Loan', 'personal_loan', 'standard', 0.0899, 5000, 50000, 50000, 650, 0.40, 0),
    ('Auto Loan', 'personal_loan', 'standard', 0.0549, 10000, 75000, 40000, 630, 0.45, 0),
    ('Home Equity Loan', 'mortgage', 'standard', 0.0699, 25000, 500000, 75000, 700, 0.35, 0),
    ('Mortgage Refinance', 'mortgage', 'standard', 0.0625, 50000, 1000000, 60000, 680, 0.30, 0),
    ('High-Yield Savings', 'savings_account', 'premium', 0.0425, 1000, 1000000, 30000, 600, 0.50, 0),
    ('Certificate of Deposit', 'cd', 'standard', 0.0475, 500, 100000, 20000, 580, 0.60, 0),
    ('Money Market Account', 'savings_account', 'standard', 0.0385, 2500, 250000, 25000, 620, 0.50, 10),
    ('Investment Account', 'investment', 'premium', 0.0000, 1000, 1000000, 50000, 650, 0.40, 25),
    ('Retirement Savings', 'savings_account', 'premium', 0.0395, 500, 500000, 35000, 580, 0.50, 0),
    ('Premium Checking', 'savings_account', 'premium', 0.0125, 5000, 1000000, 75000, 700, 0.30, 25)
]

for i, template in enumerate(product_templates, start=4):
    product = {
        'product_id': i,
        'product_name': template[0],
        'product_type': template[1],
        'product_category': template[2],
        'interest_rate': template[3],
        'credit_limit_min': template[4],
        'credit_limit_max': template[5],
        'minimum_income_required': template[6],
        'minimum_credit_score': template[7],
        'maximum_debt_to_income': template[8],
        'annual_fee': template[9],
        'rewards_program': 'Standard' if template[1] != 'credit_card' else random.choice(['Cashback', 'Points', 'Miles']),
        'benefits': f"Benefits for {template[0]}",
        'eligibility_criteria': f"Standard eligibility for {template[0]}"
    }
    products.append(product)

# Add remaining products to reach NUM_PRODUCTS
while len(products) < NUM_PRODUCTS:
    i = len(products) + 1
    product = {
        'product_id': i,
        'product_name': f"Financial Product {i}",
        'product_type': random.choice(['credit_card', 'personal_loan', 'savings_account']),
        'product_category': random.choice(['standard', 'premium', 'basic']),
        'interest_rate': round(random.uniform(0.05, 0.25), 4),
        'credit_limit_min': random.randint(500, 5000),
        'credit_limit_max': random.randint(10000, 100000),
        'minimum_income_required': random.randint(25000, 100000),
        'minimum_credit_score': random.randint(550, 750),
        'maximum_debt_to_income': round(random.uniform(0.3, 0.6), 2),
        'annual_fee': random.choice([0, 25, 50, 95, 150]),
        'rewards_program': random.choice(['None', 'Cashback', 'Points', 'Miles']),
        'benefits': f"Standard benefits package",
        'eligibility_criteria': f"Standard eligibility requirements"
    }
    products.append(product)

# Save FINANCIAL_PRODUCTS to CSV
products_df = pd.DataFrame(products)
products_df.to_csv(f"{OUTPUT_DIR}/financial_products.csv", index=False)
print(f"✅ Generated {len(products)} financial products")

# ==========================================
# 3. GENERATE CREDIT_CARDS TABLE
# ==========================================
print("\n💳 Generating CREDIT_CARDS table...")

credit_cards = []
card_id = 1

for member in members:
    # Determine number of cards based on income and credit profile
    if member['annual_income'] < 30000:
        num_cards = random.choices([0, 1], weights=[20, 80])[0]
    elif member['annual_income'] < 60000:
        num_cards = random.choices([1, 2], weights=[70, 30])[0]
    elif member['annual_income'] < 100000:
        num_cards = random.choices([1, 2, 3], weights=[40, 50, 10])[0]
    else:
        num_cards = random.choices([2, 3, 4], weights=[50, 40, 10])[0]
    
    for _ in range(num_cards):
        # Credit limit based on income
        base_limit = member['annual_income'] * random.uniform(0.1, 0.8)
        credit_limit = round(base_limit / 500) * 500  # Round to nearest 500
        credit_limit = max(500, min(credit_limit, 100000))  # Bounds
        
        # Current balance (realistic utilization)
        utilization = random.choices(
            [0.0, 0.1, 0.3, 0.5, 0.8, 0.95], 
            weights=[10, 30, 35, 15, 8, 2]
        )[0]
        current_balance = round(credit_limit * utilization, 2)
        
        # Generate realistic card number
        card_type = random.choice(['visa', 'mastercard', 'amex', 'discover'])
        if card_type == 'visa':
            card_number = '4' + ''.join([str(random.randint(0, 9)) for _ in range(15)])
        elif card_type == 'mastercard':
            card_number = '5' + ''.join([str(random.randint(0, 9)) for _ in range(15)])
        elif card_type == 'amex':
            card_number = '3' + ''.join([str(random.randint(0, 9)) for _ in range(14)])
        else:  # discover
            card_number = '6' + ''.join([str(random.randint(0, 9)) for _ in range(15)])
        
        issue_date = fake.date_between(start_date=member['member_since'], end_date='today')
        expiry_date = issue_date + timedelta(days=random.randint(1095, 1825))  # 3-5 years
        
        card = {
            'card_id': card_id,
            'member_id': member['member_id'],
            'card_number': card_number,
            'card_type': card_type,
            'credit_limit': credit_limit,
            'current_balance': current_balance,
            'apr_rate': round(random.uniform(0.12, 0.25), 4),
            'minimum_payment': round(max(25, current_balance * 0.02), 2),
            'payment_due_date': fake.date_between(start_date='today', end_date='+1m'),
            'card_status': random.choices(['active', 'blocked', 'expired'], weights=[90, 5, 5])[0],
            'issue_date': issue_date,
            'expiry_date': expiry_date
        }
        credit_cards.append(card)
        card_id += 1

# Save CREDIT_CARDS to CSV
credit_cards_df = pd.DataFrame(credit_cards)
credit_cards_df.to_csv(f"{OUTPUT_DIR}/credit_cards.csv", index=False)
print(f"✅ Generated {len(credit_cards)} credit cards")

# ==========================================
# 4. GENERATE PAYMENT_HISTORY TABLE
# ==========================================
print("\n💰 Generating PAYMENT_HISTORY table...")

payment_history = []
payment_id = 1

# Generate 6 months of payment history for each card
for card in credit_cards:
    member = next(m for m in members if m['member_id'] == card['member_id'])
    
    # Generate 3-8 payments per card over the last 6 months
    num_payments = random.randint(3, 8)
    
    for i in range(num_payments):
        # Payment date in the last 6 months
        payment_date = fake.date_between(start_date='-6m', end_date='today')
        
        # Determine payment behavior based on member profile
        if member['annual_income'] > 80000:
            payment_behavior = random.choices(['on_time', 'late'], weights=[90, 10])[0]
        elif member['annual_income'] > 40000:
            payment_behavior = random.choices(['on_time', 'late', 'partial'], weights=[80, 15, 5])[0]
        else:
            payment_behavior = random.choices(['on_time', 'late', 'partial', 'missed'], weights=[60, 25, 10, 5])[0]
        
        # Calculate payment amounts
        statement_balance = random.uniform(card['current_balance'] * 0.5, card['current_balance'] * 1.2)
        minimum_due = max(25, statement_balance * 0.02)
        
        if payment_behavior == 'on_time':
            payment_amount = random.choice([
                minimum_due,  # Minimum payment
                statement_balance * random.uniform(0.3, 0.8),  # Partial payment
                statement_balance  # Full payment
            ])
            days_late = 0
            late_fee = 0.00
        elif payment_behavior == 'late':
            payment_amount = random.uniform(minimum_due, statement_balance)
            days_late = random.randint(1, 30)
            late_fee = 25.00 if days_late > 15 else 0.00
        elif payment_behavior == 'partial':
            payment_amount = random.uniform(minimum_due * 0.5, minimum_due * 0.9)
            days_late = random.randint(0, 10)
            late_fee = 25.00 if days_late > 5 else 0.00
        else:  # missed
            payment_amount = 0.00
            days_late = random.randint(15, 60)
            late_fee = 35.00
        
        payment = {
            'payment_id': payment_id,
            'member_id': card['member_id'],
            'card_id': card['card_id'],
            'payment_date': payment_date,
            'payment_amount': round(payment_amount, 2),
            'minimum_due': round(minimum_due, 2),
            'payment_status': payment_behavior,
            'days_late': days_late,
            'late_fee': late_fee,
            'statement_balance': round(statement_balance, 2),
            'payment_method': random.choice(['auto_pay', 'online', 'phone', 'mail', 'branch'])
        }
        payment_history.append(payment)
        payment_id += 1

# Save PAYMENT_HISTORY to CSV
payment_history_df = pd.DataFrame(payment_history)
payment_history_df.to_csv(f"{OUTPUT_DIR}/payment_history.csv", index=False)
print(f"✅ Generated {len(payment_history)} payment records")

# ==========================================
# 5. GENERATE FINANCIAL_HEALTH_METRICS TABLE
# ==========================================
print("\n📊 Generating FINANCIAL_HEALTH_METRICS table...")

financial_health_metrics = []

for member in members:
    # Get member's cards and payment history
    member_cards = [c for c in credit_cards if c['member_id'] == member['member_id']]
    member_payments = [p for p in payment_history if p['member_id'] == member['member_id']]
    
    # Calculate metrics
    total_credit_limit = sum(card['credit_limit'] for card in member_cards)
    total_balance = sum(card['current_balance'] for card in member_cards)
    
    # Credit utilization ratio
    credit_utilization = (total_balance / total_credit_limit) if total_credit_limit > 0 else 0
    credit_utilization = min(1.0, credit_utilization)
    
    # Payment reliability score based on payment history
    if member_payments:
        on_time_payments = sum(1 for p in member_payments if p['payment_status'] == 'on_time')
        payment_reliability = (on_time_payments / len(member_payments)) * 100
    else:
        payment_reliability = 85.0  # Default for new members
    
    # Credit score based on multiple factors
    base_score = 650
    
    # Income factor
    if member['annual_income'] > 100000:
        base_score += 100
    elif member['annual_income'] > 60000:
        base_score += 50
    elif member['annual_income'] < 30000:
        base_score -= 50
    
    # Utilization factor
    if credit_utilization < 0.1:
        base_score += 50
    elif credit_utilization < 0.3:
        base_score += 20
    elif credit_utilization > 0.8:
        base_score -= 100
    elif credit_utilization > 0.5:
        base_score -= 50
    
    # Payment reliability factor
    if payment_reliability > 95:
        base_score += 50
    elif payment_reliability > 85:
        base_score += 25
    elif payment_reliability < 70:
        base_score -= 75
    elif payment_reliability < 80:
        base_score -= 40
    
    credit_score = max(300, min(850, base_score + random.randint(-20, 20)))
    
    # Debt to income ratio
    total_debt = total_balance + random.uniform(0, member['annual_income'] * 0.2)  # Other debts
    debt_to_income = total_debt / member['annual_income'] if member['annual_income'] > 0 else 0
    debt_to_income = min(1.0, debt_to_income)
    
    # Calculate overall health score
    health_score = (
        (credit_score / 850) * 40 +  # 40% weight
        ((1 - credit_utilization) * 25) +  # 25% weight
        (payment_reliability / 100 * 20) +  # 20% weight
        ((1 - debt_to_income) * 15)  # 15% weight
    ) * 100
    
    health_score = max(0, min(100, health_score))
    
    # Risk category
    if health_score >= 80:
        risk_category = 'low'
    elif health_score >= 60:
        risk_category = 'medium'
    else:
        risk_category = 'high'
    
    metric = {
        'metric_id': member['member_id'],
        'member_id': member['member_id'],
        'assessment_date': fake.date_between(start_date='-1m', end_date='today'),
        'credit_score': int(credit_score),
        'debt_to_income_ratio': round(debt_to_income, 4),
        'credit_utilization_ratio': round(credit_utilization, 4),
        'payment_reliability_score': round(payment_reliability, 2),
        'savings_balance': round(random.uniform(0, member['annual_income'] * 0.5), 2),
        'checking_balance': round(random.uniform(500, member['annual_income'] * 0.1), 2),
        'total_debt': round(total_debt, 2),
        'number_of_accounts': len(member_cards) + random.randint(1, 3),
        'recent_inquiries': random.randint(0, 5),
        'delinquent_accounts': random.choices([0, 1, 2], weights=[85, 12, 3])[0],
        'health_score': round(health_score, 2),
        'risk_category': risk_category
    }
    financial_health_metrics.append(metric)

# Save FINANCIAL_HEALTH_METRICS to CSV
health_metrics_df = pd.DataFrame(financial_health_metrics)
health_metrics_df.to_csv(f"{OUTPUT_DIR}/financial_health_metrics.csv", index=False)
print(f"✅ Generated {len(financial_health_metrics)} health metrics")

# ==========================================
# 6. GENERATE PRODUCT_RECOMMENDATIONS TABLE
# ==========================================
print("\n🤖 Generating PRODUCT_RECOMMENDATIONS table...")

product_recommendations = []
recommendation_id = 1

for member in members:
    member_health = next(h for h in financial_health_metrics if h['member_id'] == member['member_id'])
    
    # Generate 1-4 recommendations per member
    num_recommendations = random.choices([1, 2, 3, 4], weights=[40, 35, 20, 5])[0]
    
    # Select appropriate products based on member profile
    eligible_products = []
    for product in products:
        # Check eligibility
        if (member['annual_income'] >= product['minimum_income_required'] and
            member_health['credit_score'] >= product['minimum_credit_score'] and
            member_health['debt_to_income_ratio'] <= product['maximum_debt_to_income']):
            eligible_products.append(product)
    
    # If no eligible products, add some basic ones
    if not eligible_products:
        eligible_products = [p for p in products if p['product_category'] in ['basic', 'secured']]
    
    # Sample products for recommendations
    recommended_products = random.sample(
        eligible_products, 
        min(num_recommendations, len(eligible_products))
    )
    
    for product in recommended_products:
        # Calculate recommendation score based on fit
        base_score = 70
        
        # Income fit
        if member['annual_income'] > product['minimum_income_required'] * 1.5:
            base_score += 15
        elif member['annual_income'] > product['minimum_income_required'] * 1.2:
            base_score += 10
        
        # Credit score fit
        if member_health['credit_score'] > product['minimum_credit_score'] + 50:
            base_score += 15
        elif member_health['credit_score'] > product['minimum_credit_score'] + 20:
            base_score += 10
        
        # Health score bonus
        if member_health['health_score'] > 80:
            base_score += 10
        elif member_health['health_score'] < 50:
            base_score -= 20
        
        recommendation_score = max(0, min(100, base_score + random.randint(-10, 10)))
        
        # Generate recommendation reason
        reasons = []
        if member_health['credit_score'] >= 750:
            reasons.append("excellent credit score")
        elif member_health['credit_score'] >= 680:
            reasons.append("good credit score")
        
        if member['annual_income'] >= 80000:
            reasons.append("high income")
        elif member['annual_income'] >= 50000:
            reasons.append("stable income")
        
        if member_health['credit_utilization_ratio'] < 0.3:
            reasons.append("low credit utilization")
        
        if member_health['payment_reliability_score'] > 90:
            reasons.append("excellent payment history")
        
        recommendation_reason = f"Recommended based on {', '.join(reasons[:2])}" if reasons else "Standard recommendation"
        
        recommendation = {
            'recommendation_id': recommendation_id,
            'member_id': member['member_id'],
            'product_id': product['product_id'],
            'recommendation_date': fake.date_between(start_date='-2m', end_date='today'),
            'recommendation_score': round(recommendation_score, 2),
            'recommendation_reason': recommendation_reason,
            'member_health_score': member_health['health_score'],
            'credit_utilization_at_time': member_health['credit_utilization_ratio'],
            'payment_reliability_at_time': member_health['payment_reliability_score'],
            'recommendation_status': random.choices(
                ['pending', 'accepted', 'declined', 'expired'], 
                weights=[40, 25, 25, 10]
            )[0],
            'expires_at': fake.date_between(start_date='today', end_date='+3m')
        }
        product_recommendations.append(recommendation)
        recommendation_id += 1

# Save PRODUCT_RECOMMENDATIONS to CSV
recommendations_df = pd.DataFrame(product_recommendations)
recommendations_df.to_csv(f"{OUTPUT_DIR}/product_recommendations.csv", index=False)
print(f"✅ Generated {len(product_recommendations)} product recommendations")

# ==========================================
# SUMMARY AND STATISTICS
# ==========================================
print("\n" + "="*60)
print("🎉 DATA GENERATION COMPLETE!")
print("="*60)
print(f"📁 Output Directory: {OUTPUT_DIR}/")
print(f"👥 Members: {len(members):,}")
print(f"💳 Credit Cards: {len(credit_cards):,}")
print(f"💰 Payment Records: {len(payment_history):,}")
print(f"📊 Health Metrics: {len(financial_health_metrics):,}")
print(f"🏦 Financial Products: {len(products):,}")
print(f"🤖 Recommendations: {len(product_recommendations):,}")
print("\n📈 STATISTICS:")
print(f"   • Average cards per member: {len(credit_cards)/len(members):.1f}")
print(f"   • Average payments per card: {len(payment_history)/len(credit_cards):.1f}")
print(f"   • Average recommendations per member: {len(product_recommendations)/len(members):.1f}")

# Risk distribution
risk_dist = health_metrics_df['risk_category'].value_counts()
print(f"   • Risk Distribution:")
for risk, count in risk_dist.items():
    print(f"     - {risk.title()} Risk: {count:,} members ({count/len(members)*100:.1f}%)")

print("\n📋 FILES CREATED:")
files = [
    "members.csv",
    "credit_cards.csv", 
    "payment_history.csv",
    "financial_health_metrics.csv",
    "financial_products.csv",
    "product_recommendations.csv"
]

for file in files:
    filepath = f"{OUTPUT_DIR}/{file}"
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        print(f"   ✅ {file} ({size:,} bytes)")

print("\n🚀 Ready for database import!")
print("💡 Use MySQL Workbench's Table Data Import Wizard or LOAD DATA INFILE commands")
