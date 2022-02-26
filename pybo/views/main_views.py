from flask import Blueprint, url_for, current_app, render_template
from werkzeug.utils import redirect
from ..views.auth_views import login_required

bp = Blueprint('main', __name__, url_prefix='/')


@bp.route('/hello')
def hello():
    return render_template('main.html')


@bp.route('/')
@login_required
def index():
    current_app.logger.info("INFO 레벨로 출력")
    return redirect(url_for('question._list'))
