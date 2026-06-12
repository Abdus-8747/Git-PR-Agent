import os

API_KEY = os.getenv("OPENROUTER_API_KEY")


def use_service(phone:str):
    query = f"SELECT * FROM users WHERE phone = '+91 {phone}'"

    print(query)
    print(API_KEY)

use_service("9266554747")