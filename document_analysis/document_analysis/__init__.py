import os
from flask import Flask
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv
from flask import Blueprint, render_template

bp = Blueprint('analysis', __name__)

@bp.route('/')
def index():
    return render_template('analysis/index.html')

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True, static_folder='static', template_folder='templates',)
    CORS(app)
    
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'document_analysis.sqlite'),
        UPLOAD_FOLDER=os.path.join(app.instance_path, 'uploads'),
        ALLOWED_EXTENSIONS={'pdf', 'docx', 'txt'}
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.update(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
        os.makedirs(app.config['UPLOAD_FOLDER'])
    except OSError:
        pass

    # Initialize Google Gemini API
    load_dotenv()
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    
    # Register database commands
    from . import db
    db.init_app(app)
    
    # Register blueprints
    from . import auth, analysis
    app.register_blueprint(auth.bp)
    app.register_blueprint(analysis.bp)
    app.add_url_rule('/', endpoint='index')
    app.add_url_rule('/', endpoint='analysis.landing')

    return app