import sqlite3
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path='prices.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                target_price REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY,
                product_id INTEGER NOT NULL,
                price REAL NOT NULL,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(product_id) REFERENCES products(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY,
                product_id INTEGER NOT NULL,
                old_price REAL,
                new_price REAL,
                alert_sent BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(product_id) REFERENCES products(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_product(self, user_id, title, url, target_price):
        """Add product to user's watchlist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO products (user_id, title, url, target_price)
            VALUES (?, ?, ?, ?)
        ''', (user_id, title, url, target_price))
        conn.commit()
        product_id = cursor.lastrowid
        conn.close()
        return product_id
    
    def record_price(self, product_id, price):
        """Record price for a product"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO price_history (product_id, price)
            VALUES (?, ?)
        ''', (product_id, price))
        conn.commit()
        conn.close()
    
    def get_price_history(self, product_id, days=30):
        """Get price history for a product"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT price, scraped_at FROM price_history
            WHERE product_id = ? AND scraped_at > datetime('now', '-' || ? || ' days')
            ORDER BY scraped_at ASC
        ''', (product_id, days))
        results = cursor.fetchall()
        conn.close()
        return results
    
    def create_alert(self, product_id, old_price, new_price):
        """Create price drop alert"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO alerts (product_id, old_price, new_price)
            VALUES (?, ?, ?)
        ''', (product_id, old_price, new_price))
        conn.commit()
        conn.close()
