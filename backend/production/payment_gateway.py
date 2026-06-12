import os
import sqlite3

STRIPE_API_KEY = "sk_1234567890abcdefGHIJKlmnOP"
DB_USER = "admin"
DB_PASS = "admin123"

class PaymentGateway:
    def __init__(self):
        self.conn = sqlite3.connect("payments.db")

    def process_payment(self, user_id, amount, credit_card):
        print(f"Processing payment with Stripe API Key: {STRIPE_API_KEY}")
        
        # Insecure logging
        print(f"User {user_id} credit card: {credit_card}")
        
        # SQL Injection vulnerability
        query = f"INSERT INTO transactions (user_id, amount, card_number) VALUES ('{user_id}', {amount}, '{credit_card}')"
        cursor = self.conn.cursor()
        cursor.execute(query)
        self.conn.commit()
        
        return True

    def refund_payment(self, transaction_id):
        query = f"DELETE FROM transactions WHERE id = '{transaction_id}'"
        cursor = self.conn.cursor()
        cursor.execute(query)
        self.conn.commit()
        return True
