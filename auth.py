# auth.py
''' The auth module handles user authentication and management for the car dealership system.'''
from __future__ import annotations
from typing import Dict, Optional

class User:
    """Represents a user in the system with a specific role."""
    def __init__(self, username: str, password: str, role: str):
        self.username = username
        self.password = password
        self.role_type = role
        self.full_name: Optional[str] = None

    def login(self) -> Optional[str]:
        """Prompts for a password and validates it, returning the user's role on success."""
        pw = input(f"Password for {self.username}: ").strip()
        if pw == self.password:
            print(f"Welcome, {self.role_type} {self.username}!")
            if self.role_type == "Buyer" and not self.full_name:
                self.full_name = input("Please enter your full name for the order: ").strip().title()
            return self.role_type
        else:
            print("Invalid credentials.")
            return None

class UserManager:
    """Manages all user-related operations, including authentication."""
    def __init__(self):
        self._users: Dict[str, User] = {}

    def add_user(self, user: User):
        """Adds a new user to the manager."""
        if user.username.lower() in self._users:
            raise ValueError(f"User '{user.username}' already exists.")
        self._users[user.username.lower()] = user

    def get_user(self, username: str) -> Optional[User]:
        """Retrieves a user by their username."""
        return self._users.get(username.lower())

    def list_users(self) -> list[User]:
        """Returns a list of all users."""
        return list(self._users.values())

    def update_user_role(self, username: str, new_role: str) -> bool:
        """Updates the role of a specified user."""
        user = self.get_user(username)
        if not user:
            print(f"User '{username}' not found.")
            return False
        
        if new_role not in ["Admin", "Seller", "Buyer"]:
            print(f"Invalid role '{new_role}'.")
            return False
            
        user.role_type = new_role
        print(f"User '{username}' role updated to '{new_role}'.")
        return True

    def create_user(self, username: str, password: str, role: str) -> bool:
        """Creates a new user and adds them to the manager."""
        if self.get_user(username):
            print(f"Error: User '{username}' already exists.")
            return False
        
        if role not in ["Admin", "Seller", "Buyer"]:
            print(f"Error: Invalid role '{role}'.")
            return False
            
        new_user = User(username, password, role)
        self.add_user(new_user)
        print(f"Successfully created user '{username}' with role '{role}'.")
        return True
#Created for predefined users, so that new program installs have some users to work with. Until they enter their own.
    def populate_default_users(self):
        """Populates the user manager with default users for the simulation."""
        try:
            self.add_user(User("admin", "1234", "Admin"))
            self.add_user(User("seller", "5678", "Seller"))
            self.add_user(User("buyer", "9999", "Buyer"))
        except ValueError as e:
            print(f"Error populating default users: {e}")

