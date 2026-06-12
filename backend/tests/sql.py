API_KEY = "sk-test-123456"


def use_service(email:str):
    query = f"SELECT * FROM users WHERE email = '{email}'"

    print(query)
    print(API_KEY)

use_service("one@gmail.com")