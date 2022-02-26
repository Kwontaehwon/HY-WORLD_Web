import datetime

from flask import Blueprint, render_template, request, url_for, g, flash, current_app
from sqlalchemy import func, nullslast
from werkzeug.utils import redirect

from .. import db
from ..forms import QuestionForm, AnswerForm, FavorForm, RatingForm
from ..models import Question, Answer, User, question_voter, Favor, Building, Category, Department, Rating, Semester
from ..views.auth_views import login_required

bp = Blueprint('question', __name__, url_prefix='/question')

def _nullslast(obj):
    if current_app.config['SQLALCHEMY_DATABASE_URI'].startswith("sqlite"):
        return obj
    else:
        return nullslast(obj)


@bp.route('/list/')
def _list():
    # 입력 파라미터
    page = request.args.get('page', type=int, default=1)
    kw = request.args.get('kw', type=str, default='')
    so = request.args.get('so', type=str, default='recent')

    # 정렬
    if so == 'recommend':
        sub_query = db.session.query(question_voter.c.question_id, func.count('*').label('num_voter')) \
            .group_by(question_voter.c.question_id).subquery()
        question_list = Question.query \
            .outerjoin(sub_query, Question.id == sub_query.c.question_id) \
            .filter(Question.category != "rating")\
            .order_by(_nullslast(sub_query.c.num_voter.desc()), Question.create_date.desc())
    elif so == 'popular':
        sub_query = db.session.query(Answer.question_id, func.count('*').label('num_answer')) \
            .group_by(Answer.question_id).subquery()
        question_list = Question.query \
            .outerjoin(sub_query, Question.id == sub_query.c.question_id) \
            .filter(Question.category != "rating")\
            .order_by(_nullslast(sub_query.c.num_answer.desc()), Question.create_date.desc())
    else:  # recent
        question_list = Question.query.filter(Question.category != "rating").order_by(Question.create_date.desc())

    # 조회
    if kw:
        search = '%%{}%%'.format(kw)
        sub_query = db.session.query(Answer.question_id, Answer.content, User.username) \
            .join(User, Answer.user_id == User.id).subquery()
        question_list = question_list \
            .join(User) \
            .outerjoin(sub_query, sub_query.c.question_id == Question.id) \
            .filter(Question.subject.ilike(search) |  # 질문제목
                    Question.content.ilike(search) |  # 질문내용
                    User.username.ilike(search) |  # 질문작성자
                    sub_query.c.content.ilike(search) |  # 답변내용
                    sub_query.c.username.ilike(search)  # 답변작성자
                    ) \
            .distinct()
    best_list = []
    num = 0
    sub_query = db.session.query(question_voter.c.question_id, func.count('*').label('num_voter')) \
        .group_by(question_voter.c.question_id).subquery()
    answer_list = Question.query \
        .outerjoin(sub_query, Question.id == sub_query.c.question_id) \
        .order_by(_nullslast(sub_query.c.num_voter.desc()), Question.create_date.desc())
    for question in answer_list:
        date_diff = (datetime.datetime.now() - question.create_date)
        if date_diff < datetime.timedelta(days=7) and num < 3:
            best_list.append(question)
            num += 1
    # 페이징
    question_list = question_list.paginate(page, per_page=10)
    return render_template('question/question_list.html', question_list=question_list, best_list = best_list, page=page, kw=kw, so=so)

@bp.route('/list/<string:category>')
def classify(category):
    # 입력 파라미터
    page = request.args.get('page', type=int, default=1)
    kw = request.args.get('kw', type=str, default='')
    so = request.args.get('so', type=str, default='recent')

    # 정렬
    if so == 'recommend':
        sub_query = db.session.query(question_voter.c.question_id, func.count('*').label('num_voter')) \
            .group_by(question_voter.c.question_id).subquery()
        question_list = Question.query \
            .outerjoin(sub_query, Question.id == sub_query.c.question_id) \
            .filter(Question.category == category) \
            .order_by(_nullslast(sub_query.c.num_voter.desc()), Question.create_date.desc())
    elif so == 'popular':
        sub_query = db.session.query(Answer.question_id, func.count('*').label('num_answer')) \
            .group_by(Answer.question_id).subquery()
        question_list = Question.query \
            .outerjoin(sub_query, Question.id == sub_query.c.question_id) \
            .filter(Question.category == category) \
            .order_by(_nullslast(sub_query.c.num_answer.desc()), Question.create_date.desc())
    else:  # recent
        question_list = Question.query.filter(Question.category == category).order_by(Question.create_date.desc())

    # 조회
    if kw:
        search = '%%{}%%'.format(kw)
        sub_query = db.session.query(Answer.question_id, Answer.content, User.username) \
            .join(User, Answer.user_id == User.id).subquery()
        question_list = question_list \
            .join(User) \
            .outerjoin(sub_query, sub_query.c.question_id == Question.id) \
            .filter(Question.subject.ilike(search) |  # 질문제목
                    Question.content.ilike(search) |  # 질문내용
                    User.username.ilike(search) |  # 질문작성자
                    sub_query.c.content.ilike(search) |  # 답변내용
                    sub_query.c.username.ilike(search)  # 답변작성자
                    ) \
            .distinct()
    best_list = []
    num = 0
    for question in question_list:
        date_diff = (datetime.datetime.now() - question.create_date)
        if date_diff < datetime.timedelta(days=7) and num < 3:
            best_list.append(question)
            num += 1
    # 페이징
    question_list = question_list.paginate(page, per_page=10)
    category_name = Category.query.get(category).description
    return render_template('question/question_list.html', question_list=question_list, best_list=best_list, page=page, kw=kw, so=so, category=category, category_name=category_name)


