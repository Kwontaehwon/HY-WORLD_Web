from flask import Blueprint, url_for, current_app, jsonify, request
from sqlalchemy import func, nullslast
import datetime
from werkzeug.security import  check_password_hash

from .. import db
from ..models import Question, question_voter, User

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
            answer_list.append(question)
    json_list = []
    for answer in answer_list:
        json_list.append(answer.subject)
    return jsonify({"result" : json_list})


@bp.route('/favor')
def favor():
    question_list = Question.query.filter(Question.is_favor == True)\
        .order_by(Question.create_date.desc())
    favor_list = []
    for question in question_list:
        date_diff = (datetime.datetime.now() - question.create_date)
        if date_diff < datetime.timedelta(days=7):
            favor_list.append(question)
    json_list = []
    for favor in favor_list:
        json_list.append({"subject" : favor.subject, "content" : favor.content, "location" : favor.favor_set.building_id})
    return jsonify({"result" : json_list})


@bp.route('/login', methods = ['POST'])
def userLogin():
    user = request.get_json()#json 데이터를 받아옴
    user_id = user['userId']
    user_pw = user['userPw']
    error = None
    user = User.query.filter_by(username=user_id).first()
    if not user:
        error = "존재하지 않는 사용자입니다."
    elif not check_password_hash(user.password, user_pw):
        error = "비밀번호가 올바르지 않습니다."
    if error is None:
        return jsonify({"result": "true"})
    return jsonify({"result": error})
    #return jsonify(user)# 받아온 데이터를 다시 전송