import logging
from typing import List, Dict, Tuple
import statistics
from textblob import TextBlob
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import json

class SentimentAnalyzer:
    """Sentiment analysis using TextBlob"""
    
    def analyze_comment(self, comment: str) -> Dict:
        """
        Analyze sentiment of a comment
        Returns: {
            'polarity': float (-1 to 1),
            'subjectivity': float (0 to 1),
            'sentiment': str ('positive', 'negative', 'neutral')
        }
        """
        if not comment or not comment.strip():
            return {
                'polarity': 0.0,
                'subjectivity': 0.0,
                'sentiment': 'neutral'
            }
        
        try:
            blob = TextBlob(comment)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Classify sentiment
            if polarity > 0.1:
                sentiment = 'positive'
            elif polarity < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            return {
                'polarity': polarity,
                'subjectivity': subjectivity,
                'sentiment': sentiment
            }
        except Exception as e:
            logging.error(f"Error analyzing sentiment: {e}")
            return {
                'polarity': 0.0,
                'subjectivity': 0.0,
                'sentiment': 'neutral'
            }
    
    def analyze_meal_feedback(self, feedback_list: List[Dict]) -> Dict:
        """
        Analyze overall sentiment for a meal based on all feedback
        """
        if not feedback_list:
            return {
                'overall_sentiment': 'neutral',
                'avg_polarity': 0.0,
                'avg_rating': 0.0,
                'total_feedback': 0,
                'sentiment_distribution': {'positive': 0, 'negative': 0, 'neutral': 0}
            }
        
        ratings = []
        polarities = []
        sentiments = []
        
        for feedback in feedback_list:
            # Rating analysis
            if 'rating' in feedback:
                ratings.append(feedback['rating'])
            
            # Comment sentiment analysis
            if feedback.get('comment'):
                sentiment_result = self.analyze_comment(feedback['comment'])
                polarities.append(sentiment_result['polarity'])
                sentiments.append(sentiment_result['sentiment'])
        
        # Calculate averages
        avg_rating = statistics.mean(ratings) if ratings else 0.0
        avg_polarity = statistics.mean(polarities) if polarities else 0.0
        
        # Determine overall sentiment
        sentiment_counts = Counter(sentiments)
        if sentiment_counts['positive'] > sentiment_counts['negative']:
            overall_sentiment = 'positive'
        elif sentiment_counts['negative'] > sentiment_counts['positive']:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'neutral'
        
        return {
            'overall_sentiment': overall_sentiment,
            'avg_polarity': avg_polarity,
            'avg_rating': avg_rating,
            'total_feedback': len(feedback_list),
            'sentiment_distribution': dict(sentiment_counts)
        }

class AttendancePredictor:
    """Simple attendance prediction using historical data"""
    
    def predict_meal_attendance(self, historical_data: List[Dict], meal_type: str, date: str) -> Dict:
        """
        Predict attendance for a meal based on historical patterns
        """
        try:
            # Filter historical data for the same meal type and day of week
            target_date = datetime.strptime(date, '%Y-%m-%d')
            target_weekday = target_date.weekday()  # 0=Monday, 6=Sunday
            
            # Get historical data for same meal type and weekday
            relevant_data = []
            for record in historical_data:
                try:
                    record_date = datetime.strptime(record['date'], '%Y-%m-%d')
                    if (record['meal_type'] == meal_type and 
                        record_date.weekday() == target_weekday):
                        relevant_data.append(record)
                except:
                    continue
            
            if not relevant_data:
                # No historical data, return default prediction
                return {
                    'predicted_attendance': 50,  # Default assumption
                    'confidence': 0.0,
                    'historical_avg': 0.0,
                    'trend': 'stable'
                }
            
            # Count unique users per date for the same meal type and weekday
            attendance_by_date = defaultdict(set)
            for record in relevant_data:
                attendance_by_date[record['date']].add(record['user_id'])
            
            # Calculate attendance numbers
            attendance_numbers = [len(users) for users in attendance_by_date.values()]
            
            if not attendance_numbers:
                return {
                    'predicted_attendance': 50,
                    'confidence': 0.0,
                    'historical_avg': 0.0,
                    'trend': 'stable'
                }
            
            # Calculate statistics
            avg_attendance = statistics.mean(attendance_numbers)
            
            # Simple trend analysis (last 3 vs previous data points)
            trend = 'stable'
            if len(attendance_numbers) >= 6:
                recent_avg = statistics.mean(attendance_numbers[-3:])
                older_avg = statistics.mean(attendance_numbers[-6:-3])
                
                if recent_avg > older_avg * 1.1:
                    trend = 'increasing'
                elif recent_avg < older_avg * 0.9:
                    trend = 'decreasing'
            
            # Confidence based on data availability
            confidence = min(len(attendance_numbers) / 10.0, 1.0)  # Max confidence with 10+ data points
            
            # Adjust prediction based on trend
            predicted = avg_attendance
            if trend == 'increasing':
                predicted *= 1.1
            elif trend == 'decreasing':
                predicted *= 0.9
            
            return {
                'predicted_attendance': int(predicted),
                'confidence': confidence,
                'historical_avg': avg_attendance,
                'trend': trend,
                'data_points': len(attendance_numbers)
            }
            
        except Exception as e:
            logging.error(f"Error predicting attendance: {e}")
            return {
                'predicted_attendance': 50,
                'confidence': 0.0,
                'historical_avg': 0.0,
                'trend': 'stable'
            }

