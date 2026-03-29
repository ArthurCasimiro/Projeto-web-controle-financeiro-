import os
from flask import Flask, render_template
from extensao import db, login_manager
import modelos
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///fintrack.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager.init_app(app)

from blueprints.bp_auth import bp_auth
from blueprints.bp_boleto import boleto_bp

app.register_blueprint(bp_auth)
app.register_blueprint(boleto_bp)

@app.route('/')
def home_page():
    return render_template('login.html')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=os.environ.get('FLASK_DEBUG', 'True') == 'True')
