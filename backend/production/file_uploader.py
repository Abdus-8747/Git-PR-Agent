import os
def upload(filename, content):
    # Path traversal risk
    with open(filename, 'w') as f:
        f.write(content)
