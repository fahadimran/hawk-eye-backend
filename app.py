from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_sock import Sock
from flask_marshmallow import Marshmallow

sock = Sock()
db = SQLAlchemy()

app = Flask(__name__)

bcrypt = Bcrypt()
ma = Marshmallow(app)


def create_app(app, sock):

    from api.admin.admin import admin_blueprint
    from api.auth.auth import auth_blueprint
    from api.alert.alert import alert_blueprint
    from api.registered_case.registered_case import registered_case_blueprint
    from api.authorized_user.authorized_user import authorized_user_blueprint
    from api.stats.stats import stats_blueprint
    import api.sock.sock

    sock.init_app(app)

    app.config.from_pyfile('config.py')
    JWTManager(app)

    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(alert_blueprint, url_prefix='/alerts')
    app.register_blueprint(registered_case_blueprint, url_prefix='/cases')
    app.register_blueprint(stats_blueprint, url_prefix='/stats')
    app.register_blueprint(authorized_user_blueprint,
                           url_prefix='/authorized-users')

    db.init_app(app)
    bcrypt.init_app(app)

    return app, sock
