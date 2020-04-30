from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_session import Session
import datetime
from flask_googlemaps import GoogleMaps
from kanapka.config import Config




#app.config['SECRET_KEY'] = 'e333d26c49ed1559e65e98354fd55e88'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:H1344@post@localhost/CJNO'
#app.config['GOOGLEMAPS_KEY'] = 'AIzaSyBme2g3oyAqgYskmcxJxts70PAdaB2qFcg'
#app.config['ACCESS_CODE'] = 'b4a767ed'
#app.config['SESSION_TYPE'] = 'filesystem'    
#app.config['SENDGRID_API_KEY'] = os.environ.get('SENDGRID_API_KEY')



sess = Session()
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'staff.login'
login_manager.login_message_category = 'info'
login_manager.login_message = u"Zanim wejdziesz na tę stronę musisz się zalogować"
 


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    sess.init_app(app)
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    from kanapka.staff.routes import staff
    from kanapka.customers.routes import customers
    from kanapka.errors.handlers import errors
    app.register_blueprint(staff)
    app.register_blueprint(customers)
    app.register_blueprint(errors)

    app.permanent_session_lifetime = datetime.timedelta(days=1)
    app.secret_key = 'a862804c907c54bc4949b5dc0b553781'

    return app