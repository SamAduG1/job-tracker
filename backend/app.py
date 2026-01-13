"""
JobTracker Flask API
Manages job application tracking data
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from models import db, Application
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///jobtracker.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "JobTracker API is running"})


@app.route('/api/applications', methods=['GET'])
def get_applications():
    """Get all applications"""
    try:
        applications = Application.query.order_by(Application.date_applied.desc()).all()
        return jsonify({
            "success": True,
            "applications": [app.to_dict() for app in applications]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/applications/<int:id>', methods=['GET'])
def get_application(id):
    """Get a specific application"""
    try:
        application = Application.query.get(id)
        if not application:
            return jsonify({"success": False, "error": "Application not found"}), 404

        return jsonify({
            "success": True,
            "application": application.to_dict()
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/applications', methods=['POST'])
def create_application():
    """Create a new application"""
    try:
        data = request.json

        # Validate required fields
        required_fields = ['company', 'position', 'date_applied', 'status']
        for field in required_fields:
            if field not in data:
                return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400

        # Create new application
        application = Application(
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
def update_application(id):
    """Update an existing application"""
    try:
        application = Application.query.get(id)
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
def delete_application(id):
    """Delete an application"""
    try:
        application = Application.query.get(id)
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
def get_statistics():
    """Get dashboard statistics"""
    try:
        all_apps = Application.query.all()
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
