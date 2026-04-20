import os
from flask import Flask, render_template
from extensao import db, login_manager
from dotenv import load_dotenv

load_dotenv(override=True)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///fintrack.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'home_page'

import modelos

from blueprints.bp_auth import bp_auth
from blueprints.bp_dashboard import bp_dashboard
from blueprints.bp_boleto import bp_boleto
from blueprints.bp_alerta import bp_alerta
from blueprints.bp_assinatura import bp_assinatura
from blueprints.bp_categoria import bp_categoria
from blueprints.bp_gasto import bp_gasto
from blueprints.bp_fundo import bp_fundo
from blueprints.bp_meta import bp_meta
from blueprints.bp_admin import bp_admin
from blueprints.bp_exportar import bp_exportar

app.register_blueprint(bp_auth)
app.register_blueprint(bp_dashboard)
app.register_blueprint(bp_boleto)
app.register_blueprint(bp_alerta)
app.register_blueprint(bp_assinatura)
app.register_blueprint(bp_categoria)
app.register_blueprint(bp_gasto)
app.register_blueprint(bp_fundo)
app.register_blueprint(bp_meta)
app.register_blueprint(bp_admin)
app.register_blueprint(bp_exportar)


@app.context_processor
def inject_now():
    from datetime import datetime
    return {'now': datetime.now()}


@app.route('/')
def home_page():
    return render_template('login.html')


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)