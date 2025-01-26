from document import generate_document_and_send
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import firebase_admin
from firebase_admin import credentials, auth, db
import os
import random
import string
import uuid
from werkzeug.utils import secure_filename
import logging
from datetime import datetime, timedelta
from send_email_notification import notify_registration, notify_registration_to_admin,notify_document_generation,notify_login
from flask import send_from_directory
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# Initialize Flask app
app = Flask(__name__, static_folder='static')

# Set a secret key for session management
app.secret_key = os.urandom(24)

# Directory for storing uploaded images
IMAGE_UPLOAD_FOLDER = "uploaded_images"
app.config['IMAGE_UPLOAD_FOLDER'] = IMAGE_UPLOAD_FOLDER

if not os.path.exists(app.config['IMAGE_UPLOAD_FOLDER']):
    os.makedirs(app.config['IMAGE_UPLOAD_FOLDER'])

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route for handling image upload
@app.route("/upload_image", methods=["POST"])
@login_required
def upload_image():
    if 'image' not in request.files:
        logging.error("No file part in the request.")
        return jsonify({"success": False, "message": "No file part"}), 400

    file = request.files['image']
    
    if file.filename == '':
        logging.error("No selected file.")
        return jsonify({"success": False, "message": "No selected file"}), 400

    if file and allowed_file(file.filename):
        # Secure and unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"

        # Construct the full path where the image will be saved
        file_path = os.path.join(app.config['IMAGE_UPLOAD_FOLDER'], unique_filename)

        try:
            # Save the image
            file.save(file_path)

            # Log successful image save
            logging.info(f"Image saved successfully at: {file_path}")

            # Store the uploaded image path in the session for later use in document generation
            session['uploaded_image_path'] = file_path

            return jsonify({"success": True, "message": "Image uploaded successfully.", "filename": unique_filename}), 200
        except Exception as e:
            logging.error(f"Error saving image: {e}")
            return jsonify({"success": False, "message": "Error saving the image. Please try again."}), 500
    else:
        logging.error(f"Invalid file format: {file.filename}. Allowed: png, jpg, jpeg, gif.")
        return jsonify({"success": False, "message": "Invalid file format. Allowed: png, jpg, jpeg, gif."}), 400


UPLOAD_FOLDER = "generated_docs"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Set up Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_page'

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, email, approved):
        self.id = id
        self.email = email
        self.approved = approved

    @classmethod
    def get(cls, user_id):
        try:
            ref = db.reference('users')
            user_data = ref.child(user_id).get()
            if user_data:
                return cls(user_id, user_data['email'], user_data['approved'])
            return None
        except Exception as e:
            logging.error(f"Error fetching user: {e}")
            return None

# Load user from the session
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Initialize Firebase Admin SDK
local_file_path = "firebase_admin_key.json"
render_file_path = "/etc/secrets/firebase_admin_key.json"

firebase_key_path = render_file_path if os.getenv("RENDER") else local_file_path

try:
    cred = credentials.Certificate(firebase_key_path)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://project-document-creator-default-rtdb.firebaseio.com/'
    })
    print("Firebase Admin SDK initialized successfully.")
except Exception as e:
    print(f"Failed to initialize Firebase Admin SDK: {e}")

# Routes
@app.route("/")
def login_page():
    return render_template("login.html")

@app.route("/register_page")
def register_page():
    return render_template("register.html")

@app.route("/login", methods=["POST"])
def login_user_route():
    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        return render_template("login.html", error="Email and password are required.")

    try:
        ref = db.reference('users')
        user_data = ref.order_by_child('email').equal_to(email).get()

        if user_data:
            for key, value in user_data.items():
                if value['password'] == password:  # Plaintext password check
                    if not value['approved']:
                        return render_template("login.html", error="Account pending approval.")
                    user = User(id=key, email=email, approved=value['approved'])
                    login_user(user)
                    notify_login(email)
                    next_page = request.args.get('next')
                    return redirect(next_page or url_for("home_page"))

        return render_template("register.html", error="User not found, please register.")
    except Exception as e:
        logging.error(f"Login error: {e}")
        return render_template("login.html", error="Login failed. Please try again.")

