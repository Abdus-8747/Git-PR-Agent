import hashlib
def login(username, password):
    # Weak hash
    return hashlib.md5(password.encode()).hexdigest()
