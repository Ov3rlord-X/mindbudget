from flask import Flask, render_template
from extensions import db, login_manager, bcrypt
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    login_manager.login_view = 'auth.login'

    with app.app_context():
        from models import User, MoodLog, Journal, Expense, Budget

        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

        from routes.auth import auth
        from routes.main import main
        from routes.mood import mood
        from routes.finance import finance

        app.register_blueprint(auth)
        app.register_blueprint(main)
        app.register_blueprint(mood)
        app.register_blueprint(finance)

        db.create_all()

        # 404 handler
        @app.errorhandler(404)
        def page_not_found(e):
            return render_template('404.html'), 404

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0')