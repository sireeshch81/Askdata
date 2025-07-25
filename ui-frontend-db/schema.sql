CREATE DATABASE IF NOT EXISTS mydb;
USE mydb;

-- User table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Role table
CREATE TABLE roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
);

-- User-Role association table
CREATE TABLE user_roles (
    user_id INT NOT NULL,
    role_id INT NOT NULL,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

INSERT INTO roles (role_name, description) VALUES
    --('admin', 'Administrator with full permissions'),
    --('user', 'Regular user with standard access'),
    --('moderator', 'User with moderation capabilities');
    ('DW_USER', 'User can query DW only'),
    ('OPS_USER', 'User can query oltp only'),
    ('DOC_USER', 'User can query document DB only'),
    ('READONLY', 'User can query DW only'),
    ('DW_USER', 'User can query DW only')


INSERT INTO users (username, password, email) VALUES
    ('alice', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 'alice@example.com'),
    ('bob', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 'bob@example.com'),
    ('carol', '713bfda78870bf9d1b261f565286f85e97ee614efe5f0faf7c34e7ca4f65baca', 'carol@example.com');


INSERT INTO user_roles (user_id, role_id) VALUES
    (1, 2), -- alice is a user
    (2, 2), -- bob is a user
    (3, 1), -- carol is admin
    (3, 2), -- carol is also a user
    (2, 3); -- bob is also a moderator


-- Companies table
CREATE TABLE companies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- Industries table
CREATE TABLE industries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    industry_name VARCHAR(100) NOT NULL UNIQUE
);

-- Countries table
CREATE TABLE countries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    country_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE sales_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    industry_id INT NOT NULL,
    country_id INT NOT NULL,
    report_date DATE NOT NULL,
    sales_amount DECIMAL(15, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id),
    FOREIGN KEY (industry_id) REFERENCES industries(id),
    FOREIGN KEY (country_id) REFERENCES countries(id)
);

-- Sample companies
INSERT INTO companies (name) VALUES ('Acme Inc.'), ('BetaCorp'), ('GlobalTech');

-- Sample industries
INSERT INTO industries (industry_name) VALUES ('Software'), ('Manufacturing'), ('Retail');

-- Sample countries
INSERT INTO countries (country_name) VALUES ('United States'), ('France'), ('India');

-- Sample sales reports (assuming IDs for Acme Inc./Software/US are all 1)
INSERT INTO sales_reports (company_id, industry_id, country_id, report_date, sales_amount, currency) VALUES
    (1, 1, 1, '2024-01-31', 120000.00, 'USD'),
    (2, 2, 2, '2024-01-31', 98500.00, 'EUR'),
    (3, 1, 3, '2024-01-31', 57000.00, 'INR');