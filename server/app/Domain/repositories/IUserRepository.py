from abc import ABC, abstractmethod
from typing import List, Optional
from app.Domain.models.User import User

class IUserRepository(ABC):
    
    @abstractmethod
    def get_all(self) -> List[User]:
        """Returns all users."""
        pass
    
    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Returns users by ID"""
        pass
    
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        """Returns a user by email."""
        pass
    
    @abstractmethod
    def create(self, user: User) -> User:
        """Creates a new user"""
        pass
    
    @abstractmethod
    def update(self, user: User) -> User:
        """Updates the user"""
        pass
    
    @abstractmethod
    def delete(self, user_id: int) -> bool:
        """Deletes the user"""
        pass
    
    @abstractmethod
    def save(self) -> None:
        """Saves changes to the database."""
        pass