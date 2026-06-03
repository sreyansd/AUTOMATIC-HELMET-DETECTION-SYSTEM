CREATE DATABASE helmet_challan;

USE helmet_challan;

CREATE TABLE vehicle_owner (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_number VARCHAR(20) UNIQUE,
    owner_name VARCHAR(100),
    phone VARCHAR(15),
    email VARCHAR(100),
    address TEXT
);

CREATE TABLE violations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_number VARCHAR(20),
    violation_type VARCHAR(50),
    fine_amount INT,
    date_time DATETIME,
    image_path TEXT,
    challan_pdf TEXT,
    status VARCHAR(20)
);