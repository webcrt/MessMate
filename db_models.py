import os
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.security import generate_password_hash, check_password_hash


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')
    name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    feedback = db.relationship('Feedback', backref='user', lazy=True, cascade='all, delete-orphan')
    confirmations = db.relationship('MealConfirmation', backref='user', lazy=True, cascade='all, delete-orphan')
    
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
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Meal(db.Model):
    __tablename__ = 'meals'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    meal_type = db.Column(db.String(20), nullable=False)  # breakfast, lunch, dinner
    date = db.Column(db.String(10), nullable=False)  # YYYY-MM-DD format
    description = db.Column(db.Text)
    price = db.Column(db.Float, default=50.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    feedback = db.relationship('Feedback', backref='meal', lazy=True, cascade='all, delete-orphan')
    confirmations = db.relationship('MealConfirmation', backref='meal', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'meal_type': self.meal_type,
            'date': self.date,
            'description': self.description,
            'price': self.price,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Feedback(db.Model):
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    meal_id = db.Column(db.Integer, db.ForeignKey('meals.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-4 scale
    comment = db.Column(db.Text)
    photo_path = db.Column(db.String(255))
    sentiment_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'meal_id': self.meal_id,
            'rating': self.rating,
            'comment': self.comment,
            'photo_path': self.photo_path,
            'sentiment_score': self.sentiment_score,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class MealConfirmation(db.Model):
    __tablename__ = 'meal_confirmations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    meal_id = db.Column(db.Integer, db.ForeignKey('meals.id'), nullable=False)
    date = db.Column(db.String(10), nullable=False)  # YYYY-MM-DD format
    meal_type = db.Column(db.String(20), nullable=False)
    confirmed = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'meal_id': self.meal_id,
            'date': self.date,
            'meal_type': self.meal_type,
            'confirmed': self.confirmed,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Menu(db.Model):
    __tablename__ = 'menu'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), nullable=False)  # YYYY-MM-DD format
    meal_type = db.Column(db.String(20), nullable=False)
    items = db.Column(db.Text)  # JSON string of menu items
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date,
            'meal_type': self.meal_type,
            'items': self.items,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }