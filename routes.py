from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from models import LoveHistory
from extensions import db
from love_test import love_result_message
from mail_sender import send_letter_mail
from filters import filter_bad_words
import random
import string
import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    if current_user.is_authenticated:
        return render_template('home.html', user=current_user)
    return render_template('index.html')

@main_bp.route('/love_test', methods=['GET', 'POST'])
@login_required
def love_test():
    result = None
    if request.method == 'POST':
        name1 = request.form.get('name1')
        name2 = request.form.get('name2')
        if not name1 or not name2:
            flash('두 이름을 모두 입력해주세요.', 'danger')
            return redirect(url_for('main.love_test'))
        
        score, msg = love_result_message(name1, name2)
        result = {'name1': name1, 'name2': name2, 'score': score, 'msg': msg}
        
        history = LoveHistory(user_id=current_user.id,
                              name1=name1,
                              name2=name2,
                              score=score,
                              result_msg=msg,
                              date=datetime.datetime.now())
        db.session.add(history)
        db.session.commit()
    return render_template('love_test.html', result=result)

@main_bp.route('/history')
@login_required
def history():
    histories = LoveHistory.query.filter_by(user_id=current_user.id).all()
    return render_template('history.html', histories=histories)

@main_bp.route('/send_letter', methods=['GET', 'POST'])
@login_required
def send_letter():
    if request.method == 'POST':
        receiver_email = request.form.get('receiver_email')
        sender_name = request.form.get('sender_name')
        content = request.form.get('content')
        subject = request.form.get('subject', '익명의 편지')
        
        if not receiver_email or not sender_name or not content:
            flash('모든 항목을 입력해주세요.', 'warning')
            return redirect(url_for('main.send_letter'))
        
        if not receiver_email.endswith('@e-mirim.hs.kr'):
            flash('학교 이메일만 입력 가능합니다.', 'danger')
            return redirect(url_for('main.send_letter'))

        send_letter_mail(receiver_email, subject, sender_name, content)
        flash('편지가 성공적으로 전송되었습니다!', 'success')
        return redirect(url_for('main.home'))
    return render_template('send_letter.html')
