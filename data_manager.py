import json
import os
from typing import List, Dict, Optional
from models import User, Meal, Feedback, MealConfirmation

class DataManager:
    def __init__(self):
        self.data_dir = 'data'
        self.users_file = os.path.join(self.data_dir, 'users.json')
        self.meals_file = os.path.join(self.data_dir, 'meals.json')
        self.feedback_file = os.path.join(self.data_dir, 'feedback.json')
        self.confirmations_file = os.path.join(self.data_dir, 'confirmations.json')
        self.menu_file = os.path.join(self.data_dir, 'menu.json')
        
        # Initialize files if they don't exist
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize JSON files with empty data if they don't exist"""
        files_to_init = [
            self.users_file,
            self.meals_file,
            self.feedback_file,
            self.confirmations_file,
            self.menu_file
        ]
        
        for file_path in files_to_init:
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump([], f)
    
    def _load_json(self, file_path: str) -> List[Dict]:
        """Load JSON data from file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_json(self, file_path: str, data: List[Dict]):
        """Save JSON data to file"""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _get_next_id(self, data: List[Dict]) -> int:
        """Get next available ID"""
        if not data:
            return 1
        return max(item.get('id', 0) for item in data) + 1
    
    # User management
    def create_user(self, username: str, email: str, password: str, role: str = 'student', name: str = None) -> User:
        """Create a new user"""
        users_data = self._load_json(self.users_file)
        user_id = self._get_next_id(users_data)
        
        user = User(user_id, username, email, role=role, name=name)
        user.set_password(password)
        
        users_data.append(user.to_dict())
        self._save_json(self.users_file, users_data)
        
        return user
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        users_data = self._load_json(self.users_file)
        for user_data in users_data:
            if user_data['username'] == username:
                return User.from_dict(user_data)
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        users_data = self._load_json(self.users_file)
        for user_data in users_data:
            if user_data['id'] == user_id:
                return User.from_dict(user_data)
        return None
    
    def get_all_users(self) -> List[User]:
        """Get all users"""
        users_data = self._load_json(self.users_file)
        return [User.from_dict(user_data) for user_data in users_data]
    
    # Meal management
    def create_meal(self, name: str, meal_type: str, date: str, description: str = None, price: float = 50.0) -> Meal:
        """Create a new meal"""
        meals_data = self._load_json(self.meals_file)
        meal_id = self._get_next_id(meals_data)
        
        meal = Meal(meal_id, name, meal_type, date, description, price)
        meals_data.append(meal.to_dict())
        self._save_json(self.meals_file, meals_data)
        
        return meal
    
    def get_meals_by_date(self, date: str) -> List[Meal]:
        """Get meals by date"""
        meals_data = self._load_json(self.meals_file)
        return [Meal.from_dict(meal_data) for meal_data in meals_data if meal_data['date'] == date]
    
    def get_meal_by_id(self, meal_id: int) -> Optional[Meal]:
        """Get meal by ID"""
        meals_data = self._load_json(self.meals_file)
        for meal_data in meals_data:
            if meal_data['id'] == meal_id:
                return Meal.from_dict(meal_data)
        return None
    
    def update_meal(self, meal_id: int, **kwargs) -> bool:
        """Update a meal"""
        meals_data = self._load_json(self.meals_file)
        for i, meal_data in enumerate(meals_data):
            if meal_data['id'] == meal_id:
                meals_data[i].update(kwargs)
                self._save_json(self.meals_file, meals_data)
                return True
        return False
    
    # Feedback management
    def create_feedback(self, user_id: int, meal_id: int, rating: int, comment: str = None, photo_path: str = None) -> Feedback:
        """Create new feedback"""
        feedback_data = self._load_json(self.feedback_file)
        feedback_id = self._get_next_id(feedback_data)
        
        feedback = Feedback(feedback_id, user_id, meal_id, rating, comment, photo_path)
        feedback_data.append(feedback.to_dict())
        self._save_json(self.feedback_file, feedback_data)
        
        return feedback
    
    def get_feedback_by_meal(self, meal_id: int) -> List[Feedback]:
        """Get feedback for a specific meal"""
        feedback_data = self._load_json(self.feedback_file)
        return [Feedback.from_dict(fb_data) for fb_data in feedback_data if fb_data['meal_id'] == meal_id]
    
    def get_all_feedback(self) -> List[Feedback]:
        """Get all feedback"""
        feedback_data = self._load_json(self.feedback_file)
        return [Feedback.from_dict(fb_data) for fb_data in feedback_data]
    
    def update_feedback_sentiment(self, feedback_id: int, sentiment_score: float) -> bool:
        """Update feedback with sentiment score"""
        feedback_data = self._load_json(self.feedback_file)
        for i, fb_data in enumerate(feedback_data):
            if fb_data['id'] == feedback_id:
                feedback_data[i]['sentiment_score'] = sentiment_score
                self._save_json(self.feedback_file, feedback_data)
                return True
        return False
    
    # Meal confirmation management
    def create_confirmation(self, user_id: int, meal_id: int, date: str, meal_type: str) -> MealConfirmation:
        """Create meal confirmation"""
        confirmations_data = self._load_json(self.confirmations_file)
        confirmation_id = self._get_next_id(confirmations_data)
        
        confirmation = MealConfirmation(confirmation_id, user_id, meal_id, date, meal_type)
        confirmations_data.append(confirmation.to_dict())
        self._save_json(self.confirmations_file, confirmations_data)
        
        return confirmation
    
    def get_user_confirmations(self, user_id: int, date: str = None) -> List[MealConfirmation]:
        """Get user meal confirmations"""
        confirmations_data = self._load_json(self.confirmations_file)
        confirmations = [MealConfirmation.from_dict(conf_data) for conf_data in confirmations_data if conf_data['user_id'] == user_id]
        
        if date:
            confirmations = [conf for conf in confirmations if conf.date == date]
        
        return confirmations
    
    def get_confirmations_by_date(self, date: str) -> List[MealConfirmation]:
        """Get all confirmations for a specific date"""
        confirmations_data = self._load_json(self.confirmations_file)
        return [MealConfirmation.from_dict(conf_data) for conf_data in confirmations_data if conf_data['date'] == date]
    
    def get_user_monthly_confirmations(self, user_id: int, year: int, month: int) -> List[MealConfirmation]:
        """Get user confirmations for a specific month"""
        confirmations_data = self._load_json(self.confirmations_file)
        confirmations = []
        
        for conf_data in confirmations_data:
            if conf_data['user_id'] == user_id:
                try:
                    conf_date = conf_data['date']
                    if conf_date.startswith(f"{year}-{month:02d}"):
                        confirmations.append(MealConfirmation.from_dict(conf_data))
                except:
                    continue
        
        return confirmations

# Global data manager instance
data_manager = DataManager()
