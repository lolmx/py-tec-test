CREATE DATABASE dev_database COLLATE utf8mb4_unicode_ci;
USE dev_database;

CREATE TABLE users (
    email VARCHAR(255) PRIMARY KEY NOT NULL,
    password VARCHAR(255) NOT NULL,
    activated TINYINT(1) NOT NULL DEFAULT 0,
    activation_code VARCHAR(4) DEFAULT NULL,
    activation_code_expiration DATETIME DEFAULT NULL
) ENGINE InnoDB;

CREATE DATABASE test_database COLLATE utf8mb4_unicode_ci;
USE test_database;

CREATE TABLE users (
    email VARCHAR(255) PRIMARY KEY NOT NULL,
    password VARCHAR(255) NOT NULL,
    activated TINYINT(1) NOT NULL DEFAULT 0,
    activation_code VARCHAR(4) DEFAULT NULL,
    activation_code_expiration DATETIME DEFAULT NULL
) ENGINE InnoDB;

INSERT INTO users (email, password, activated, activation_code)
VALUES
    ('activated@domain.com', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 1, null),
    ('user@domain.com', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 0, '1234');
