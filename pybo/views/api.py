from flask import Blueprint, url_for, current_app, jsonify, request
from sqlalchemy import func, nullslast
from bs4 import BeautifulSoup
import requests
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
        .filter(Question.category != "rating") \
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
        if date_diff < datetime.timedelta(days=7) and question.favor_set[0].resolve_answer_id == None:
            favor_list.append(question)
    json_list = []
    for favor in favor_list:
        json_list.append({"subject" : favor.subject, "content" : favor.content,
                          "location" : favor.favor_set[0].building_id, "favor_date" : favor.favor_set[0].favor_date.strftime('%Y-%m-%d'),
                          "favor_time" : favor.favor_set[0].favor_date.strftime("%H:%M"), "create_time" : favor.create_date.strftime("%H:%M"),
                          "create_date" : favor.create_date.strftime('%Y-%m-%d'), "user" : favor.user.username, "question_id" : favor.id})
    return jsonify({"favor_list" : json_list})

@bp.route('/menu')
def menu():
    daylist = ['월', '화', '수', '목', '금', '토', '일']
    year = datetime.datetime.now().strftime("%Y")
    real_month = datetime.datetime.now().strftime("%m")
    date = datetime.datetime.now().strftime("%d")
    day = datetime.datetime.now().weekday()
    month = "0" + str(int(real_month)-1)
    json_list = []
    for loc in range(11,16):
        url = "https://www.hanyang.ac.kr/web/www/re" + str(loc) + "?" \
              "p_p_id=foodView_WAR_foodportlet&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_pos=1&p_p_col_count=2&_foodView_WAR_foodportlet_s" \
              "FoodDateDay=" + date + "&"  \
              "_foodView_WAR_foodportlet_sFoodDateYear=" + year + "&" \
              "_foodView_WAR_foodportlet_action=view&_foodView_WAR_foodportlet" \
              "_sFoodDateMonth=" + month
        response = requests.get(url)
        if loc == 13 :
            provide_days = 6
        else :
            provide_days = 5
        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            menu_list = soup.find_all("ul", {"class": "bs-ul"})[4:]
            answer = []
            if (menu_list != None):
                for i in range(len(menu_list)):
                    menu_day = menu_list[i].find_all("li")
                    for j in range(len(menu_day)):
                        answer.append({"menu": menu_day[j].get_text(), "day_code": daylist[i % provide_days] , "day_plus": i//provide_days})
                json_list.append({"result": answer, "location_code":loc})
            else:
                json_list.append({"result": "None", "location_code":loc})
        else:
            return jsonify({"result": response.status_code, "base_date": year+real_month+date})
    return jsonify({"result": json_list, "base_date": year+real_month+date})



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
        return jsonify({"result": "true", "user_name" : user.username, "user_point" : user.point})
    return jsonify({"result": error})
    #return jsonify(user)# 받아온 데이터를 다시 전송