@app.route("/register", methods=["POST"])
def register_user():
    email = request.form.get("email")
    password = request.form.get("password")
    name = request.form.get("name")
    otp = request.form.get("otp")

    if not email or not password or not name:
        return render_template("register.html", error="All fields are required.")
    if not verify_otp(email, otp):
        return render_template("register.html", error="Invalid or expired OTP.")

    try:
        ref = db.reference('users')
        user_data = ref.order_by_child('email').equal_to(email).get()

        if user_data:
            return render_template("login.html", error="Email already exists. Please log in.")

        ref.push({'email': email, 'password': password, 'name': name, 'approved': False})
        notify_registration_to_admin(name, email, password)
        return render_template("register.html", message="Registration successful, pending approval.")
    except Exception as e:
        logging.error(f"Registration error: {e}")
        return render_template("register.html", error="Registration failed.")

@app.route("/send_otp", methods=["POST"])
def send_otp():
    data = request.json
    email = data.get("email")

    if not email:
        return jsonify({"success": False, "message": "Email is required."}), 400

    try:
        otp = generate_otp()
        save_otp(email, otp)
        notify_registration(email, otp)
        return jsonify({"success": True, "message": "OTP sent to your email."})
    except Exception as e:
        logging.error(f"OTP sending error: {e}")
        return jsonify({"success": False, "message": "Failed to send OTP."}), 500

@app.route("/verify_otp", methods=["POST"])
def verify_otp_route():
    data = request.json
    email = data.get("email")
    otp = data.get("otp")

    if not email or not otp:
        return jsonify({"success": False, "message": "Email and OTP are required."}), 400

    if verify_otp(email, otp):
        return jsonify({"success": True, "message": "OTP verified."})
    return jsonify({"success": False, "message": "Invalid OTP or expired."}), 400

@app.route("/home")
@login_required
def home_page():
    return render_template("index.html")

# Protect the document route (requires login)
@app.route("/document")
@login_required
def document_page():
    return render_template("document.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login_page"))

# OTP management
otp_cache = {}

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def save_otp(email, otp):
    otp_cache[email] = {'otp': otp, 'expires_at': datetime.now() + timedelta(minutes=5)}

def verify_otp(email, otp):
    if email in otp_cache:
        data = otp_cache[email]
        if data['otp'] == otp and data['expires_at'] > datetime.now():
            del otp_cache[email]
            return True
    return False

# Document generation
@app.route("/generate_document", methods=["POST"])
@login_required
def generate_document():
    project_description = request.form.get("project_description")
    # Retrieve the image path from the session or use the default image path
    image_path = session.get('uploaded_image_path', 'static/images/document.png')

    if not project_description:
        return render_template("document.html", message="Project description is required.")
    
    try:
        # Pass both project_description and image_path to the generate_document_and_send function
        filename = generate_document_and_send(project_description, image_path=image_path)

        # Clear the uploaded image path from session after use
        session.pop('uploaded_image_path', None)

        notify_document_generation(email=current_user.email, project_description=project_description)
        download_url = url_for('download_document', filename=filename)
        return render_template("document.html", message="Document generated!", download_url=download_url)
    except Exception as e:
        logging.error(f"Document generation error: {e}")
        return render_template("document.html", message="Failed to generate document.")



@app.route('/download/<filename>')
def download_document(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except Exception as e:
        logging.error(f"Download error: {e}")
        return jsonify({"error": str(e)}), 500

# Admin routes
@app.route("/admin/approve_users")
@login_required
def approve_users():
    if current_user.email != "admin_email@example.com":
        return redirect(url_for('home_page'))

    try:
        ref = db.reference('users')
        pending_users_data = ref.order_by_child('approved').equal_to(False).get()
        pending_users = [
            {'id': user_id, 'name': info['name'], 'email': info['email']}
            for user_id, info in pending_users_data.items()
        ] if pending_users_data else []
        return render_template("approve_users.html", pending_users=pending_users)
    except Exception as e:
        logging.error(f"Error fetching users for approval: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/admin/approve_user/<user_id>", methods=["POST"])
@login_required
def approve_user(user_id):
    try:
        ref = db.reference('users')
        ref.child(user_id).update({'approved': True})
        return redirect(url_for('approve_users'))
    except Exception as e:
        logging.error(f"Approval error: {e}")
        return jsonify({"error": str(e)}), 500

# Check login and approval status
@app.before_request
def check_if_logged_in():
    public_routes = ['login_page', 'login_user_route', 'register_page', 'register_user', 'send_otp', 'verify_otp_route']
    if request.endpoint and request.endpoint.startswith('static'):
        return None

    if not current_user.is_authenticated and request.endpoint not in public_routes:
        return redirect(url_for('login_page', next=request.url))

    if current_user.is_authenticated and not current_user.approved:
        return redirect(url_for('login_page', error="Your account is pending approval."))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
