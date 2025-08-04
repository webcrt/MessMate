from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    def __init__(self, user_id, username, email, password_hash=None, role='student', name=None):
        self.id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role  # 'student' or 'admin'
        self.name = name or username
        self.created_at = datetime.now().isoformat()
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'role': self.role,
            'name': self.name,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        user = cls(
            data['id'],
            data['username'],
            data['email'],
            data['password_hash'],
            data.get('role', 'student'),
            data.get('name')
        )
        user.created_at = data.get('created_at', datetime.now().isoformat())
        return user

class Meal:
    def __init__(self, meal_id, name, meal_type, date, description=None, price=50.0):
        self.id = meal_id
        self.name = name
        self.meal_type = meal_type  # 'breakfast', 'lunch', 'dinner'
        self.date = date
        self.description = description
        self.price = price
        self.created_at = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'meal_type': self.meal_type,
            'date': self.date,
            'description': self.description,
            'price': self.price,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        meal = cls(
            data['id'],
            data['name'],
            data['meal_type'],
            data['date'],
            data.get('description'),
            data.get('price', 50.0)
        )
        meal.created_at = data.get('created_at', datetime.now().isoformat())
        return meal

class Feedback:
    def __init__(self, feedback_id, user_id, meal_id, rating, comment=None, photo_path=None):
        self.id = feedback_id
        self.user_id = user_id
        self.meal_id = meal_id
        self.rating = rating  # 1-4 (Bad, Average, Good, Excellent)
        self.comment = comment
        self.photo_path = photo_path
        self.sentiment_score = None
        self.created_at = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'meal_id': self.meal_id,
            'rating': self.rating,
            'comment': self.comment,
            'photo_path': self.photo_path,
            'sentiment_score': self.sentiment_score,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        feedback = cls(
            data['id'],
            data['user_id'],
            data['meal_id'],
            data['rating'],
            data.get('comment'),
            data.get('photo_path')
        )
        feedback.sentiment_score = data.get('sentiment_score')
        feedback.created_at = data.get('created_at', datetime.now().isoformat())
        return feedback

class MealConfirmation:
    def __init__(self, confirmation_id, user_id, meal_id, date, meal_type, confirmed=True):
        self.id = confirmation_id
        self.user_id = user_id
        self.meal_id = meal_id
        self.date = date
        self.meal_type = meal_type
        self.confirmed = confirmed
        self.created_at = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'meal_id': self.meal_id,
            'date': self.date,
            'meal_type': self.meal_type,
            'confirmed': self.confirmed,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        confirmation = cls(
            data['id'],
            data['user_id'],
            data['meal_id'],
            data['date'],
            data['meal_type'],
            data.get('confirmed', True)
        )
        confirmation.created_at = data.get('created_at', datetime.now().isoformat())
        return confirmation
