from flask import Flask, request, jsonify, render_template, redirect, url_for, send_from_directory
import firebase_admin
from firebase_admin import credentials, auth, db
import os
import logging
from document import generate_document_and_send



# Initialize Flask app
app = Flask(__name__)

UPLOAD_FOLDER = "generated_docs"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the UPLOAD_FOLDER exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Initialize Firebase Admin SDK
cred = credentials.Certificate("firebase_admin_key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://project-document-creator-default-rtdb.firebaseio.com/'
})

# Serve the login page (HTML)
@app.route("/")
def login_page():
    return render_template("login.html")

# Serve the registration page (HTML)
@app.route("/register_page")
def register_page():
    return render_template("register.html")

# User Login Route (backend logic for login)
@app.route("/login", methods=["POST"])
def login_user():
    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        return render_template("login.html", error="Email and password are required")

    try:
        # Check if the email exists in Firebase Realtime Database
        ref = db.reference('users')
        user_data = ref.order_by_child('email').equal_to(email).get()

        if user_data:
            # Loop through each user to check password
            for key, value in user_data.items():
                if value['password'] == password:  # Check if the passwords match
                    return redirect(url_for("home_page"))  # Login successful, redirect to home
                else:
                    return render_template("login.html", error="Invalid password")
        else:
            # User not found in the database
            return render_template("login.html", error="User not found, please register.")

    except Exception as e:
        logging.error(f"Error during login: {e}")
        return render_template("login.html", error="Error during login process.")


# User Registration Route (backend logic for registration)
@app.route("/register", methods=["POST"])
def register_user():
    email = request.form.get("email")
    password = request.form.get("password")
    name = request.form.get("name")

    if not email or not password or not name:
        return render_template("register.html", error="Email, password, and name are required")

    try:
        # Check if the email already exists in Firebase Realtime Database
        ref = db.reference('users')
        user_data = ref.order_by_child('email').equal_to(email).get()

        if user_data:
            # If email already exists, show error and redirect to login
            return render_template("register.html", error="Email already exists. Please login.")

        # Store user credentials in Firebase Realtime Database
        ref.push({
            'email': email,
            'password': password,  # Store the password (consider hashing it for security)
            'name': name
        })

        # Return success message and redirect to login page
        return render_template("register.html", message="Registration successful, please log in.")

    except Exception as e:
        logging.error(f"Error registering user: {e}")
        return render_template("register.html", error="Error occurred during registration.")

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
        logging.error(f"Error generating document: {e}")
        return render_template("document.html", message=f"Error generating document: {str(e)}")

# Route to download the generated document
@app.route('/download/<filename>')
def download_document(filename):
    try:
        # Path to the file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Send the file as an attachment
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except Exception as e:
        logging.error(f"Error downloading document: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
