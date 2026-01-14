"""
Flask API System with Authentication and Database Integration
Professional web application demonstrating REST API development
Author: Jorge de la Flor
"""

from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
import sqlite3
from functools import wraps
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-me')


class DatabaseService:
    def __init__(self, db_path='api_system.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Operations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                operation_type TEXT NOT NULL,
                data TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    
    def create_user(self, username, email, password, role='user'):
        """Create new user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            password_hash = generate_password_hash(password)
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, role)
                VALUES (?, ?, ?, ?)
            ''', (username, email, password_hash, role))
            
            user_id = cursor.lastrowid
            conn.commit()
            return user_id
            
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def get_user_by_username(self, username):
        """Get user by username"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        return dict(user) if user else None
    
    def create_operation(self, user_id, operation_type, data):
        """Create new operation"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO api_operations (user_id, operation_type, data)
            VALUES (?, ?, ?)
        ''', (user_id, operation_type, json.dumps(data)))
        
        operation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return operation_id
    
    def get_user_operations(self, user_id, limit=10):
        """Get operations for user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM api_operations 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (user_id, limit))
        
        operations = cursor.fetchall()
        conn.close()
        
        return [dict(op) for op in operations]

# Initialize database service
db_service = DatabaseService()

def token_required(f):
    """Decorator for protecting routes with JWT tokens"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = db_service.get_user_by_username(data['username'])
            
            if not current_user:
                return jsonify({'message': 'Token is invalid'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

@app.route('/api/register', methods=['POST'])
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password']
        if not all(field in data for field in required_fields):
            return jsonify({'message': 'Missing required fields'}), 400
        
        # Create user
        user_id = db_service.create_user(
            data['username'], 
            data['email'], 
            data['password'],
            data.get('role', 'user')
        )
        
        if user_id:
            return jsonify({
                'message': 'User created successfully',
                'user_id': user_id
            }), 201
        else:
            return jsonify({'message': 'Username or email already exists'}), 409
            
    except Exception as e:
        return jsonify({'message': f'Registration failed: {str(e)}'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """User authentication endpoint"""
    try:
        data = request.get_json()
        
        if not data.get('username') or not data.get('password'):
            return jsonify({'message': 'Username and password required'}), 400
        
        user = db_service.get_user_by_username(data['username'])
        
        if user and check_password_hash(user['password_hash'], data['password']):
            # Generate JWT token
            token = jwt.encode({
                'username': user['username'],
                'user_id': user['id'],
                'role': user['role'],
                'exp': datetime.utcnow() + timedelta(hours=24)
            }, app.config['SECRET_KEY'], algorithm='HS256')
            
            return jsonify({
                'message': 'Login successful',
                'token': token,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'role': user['role']
                }
            }), 200
        else:
            return jsonify({'message': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'message': f'Login failed: {str(e)}'}), 500

@app.route('/api/operations', methods=['POST'])
@token_required
def create_operation(current_user):
    """Create new operation (protected route)"""
    try:
        data = request.get_json()
        
        if not data.get('operation_type'):
            return jsonify({'message': 'Operation type is required'}), 400
        
        operation_id = db_service.create_operation(
            current_user['id'],
            data['operation_type'],
            data.get('data', {})
        )
        
        return jsonify({
            'message': 'Operation created successfully',
            'operation_id': operation_id
        }), 201
        
    except Exception as e:
        return jsonify({'message': f'Operation creation failed: {str(e)}'}), 500

@app.route('/api/operations', methods=['GET'])
@token_required
def get_operations(current_user):
    """Get user operations (protected route)"""
    try:
        limit = request.args.get('limit', 10, type=int)
        operations = db_service.get_user_operations(current_user['id'], limit)
        
        return jsonify({
            'operations': operations,
            'count': len(operations)
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to retrieve operations: {str(e)}'}), 500

@app.route('/api/status', methods=['GET'])
def api_status():
    """API health check endpoint"""
    return jsonify({
        'status': 'active',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'message': 'API is running successfully'
    }), 200

@app.route('/api/user/profile', methods=['GET'])
@token_required
def get_user_profile(current_user):
    """Get current user profile (protected route)"""
    try:
        # Get user's operation count
        operations = db_service.get_user_operations(current_user['id'], limit=1000)
        
        profile = {
            'user_info': {
                'id': current_user['id'],
                'username': current_user['username'],
                'email': current_user['email'],
                'role': current_user['role'],
                'member_since': current_user['created_at']
            },
            'statistics': {
                'total_operations': len(operations),
                'recent_activity': len([op for op in operations if op['created_at'] > (datetime.now() - timedelta(days=7)).isoformat()])
            }
        }
        
        return jsonify(profile), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get profile: {str(e)}'}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'message': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'message': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Starting Flask API System...")
    print("📡 Available endpoints:")
    print("   POST /api/register - User registration")
    print("   POST /api/login - User authentication") 
    print("   GET  /api/status - API health check")
    print("   POST /api/operations - Create operation (auth required)")
    print("   GET  /api/operations - Get operations (auth required)")
    print("   GET  /api/user/profile - Get user profile (auth required)")
    print("\n🔧 To test the API:")
    print("   1. Register: curl -X POST http://localhost:5000/api/register -H 'Content-Type: application/json' -d '{\"username\":\"testuser\",\"email\":\"test@example.com\",\"password\":\"testpass123\"}'")
    print("   2. Login: curl -X POST http://localhost:5000/api/login -H 'Content-Type: application/json' -d '{\"username\":\"testuser\",\"password\":\"testpass123\"}'")
    print("   3. Use the returned token in Authorization header for protected routes")
    
    app.run(debug=True, host='0.0.0.0', port=5000)