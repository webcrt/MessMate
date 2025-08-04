# Mess Management System

## Overview

A comprehensive Flask-based web application for managing college/institutional mess operations. The system provides intelligent meal management with ML-powered features including sentiment analysis of feedback, attendance prediction, and automated billing. It supports both student and administrative interfaces with role-based access control.

The application handles meal planning, student meal confirmations, feedback collection with sentiment analysis, billing based on actual consumption, and administrative oversight with analytics dashboards.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask web application with modular route handling
- **Data Storage**: JSON file-based persistence for users, meals, feedback, confirmations, and menu data
- **Authentication**: Session-based authentication with password hashing using Werkzeug security
- **Role-Based Access**: Two-tier system (student/admin) with decorator-based authorization
- **File Management**: Secure file upload handling for meal images with size and type restrictions

### Data Management
- **Data Layer**: Custom DataManager class handling JSON file operations for all entities
- **Models**: Object-oriented design with User, Meal, Feedback, and MealConfirmation classes
- **Storage Structure**: Organized data directory with separate JSON files for each entity type
- **ID Management**: Auto-incrementing ID system for all entities

### Machine Learning Components
- **Sentiment Analysis**: TextBlob-based sentiment analysis for feedback comments
- **Attendance Prediction**: ML models for predicting meal attendance patterns
- **Feedback Analytics**: Automated analysis of feedback trends and sentiment patterns
- **Smart Insights**: Data-driven recommendations for menu optimization

### Frontend Architecture
- **Template Engine**: Jinja2 templating with Bootstrap 5 for responsive design
- **Component Design**: Modular template inheritance with base template
- **Interactive Elements**: Chart.js integration for data visualization
- **User Experience**: Role-specific dashboards with contextual navigation

### Security Architecture
- **Password Security**: Werkzeug password hashing with salt
- **Session Management**: Flask session handling with configurable secret keys
- **File Upload Security**: Filename sanitization and file type validation
- **Access Control**: Decorator-based authentication and authorization

### Application Flow
- **Student Workflow**: Registration → Login → Dashboard → Meal Confirmation → Feedback → Billing
- **Admin Workflow**: Login → Dashboard → Menu Management → Analytics → User Management
- **Data Flow**: Request → Authentication → Data Layer → Business Logic → Response

## External Dependencies

### Core Framework Dependencies
- **Flask**: Web application framework with routing and templating
- **Werkzeug**: WSGI utilities and security functions for password hashing
- **Jinja2**: Template engine (included with Flask)

### Machine Learning Libraries
- **TextBlob**: Natural language processing for sentiment analysis
- **Statistics**: Built-in Python module for statistical calculations

### Frontend Dependencies
- **Bootstrap 5**: CSS framework for responsive design and UI components
- **Font Awesome**: Icon library for consistent iconography
- **Chart.js**: JavaScript charting library for data visualization

### File Handling
- **JSON**: Built-in Python module for data persistence
- **OS/UUID**: File system operations and unique identifier generation
- **Secure Filename**: Werkzeug utility for safe file naming

### Development and Deployment
- **ProxyFix**: Werkzeug middleware for reverse proxy deployment
- **Logging**: Built-in Python logging for debugging and monitoring

### Data Storage
- **File System**: JSON files for data persistence (can be migrated to database later)
- **Upload Directory**: Local file storage for meal images and attachments

Note: The application is designed with a modular architecture that can easily accommodate database integration (such as PostgreSQL with Drizzle ORM) to replace the current JSON file storage system.