import os
import uuid
import csv
import io
from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, session, flash, jsonify, make_response
from werkzeug.utils import secure_filename
from app import app
from data_manager import data_manager
from ml_models import sentiment_analyzer, attendance_predictor, feedback_analyzer
import logging

# Helper functions
def login_required(f):
    """Decorator to require login"""
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

def admin_required(f):
    """Decorator to require admin privileges"""
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        
        user = data_manager.get_user_by_id(session['user_id'])
        if not user or user.role != 'admin':
            flash('Admin privileges required.', 'error')
            return redirect(url_for('student_dashboard'))
        
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        role = request.form.get('role', 'student')
        
        # Validation
        if not all([username, email, password, name]):
            flash('All fields are required.', 'error')
            return render_template('register.html')
        
        # Check if user already exists
        if data_manager.get_user_by_username(username):
            flash('Username already exists.', 'error')
            return render_template('register.html')
        
        # Create user
        try:
            user = data_manager.create_user(username, email, password, role, name)
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            logging.error(f"Registration error: {e}")
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not all([username, password]):
            flash('Username and password are required.', 'error')
            return render_template('login.html')
        
        user = data_manager.get_user_by_username(username)
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            
            flash(f'Welcome back, {user.name}!', 'success')
            
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/student_dashboard')
@login_required
def student_dashboard():
    """Student dashboard"""
    user = data_manager.get_user_by_id(session['user_id'])
    if user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    
    # Get today's date
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Get today's meals
    today_meals = data_manager.get_meals_by_date(today)
    
    # Get user's confirmations for today
    user_confirmations = data_manager.get_user_confirmations(user.id, today)
    confirmed_meal_types = [conf.meal_type for conf in user_confirmations]
    
    # Get upcoming meals (next 3 days)
    upcoming_meals = []
    for i in range(1, 4):
        future_date = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
        future_meals = data_manager.get_meals_by_date(future_date)
        if future_meals:
            upcoming_meals.extend(future_meals)
    
    return render_template('student_dashboard.html', 
                         user=user, 
                         today_meals=today_meals,
                         confirmed_meal_types=confirmed_meal_types,
                         upcoming_meals=upcoming_meals,
                         today=today)

@app.route('/admin_dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    user = data_manager.get_user_by_id(session['user_id'])
    
    # Get today's date
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Get today's meals and confirmations
    today_meals = data_manager.get_meals_by_date(today)
    today_confirmations = data_manager.get_confirmations_by_date(today)
    
    # Calculate attendance statistics
    attendance_stats = {}
    for meal in today_meals:
        meal_confirmations = [conf for conf in today_confirmations if conf.meal_type == meal.meal_type]
        attendance_stats[meal.meal_type] = len(meal_confirmations)
    
    # Get recent feedback
    all_feedback = data_manager.get_all_feedback()
    recent_feedback = sorted(all_feedback, key=lambda x: x.created_at, reverse=True)[:5]
    
    # Get meal performance analytics
    meal_analytics = []
    for meal in today_meals:
        meal_feedback = data_manager.get_feedback_by_meal(meal.id)
        feedback_dicts = [fb.to_dict() for fb in meal_feedback]
        analysis = feedback_analyzer.analyze_meal_performance(meal.id, feedback_dicts)
        analysis['meal_name'] = meal.name
        meal_analytics.append(analysis)
    
    return render_template('admin_dashboard.html',
                         user=user,
                         today_meals=today_meals,
                         attendance_stats=attendance_stats,
                         recent_feedback=recent_feedback,
                         meal_analytics=meal_analytics,
                         today=today)

@app.route('/meal_confirmation', methods=['GET', 'POST'])
@login_required
def meal_confirmation():
    """Meal confirmation page"""
    if request.method == 'POST':
        meal_type = request.form.get('meal_type')
        date = request.form.get('date')
        
        if not all([meal_type, date]):
            flash('Meal type and date are required.', 'error')
            return redirect(url_for('meal_confirmation'))
        
        # Check if meal exists for that date and type
        meals = data_manager.get_meals_by_date(date)
        meal = next((m for m in meals if m.meal_type == meal_type), None)
        
        if not meal:
            # Create a default meal if it doesn't exist
            meal_names = {
                'breakfast': 'Breakfast',
                'lunch': 'Lunch', 
                'dinner': 'Dinner'
            }
            meal = data_manager.create_meal(meal_names[meal_type], meal_type, date)
        
        # Check if already confirmed
        existing_confirmations = data_manager.get_user_confirmations(session['user_id'], date)
        already_confirmed = any(conf.meal_type == meal_type for conf in existing_confirmations)
        
        if already_confirmed:
            flash(f'You have already confirmed {meal_type} for {date}.', 'warning')
        else:
            # Create confirmation
            data_manager.create_confirmation(session['user_id'], meal.id, date, meal_type)
            flash(f'{meal_type.title()} confirmed for {date}.', 'success')
        
        return redirect(url_for('student_dashboard'))
    
    # GET request - show confirmation form
    today = datetime.now().strftime('%Y-%m-%d')
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    return render_template('meal_confirmation.html', today=today, tomorrow=tomorrow)

@app.route('/feedback/<int:meal_id>', methods=['GET', 'POST'])
@login_required
def feedback(meal_id):
    """Feedback submission page"""
    meal = data_manager.get_meal_by_id(meal_id)
    if not meal:
        flash('Meal not found.', 'error')
        return redirect(url_for('student_dashboard'))
    
    if request.method == 'POST':
        rating = request.form.get('rating', type=int)
        comment = request.form.get('comment', '').strip()
        
        if not rating or rating not in [1, 2, 3, 4]:
            flash('Please select a valid rating.', 'error')
            return render_template('feedback.html', meal=meal)
        
        # Handle photo upload
        photo_path = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename and allowed_file(file.filename):
                filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(photo_path)
        
        # Create feedback
        feedback_obj = data_manager.create_feedback(session['user_id'], meal_id, rating, comment, photo_path)
        
        # Analyze sentiment if comment provided
        if comment:
            sentiment_result = sentiment_analyzer.analyze_comment(comment)
            data_manager.update_feedback_sentiment(feedback_obj.id, sentiment_result['polarity'])
        
        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('student_dashboard'))
    
    return render_template('feedback.html', meal=meal)

