from document import generate_document_and_send
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import firebase_admin
from firebase_admin import credentials, auth, db
import os
import logging
from send_email_notification import notify_registration, notify_login,notify_document_generation
from flask import send_from_directory
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# Initialize Flask app
app = Flask(__name__, static_folder='static')

# Set a secret key for session management
app.secret_key = os.urandom(24)

UPLOAD_FOLDER = "generated_docs"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Set up Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_page'  # Redirect unauthorized users to login page

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, email, approved):
        self.id = id
        self.email = email
        self.approved = approved  # Add 'approved' attribute

    # Implement the `get` method to fetch user from Firebase by user_id
    @classmethod
    def get(cls, user_id):
        try:
            ref = db.reference('users')
            user_data = ref.child(user_id).get()  # Fetch user by user_id
            if user_data:
                return User(user_id, user_data['email'], user_data['approved'])
            return None
        except Exception as e:
            print(f"Error fetching user: {e}")
            return None

# Load user from the session
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Initialize Firebase Admin SDK with Firebase credentials
local_file_path = "firebase_admin_key.json"  # Local path for Windows
render_file_path = "/etc/secrets/firebase_admin_key.json"  # Render secret file path

# Check if running on Render
if os.getenv("RENDER"):
    firebase_key_path = render_file_path
else:
    firebase_key_path = local_file_path

try:
    # Initialize Firebase Admin SDK with the selected file path
    cred = credentials.Certificate(firebase_key_path)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://project-document-creator-default-rtdb.firebaseio.com/'
    })
    print("Firebase Admin SDK initialized successfully.")
except Exception as e:
    print(f"Failed to initialize Firebase Admin SDK: {e}")

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
def login_user_route():
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
                    if not value['approved']:
                        return render_template("login.html", error="Your account is pending approval. Please wait for the admin to approve your registration.")

                    # Create user instance and log them in
                    user = User(id=key, email=email, approved=value['approved'])
                    login_user(user)

                    # Notify admin about the login
                    notify_login(email)

                    # Redirect to the page that the user was trying to access before being redirected to the login page
                    next_page = request.args.get('next')
                    return redirect(next_page or url_for("home_page"))  # Default to home page if no 'next' param

        else:
            return render_template("register.html", error="User not found, please register.")

    except Exception as e:
        return render_template("login.html", error="Error during login process.")

@app.route("/admin/approve_users")
@login_required
def approve_users():
    if not current_user.is_authenticated:
        return redirect(url_for('login_page'))

    try:
        # Get all users who are not approved
        ref = db.reference('users')
        pending_users = ref.order_by_child('approved').equal_to(False).get()

        return render_template("approve_users.html", pending_users=pending_users)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admin/approve_user/<user_id>", methods=["POST"])
@login_required
def approve_user(user_id):
    if not current_user.is_authenticated:
        return redirect(url_for('login_page'))

    try:
        # Get the user data from Firebase
        ref = db.reference('users')
        user_ref = ref.child(user_id)

        # Update the "approved" field to True
        user_ref.update({'approved': True})

        return redirect(url_for('approve_users'))  # Redirect to the approval page after approval

    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
            return render_template("login.html", error="Email already exists. Please login.")

        # Store user credentials in Firebase Realtime Database with "approved" flag set to False
        ref.push({
            'email': email,
            'password': password,  # Store the password (consider hashing it for security)
            'name': name,
            'approved': False  # Set the default approval status to False
        })

        # Notify admin about the new registration
        try:
            notify_registration(name, email, password)
        except Exception as e:
            print(f"Error sending notification email: {e}")

        return render_template("register.html", message="Registration successful, but pending approval.")

    except Exception as e:
        return render_template("register.html", error=f"Error occurred during registration: {str(e)}")

# Serve the home page after login
@app.route("/home")
@login_required
def home_page():
    return render_template("index.html")

# Protect the document route (requires login)
@app.route("/document")
@login_required
def document_page():
    return render_template("document.html")

# Handle the project description and generate documentation
@app.route("/generate_document", methods=["POST"])
@login_required
def generate_document():
    project_description = request.form.get('project_description')

    if not project_description:
        return render_template("document.html", message="Project description is required!")

    try:
        # Generate the document and save it to the UPLOAD_FOLDER
        filename = generate_document_and_send(project_description)

        # Notify admin about the document generation
        notify_document_generation(email=current_user.email, project_description=project_description)

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
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except Exception as e:
        logging.error(f"Error downloading document: {e}")
        return jsonify({"error": str(e)}), 500

# Log out the user
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login_page"))

# Only protect certain routes from unauthorized access
@app.before_request
def check_if_logged_in():
    # List of routes that are publicly accessible
    public_routes = ['login_page', 'login_user_route', 'register_page', 'register_user']
    # Allow access to static files
    if request.endpoint and request.endpoint.startswith('static'):
        return None  # No need to redirect for static files

    if not current_user.is_authenticated and request.endpoint not in public_routes:
        return redirect(url_for('login_page', next=request.url))

    # Check if the user is approved
    if current_user.is_authenticated and not current_user.approved:
        return redirect(url_for('login_page', error="Your account is pending approval"))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