class FeedbackAnalyzer:
    """Comprehensive feedback analysis for meal insights"""
    
    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()
    
    def analyze_meal_performance(self, meal_id: int, feedback_list: List[Dict]) -> Dict:
        """
        Comprehensive analysis of meal performance
        """
        if not feedback_list:
            return {
                'meal_id': meal_id,
                'total_feedback': 0,
                'avg_rating': 0.0,
                'rating_distribution': {1: 0, 2: 0, 3: 0, 4: 0},
                'sentiment_analysis': {},
                'recommendations': ['No feedback available for analysis'],
                'performance_score': 0.0
            }
        
        # Rating analysis
        ratings = [fb['rating'] for fb in feedback_list if 'rating' in fb]
        avg_rating = statistics.mean(ratings) if ratings else 0.0
        
        rating_distribution = Counter(ratings)
        rating_dist = {i: rating_distribution.get(i, 0) for i in range(1, 5)}
        
        # Sentiment analysis
        sentiment_analysis = self.sentiment_analyzer.analyze_meal_feedback(feedback_list)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(avg_rating, sentiment_analysis, rating_dist)
        
        # Calculate performance score (0-100)
        performance_score = self._calculate_performance_score(avg_rating, sentiment_analysis)
        
        return {
            'meal_id': meal_id,
            'total_feedback': len(feedback_list),
            'avg_rating': avg_rating,
            'rating_distribution': rating_dist,
            'sentiment_analysis': sentiment_analysis,
            'recommendations': recommendations,
            'performance_score': performance_score
        }
    
    def _generate_recommendations(self, avg_rating: float, sentiment_analysis: Dict, rating_dist: Dict) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        # Rating-based recommendations
        if avg_rating < 2.0:
            recommendations.append("Consider replacing this dish - consistently poor ratings")
        elif avg_rating < 2.5:
            recommendations.append("Recipe needs significant improvement")
        elif avg_rating < 3.0:
            recommendations.append("Minor adjustments needed - check seasoning and preparation")
        elif avg_rating >= 3.5:
            recommendations.append("Well-received dish - consider making it a regular item")
        
        # Sentiment-based recommendations
        if sentiment_analysis.get('overall_sentiment') == 'negative':
            recommendations.append("Negative feedback detected - review preparation methods")
        elif sentiment_analysis.get('overall_sentiment') == 'positive':
            recommendations.append("Positive feedback - maintain current preparation standards")
        
        # Distribution-based recommendations
        if rating_dist.get(1, 0) > rating_dist.get(4, 0):
            recommendations.append("High number of poor ratings - immediate attention required")
        
        if not recommendations:
            recommendations.append("Continue monitoring feedback for trends")
        
        return recommendations
    
    def _calculate_performance_score(self, avg_rating: float, sentiment_analysis: Dict) -> float:
        """Calculate overall performance score (0-100)"""
        # Rating component (0-75 points)
        rating_score = (avg_rating / 4.0) * 75
        
        # Sentiment component (0-25 points)
        sentiment_score = 0
        avg_polarity = sentiment_analysis.get('avg_polarity', 0.0)
        if avg_polarity > 0:
            sentiment_score = min(avg_polarity * 25, 25)
        
        return min(rating_score + sentiment_score, 100.0)

# Global ML models instance
sentiment_analyzer = SentimentAnalyzer()
attendance_predictor = AttendancePredictor()
feedback_analyzer = FeedbackAnalyzer()
