from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.urandom(24)
    app.config.from_object('config.Config')

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(idUser):
        from .models.users import Users
        return Users.query.get(int(idUser))

    from app.routes import auth,users_route,productos_route,menu_route,contacto_route,carrito_routes
    app.register_blueprint(auth.bp)
    app.register_blueprint(users_route.bp)
    app.register_blueprint(productos_route.bp)
    app.register_blueprint(menu_route.bp)
    app.register_blueprint(contacto_route.bp)
    app.register_blueprint(carrito_routes.bp)
    return app 