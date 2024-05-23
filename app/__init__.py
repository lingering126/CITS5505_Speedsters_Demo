from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,current_user
from flask_migrate import Migrate
from flask_session import Session



# Initialize database
db = SQLAlchemy()

# Initialize login manager
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    app.config['UPLOADED_PHOTOS_DEST'] = 'static/uploads'

    
    db.init_app(app)
    migrate = Migrate(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Update this as per your Blueprint
    Session(app)


    from app.blueprint.pnr.filters import strip_html, truncate_words
    app.jinja_env.filters['strip_html'] = strip_html
    app.jinja_env.filters['truncate_words'] = truncate_words


    from app.blueprint.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    from app.blueprint.pnr import pr as pr_blueprint
    app.register_blueprint(pr_blueprint)
    from app.blueprint.user import user as user_blueprint
    app.register_blueprint(user_blueprint)
    from app.blueprint.notifications import notifications_bp
    app.register_blueprint(notifications_bp, url_prefix='/notifications')
 

    
    # Load the user with the login manager
    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Context Processor for Notifications Count
    from app.models.models import Notification
    @app.context_processor
    def inject_notification_count():
        if current_user.is_authenticated:
            new_notifications_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        else:
            new_notifications_count = 0
        return dict(new_notifications_count=new_notifications_count)
    


    
    return app

