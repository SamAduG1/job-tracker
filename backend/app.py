"""
JobTracker Flask API with JWT Authentication
Manages job application tracking data with user authentication
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_mail import Mail, Message
from models import db, User, Application, PasswordResetToken
from datetime import datetime, timedelta
import os

app = Flask(__name__)
CORS(app)

# Database configuration
database_url = os.environ.get('DATABASE_URL', 'sqlite:///jobtracker.db')
# Fix for Render PostgreSQL URLs (postgres:// -> postgresql://)
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# JWT configuration
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)

# Email configuration (Gmail SMTP)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')

# Frontend URL for password reset links
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:5173')

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)
mail = Mail(app)

with app.app_context():
    db.create_all()


# ============= Authentication Endpoints =============

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.json

        # Validate required fields
        required_fields = ['email', 'password', 'name']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400

        # Check if user already exists
        if User.query.filter_by(email=data['email'].lower()).first():
            return jsonify({"success": False, "error": "Email already registered"}), 409

        # Validate password length
        if len(data['password']) < 6:
            return jsonify({"success": False, "error": "Password must be at least 6 characters"}), 400

        # Create new user
        user = User(
            email=data['email'].lower(),
            name=data['name']
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        # Create access token (identity must be string for Flask-JWT-Extended 4.x)
        access_token = create_access_token(identity=str(user.id))

        return jsonify({
            "success": True,
            "user": user.to_dict(),
            "access_token": access_token
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.json

        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({"success": False, "error": "Email and password required"}), 400

        # Find user
        user = User.query.filter_by(email=data['email'].lower()).first()

        if not user or not user.check_password(data['password']):
            return jsonify({"success": False, "error": "Invalid email or password"}), 401

        # Create access token (identity must be string for Flask-JWT-Extended 4.x)
        access_token = create_access_token(identity=str(user.id))

        return jsonify({
            "success": True,
            "user": user.to_dict(),
            "access_token": access_token
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user info"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404

        return jsonify({
            "success": True,
            "user": user.to_dict()
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    """Send password reset email"""
    try:
        data = request.json
        email = data.get('email', '').lower()

        if not email:
            return jsonify({"success": False, "error": "Email is required"}), 400

        # Find user (always return success to prevent email enumeration)
        user = User.query.filter_by(email=email).first()

        if user:
            # Invalidate any existing tokens for this user
            PasswordResetToken.query.filter_by(user_id=user.id, used=False).update({'used': True})

            # Create new reset token
            reset_token = PasswordResetToken.create_for_user(user.id)
            db.session.add(reset_token)
            db.session.commit()

            # Send email
            reset_url = f"{FRONTEND_URL}/reset-password?token={reset_token.token}"

            msg = Message(
                subject="Reset Your JobTracker Password",
                recipients=[user.email]
            )
            msg.html = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(to right, #16a34a, #10b981); padding: 20px; text-align: center;">
                    <h1 style="color: white; margin: 0;">JobTracker</h1>
                </div>
                <div style="padding: 30px; background: #f9fafb;">
                    <h2 style="color: #374151;">Password Reset Request</h2>
                    <p style="color: #6b7280;">Hi {user.name},</p>
                    <p style="color: #6b7280;">We received a request to reset your password. Click the button below to create a new password:</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{reset_url}" style="background: #16a34a; color: white; padding: 12px 30px; text-decoration: none; border-radius: 8px; font-weight: bold;">Reset Password</a>
                    </div>
                    <p style="color: #6b7280; font-size: 14px;">This link will expire in 1 hour.</p>
                    <p style="color: #6b7280; font-size: 14px;">If you didn't request this, you can safely ignore this email.</p>
                    <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
                    <p style="color: #9ca3af; font-size: 12px;">If the button doesn't work, copy and paste this link into your browser:</p>
                    <p style="color: #9ca3af; font-size: 12px; word-break: break-all;">{reset_url}</p>
                </div>
            </div>
            """

            try:
                mail.send(msg)
            except Exception as e:
                print(f"Failed to send email: {e}")
                # Don't expose email errors to user

        # Always return success (security: don't reveal if email exists)
        return jsonify({
            "success": True,
            "message": "If an account with that email exists, we've sent a password reset link."
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    """Reset password using token"""
    try:
        data = request.json
        token = data.get('token')
        new_password = data.get('password')

        if not token or not new_password:
            return jsonify({"success": False, "error": "Token and new password are required"}), 400

        if len(new_password) < 6:
            return jsonify({"success": False, "error": "Password must be at least 6 characters"}), 400

        # Find and validate token
        reset_token = PasswordResetToken.query.filter_by(token=token).first()

        if not reset_token:
            return jsonify({"success": False, "error": "Invalid or expired reset link"}), 400

        if not reset_token.is_valid():
            return jsonify({"success": False, "error": "Reset link has expired. Please request a new one."}), 400

        # Update password
        user = User.query.get(reset_token.user_id)
        user.set_password(new_password)

        # Mark token as used
        reset_token.used = True

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Password reset successfully. You can now log in with your new password."
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/auth/verify-reset-token', methods=['POST'])
def verify_reset_token():
    """Verify if a reset token is valid"""
    try:
        data = request.json
        token = data.get('token')

        if not token:
            return jsonify({"success": False, "error": "Token is required"}), 400

        reset_token = PasswordResetToken.query.filter_by(token=token).first()

        if not reset_token or not reset_token.is_valid():
            return jsonify({"success": False, "valid": False, "error": "Invalid or expired reset link"}), 400

        return jsonify({
            "success": True,
            "valid": True
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============= Application Endpoints (Protected) =============

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "JobTracker API is running"})


@app.route('/api/applications', methods=['GET'])
@jwt_required()
def get_applications():
    """Get all applications for current user"""
    try:
        user_id = int(get_jwt_identity())
        applications = Application.query.filter_by(user_id=user_id).order_by(Application.date_applied.desc()).all()
        return jsonify({
            "success": True,
            "applications": [app.to_dict() for app in applications]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/applications/<int:id>', methods=['GET'])
@jwt_required()
def get_application(id):
    """Get a specific application"""
    try:
        user_id = int(get_jwt_identity())
        application = Application.query.filter_by(id=id, user_id=user_id).first()

        if not application:
            return jsonify({"success": False, "error": "Application not found"}), 404

        return jsonify({
            "success": True,
            "application": application.to_dict()
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/applications', methods=['POST'])
@jwt_required()
def create_application():
    """Create a new application"""
    try:
        user_id = int(get_jwt_identity())
        data = request.json

        # Validate required fields
        required_fields = ['company', 'position', 'date_applied', 'status']
        for field in required_fields:
            if field not in data:
                return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400

        # Create new application
        application = Application(
            user_id=user_id,
            company=data['company'],
            position=data['position'],
            status=data['status'],
            date_applied=datetime.strptime(data['date_applied'], '%Y-%m-%d').date(),
            job_url=data.get('job_url'),
            location=data.get('location'),
            salary_range=data.get('salary_range'),
            notes=data.get('notes')
        )

        db.session.add(application)
        db.session.commit()

        return jsonify({
            "success": True,
            "application": application.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/applications/<int:id>', methods=['PUT'])
@jwt_required()
def update_application(id):
    """Update an existing application"""
    try:
        user_id = int(get_jwt_identity())
        application = Application.query.filter_by(id=id, user_id=user_id).first()

        if not application:
            return jsonify({"success": False, "error": "Application not found"}), 404

        data = request.json

        # Update fields
        if 'company' in data:
            application.company = data['company']
        if 'position' in data:
            application.position = data['position']
        if 'status' in data:
            application.status = data['status']
        if 'date_applied' in data:
            application.date_applied = datetime.strptime(data['date_applied'], '%Y-%m-%d').date()
        if 'job_url' in data:
            application.job_url = data['job_url']
        if 'location' in data:
            application.location = data['location']
        if 'salary_range' in data:
            application.salary_range = data['salary_range']
        if 'notes' in data:
            application.notes = data['notes']

        application.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            "success": True,
            "application": application.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/applications/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_application(id):
    """Delete an application"""
    try:
        user_id = int(get_jwt_identity())
        application = Application.query.filter_by(id=id, user_id=user_id).first()

        if not application:
            return jsonify({"success": False, "error": "Application not found"}), 404

        db.session.delete(application)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Application deleted successfully"
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/stats', methods=['GET'])
@jwt_required()
def get_statistics():
    """Get dashboard statistics for current user"""
    try:
        user_id = int(get_jwt_identity())
        all_apps = Application.query.filter_by(user_id=user_id).all()
        total = len(all_apps)

        # Count by status
        status_counts = {}
        for app in all_apps:
            status_counts[app.status] = status_counts.get(app.status, 0) + 1

        # Calculate response rate (any status beyond "Applied")
        responses = sum(1 for app in all_apps if app.status != 'Applied')
        response_rate = round((responses / total * 100) if total > 0 else 0, 1)

        return jsonify({
            "success": True,
            "stats": {
                "total_applications": total,
                "response_rate": response_rate,
                "by_status": status_counts
            }
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
