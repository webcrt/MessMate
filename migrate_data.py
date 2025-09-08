#!/usr/bin/env python3
"""
Data migration script to move data from JSON files to PostgreSQL database
"""
import json
import os
import sys
from datetime import datetime
from app import app
from db_models import db, User, Meal, Feedback, MealConfirmation, Menu


def load_json_file(file_path):
    """Load data from JSON file"""
    if not os.path.exists(file_path):
        print(f"File {file_path} not found, skipping...")
        return []
    
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        print(f"Error loading {file_path}, skipping...")
        return []


def migrate_users():
    """Migrate users from JSON to database"""
    print("Migrating users...")
    users_data = load_json_file('data/users.json')
    migrated = 0
    
    for user_data in users_data:
        # Check if user already exists
        existing_user = User.query.filter_by(username=user_data['username']).first()
        if existing_user:
            print(f"User {user_data['username']} already exists, skipping...")
            continue
        
        try:
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                password_hash=user_data['password_hash'],
                role=user_data.get('role', 'student'),
                name=user_data.get('name'),
                created_at=datetime.fromisoformat(user_data.get('created_at', datetime.now().isoformat()))
            )
            db.session.add(user)
            migrated += 1
        except Exception as e:
            print(f"Error migrating user {user_data.get('username', 'unknown')}: {e}")
    
    db.session.commit()
    print(f"Migrated {migrated} users")


def migrate_meals():
    """Migrate meals from JSON to database"""
    print("Migrating meals...")
    meals_data = load_json_file('data/meals.json')
    migrated = 0
    
    for meal_data in meals_data:
        try:
            meal = Meal(
                name=meal_data['name'],
                meal_type=meal_data['meal_type'],
                date=meal_data['date'],
                description=meal_data.get('description'),
                price=meal_data.get('price', 50.0),
                created_at=datetime.fromisoformat(meal_data.get('created_at', datetime.now().isoformat()))
            )
            db.session.add(meal)
            migrated += 1
        except Exception as e:
            print(f"Error migrating meal {meal_data.get('name', 'unknown')}: {e}")
    
    db.session.commit()
    print(f"Migrated {migrated} meals")


def migrate_feedback():
    """Migrate feedback from JSON to database"""
    print("Migrating feedback...")
    feedback_data = load_json_file('data/feedback.json')
    migrated = 0
    
    for fb_data in feedback_data:
        try:
            feedback = Feedback(
                user_id=fb_data['user_id'],
                meal_id=fb_data['meal_id'],
                rating=fb_data['rating'],
                comment=fb_data.get('comment'),
                photo_path=fb_data.get('photo_path'),
                sentiment_score=fb_data.get('sentiment_score'),
                created_at=datetime.fromisoformat(fb_data.get('created_at', datetime.now().isoformat()))
            )
            db.session.add(feedback)
            migrated += 1
        except Exception as e:
            print(f"Error migrating feedback {fb_data.get('id', 'unknown')}: {e}")
    
    db.session.commit()
    print(f"Migrated {migrated} feedback entries")


def migrate_confirmations():
    """Migrate meal confirmations from JSON to database"""
    print("Migrating meal confirmations...")
    confirmations_data = load_json_file('data/confirmations.json')
    migrated = 0
    
    for conf_data in confirmations_data:
        try:
            confirmation = MealConfirmation(
                user_id=conf_data['user_id'],
                meal_id=conf_data['meal_id'],
                date=conf_data['date'],
                meal_type=conf_data['meal_type'],
                confirmed=conf_data.get('confirmed', True),
                created_at=datetime.fromisoformat(conf_data.get('created_at', datetime.now().isoformat()))
            )
            db.session.add(confirmation)
            migrated += 1
        except Exception as e:
            print(f"Error migrating confirmation {conf_data.get('id', 'unknown')}: {e}")
    
    db.session.commit()
    print(f"Migrated {migrated} meal confirmations")


def migrate_menu():
    """Migrate menu from JSON to database"""
    print("Migrating menu...")
    menu_data = load_json_file('data/menu.json')
    migrated = 0
    
    for menu_item in menu_data:
        try:
            menu = Menu(
                date=menu_item['date'],
                meal_type=menu_item['meal_type'],
                items=menu_item.get('items', ''),
                created_at=datetime.fromisoformat(menu_item.get('created_at', datetime.now().isoformat()))
            )
            db.session.add(menu)
            migrated += 1
        except Exception as e:
            print(f"Error migrating menu item: {e}")
    
    db.session.commit()
    print(f"Migrated {migrated} menu items")


def main():
    """Main migration function"""
    print("Starting data migration from JSON to PostgreSQL...")
    
    with app.app_context():
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        
        # Migrate data in order (users first, then meals, then feedback/confirmations)
        migrate_users()
        migrate_meals()
        migrate_feedback()
        migrate_confirmations()
        migrate_menu()
        
        print("Migration completed successfully!")


if __name__ == '__main__':
    main()