@bp.route('/detail/<int:question_id>/')
def detail(question_id):
    form = AnswerForm()
    question = Question.query.get_or_404(question_id)
    category = Category.query.get(question.category).description
    return render_template('question/question_detail.html', question=question, form=form, category=category)


@bp.route('/create/', methods=('GET', 'POST'))
@login_required
def create():
    form = QuestionForm()
    if request.method == 'POST' and form.validate_on_submit():
        question = Question(subject=form.subject.data, content=form.content.data, category=form.category.data,
                            create_date=datetime.datetime.now(), user=g.user, is_favor=False, is_rating=False)
        db.session.add(question)
        g.user.point += 1
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('question/question_form.html', form=form, is_favor=False)


@bp.route('/create-favor/', methods=('GET', 'POST'))
@login_required
def create_favor():
    form = FavorForm()
    if request.method == 'POST' and form.validate_on_submit():
        question = Question(subject=form.subject.data, content=form.content.data, category="favor",
                            create_date=datetime.datetime.now(), user=g.user, is_favor=True, is_rating=False)
        db.session.add(question)
        py_favor_datetime = datetime.datetime.fromisoformat(form.favor_date.data)
        building_id = form.building.data
        building = Building.query.get(building_id)
        favor = Favor(favor_date=py_favor_datetime, building_id=building_id)
        db.session.add(favor)
        question.favor_set.append(favor)
        building.building_set.append(favor)
        g.user.point += 5
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('question/question_form.html', form=form, is_favor=True)


@bp.route('/create-rating/', methods=('GET', 'POST'))
@login_required
def create_rating():
    form = RatingForm()
    semester_list = Semester.query.order_by(_nullslast(Semester.id.desc()))
    department_list = Department.query.order_by(_nullslast(Department.id.asc()))
    if request.method == 'POST' and form.validate_on_submit():
        question = Question(subject=form.subject.data, content=form.content.data, category="rating",
                            create_date=datetime.datetime.now(), user=g.user, is_rating=True, is_favor=False)
        db.session.add(question)
        if form.is_major.data == 1 :
            is_major = True
        else:
            is_major = False

        semester_id = form.semester.data
        department_id = form.department.data
        rating = Rating(semester_id= semester_id, department_id=department_id,
                        is_major=is_major, score=form.score.data, professor=form.professor.data)
        semester = Semester.query.get(semester_id)
        department = Department.query.get(department_id)
        db.session.add(rating)
        question.rating_set.append(rating)
        semester.semester_set.append(rating)
        department.department_set.append(rating)
        g.user.point += 5
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('question/rating_form.html', form=form, semester_list=semester_list, department_list=department_list)

@bp.route('/rating/detail/<int:question_id>/')
def rating_detail(question_id):
    form = AnswerForm()
    question = Question.query.get_or_404(question_id)
    category = Category.query.get(question.category).description
    return render_template('question/rating_detail.html', question=question, form=form, category=category)



@bp.route('/modify/<int:question_id>', methods=('GET', 'POST'))
@login_required
def modify(question_id):
    question = Question.query.get_or_404(question_id)
    if g.user != question.user:
        flash('수정권한이 없습니다')
        return redirect(url_for('question.detail', question_id=question_id))
    if request.method == 'POST':
        if question.is_favor:
            form = FavorForm()
        else:
            form = QuestionForm()
        if form.validate_on_submit():
            form.populate_obj(question)
            question.modify_date = datetime.datetime.now()  # 수정일시
            if question.is_favor:
                py_favor_datetime = datetime.datetime.fromisoformat(form.favor_date.data)
                question.favor_set[0].favor_date = py_favor_datetime
                question.favor_set[0].building_id = form.building.data
            db.session.commit()
            return redirect(url_for('question.detail', question_id=question_id))
    else:
        if question.is_favor:
            form = FavorForm(obj=question)
        else:
            form = QuestionForm(obj=question)
    return render_template('question/question_form.html', form=form, is_favor=question.is_favor)


@bp.route('/delete/<int:question_id>')
@login_required
def delete(question_id):
    question = Question.query.get_or_404(question_id)
    if g.user != question.user:
        flash('삭제권한이 없습니다')
        return redirect(url_for('question.detail', question_id=question_id))
    db.session.delete(question.favor_set[0])
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for('question._list'))

