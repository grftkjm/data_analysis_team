from flask import Blueprint, render_template

index_bp = Blueprint("index", __name__)

@index_bp.route('/')
def index():
    return render_template('index.html')


@index_bp.route('/analysis')
def analysis():
    return render_template('analysis.html')