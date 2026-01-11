CREATE DATABASE cinema_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE cinema_db;

CREATE TABLE movies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    duration INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE shows (
    id INT AUTO_INCREMENT PRIMARY KEY,
    movie_id INT NOT NULL,
    show_time DATETIME NOT NULL,
    price INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (movie_id) REFERENCES movies(id)
        ON DELETE CASCADE
);

CREATE TABLE seats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    show_id INT NOT NULL,
    seat_code VARCHAR(5) NOT NULL,
    status ENUM('FREE','HELD','BOOKED') DEFAULT 'FREE',
    FOREIGN KEY (show_id) REFERENCES shows(id)
        ON DELETE CASCADE,
    UNIQUE(show_id, seat_code)
);

CREATE TABLE seat_holds (
    id INT AUTO_INCREMENT PRIMARY KEY,
    seat_id INT NOT NULL,
    hold_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    FOREIGN KEY (seat_id) REFERENCES seats(id)
        ON DELETE CASCADE
);

CREATE TABLE tickets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    seat_id INT NOT NULL,
    booked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (seat_id) REFERENCES seats(id)
        ON DELETE CASCADE
);

INSERT INTO movies (title, duration)
VALUES
('Ai Thương Ai Mến', 120),
('Nhà Hai Chủ', 115),
('Thiên Đường Máu', 110);

INSERT INTO shows (movie_id, show_time, price)
VALUES (1, NOW(), 75000);

INSERT INTO seats (show_id, seat_code)
VALUES
(1,'A1'),(1,'A2'),(1,'A3'),(1,'A4'),
(1,'B1'),(1,'B2'),(1,'B3'),(1,'B4');

INSERT INTO seat_holds (seat_id, expires_at)
VALUES (1, DATE_ADD(NOW(), INTERVAL 10 MINUTE));

UPDATE seats
SET status = 'HELD'
WHERE id = 1;

UPDATE seats
SET status = 'FREE'
WHERE id IN (
    SELECT seat_id
    FROM seat_holds
    WHERE expires_at < NOW()
);

DELETE FROM seat_holds
WHERE expires_at < NOW();

INSERT INTO tickets (seat_id)
VALUES (1);

UPDATE seats
SET status = 'BOOKED'
WHERE id = 1;

DELETE FROM seat_holds
WHERE seat_id = 1;

SELECT 
COUNT(*) AS total_seats,
SUM(status='BOOKED') AS booked,
ROUND(SUM(status='BOOKED')/COUNT(*)*100,2) AS fill_rate
FROM seats
WHERE show_id = 1;

SELECT 
SUM(s.price) AS revenue
FROM tickets t
JOIN seats se ON t.seat_id = se.id
JOIN shows s ON se.show_id = s.id;