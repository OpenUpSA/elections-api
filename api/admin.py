from api import app
from flask.ext.admin import Admin, AdminIndexView, expose, helpers
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.model.template import macro
from wtforms.fields import SelectField, TextAreaField
from wtforms import form, fields, validators
from flask import request, url_for, redirect, flash
from flask.ext import login
import jinja2
from api import db
from models import User, VotingDistrict, Ward, Municipality, Province
import json

environment = app.jinja_env
environment.filters['parse_json'] = json.loads

# Define login and registration forms (for flask-login)
class LoginForm(form.Form):
    email = fields.TextField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Invalid user')

        if user.password != hash(self.password.data):
            raise validators.ValidationError('Invalid password')

    def get_user(self):
        return db.session.query(User).filter_by(email=self.email.data).first()


class RegistrationForm(form.Form):
    email = fields.TextField(validators=[validators.required(), validators.email()])
    password = fields.PasswordField(
        validators=[
            validators.required(),
            validators.length(min=6, message="Your password needs to have at least six characters.")
        ]
    )

    def validate_login(self, field):
        if db.session.query(User).filter_by(email=self.email.data).count() > 0:
            raise validators.ValidationError('Duplicate users')


class MyModelView(ModelView):
    can_create = True
    can_edit = True
    can_delete = True
    page_size = 50

    form_overrides = {
        'results_national': TextAreaField,
        'results_provincial': TextAreaField
    }
    form_widget_args = {
        'results_national': {
            'rows': 15,
            'class': "input-xxlarge"
        },
        'results_provincial': {
            'rows': 15,
            'class': "input-xxlarge"
        },
    }
    list_template = 'admin/custom_list_template.html'
    column_formatters = {
        'results_national': macro('render_results'),
        'results_provincial': macro('render_results')
    }

    def is_accessible(self):
        return login.current_user.is_authenticated()


# Customized index view that handles login & registration
class HomeView(AdminIndexView):

    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated():
            return redirect(url_for('.login_view'))
        return self.render('admin/home.html')

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            if user:
                login.login_user(user)
            else:
                flash('Username or Password is invalid' , 'error')
                return redirect(url_for('.login_view'))

        if login.current_user.is_authenticated():
            return redirect(url_for('.index'))
        link = '<p>Don\'t have an account? <a href="' + url_for('.register_view') + '">Click here to register.</a></p>'
        return self.render('admin/home.html', form=form, link=link)

    @expose('/register/', methods=('GET', 'POST'))
    def register_view(self):
        form = RegistrationForm(request.form)
        if helpers.validate_form_on_submit(form):
            if form.email.data == app.config['ADMIN_USER']:
                user = User()

                # hash password, before populating User object
                form.password.data = hash(form.password.data)
                form.populate_obj(user)

                db.session.add(user)
                db.session.commit()

                login.login_user(user)
                if login.current_user.is_authenticated():
                    return redirect(url_for('.index'))
            else:
                flash('You cannot be registered.', 'info')
                return redirect(url_for('.login_view'))
        link = '<p>Already have an account? <a href="' + url_for('.login_view') + '">Click here to log in.</a></p>'
        return self.render('admin/home.html', form=form, link=link, register=True)

    @expose('/logout/')
    def logout_view(self):
        login.logout_user()
        return redirect(url_for('.index'))


# Initialize flask-login
def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = ".login_view"

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.query(User).get(user_id)

init_login()

admin = Admin(app, name='Elections API', base_template='admin/my_master.html', index_view=HomeView(name='Home'))

admin.add_view(MyModelView(Province, db.session))
admin.add_view(MyModelView(Municipality, db.session))
