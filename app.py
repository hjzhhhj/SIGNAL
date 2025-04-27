from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from config import Config
from extensions import db, mail, login_manager
from routes import main_bp  # 메인 라우터 블루프린트
from auth import auth_bp   # 인증 라우터 블루프린트

# Flask 확장 모듈 초기화
db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 확장 모듈 등록
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)

    # 로그인 안한 사용자가 접근 시 리다이렉트할 페이지
    login_manager.login_view = 'auth.login'

    # 로그인 유저 로드 함수
    from models import User, LoveHistory  # 모델 import

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # 블루프린트 등록
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    # 에러 처리
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500

    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
