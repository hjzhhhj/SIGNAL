from flask import Flask, render_template
from config import Config
from extensions import db, login_manager, migrate
from routes import main_bp
from auth import auth_bp
from pytz import timezone

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    login_manager.login_view = 'auth.login'

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

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
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(port=5001, debug=True)