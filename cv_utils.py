import os
import PyPDF2
import docx
from werkzeug.utils import secure_filename
from datetime import datetime

# This can be a global or passed from app.config
UPLOAD_FOLDER_PATH = 'uploads' # Relative to where script is run, or make absolute
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}

# Ensure uploads directory exists when module is loaded or functions are called
os.makedirs(UPLOAD_FOLDER_PATH, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, upload_folder_override=None):
    """Saves the uploaded file to the UPLOAD_FOLDER_PATH or an override path."""
    target_folder = upload_folder_override if upload_folder_override else UPLOAD_FOLDER_PATH
    os.makedirs(target_folder, exist_ok=True) # Ensure it exists

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(target_folder, unique_filename)
        try:
            file.save(filepath)
            return filepath, unique_filename
        except Exception as e:
            print(f"Error saving file {unique_filename} to {filepath}: {e}")
            return None, None
    return None, None


def extract_text_from_pdf(file_path):
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text: # PyPDF2 can return None
                    text += page_text
            return text
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return ""

def extract_text_from_docx(file_path):
    try:
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        print(f"Error extracting DOCX: {e}")
        return ""

def extract_text_from_txt(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error extracting TXT: {e}")
        return ""

def extract_cv_text_from_file(file_path, filename): # Renamed from your single file's extract_cv_text
    extension = filename.rsplit('.', 1)[1].lower()
    
    if extension == 'pdf':
        return extract_text_from_pdf(file_path)
    elif extension == 'docx':
        return extract_text_from_docx(file_path)
    elif extension in ['txt', 'doc']:
        return extract_text_from_txt(file_path)
    else:
        print(f"Unsupported file type for text extraction: {extension}")
        return ""

def cleanup_file(filepath):
    if filepath and os.path.exists(filepath):
        try:
            os.remove(filepath)
            print(f"🗑️ Removed temp file: {filepath}")
        except Exception as e_rm:
            print(f"⚠️ Error removing temp file {filepath}: {e_rm}")