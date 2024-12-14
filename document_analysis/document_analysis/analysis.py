import os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app, 
    send_from_directory, jsonify
)
from werkzeug.exceptions import abort # abort , used to return an HTTP status code
from werkzeug.utils import secure_filename # secure_filename, used to secure the filename of the uploaded file
from document_analysis.auth import login_required # login_required, used to require authentication to access a view
from document_analysis.db import get_db # get_db, used to get a connection to the database
import google.generativeai as genai # Import the generativeai module from the google package
import PyPDF2 # Import the PyPDF2 module
import docx # Import the docx module
import json 

bp = Blueprint('analysis', __name__) # Blueprint object for the analysis module, that defines the routes and views for the analysis module

def allowed_file(filename):
    """Check if a file has an allowed extension.

    Args:
        filename (str): The name of the file to check.

    Returns:
        bool: True if the file has an allowed extension, False otherwise.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def extract_text(file):
    """Extract text from a file.

    Args:
        file (FileStorage): The file from which to extract text.

    Returns:
        str: The extracted text from the file.
    """
    filename = secure_filename(file.filename)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    try:
        if filename.endswith('.pdf'):
            with open(file_path, 'rb') as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
        elif filename.endswith('.docx'):
            doc = docx.Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
        else:
            with open(file_path, 'r', encoding='utf-8') as txt_file:
                text = txt_file.read()
    finally:
        os.remove(file_path)
    
    return text

@bp.route('/') # Define the index route for the analysis module
def index():
    return render_template('analysis/index.html')

@bp.route('/landing') # Define the landing route for the analysis module
def landing():
    return render_template('analysis/landing.html')

@bp.route('/dashboard') # Define the dashboard route for the analysis module it requires authentication to access
@login_required
def dashboard():
    """Render the dashboard view for the analysis module.

    Returns:
        _io.TextIOWrapper: The rendered dashboard view.
    """
    db = get_db()
    documents = db.execute(
        'SELECT d.id, title, content, created, author_id, username'
        ' FROM document d JOIN user u ON d.author_id = u.id'
        ' WHERE d.author_id = ?'
        ' ORDER BY created DESC',
        (g.user['id'],)
    ).fetchall()
    
    recent_analysis = db.execute(
        'SELECT a.id, a.type, a.content, a.created, d.title'
        ' FROM analysis a JOIN document d ON a.document_id = d.id'
        ' WHERE d.author_id = ?'
        ' ORDER BY a.created DESC LIMIT 5',
        (g.user['id'],)
    ).fetchall()
    
    return render_template('analysis/dashboard.html', 
                         documents=documents, 
                         recent_analysis=recent_analysis)

@bp.route('/upload', methods=['POST']) # Define the upload route for the analysis module it requires authentication to access
@login_required
def upload_document():
    """Upload a document file and extract text from it.

    Returns:
        str: A JSON response with a message indicating if the file was successfully processed or an error
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename): # allowed_file func call
        try:
            text = extract_text(file)
            db = get_db()
            db.execute(
                'INSERT INTO document (title, content, author_id)'
                ' VALUES (?, ?, ?)',
                (secure_filename(file.filename), text, g.user['id'])
            )
            db.commit()
            return jsonify({"message": "File successfully processed", "text": text})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    return jsonify({"error": "File type not allowed"}), 400

@bp.route('/analyze/<int:id>', methods=['GET']) # Define the analyze route for the analysis module it requires authentication to access
@login_required
def analyze(id):
    """Analyze a document by generating a quiz, summary, keywords, or translation.

    Args:
        id (int): The id of the document to analyze.

    Returns:
        _io.TextIOWrapper: The rendered analysis view.
    """
    document = get_db().execute(
        'SELECT d.id, title, content, created, author_id, username'
        ' FROM document d JOIN user u ON d.author_id = u.id'
        ' WHERE d.id = ?',
        (id,)
    ).fetchone()

    if document is None:
        abort(404, f"Document id {id} doesn't exist.")

    analyses = get_db().execute(
        'SELECT id, type, content, created'
        ' FROM analysis'
        ' WHERE document_id = ?'
        ' ORDER BY created DESC',
        (id,)
    ).fetchall()

    return render_template('analysis/view.html', 
                         document=document, 
                         analyses=analyses)

