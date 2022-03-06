from flask import Blueprint, url_for, current_app, render_template, g, request
from werkzeug.utils import redirect
from ..views.auth_views import login_required

bp = Blueprint('main', __name__, url_prefix='/')


@bp.route('/')
def hello():

    if g.user != None :
        return redirect(url_for('question._list'))
    else :
        user_agent = request.headers.get('User-Agent')
        user_agent = user_agent.lower()

        # In your templates directory, create a mobile version of your site (mobile.index.html).
        # Likewise, add your desired desktop template as well (desktop.index.html).

        if "iphone" in user_agent:
            return redirect(url_for('auth.login'))
        elif "android" in user_agent:
            return redirect(url_for('auth.login'))
        else:
            return render_template('main.html')


@bp.route('/index')
@login_required
def index():
    current_app.logger.info("INFO 레벨로 출력")
    return redirect(url_for('question._list'))
