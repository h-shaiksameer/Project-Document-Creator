from flask import Flask, request, jsonify, render_template, redirect, url_for, send_from_directory
import firebase_admin
from firebase_admin import credentials, auth
from document import generate_document_and_send
import os
import time

# Initialize Flask app
app = Flask(__name__)

UPLOAD_FOLDER = "generated_docs"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the UPLOAD_FOLDER exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Initialize Firebase Admin SDK
cred = credentials.Certificate("firebase_admin_key.json")
firebase_admin.initialize_app(cred)

# Middleware to verify Firebase ID token
def verify_firebase_token(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        return uid
    except Exception as e:
        return str(e)

# Serve the login page (HTML)
@app.route("/")
def login_page():
    return render_template("login.html")

# Serve the registration page (HTML)
@app.route("/register_page")
def register_page():
    return render_template("register.html")

# User Login Route
@app.route("/login", methods=["POST"])
def login_user():
    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    try:
        # If login is successful, redirect to the home page
        return redirect(url_for('home_page'))  # Redirect to the home page after login
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# User Registration Route
@app.route("/register", methods=["POST"])
def register_user():
    try:
        email = request.form.get("email")
        password = request.form.get("password")
        name = request.form.get("name")

        if not email or not password or not name:
            return jsonify({"error": "Email, password, and name are required"}), 400
        
        # Create a new user in Firebase Authentication
        user = auth.create_user(
            email=email,
            password=password,
            display_name=name
        )
        
        # After registration, redirect to the home page (not the registration page)
        return redirect(url_for("home_page"))
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Serve the home page after login
@app.route("/home")
def home_page():
    return render_template("index.html")

@app.route("/document")
def document_page():
    return render_template("document.html")

# Handle the project description and generate documentation
@app.route("/generate_document", methods=["POST"])
def generate_document():
    project_description = request.form.get('project_description')
    
    if not project_description:
        return render_template("document.html", message="Project description is required!")
    
    try:
        # Generate the document and save it to the UPLOAD_FOLDER
        filename = generate_document_and_send(project_description)
        
        # Provide success message and a download link
        message = f"Document generated successfully!"
        download_url = url_for('download_document', filename=filename)
        return render_template("document.html", message=message, download_url=download_url)
    
    except Exception as e:
        return render_template("document.html", message=f"Error generating document: {str(e)}")

# Route to download the generated document
@app.route('/download/<filename>')
def download_document(filename):
    try:
        # Path to the file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Send the file as an attachment
        response = send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
        # time.sleep(100)
        # # Delete the file after sending it
        # os.remove(file_path)
        
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)  # Replace 5001 with the port number you want to use

