from flask import Blueprint, render_template, redirect, url_for
from flask_jwt_extended import verify_jwt_in_request

views_bp = Blueprint('views', __name__)

@views_bp.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@views_bp.route('/dashboard', methods=['GET'])
def dashboard_page():
    try:
        verify_jwt_in_request(locations=['cookies'])
    except Exception:
        return redirect((url_for('views.login_page')))
    return render_template('dashboard.html')