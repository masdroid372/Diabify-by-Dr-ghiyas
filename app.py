from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diabetes_management.db'
db = SQLAlchemy(app)

# Database Models
class Reading(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    blood_sugar = db.Column(db.Float, nullable=False)
    blood_sugar_unit = db.Column(db.String(10), nullable=False)
    meal_status = db.Column(db.String(20), nullable=False)
    symptoms = db.Column(db.Text)
    notes = db.Column(db.Text)

class HbA1c(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    value = db.Column(db.Float, nullable=False)

class Medication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    medication_name = db.Column(db.String(100), nullable=False)
    dose = db.Column(db.String(50), nullable=False)
    frequency = db.Column(db.String(50), nullable=False)
    active = db.Column(db.Boolean, default=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/reading', methods=['POST'])
def add_reading():
    data = request.json
    reading = Reading(
        blood_sugar=data['blood_sugar'],
        blood_sugar_unit=data['unit'],
        meal_status=data['meal_status'],
        symptoms=data.get('symptoms', '')
    )
    db.session.add(reading)
    db.session.commit()
    return analyze_blood_sugar(reading)

def analyze_blood_sugar(reading):
    MMOL_TO_MGDL = 18.0182
    DKA_THRESHOLD = 11

    blood_sugar = reading.blood_sugar
    if reading.blood_sugar_unit == 'mg/dL':
        blood_sugar = blood_sugar / MMOL_TO_MGDL

    response = {
        'alert_level': 'normal',
        'messages': [],
        'recommendations': []
    }

    if blood_sugar < 4:
        response['alert_level'] = 'danger'
        response['messages'].append("HYPOGLYCEMIA ALERT!")
        response['messages'].append("""
            Immediate actions needed:
            1. Take 15-20g fast-acting carbohydrate
            2. Check blood sugar after 15 minutes
            3. Repeat treatment if still < 4 mmol/L
            4. Once recovered, eat a snack or meal
            5. If unconscious/severe: Need glucagon injection and emergency services
        """)
    elif blood_sugar > DKA_THRESHOLD:
        response['alert_level'] = 'danger'
        response['messages'].append("HIGH BLOOD SUGAR ALERT - DKA Risk!")
        response['recommendations'].append("""
            Check for DKA symptoms and:
            1. Check ketones
            2. Stay hydrated
            3. Continue insulin
            4. Seek immediate medical attention if ketones present
        """)
    elif reading.meal_status == 'before' and blood_sugar > 7:
        response['alert_level'] = 'warning'
        response['messages'].append("Blood sugar is above target range for pre-meal.")
    elif reading.meal_status == 'after' and blood_sugar > 9:
        response['alert_level'] = 'warning'
        response['messages'].append("Blood sugar is above target range for post-meal.")

    return jsonify(response)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
