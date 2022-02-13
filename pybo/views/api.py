from flask import Blueprint, url_for, current_app, jsonify, request
from sqlalchemy import func, nullslast
import datetime

from .. import db
from ..models import Question, question_voter

bp = Blueprint('api', __name__, url_prefix='/api')

def _nullslast(obj):
    if current_app.config['SQLALCHEMY_DATABASE_URI'].startswith("sqlite"):
        return obj
    else:
        return nullslast(obj)

@bp.route('/hotboard')
def environments():
    sub_query = db.session.query(question_voter.c.question_id, func.count('*').label('num_voter')) \
        .group_by(question_voter.c.question_id).subquery()
    question_list = Question.query \
        .outerjoin(sub_query, Question.id == sub_query.c.question_id) \
        .order_by(_nullslast(sub_query.c.num_voter.desc()), Question.create_date.desc())
    num = 0
    answer_list = []
    for question in question_list:
        date_diff = (datetime.datetime.now() - question.create_date)
        if date_diff < datetime.timedelta(days=7) and num < 4:
            answer_list.append(question.subject)
    return jsonify({"subject" : answer_list})


@bp.route('/test', methods = ['POST'])
def userLogin():
    user = request.get_json()#json 데이터를 받아옴
    return jsonify(user)# 받아온 데이터를 다시 전송