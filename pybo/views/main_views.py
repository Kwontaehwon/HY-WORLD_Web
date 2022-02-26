from flask import Blueprint, url_for, current_app, render_template, g
from werkzeug.utils import redirect
from ..views.auth_views import login_required

bp = Blueprint('main', __name__, url_prefix='/')


@bp.route('/')
def hello():
    if g.user != None :
        return redirect(url_for('question._list'))
    else :
        return render_template('main.html')


@bp.route('/index')
@login_required
def index():
    current_app.logger.info("INFO 레벨로 출력")
    return redirect(url_for('question._list'))
