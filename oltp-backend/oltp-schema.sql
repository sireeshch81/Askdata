-- 1. MEMBERS TABLE - Core member information
CREATE TABLE members (
    member_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15),
    date_of_birth DATE,
    address VARCHAR(255),
    city VARCHAR(50),
    state VARCHAR(50),
    zip_code VARCHAR(10),
    annual_income DECIMAL(12,2),
    employment_status ENUM('employed', 'self_employed', 'unemployed', 'retired'),
    member_since DATE,
    member_status ENUM('active', 'inactive', 'suspended') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 2. CREDIT_CARDS TABLE - Credit card details and limits
CREATE TABLE credit_cards (
    card_id INT PRIMARY KEY AUTO_INCREMENT,
    member_id INT NOT NULL,
    card_number VARCHAR(16) NOT NULL, -- Encrypted in production
    card_type ENUM('visa', 'mastercard', 'amex', 'discover'),
    credit_limit DECIMAL(10,2) NOT NULL,
    current_balance DECIMAL(10,2) DEFAULT 0.00,
    available_credit DECIMAL(10,2) GENERATED ALWAYS AS (credit_limit - current_balance) STORED,
    apr_rate DECIMAL(5,4),
    minimum_payment DECIMAL(8,2),
    payment_due_date DATE,
    card_status ENUM('active', 'blocked', 'expired', 'closed') DEFAULT 'active',
    issue_date DATE,
    expiry_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE
);

-- 3. PAYMENT_HISTORY TABLE - Track payment patterns and behavior
CREATE TABLE payment_history (
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    member_id INT NOT NULL,
    card_id INT NOT NULL,
    payment_date DATE NOT NULL,
    payment_amount DECIMAL(10,2) NOT NULL,
    minimum_due DECIMAL(10,2) NOT NULL,
    payment_status ENUM('on_time', 'late', 'missed', 'partial') NOT NULL,
    days_late INT DEFAULT 0,
    late_fee DECIMAL(6,2) DEFAULT 0.00,
    statement_balance DECIMAL(10,2),
    payment_method ENUM('auto_pay', 'online', 'phone', 'mail', 'branch'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE,
    FOREIGN KEY (card_id) REFERENCES credit_cards(card_id) ON DELETE CASCADE
);

-- 4. FINANCIAL_HEALTH_METRICS TABLE - Member's financial health indicators
CREATE TABLE financial_health_metrics (
    metric_id INT PRIMARY KEY AUTO_INCREMENT,
    member_id INT NOT NULL,
    assessment_date DATE NOT NULL,
    credit_score INT,
    debt_to_income_ratio DECIMAL(5,4), -- e.g., 0.3500 for 35%
    credit_utilization_ratio DECIMAL(5,4), -- e.g., 0.2500 for 25%
    payment_reliability_score DECIMAL(5,2), -- Scale 1-100
    savings_balance DECIMAL(12,2),
    checking_balance DECIMAL(12,2),
    total_debt DECIMAL(12,2),
    number_of_accounts INT,
    recent_inquiries INT, -- Last 12 months
    delinquent_accounts INT,
    health_score DECIMAL(5,2), -- Overall financial health (1-100)
    risk_category ENUM('low', 'medium', 'high'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE
);

-- 5. FINANCIAL_PRODUCTS TABLE - Available products for recommendation
CREATE TABLE financial_products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    product_name VARCHAR(100) NOT NULL,
    product_type ENUM('credit_card', 'personal_loan', 'mortgage', 'savings_account', 'cd', 'investment'),
    product_category ENUM('premium', 'standard', 'basic', 'secured'),
    interest_rate DECIMAL(5,4),
    credit_limit_min DECIMAL(10,2),
    credit_limit_max DECIMAL(10,2),
    minimum_income_required DECIMAL(10,2),
    minimum_credit_score INT,
    maximum_debt_to_income DECIMAL(5,4),
    annual_fee DECIMAL(6,2) DEFAULT 0.00,
    rewards_program VARCHAR(100),
    benefits TEXT,
    eligibility_criteria TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 6. PRODUCT_RECOMMENDATIONS TABLE - AI-generated product suggestions
CREATE TABLE product_recommendations (
    recommendation_id INT PRIMARY KEY AUTO_INCREMENT,
    member_id INT NOT NULL,
    product_id INT NOT NULL,
    recommendation_date DATE NOT NULL,
    recommendation_score DECIMAL(5,2), -- Confidence score 1-100
    recommendation_reason TEXT,
    member_health_score DECIMAL(5,2),
    credit_utilization_at_time DECIMAL(5,4),
    payment_reliability_at_time DECIMAL(5,2),
    recommendation_status ENUM('pending', 'accepted', 'declined', 'expired') DEFAULT 'pending',
    expires_at DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES financial_products(product_id) ON DELETE CASCADE
);

-- INDEXES for better query performance
CREATE INDEX idx_members_income ON members(annual_income);
CREATE INDEX idx_members_status ON members(member_status);
CREATE INDEX idx_cards_member_status ON credit_cards(member_id, card_status);
CREATE INDEX idx_payment_history_member_date ON payment_history(member_id, payment_date);
CREATE INDEX idx_payment_history_status ON payment_history(payment_status);
CREATE INDEX idx_health_metrics_member_date ON financial_health_metrics(member_id, assessment_date);
CREATE INDEX idx_health_metrics_score ON financial_health_metrics(health_score);
CREATE INDEX idx_recommendations_member_date ON product_recommendations(member_id, recommendation_date);
CREATE INDEX idx_recommendations_status ON product_recommendations(recommendation_status);

