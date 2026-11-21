import os 
from flask import Blueprint, send_from_directory

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')

web_bp = Blueprint(
    'web',
    __name__,
    static_folder=FRONTEND_DIR,
    static_url_path='/assets'
)

@web_bp.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')