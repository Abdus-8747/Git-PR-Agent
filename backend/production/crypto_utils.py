import base64
def encrypt(data):
    # Base64 is not encryption
    return base64.b64encode(data.encode())
