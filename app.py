import os
import logging
from dotenv import load_dotenv
from urllib.parse import urlparse

from flask import Flask
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix
from models import db, User
from routes import routes_bp

load_dotenv()

logging.basicConfig(level=logging.DEBUG)

# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# configure the database
database_url = os.environ.get("DATABASE_URL")
if database_url:
    # Handle Supabase connection string
    if "supabase" in database_url:
        # Parse the URL to ensure it's properly formatted
        parsed = urlparse(database_url)
        # Ensure the connection string uses the correct format
        database_url = f"postgresql://{parsed.netloc.split('@')[0]}@{parsed.netloc.split('@')[1]}{parsed.path}"

app.config["SQLALCHEMY_DATABASE_URI"] = database_url or "sqlite:///mikrotik_generator.db"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
    "pool_size": 5,
    "max_overflow": 10,
    "connect_args": {
        "connect_timeout": 10
    }
}

# initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Register the blueprint
app.register_blueprint(routes_bp)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()
    
    # Create default admin user if none exists
    from werkzeug.security import generate_password_hash
    
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Default admin user created: admin/admin123")

@app.route('/test')
def test_route():
    return 'Test route is working!'

if __name__ == '__main__':
    app.run(debug=True)