@bp.route('/generate_quiz', methods=['POST']) # Define the generate_quiz route for the analysis module it requires authentication to access
@login_required
def generate_quiz():
    """Generate a quiz based on the provided text.
    
    Returns:
        str: A JSON response with the generated quiz or an error message
    """
    data = request.get_json()
    text = data.get('text')
    document_id = data.get('document_id')
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    # Prompt for quiz  generation    
    prompt = f"""Generate a quiz based on the following text. Include:
    - 15 multiple-choice questions
    - 3 fill-in-the-blank questions with associated answer choices 
    - 2 true/false questions
    Format the output as a JSON object.
    
    Text: {text}"""
    
    model = genai.GenerativeModel('gemini-pro') # Create a generative model object.
    response = model.generate_content(prompt)
    
    if document_id:
        db = get_db()
        db.execute(
            'INSERT INTO analysis (document_id, type, content)'
            ' VALUES (?, ?, ?)',
            (document_id, 'quiz', response.text)
        )
        db.commit()
    
    return jsonify({"quiz": response.text}) 

@bp.route('/summarize', methods=['POST']) # Define the summarize route for the analysis module it requires authentication to access
@login_required
def summarize():
    """Summarize the provided text.

    Returns:
        str: A JSON response with the generated summary or an error message
    """
    data = request.get_json()
    text = data.get('text')
    document_id = data.get('document_id')
    length = data.get('length', 'medium')
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
        
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(
        f"Summarize the following text. Provide a {length} summary.\n\nText: {text}"
    )
    
    if document_id:
        db = get_db()
        db.execute(
            'INSERT INTO analysis (document_id, type, content)'
            ' VALUES (?, ?, ?)',
            (document_id, 'summary', response.text)
        )
        db.commit()
    
    return jsonify({"summary": response.text})

@bp.route('/extract_keywords', methods=['POST']) # Define the extract_keywords route for the analysis module it requires authentication to access
@login_required
def extract_keywords():
    """Extract keywords from the provided text.

    Returns: str: A JSON response with the extracted keywords or an error message
    """
    data = request.get_json()
    text = data.get('text')
    document_id = data.get('document_id')
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
        
    model = genai.GenerativeModel('gemini-pro')
    prompt = """Extract key terms and important phrases from this text. 
    Return them as a simple array of strings, for example: ["keyword1", "keyword2", "keyword3"].
    Do not include any additional formatting or explanation.
    
    Text:
    {}""".format(text)
    
    response = model.generate_content(prompt)
    
    try:
        # Try to parse response as JSON array
        keywords = json.loads(response.text)
        if not isinstance(keywords, list):
            keywords = [response.text]
    except json.JSONDecodeError:
        # If parsing fails, split by newlines and clean up
        keywords = [k.strip() for k in response.text.split('\n') if k.strip()]
    
    if document_id:
        db = get_db()
        db.execute(
            'INSERT INTO analysis (document_id, type, content)'
            ' VALUES (?, ?, ?)',
            (document_id, 'keywords', json.dumps(keywords))
        )
        db.commit()
    
    return jsonify({"keywords": keywords})

@bp.route('/translate', methods=['POST']) # Define the translate route for the analysis module it requires authentication to access
@login_required
def translate():
    """Translate the provided text to the target language.

    Returns:
        str: A JSON response with the translated text or an error message
    """
    data = request.get_json()
    text = data.get('text')
    target_language = data.get('target_language')
    document_id = data.get('document_id')
    
    if not text or not target_language:
        return jsonify({"error": "Missing required parameters"}), 400
        
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(
        f"Translate this text to {target_language}:\n\n{text}"
    )
    
    if document_id:
        db = get_db()
        db.execute(
            'INSERT INTO analysis (document_id, type, content)'
            ' VALUES (?, ?, ?)',
            (document_id, f'translation_{target_language.lower()}', response.text)
        )
        db.commit()
    
    return jsonify({"translation": response.text})

