-- Designed for analytical queries on member financial health, payment patterns, and product recommendations

-- Dimensions
-- DIM_MEMBER - Member dimension table
CREATE TABLE dim_member (
    member_key INT PRIMARY KEY AUTO_INCREMENT,
    member_id INT NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100),
    phone VARCHAR(15),
    date_of_birth DATE,
    age_group VARCHAR(20), -- Derived: '18-25', '26-35', '36-45', '46-55', '56-65', '65+'
    address VARCHAR(255),
    city VARCHAR(50),
    state VARCHAR(50),
    zip_code VARCHAR(10),
    region VARCHAR(50), -- Derived from state
    annual_income DECIMAL(12,2),
    income_bracket VARCHAR(20), -- Derived: 'Low', 'Medium', 'High', 'Premium'
    employment_status ENUM('employed', 'self_employed', 'unemployed', 'retired'),
    member_since DATE,
    member_tenure_years INT, -- Derived
    member_status ENUM('active', 'inactive', 'suspended'),
    -- SCD Type 2 fields
    effective_date DATE,
    expiry_date DATE,
    is_current BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- DIM_CREDIT_CARD - Credit card dimension table
CREATE TABLE dim_credit_card (
    card_key INT PRIMARY KEY AUTO_INCREMENT,
    card_id INT NOT NULL,
    member_key INT NOT NULL,
    card_type ENUM('visa', 'mastercard', 'amex', 'discover'),
    credit_limit DECIMAL(10,2),
    credit_limit_tier VARCHAR(20), -- Derived: 'Low', 'Medium', 'High', 'Premium'
    apr_rate DECIMAL(5,4),
    apr_category VARCHAR(20), -- Derived: 'Low', 'Medium', 'High'
    card_status ENUM('active', 'blocked', 'expired', 'closed'),
    issue_date DATE,
    expiry_date DATE,
    card_age_months INT, -- Derived
    -- SCD Type 2 fields
    effective_date DATE,
    expiry_date_scd DATE,
    is_current BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (member_key) REFERENCES dim_member(member_key)
);

-- DIM_FINANCIAL_PRODUCT - Financial product dimension table
CREATE TABLE dim_financial_product (
    product_key INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT NOT NULL,
    product_name VARCHAR(100),
    product_type ENUM('credit_card', 'personal_loan', 'mortgage', 'savings_account', 'cd', 'investment'),
    product_category ENUM('premium', 'standard', 'basic', 'secured'),
    interest_rate DECIMAL(5,4),
    interest_rate_tier VARCHAR(20), -- Derived: 'Low', 'Medium', 'High'
    credit_limit_min DECIMAL(10,2),
    credit_limit_max DECIMAL(10,2),
    minimum_income_required DECIMAL(10,2),
    minimum_credit_score INT,
    maximum_debt_to_income DECIMAL(5,4),
    annual_fee DECIMAL(6,2),
    fee_category VARCHAR(20), -- Derived: 'No Fee', 'Low Fee', 'High Fee'
    rewards_program VARCHAR(100),
    has_rewards BOOLEAN, -- Derived
    eligibility_tier VARCHAR(20), -- Derived: 'Easy', 'Medium', 'Strict'
    is_active BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- DIM_DATE - Date dimension table
CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,
    date_value DATE NOT NULL,
    day_of_week INT,
    day_name VARCHAR(10),
    day_of_month INT,
    day_of_year INT,
    week_of_year INT,
    month_number INT,
    month_name VARCHAR(10),
    quarter INT,
    year INT,
    is_weekend BOOLEAN,
    is_holiday BOOLEAN,
    fiscal_year INT,
    fiscal_quarter INT,
    fiscal_month INT
);

-- DIM_PAYMENT_METHOD - Payment method dimension
CREATE TABLE dim_payment_method (
    payment_method_key INT PRIMARY KEY AUTO_INCREMENT,
    payment_method ENUM('auto_pay', 'online', 'phone', 'mail', 'branch'),
    payment_channel VARCHAR(20), -- Derived: 'Digital', 'Traditional'
    convenience_score INT -- Derived: 1-5 scale
);