@app.route('/billing')
@login_required
def billing():
    """User billing page"""
    user = data_manager.get_user_by_id(session['user_id'])
    
    # Get current month and year
    now = datetime.now()
    year = request.args.get('year', now.year, type=int)
    month = request.args.get('month', now.month, type=int)
    
    # Get user's confirmations for the month
    monthly_confirmations = data_manager.get_user_monthly_confirmations(user.id, year, month)
    
    # Calculate billing
    total_meals = len(monthly_confirmations)
    meal_price = 50.0  # Default price per meal
    total_amount = total_meals * meal_price
    
    # Group confirmations by meal type
    meal_type_counts = {'breakfast': 0, 'lunch': 0, 'dinner': 0}
    for conf in monthly_confirmations:
        if conf.meal_type in meal_type_counts:
            meal_type_counts[conf.meal_type] += 1
    
    # Generate month options for dropdown
    months = [
        {'value': i, 'name': datetime(2024, i, 1).strftime('%B')} 
        for i in range(1, 13)
    ]
    
    years = [now.year - 1, now.year, now.year + 1]
    
    return render_template('billing.html',
                         user=user,
                         year=year,
                         month=month,
                         months=months,
                         years=years,
                         monthly_confirmations=monthly_confirmations,
                         meal_type_counts=meal_type_counts,
                         total_meals=total_meals,
                         meal_price=meal_price,
                         total_amount=total_amount)

@app.route('/menu_management', methods=['GET', 'POST'])
@admin_required
def menu_management():
    """Menu management for admins"""
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add_meal':
            name = request.form.get('name')
            meal_type = request.form.get('meal_type')
            date = request.form.get('date')
            description = request.form.get('description', '')
            price = request.form.get('price', 50.0, type=float)
            
            if not all([name, meal_type, date]):
                flash('Name, meal type, and date are required.', 'error')
            else:
                data_manager.create_meal(name, meal_type, date, description, price)
                flash('Meal added successfully!', 'success')
        
        elif action == 'update_meal':
            meal_id = request.form.get('meal_id', type=int)
            name = request.form.get('name')
            description = request.form.get('description', '')
            price = request.form.get('price', type=float)
            
            if meal_id and name:
                data_manager.update_meal(meal_id, name=name, description=description, price=price)
                flash('Meal updated successfully!', 'success')
            else:
                flash('Invalid meal data.', 'error')
    
    # Get upcoming week's meals
    today = datetime.now()
    upcoming_meals = []
    
    for i in range(7):  # Next 7 days
        date = (today + timedelta(days=i)).strftime('%Y-%m-%d')
        daily_meals = data_manager.get_meals_by_date(date)
        for meal in daily_meals:
            meal_feedback = data_manager.get_feedback_by_meal(meal.id)
            feedback_dicts = [fb.to_dict() for fb in meal_feedback]
            analysis = feedback_analyzer.analyze_meal_performance(meal.id, feedback_dicts)
            meal.analysis = analysis
            upcoming_meals.append(meal)
    
    return render_template('menu_management.html', upcoming_meals=upcoming_meals)

@app.route('/forecast')
@admin_required
def forecast():
    """Attendance forecasting for admins"""
    # Get historical confirmation data
    all_confirmations = data_manager._load_json(data_manager.confirmations_file)
    
    # Predict for next 3 days
    predictions = []
    for i in range(1, 4):
        future_date = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
        
        for meal_type in ['breakfast', 'lunch', 'dinner']:
            prediction = attendance_predictor.predict_meal_attendance(
                all_confirmations, meal_type, future_date
            )
            prediction['date'] = future_date
            prediction['meal_type'] = meal_type
            predictions.append(prediction)
    
    return render_template('forecast.html', predictions=predictions)

