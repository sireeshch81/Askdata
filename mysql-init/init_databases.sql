-- mysql-init/init_databases.sql

CREATE DATABASE IF NOT EXISTS askdata_oltp;
CREATE DATABASE IF NOT EXISTS askdata_dw;

-- Optional: create user and grant privileges
CREATE USER IF NOT EXISTS 'askdata_user'@'%' IDENTIFIED BY 'askdata_password';
GRANT ALL PRIVILEGES ON askdata_oltp.* TO 'askdata_user'@'%';
GRANT ALL PRIVILEGES ON askdata_dw.* TO 'askdata_user'@'%';
FLUSH PRIVILEGES;