-- Facts
-- FACT_PAYMENT - Payment transactions fact table
CREATE TABLE fact_payment (
    payment_key INT PRIMARY KEY AUTO_INCREMENT,
    member_key INT NOT NULL,
    card_key INT NOT NULL,
    payment_date_key INT NOT NULL,
    payment_method_key INT NOT NULL,
    
    -- Measures
    payment_amount DECIMAL(10,2) NOT NULL,
    minimum_due DECIMAL(10,2) NOT NULL,
    statement_balance DECIMAL(10,2),
    late_fee DECIMAL(6,2) DEFAULT 0.00,
    days_late INT DEFAULT 0,
    
    -- Derived measures
    payment_ratio DECIMAL(5,4), -- payment_amount / minimum_due
    excess_payment DECIMAL(10,2), -- payment_amount - minimum_due
    
    -- Flags
    is_on_time BOOLEAN,
    is_full_payment BOOLEAN, -- payment >= statement_balance
    is_minimum_payment BOOLEAN, -- payment >= minimum_due
    is_over_payment BOOLEAN, -- payment > statement_balance

    -- Performance Opty in MySQL, but not in PostgreSQL, defaulting to supported
    -- ENUM('on_time', 'late', 'missed', 'partial')
    payment_status CHAR(10) NOT NULL,
    
    created_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (member_key) REFERENCES dim_member(member_key),
    FOREIGN KEY (card_key) REFERENCES dim_credit_card(card_key),
    FOREIGN KEY (payment_date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (payment_method_key) REFERENCES dim_payment_method(payment_method_key)
);

-- FACT_FINANCIAL_HEALTH - Financial health metrics fact table
CREATE TABLE fact_financial_health (
    health_key INT PRIMARY KEY AUTO_INCREMENT,
    member_key INT NOT NULL,
    assessment_date_key INT NOT NULL,
    
    -- Measures
    credit_score INT,
    debt_to_income_ratio DECIMAL(5,4),
    credit_utilization_ratio DECIMAL(5,4),
    payment_reliability_score DECIMAL(5,2),
    savings_balance DECIMAL(12,2),
    checking_balance DECIMAL(12,2),
    total_debt DECIMAL(12,2),
    number_of_accounts INT,
    recent_inquiries INT,
    delinquent_accounts INT,
    health_score DECIMAL(5,2),
    
    -- Derived measures
    total_liquid_assets DECIMAL(12,2), -- savings + checking
    debt_to_assets_ratio DECIMAL(5,4), -- total_debt / total_liquid_assets
    net_worth DECIMAL(12,2), -- total_liquid_assets - total_debt
    
    -- Categorical measures
    -- ENUM('low', 'medium', 'high')
    risk_category CHAR(10),
    credit_score_tier CHAR(12), -- Derived: 'Excellent', 'Good', 'Fair', 'Poor'
    utilization_tier CHAR(12), -- Derived: 'Low', 'Medium', 'High', 'Maxed'
    
    created_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (member_key) REFERENCES dim_member(member_key),
    FOREIGN KEY (assessment_date_key) REFERENCES dim_date(date_key)
);

-- FACT_PRODUCT_RECOMMENDATION - Product recommendations fact table
CREATE TABLE fact_product_recommendation (
    recommendation_key INT PRIMARY KEY AUTO_INCREMENT,
    member_key INT NOT NULL,
    product_key INT NOT NULL,
    recommendation_date_key INT NOT NULL,
    expires_date_key INT,
    
    -- Measures
    recommendation_score DECIMAL(5,2),
    member_health_score DECIMAL(5,2),
    credit_utilization_at_time DECIMAL(5,4),
    payment_reliability_at_time DECIMAL(5,2),
    
    -- Derived measures
    recommendation_tier CHAR(20), -- Derived from score: 'High', 'Medium', 'Low'
    days_to_expiry INT, -- Calculated from expires_at
    
    -- Flags
    is_expired BOOLEAN,
    is_high_confidence BOOLEAN, -- recommendation_score > 80

    -- ENUM('pending', 'accepted', 'declined', 'expired')
    recommendation_status CHAR(10),
    
    created_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (member_key) REFERENCES dim_member(member_key),
    FOREIGN KEY (product_key) REFERENCES dim_financial_product(product_key),
    FOREIGN KEY (recommendation_date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (expires_date_key) REFERENCES dim_date(date_key)
);

-- FACT_CREDIT_CARD_BALANCE - Monthly credit card balance snapshots
CREATE TABLE fact_credit_card_balance (
    balance_key INT PRIMARY KEY AUTO_INCREMENT,
    member_key INT NOT NULL,
    card_key INT NOT NULL,
    snapshot_date_key INT NOT NULL,
    
    -- Measures
    credit_limit DECIMAL(10,2),
    current_balance DECIMAL(10,2),
    available_credit DECIMAL(10,2),
    minimum_payment DECIMAL(8,2),
    
    -- Derived measures
    utilization_ratio DECIMAL(5,4), -- current_balance / credit_limit
    utilization_tier CHAR(12), -- Derived: 'Low', 'Medium', 'High', 'Maxed'
    balance_trend CHAR(20), -- Derived: 'Increasing', 'Decreasing', 'Stable'
    
    -- Flags
    is_over_limit BOOLEAN,
    is_high_utilization BOOLEAN, -- > 80%
    is_maxed_out BOOLEAN, -- > 95%
    
    created_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (member_key) REFERENCES dim_member(member_key),
    FOREIGN KEY (card_key) REFERENCES dim_credit_card(card_key),
    FOREIGN KEY (snapshot_date_key) REFERENCES dim_date(date_key)
);


-- Indexes
-- Dimension table indexes
CREATE INDEX idx_dim_member_id ON dim_member(member_id);
CREATE INDEX idx_dim_member_income ON dim_member(annual_income);
CREATE INDEX idx_dim_member_status ON dim_member(member_status);
CREATE INDEX idx_dim_card_member ON dim_credit_card(member_key);
CREATE INDEX idx_dim_card_type ON dim_credit_card(card_type);
CREATE INDEX idx_dim_product_type ON dim_financial_product(product_type);
CREATE INDEX idx_dim_date_year_month ON dim_date(year, month_number);

-- Fact table indexes
CREATE INDEX idx_fact_payment_member_date ON fact_payment(member_key, payment_date_key);
CREATE INDEX idx_fact_payment_card_date ON fact_payment(card_key, payment_date_key);
CREATE INDEX idx_fact_payment_status ON fact_payment(payment_status);
CREATE INDEX idx_fact_health_member_date ON fact_financial_health(member_key, assessment_date_key);
CREATE INDEX idx_fact_health_score ON fact_financial_health(health_score);
CREATE INDEX idx_fact_recommendation_member_date ON fact_product_recommendation(member_key, recommendation_date_key);
CREATE INDEX idx_fact_recommendation_product ON fact_product_recommendation(product_key);
CREATE INDEX idx_fact_balance_member_date ON fact_credit_card_balance(member_key, snapshot_date_key);
CREATE INDEX idx_fact_balance_card_date ON fact_credit_card_balance(card_key, snapshot_date_key);

-- Views for analytical queries
-- Member payment behavior summary
CREATE VIEW vw_member_payment_summary AS
SELECT 
    dm.member_id,
    dm.first_name,
    dm.last_name,
    dm.income_bracket,
    dm.employment_status,
    COUNT(fp.payment_key) as total_payments,
    AVG(fp.payment_amount) as avg_payment_amount,
    SUM(CASE WHEN fp.is_on_time = 1 THEN 1 ELSE 0 END) / COUNT(*) as on_time_rate,
    SUM(fp.late_fee) as total_late_fees,
    AVG(fp.days_late) as avg_days_late
FROM dim_member dm
JOIN fact_payment fp ON dm.member_key = fp.member_key
WHERE dm.is_current = 1
GROUP BY dm.member_key, dm.member_id, dm.first_name, dm.last_name, dm.income_bracket, dm.employment_status;

-- Product recommendation success rate
CREATE VIEW vw_product_recommendation_metrics AS
SELECT 
    dp.product_name,
    dp.product_type,
    dp.product_category,
    COUNT(fpr.recommendation_key) as total_recommendations,
    SUM(CASE WHEN fpr.recommendation_status = 'accepted' THEN 1 ELSE 0 END) as accepted_count,
    SUM(CASE WHEN fpr.recommendation_status = 'accepted' THEN 1 ELSE 0 END) / COUNT(*) as acceptance_rate,
    AVG(fpr.recommendation_score) as avg_recommendation_score
FROM dim_financial_product dp
JOIN fact_product_recommendation fpr ON dp.product_key = fpr.product_key
GROUP BY dp.product_key, dp.product_name, dp.product_type, dp.product_category;

-- Member financial health trends
CREATE VIEW vw_member_health_trends AS
SELECT 
    dm.member_id,
    dm.first_name,
    dm.last_name,
    dd.year,
    dd.month_name,
    AVG(ffh.health_score) as avg_health_score,
    AVG(ffh.credit_score) as avg_credit_score,
    AVG(ffh.debt_to_income_ratio) as avg_debt_to_income,
    AVG(ffh.credit_utilization_ratio) as avg_credit_utilization
FROM dim_member dm
JOIN fact_financial_health ffh ON dm.member_key = ffh.member_key
JOIN dim_date dd ON ffh.assessment_date_key = dd.date_key
WHERE dm.is_current = 1
GROUP BY dm.member_key, dm.member_id, dm.first_name, dm.last_name, dd.year, dd.month_number, dd.month_name
ORDER BY dm.member_id, dd.year, dd.month_number;