from flask import Flask, url_for
from flask_bcrypt import Bcrypt
from flask_mail import Mail


from my_flask_blog.config import Config
from my_flask_blog.models import db, login_manager

from flask_admin.contrib.sqla import ModelView
from my_flask_blog.models import User, Post, Comment, Role
from my_flask_blog.admin import MyAdminIndexView, MyModelView

from flask_security import SQLAlchemyUserDatastore, Security
import flask_admin
from flask_admin import helpers

bcrypt = Bcrypt()
mail = Mail()


def reverse_filter(s):
    return s[::-1]


def create_app(config_class=Config):
    app = Flask(__name__)

    app.config.from_object(Config)

    app.config['FLASK_ADMIN_SWATCH'] = 'Darkly'

    app.config['BASIC_AUTH_USERNAME'] = 'admin'
    app.config['BASIC_AUTH_PASSWORD'] = '12345'

    from my_flask_blog.main.routes import main
    app.register_blueprint(main)

    from my_flask_blog.users.routes import users
    app.register_blueprint(users)

    from my_flask_blog.posts.routes import posts
    app.register_blueprint(posts)

    from my_flask_blog.errors.handlers import errors
    app.register_blueprint(errors)

    from my_flask_blog.admin.routes import admin_bp
    app.register_blueprint(admin_bp, url_prefix="/admin")

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)

    login_manager.login_view = 'admin_blueprint.login'
    app.jinja_env.filters['reverse'] = reverse_filter

    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)

    admin = flask_admin.Admin(app, index_view=MyAdminIndexView(), base_template='admin/master-extended.html', template_mode='bootstrap3')
    print('создан админ')

    # Add view
    admin.add_view(MyModelView(User, db.session))
    admin.add_view(MyModelView(Role, db.session))
    admin.add_view(MyModelView(Post, db.session))
    admin.add_view(MyModelView(Comment, db.session))

    @security.context_processor
    def security_context_processor():
        return dict(
            admin_base_template=admin.base_template,
            admin_view=admin.index_view,
            h=helpers,
            get_url=url_for
        )

    return app
