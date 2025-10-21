from flask import Flask, render_template
from config import Config
from extensions import db, login_manager, migrate
from routes import main_bp
from auth import auth_bp
from pytz import timezone

def create_app():
    app = Flask(__name__)  # Flask 애플리케이션 인스턴스 생성
    app.config.from_object(Config) 

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # SQLAlchemy의 변경 추적 비활성화

    db.init_app(app)          
    migrate.init_app(app, db) 
    login_manager.init_app(app)  

    # 로그인이 필요한 화면이면,
    login_manager.login_view = 'auth.login' 
    login_manager.login_message = '로그인이 필요한 페이지입니다.' 

    from models import User  
    @login_manager.user_loader
    def load_user(user_id):
        # 로그인 세션에서 사용자 아이디로 반환
        return db.session.get(User, int(user_id))


    # 한국 시간으로 포맷
    @app.template_filter('datetime_kst')
    def format_datetime_kst(dt):
        if dt:
            if dt.tzinfo is None:
                utc_dt = timezone('UTC').localize(dt)  
            else:
                utc_dt = dt.astimezone(timezone('UTC'))  

            kst_dt = utc_dt.astimezone(timezone('Asia/Seoul')) 
            return kst_dt.strftime('%Y년 %m월 %d일 %H:%M')  
        return ''

    app.register_blueprint(main_bp) 
    app.register_blueprint(auth_bp)  

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    with app.app_context():
        db.create_all()  # 데이터베이스 테이블이 없으면 생성

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)  # 실행!
