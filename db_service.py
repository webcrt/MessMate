from typing import List, Optional
from datetime import datetime
from db_models import db, User, Meal, Feedback, MealConfirmation, Menu
from sqlalchemy.exc import IntegrityError


class DatabaseService:
    """Database service layer for handling all database operations"""
    
    # User management
    def create_user(self, username: str, email: str, password: str, role: str = 'student', name: str = None) -> Optional[User]:
        """Create a new user"""
        try:
            user = User(
                username=username,
                email=email,
                role=role,
                name=name or username
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            return user
        except IntegrityError:
            db.session.rollback()
            return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return User.query.filter_by(username=username).first()
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return User.query.get(user_id)
    
    def get_all_users(self) -> List[User]:
        """Get all users"""
        return User.query.all()
    
    # Meal management
    def create_meal(self, name: str, meal_type: str, date: str, description: str = None, price: float = 50.0) -> Meal:
        """Create a new meal"""
        meal = Meal(
            name=name,
            meal_type=meal_type,
            date=date,
            description=description,
            price=price
        )
        
        db.session.add(meal)
        db.session.commit()
        return meal
    
    def get_meals_by_date(self, date: str) -> List[Meal]:
        """Get meals by date"""
        return Meal.query.filter_by(date=date).all()
    
    def get_meal_by_id(self, meal_id: int) -> Optional[Meal]:
        """Get meal by ID"""
        return Meal.query.get(meal_id)
    
    def update_meal(self, meal_id: int, **kwargs) -> bool:
        """Update a meal"""
        meal = Meal.query.get(meal_id)
        if meal:
            for key, value in kwargs.items():
                if hasattr(meal, key):
                    setattr(meal, key, value)
            db.session.commit()
            return True
        return False
    
    def get_all_meals(self) -> List[Meal]:
        """Get all meals"""
        return Meal.query.all()
    
    # Feedback management
    def create_feedback(self, user_id: int, meal_id: int, rating: int, comment: str = None, photo_path: str = None) -> Feedback:
        """Create new feedback"""
        feedback = Feedback(
            user_id=user_id,
            meal_id=meal_id,
            rating=rating,
            comment=comment,
            photo_path=photo_path
        )
        
        db.session.add(feedback)
        db.session.commit()
        return feedback
    
    def get_feedback_by_meal(self, meal_id: int) -> List[Feedback]:
        """Get feedback for a specific meal"""
        return Feedback.query.filter_by(meal_id=meal_id).all()
    
    def get_all_feedback(self) -> List[Feedback]:
        """Get all feedback"""
        return Feedback.query.all()
    
    def update_feedback_sentiment(self, feedback_id: int, sentiment_score: float) -> bool:
        """Update feedback with sentiment score"""
        feedback = Feedback.query.get(feedback_id)
        if feedback:
            feedback.sentiment_score = sentiment_score
            db.session.commit()
            return True
        return False
    
    # Meal confirmation management
    def create_confirmation(self, user_id: int, meal_id: int, date: str, meal_type: str) -> MealConfirmation:
        """Create meal confirmation"""
        confirmation = MealConfirmation(
            user_id=user_id,
            meal_id=meal_id,
            date=date,
            meal_type=meal_type
        )
        
        db.session.add(confirmation)
        db.session.commit()
        return confirmation
    
    def get_user_confirmations(self, user_id: int, date: str = None) -> List[MealConfirmation]:
        """Get user meal confirmations"""
        query = MealConfirmation.query.filter_by(user_id=user_id)
        if date:
            query = query.filter_by(date=date)
        return query.all()
    
    def get_confirmations_by_date(self, date: str) -> List[MealConfirmation]:
        """Get all confirmations for a specific date"""
        return MealConfirmation.query.filter_by(date=date).all()
    
    def get_user_monthly_confirmations(self, user_id: int, year: int, month: int) -> List[MealConfirmation]:
        """Get user confirmations for a specific month"""
        start_date = f"{year}-{month:02d}-01"
        
        # For end date, handle month overflow
        if month == 12:
            end_date = f"{year + 1}-01-01"
        else:
            end_date = f"{year}-{month + 1:02d}-01"
        
        return MealConfirmation.query.filter(
            MealConfirmation.user_id == user_id,
            MealConfirmation.date >= start_date,
            MealConfirmation.date < end_date
        ).all()
    
    def get_all_confirmations(self) -> List[MealConfirmation]:
        """Get all confirmations"""
        return MealConfirmation.query.all()
    
    # Menu management
    def create_menu_item(self, date: str, meal_type: str, items: str) -> Menu:
        """Create menu item"""
        menu = Menu(
            date=date,
            meal_type=meal_type,
            items=items
        )
        
        db.session.add(menu)
        db.session.commit()
        return menu
    
    def get_menu_by_date_and_type(self, date: str, meal_type: str) -> Optional[Menu]:
        """Get menu by date and meal type"""
        return Menu.query.filter_by(date=date, meal_type=meal_type).first()
    
    def get_all_menu_items(self) -> List[Menu]:
        """Get all menu items"""
        return Menu.query.all()


# Global database service instance
db_service = DatabaseService()