@app.route('/admin/generate_report')
@admin_required
def generate_report():
    """Generate comprehensive admin report"""
    try:
        # Get all data for report
        all_users = data_manager.get_all_users()
        all_meals = data_manager._load_json(data_manager.meals_file)
        all_feedback = data_manager.get_all_feedback()
        all_confirmations = data_manager._load_json(data_manager.confirmations_file)
        
        # Calculate statistics
        total_students = len([u for u in all_users if u.role == 'student'])
        total_meals = len(all_meals)
        total_feedback = len(all_feedback)
        total_confirmations = len(all_confirmations)
        
        # Average rating
        avg_rating = sum(f.rating for f in all_feedback) / len(all_feedback) if all_feedback else 0
        
        # Recent activity
        recent_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        recent_feedback = [f for f in all_feedback if f.created_at >= recent_date]
        recent_confirmations = [c for c in all_confirmations if c['date'] >= recent_date]
        
        report_data = {
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_students': total_students,
            'total_meals': total_meals,
            'total_feedback': total_feedback,
            'total_confirmations': total_confirmations,
            'average_rating': round(avg_rating, 2),
            'recent_feedback_count': len(recent_feedback),
            'recent_confirmations_count': len(recent_confirmations)
        }
        
        return jsonify({
            'success': True,
            'message': 'Report generated successfully',
            'data': report_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error generating report: {str(e)}'
        })

@app.route('/admin/predictions')
@admin_required
def get_predictions():
    """Get attendance predictions for next 3 days"""
    try:
        all_confirmations = data_manager._load_json(data_manager.confirmations_file)
        
        predictions = []
        for i in range(1, 4):
            future_date = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
            
            for meal_type in ['breakfast', 'lunch', 'dinner']:
                prediction = attendance_predictor.predict_meal_attendance(
                    all_confirmations, meal_type, future_date
                )
                prediction['date'] = future_date
                prediction['meal_type'] = meal_type
                predictions.append(prediction)
        
        return jsonify({
            'success': True,
            'message': 'Predictions generated successfully',
            'data': predictions
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error generating predictions: {str(e)}'
        })

@app.route('/admin/export_data')
@admin_required
def export_data():
    """Export all system data as CSV"""
    try:
        # Create CSV data
        output = io.StringIO()
        
        # Export feedback data
        all_feedback = data_manager.get_all_feedback()
        if all_feedback:
            writer = csv.writer(output)
            writer.writerow(['Feedback ID', 'User ID', 'Meal ID', 'Rating', 'Comment', 'Created At'])
            
            for feedback in all_feedback:
                writer.writerow([
                    feedback.id,
                    feedback.user_id,
                    feedback.meal_id,
                    feedback.rating,
                    feedback.comment or '',
                    feedback.created_at
                ])
        
        csv_data = output.getvalue()
        output.close()
        
        # Create response
        response = make_response(csv_data)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=messmate_data_{datetime.now().strftime("%Y%m%d")}.csv'
        
        return response
    except Exception as e:
        flash(f'Error exporting data: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/test_ml_analysis')
@admin_required  
def test_ml_analysis():
    """Test ML analysis functionality with current feedback data"""
    try:
        # Get all feedback
        all_feedback = data_manager.get_all_feedback()
        
        if not all_feedback:
            return jsonify({
                'success': False,
                'message': 'No feedback data available for analysis'
            })
        
        # Convert feedback to dict format for ML analysis
        feedback_dicts = [feedback.to_dict() for feedback in all_feedback]
        
        # Group feedback by meal
        meal_feedback = {}
        for feedback in feedback_dicts:
            meal_id = feedback['meal_id']
            if meal_id not in meal_feedback:
                meal_feedback[meal_id] = []
            meal_feedback[meal_id].append(feedback)
        
        # Analyze each meal's feedback using ML
        analysis_results = {}
        for meal_id, feedbacks in meal_feedback.items():
            meal = data_manager.get_meal_by_id(meal_id)
            meal_name = meal.name if meal else f"Meal {meal_id}"
            
            # Perform ML sentiment analysis
            sentiment_analysis = sentiment_analyzer.analyze_meal_feedback(feedbacks)
            
            # Individual comment analysis
            comment_analysis = []
            for feedback in feedbacks:
                if feedback.get('comment'):
                    sentiment_result = sentiment_analyzer.analyze_comment(feedback['comment'])
                    comment_analysis.append({
                        'comment': feedback['comment'],
                        'rating': feedback['rating'],
                        'sentiment': sentiment_result['sentiment'],
                        'polarity': round(sentiment_result['polarity'], 3),
                        'subjectivity': round(sentiment_result['subjectivity'], 3)
                    })
            
            analysis_results[meal_name] = {
                'overall_analysis': sentiment_analysis,
                'individual_comments': comment_analysis
            }
        
        return jsonify({
            'success': True,
            'message': 'ML analysis completed successfully',
            'data': analysis_results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error in ML analysis: {str(e)}'
        })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    flash('Page not found.', 'error')
    return redirect(url_for('index'))

@app.errorhandler(500)
def internal_error(error):
    flash('An internal error occurred. Please try again.', 'error')
    return redirect(url_for('index'))
