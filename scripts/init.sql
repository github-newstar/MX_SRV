# 数据库初始化脚本

CREATE DATABASE IF NOT EXISTS user_srv CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE user_srv;

-- 用户表
CREATE TABLE IF NOT EXISTS user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mobile VARCHAR(20) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    nick_name VARCHAR(20) DEFAULT NULL,
    head_url VARCHAR(200) DEFAULT NULL,
    birthday DATE DEFAULT NULL,
    address VARCHAR(200) DEFAULT NULL,
    `desc` TEXT DEFAULT NULL,
    gender ENUM('male', 'female') DEFAULT NULL,
    role INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_mobile (mobile),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;