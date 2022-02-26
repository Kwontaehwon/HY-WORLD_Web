import datetime

from flask import Blueprint, render_template, request, url_for, g, flash, current_app
from sqlalchemy import func, nullslast
from werkzeug.utils import redirect

from .. import db
from ..forms import QuestionForm
from ..models import Question
from ..views.auth_views import login_required

bp = Blueprint('information', __name__, url_prefix='/information')

def _nullslast(obj):
    if current_app.config['SQLALCHEMY_DATABASE_URI'].startswith("sqlite"):
        return obj
    else:
        return nullslast(obj)


@bp.route('/bus')
@login_required
def bus():
    return render_template('information/bus.html')
