from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from utils import send_otp_to_email, generate_otp


# Create a Blueprint for authentication routes
auth_bp = Blueprint('auth', __name__)

# Login Route
@auth_bp.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    stay_logged_in = request.form.get('stayLoggedIn') == 'true'

    # Query the database for the user
    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        # Set token expiration based on stay_logged_in flag
        expires = timedelta(days=30) if stay_logged_in else timedelta(hours=1)
        access_token = create_access_token(identity={'user_id': user.id, 'role': user.role}, expires_delta=expires)
        return jsonify({
            'message': f"Welcome {user.username}",
            'access_token': access_token,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'user_id': user.id
        }), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401

# Registration Route
@auth_bp.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role')

    # Validate required fields
    if not username or not password or not email or not role:
        return {'message': 'Username, password, role, and email are required'}, 400
    
    if role not in ['event_organizer', 'customer']:
        return {'message': 'Invalid role. Choose either "event_organizer" or "customer"'}, 400

    # Check if the user already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return {'message': 'User already exists'}, 400

    # Hash the password for security
    hashed_password = generate_password_hash(password)

    # Generate OTP and set its expiration time
    otp_code = generate_otp()
    otp_expiration = datetime.utcnow() + timedelta(minutes=10)

    # Send OTP to user's email
    send_otp_to_email(email, otp_code)

    # Create new user and store in the database
    new_user = User(username=username, email=email, password=hashed_password, role=role, otp=otp_code, otp_expiration=otp_expiration)
    db.session.add(new_user)
    db.session.commit()

    return {'message': 'OTP sent to email. Please verify.'}, 200

# Verify OTP Route
@auth_bp.route('/verify_otp', methods=['POST'])
def verify_otp():
    entered_otp = request.json.get('otp')

    # Check if OTP is provided
    if not entered_otp:
        return {'message': 'OTP is required'}, 400

    # Look for the user in the database using the entered OTP
    user = User.query.filter_by(otp=entered_otp).first()

    # Validate if OTP exists and is not expired
    if not user or datetime.utcnow() > user.otp_expiration:
        return {'message': 'Invalid or expired OTP'}, 400

    # Clear OTP and expiration from the database once validated
    user.otp = None
    user.otp_expiration = None
    db.session.commit()

    return {'message': 'User registered successfully'}, 201
