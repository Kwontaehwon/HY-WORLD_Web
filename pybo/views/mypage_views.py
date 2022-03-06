import datetime

from flask import Blueprint, render_template, request, url_for, g, flash, current_app
from sqlalchemy import func, nullslast
from werkzeug.utils import redirect

from .. import db
from ..forms import QuestionForm, AnswerForm, FavorForm
from ..models import Question, Answer, User, question_voter, Favor, Building, Category
from ..views.auth_views import login_required

bp = Blueprint('mypage', __name__, url_prefix='/mypage')

def _nullslast(obj):
    if current_app.config['SQLALCHEMY_DATABASE_URI'].startswith("sqlite"):
        return obj
    else:
        return nullslast(obj)


@bp.route('/')
@login_required
def mypage():
    user = g.user
    question_query = Question.query.filter(Question.user_id == user.id)\
        .order_by(Question.create_date.desc())
    answer_query = Answer.query.filter(Answer.user_id == user.id)\
        .order_by(Answer.create_date.desc())

    num = 0
    vote = 0
    MAX_ELEMENT = 5
    question_list = []
    answer_list = []


    for question in question_query:
        if num < MAX_ELEMENT:
            question_list.append(question)
        num += 1
        vote += len(question.voter)
    question_num = num
    num = 0
    for answer in answer_query:
        if num < MAX_ELEMENT:
            answer_list.append(answer)
        num += 1
        vote += len(answer.voter)
    answer_num = num
    spent_time = (datetime.datetime.now() - user.signup_date)
    spent_days = spent_time.days

    return render_template('mypage/mypage.html', user=user, question_list=question_list, answer_list=answer_list,
                           vote=vote, question_num=question_num, answer_num=answer_num, spent_time=spent_days)