from flask import Flask, request, jsonify, session
import mysql.connector
import pandas as pd
from flask_cors import CORS
from mysql.connector import pooling
import json
from config import DevelopmentConfig, DatabaseConfig

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": DevelopmentConfig.CORS_ORIGIN}}, supports_credentials=True)


app.config.from_object(DevelopmentConfig)


def db_connect():
    return mysql.connector.connect(
        host=DatabaseConfig.DB_HOST,
        user=DatabaseConfig.DB_USER,
        password=DatabaseConfig.DB_PASSWORD,
        database=DatabaseConfig.DB_NAME
    )

# Function to load subjects and electives from a JSON file
def load_subjects(file_path='subjects.json'):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data['core_subjects'], data['electives']

# Function to load grade mapping from a JSON file
def load_grade_mapping(file_path='grade_mapping.json'):
    with open(file_path, 'r') as file:
        grade_mapping = json.load(file)
    return grade_mapping

# Load data during the application startup
core_subjects, electives = load_subjects()
grade_mapping = load_grade_mapping()

# Login route
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    register_number = data.get('register_number')
    
    conn = db_connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM studentdetails WHERE register_number = %s", (register_number,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        session['register_number'] = register_number
        return jsonify({"message": "Login successful", "user": user}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401

# Add student interests
@app.route('/add-interests', methods=['POST'])
# Example of improved error handling
def add_interests():
    data = request.json
    student_id = data.get('register_number')
    interests = data.get('user_choice')

    if not interests:
        return jsonify({"message": "No interests provided"}), 400

    conn = db_connect()
    cursor = conn.cursor()

    try:
        cursor.execute("UPDATE studentdetails SET user_choice = %s WHERE register_number = %s", (interests, student_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({"message": "Failed to update interests", "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "Interests updated successfully"}), 200


# Get recommended courses
# Get recommended courses
@app.route('/recommendations', methods=['GET'])
def recommend():
    # Get register number from session
    register_number = session.get('register_number')

    if not register_number:
        return jsonify({"message": "User not logged in"}), 401

    # Fetch student details and interests in a single query
    conn = db_connect()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Fetch student details only once
        cursor.execute("SELECT * FROM studentdetails WHERE register_number = %s", (register_number,))
        student = cursor.fetchone()

        if student is None:
            return jsonify({"message": "Student not found"}), 404

        # Access student grades from the fetched record
        student_grades = [student['dbms'], student['ai'], student['os'], student['cn'], student['fla'], student['cc'], student['sepm']]

        # Generate recommendations
        rule_based_filtering_ans1, rule_based_filtering_ans2 = rule_based_filtering(student, electives, core_subjects, student_grades)
        content_based_filtering_ans1, content_based_filtering_ans2 = content_based_filtering(rule_based_filtering_ans1, rule_based_filtering_ans2)
        threshold_based_filtering_ans1, threshold_based_filtering_ans2 = threshold_based_filtering(content_based_filtering_ans1, content_based_filtering_ans2)
        recommended_courses = hybrid_recommendation(threshold_based_filtering_ans1, threshold_based_filtering_ans2)

        # Update recommended courses in the database
        cursor.execute("UPDATE studentdetails SET recommended_courses = %s WHERE register_number = %s", 
                       (','.join(recommended_courses), register_number))
        conn.commit()

        # Return the updated recommended courses directly from the current calculation (no need for another fetch)
        response = jsonify({"recommended_courses": recommended_courses})

        # Clear the 'user_choice' and 'recommended_courses' columns after recommendations are fetched
        cursor.execute("UPDATE studentdetails SET user_choice = NULL, recommended_courses = NULL WHERE register_number = %s", (register_number,))
        conn.commit()

        return response
    
    except Exception as e:
        conn.rollback()
        return jsonify({"message": "Failed to update recommended courses", "error": str(e)}), 500
    
    finally:
        cursor.close()
        conn.close()



# Optimize the rule-based filtering
def rule_based_filtering(student, electives, core_subjects, student_grades):
    student_interests = set(student['user_choice'].split(','))
    filtered_electives = {elective: details for elective, details in electives.items() if details['domain'] in student_interests}

    student_grades_df = pd.DataFrame([student_grades], columns=core_subjects.keys()).replace(grade_mapping)

    return filtered_electives, student_grades_df


def content_based_filtering(filtered_electives,student_grades_df):
        domain_grades_interest = {}
        for elective, details in filtered_electives.items():
            domain = details['domain']
            if domain not in domain_grades_interest:
                domain_grades_interest[domain] = []
            for subject, subject_domain in core_subjects.items():
                if subject_domain == domain and subject in student_grades_df.columns:
                    domain_grades_interest[domain].append(student_grades_df[subject].values[0])
            avg_domain_grades_interest = {domain: sum(grades) / len(grades) if grades else 0 for domain, grades in domain_grades_interest.items()}

        return filtered_electives,avg_domain_grades_interest


def  threshold_based_filtering(filtered_electives,avg_domain_grades_interest):
    threshold = 3  
    recommended_electives_interest = []
    for elective, details in filtered_electives.items():
        domain = details['domain']
        avg_grade = avg_domain_grades_interest.get(domain, 0)
        if avg_grade > threshold:
            recommended_electives_interest.append((elective, details['difficulty']))
        elif details['difficulty'] == 'Easy':
            recommended_electives_interest.append((elective, details['difficulty']))

    return recommended_electives_interest,avg_domain_grades_interest


def hybrid_recommendation(recommended_electives_interest, avg_domain_grades_interest):
    # Sort only once based on grades in descending order
    recommendations = sorted(
        recommended_electives_interest, 
        key=lambda x: avg_domain_grades_interest.get(electives[x[0]]['domain'], 0), 
        reverse=True
    )
    
    return [f"{elective} (Difficulty: {difficulty})" for elective, difficulty in recommendations]


if __name__ == '__main__':
    app.run(debug=True)
