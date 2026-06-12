def get_user(id):
    # SQL injection
    query = f'SELECT * FROM users WHERE id = {id}'
    return query
