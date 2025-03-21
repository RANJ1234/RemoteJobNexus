
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User:
    def __init__(self):
        self.users = {}
        self.reset_tokens = {}
        
        # Initialize admin user
        self.add_user('admin', 'remotework_admin2025', ['admin'])
    
    def add_user(self, username, password, roles):
        if username not in self.users:
            self.users[username] = {
                'password_hash': generate_password_hash(password),
                'roles': roles,
                'created_at': datetime.now()
            }
            return True
        return False
    
    def verify_password(self, username, password):
        if username in self.users:
            return check_password_hash(self.users[username]['password_hash'], password)
        return False
    
    def change_password(self, username, new_password):
        if username in self.users:
            self.users[username]['password_hash'] = generate_password_hash(new_password)
            return True
        return False
    
    def delete_user(self, username):
        if username in self.users and username != 'admin':
            del self.users[username]
            return True
        return False
    
    def get_user_roles(self, username):
        return self.users.get(username, {}).get('roles', [])
    
    def generate_reset_token(self, username):
        if username in self.users:
            token = generate_password_hash(str(datetime.now()))[-8:]
            self.reset_tokens[token] = {
                'username': username,
                'expires': datetime.now().timestamp() + 3600  # 1 hour expiry
            }
            return token
        return None
    
    def reset_password_with_token(self, token, new_password):
        token_data = self.reset_tokens.get(token)
        if token_data and token_data['expires'] > datetime.now().timestamp():
            username = token_data['username']
            success = self.change_password(username, new_password)
            if success:
                del self.reset_tokens[token]
            return success
        return False
