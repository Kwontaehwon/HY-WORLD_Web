import datetime

from flask import Blueprint, render_template, request, url_for, g, flash, current_app
from sqlalchemy import func, nullslast
from werkzeug.utils import redirect
from bs4 import BeautifulSoup
import requests

from .. import db
from ..forms import QuestionForm
from ..models import Question, Restaurant
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


@bp.route('/menu')
@login_required
def menu():
    restaurant_list = Restaurant.query.order_by(_nullslast(Restaurant.id.asc()))
    return render_template('information/menu.html', restaurant_list=restaurant_list)


@bp.route('/menu/<int:restaurant_id>')
@login_required
def menu_detail(restaurant_id):
    daylist = ['월', '화', '수', '목', '금', '토', '일']
    year = datetime.datetime.now().strftime("%Y")
    real_month = datetime.datetime.now().strftime("%m")
    date = datetime.datetime.now().strftime("%d")
    day = datetime.datetime.now().weekday()
    month = "0" + str(int(real_month) - 1)
    restaurant = Restaurant.query.get(restaurant_id)
    restaurant_id
    url = "https://www.hanyang.ac.kr/web/www/re" + str(restaurant_id) + "?" \
          "p_p_id=foodView_WAR_foodportlet&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_pos=1&p_p_col_count=2&_foodView_WAR_foodportlet_s" \
          "FoodDateDay=" + date + "&" \
          "_foodView_WAR_foodportlet_sFoodDateYear=" + year + "&" \
          "_foodView_WAR_foodportlet_action=view&_foodView_WAR_foodportlet" \
          "_sFoodDateMonth=" + month
    response = requests.get(url)
    if restaurant_id == 13:
        provide_days = 6
        service_time = 3
    else:
        provide_days = 5
        service_time = 2
    breakfast_list = []
    lunch_list = []
    dinner_list = []
    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        menu_list = soup.find_all("ul", {"class": "bs-ul"})[4:]

        if menu_list != None:
            for i in range(len(menu_list)):
                menu_day = menu_list[i].find_all("li")
                answer = []
                for j in range(len(menu_day)):
                    #answer.append({"menu": menu_day[j].get_text(), "day_code": daylist[i % provide_days], "code":i % provide_days, "len_menu" : len(menu_day)} )
                    answer.append(menu_day[j].get_text())
                if service_time == 2 :
                    if i // provide_days == 0 :
                        lunch_list.append(answer)
                    if i // provide_days == 1 :
                        dinner_list.append(answer)
                else :
                    if i // provide_days == 0:
                        breakfast_list.append(answer)
                    elif i // provide_days == 1:
                        lunch_list.append(answer)
                    else :
                        dinner_list.append(answer)
        else:
            lunch_list.append(None)
    else:
        lunch_list.append("ERROR")
    return render_template('information/menu_detail.html', lunch_list=lunch_list, dinner_list=dinner_list,
                           restaurant=restaurant, daylist=daylist, provide_days=provide_days, breakfast_list=breakfast_list)