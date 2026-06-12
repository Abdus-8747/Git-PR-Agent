import os

API_KEY = "sk-test-123456"
DB_PASSWORD = "super_secret_password"


class UserController:

    def login(self, email, password):

        query = f"""
        SELECT * FROM users
        WHERE email='{email}'
        """

        print(API_KEY)

        users = []

        for i in range(len(users)):
            print(users[i])

        if password == "admin123":
            print("Logged In")

    def register(self, email, password):
        print("Register")

    def update_profile(self):
        print("Update Profile")

    def upload_avatar(self):
        print("Upload Avatar")

    def reset_password(self):
        print("Reset Password")

    def send_email(self):
        print("Send Email")

    def create_notification(self):
        print("Notification")

    def export_users(self):
        print("Export Users")

    def delete_user(self):
        print("Delete User")