from flask import Blueprint, url_for, flash, g
from werkzeug.utils import redirect

from pybo import db
from pybo.models import Question, Answer, User, Favor
from pybo.views.auth_views import login_required

bp = Blueprint('vote', __name__, url_prefix='/vote')


@bp.route('/question/<int:question_id>/')
@login_required
def question(question_id):
    _question = Question.query.get_or_404(question_id)
    question_author = User.query.get(_question.user_id)
    if g.user == _question.user:
        flash('본인이 작성한 글은 추천할수 없습니다')
    else:
        _question.voter.append(g.user)
        question_author.point += 1
        db.session.commit()
    return redirect(url_for('question.detail', question_id=question_id))


@bp.route('/answer/<int:answer_id>/')
@login_required
def answer(answer_id):
    _answer = Answer.query.get_or_404(answer_id)
    answer_author = User.query.get(_answer.user_id)
    if g.user == _answer.user:
        flash('본인이 작성한 글은 추천할수 없습니다')
    else:
        _answer.voter.append(g.user)
        answer_author.point += 1
        db.session.commit()
    return redirect(url_for('question.detail', question_id=_answer.question.id))


@bp.route('/answer/resolve/<int:answer_id>/')
@login_required
def resolve(answer_id):
    _answer = Answer.query.get_or_404(answer_id)
    answer_author = User.query.get(_answer.user_id)
    question = Question.query.get(_answer.question_id)
    if g.user == _answer.user:
        flash('본인이 작성한 글은 채택할 수 없습니다')
    else:
        if g.user == question.user:
            favor = question.favor_set[0]
            if favor.resolve_answer_id is None:
                favor.resolve_answer_id = answer_id
                _answer.resolve_answer.append(favor)
                answer_author.point += 10
                db.session.commit()
            else:
                flash('이미 다른 댓글이 채택되었습니다. 하나의 댓글만 채택 가능합니다.')
        else:
            flash('게시물 작성자 외의 이용자는 채택할 수 있습니다')
    return redirect(url_for('question.detail', question_id=_answer.question.id))
