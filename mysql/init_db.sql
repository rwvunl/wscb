-- init_db.sql

CREATE DATABASE IF NOT EXISTS wscb_db;
USE wscb_db;

CREATE TABLE IF NOT EXISTS user (
    username VARCHAR(256) PRIMARY KEY,
    userpassword VARCHAR(512) NOT NULL,
    usersalt CHAR(32) NOT NULL,
    UNIQUE (username),
    INDEX (username)
);

CREATE TABLE IF NOT EXISTS url_mapping (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(256) NOT NULL,
    short_url VARCHAR(512) NOT NULL,
    long_url VARCHAR(512) NOT NULL,
    UNIQUE (id),
    INDEX (username)
);
