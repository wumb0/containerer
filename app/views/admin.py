from flask_admin import AdminIndexView, BaseView
from flask_admin.contrib.sqla.view import ModelView
from flask_security import current_user, utils
from wtforms import PasswordField, validators
from flask import redirect, url_for, flash

"""
AdminBaseView: Access control for the admin panel, without this there is none!
Parent: flask.ext.admin.BaseView
"""
class AdminBaseView(BaseView):
    """Who can see the admin page?"""
    def is_accessible(self):
        if current_user.is_authenticated and current_user.is_admin:
            return True
        return False

    """This is run when a user tries to visit an admin page"""
    def _handle_view(self, name, **kwargs):
            # add a check to make sure that the user has permission
            if not self.is_accessible():
                # if not then print an error and redirect
                flash("You don't have permission to go there", category="warning")
                return redirect(url_for('main.index'))


"""
AdminIndexView: Just overwrite AdminIndexView from flask.ext.admin so that
                it requires RBAC...
Parents: flask.ext.admin.AdminIndexView, .AdminBaseView
I probably should call it something else to avoid confusion...
"""
class AdminIndexView(AdminIndexView, AdminBaseView):
    pass


"""
AdminModelView: Add RBAC to flask-admin's model view
Parents: flask.ext.admin.contrib.sqla.view.ModelView, .AdminBaseView
"""
class AdminModelView(ModelView, AdminBaseView):
    pass


"""
UserModelView: The model view for users
Parent: .AdminModelView
"""
class UserModelView(AdminModelView):
    # we don't need to see the huge password hash in the list display
    column_exclude_list = ['password']

    # this information should not be changed, so don't make it editable
    form_excluded_columns = ['last_login_at', 'current_login_at',
                             'last_login_ip', 'current_login_ip',
                             'login_count']

    # make sure the password can't be seen when typing it
    form_overrides = dict(password=PasswordField)

    # add a confirm password field and make sure it equals the other password field
    form_extra_fields = {'password2': PasswordField('Confirm Password',
                                                    [validators.EqualTo('password', message='Passwords must match')])}

    # this just sets the order of the form fields, otherwise confirm pass is on the bottom
    form_columns = ('roles', 'email', 'password', 'password2', 'active')

    # make sure the password is actually encrypted when it is changed or created!
    def on_model_change(self, form, model, is_created):
        if form.password.data:
            model.password = utils.encrypt_password(model.password)


"""
RoleModelView: The model view for roles
Parent: .AdminModelView
"""
class RoleModelView(AdminModelView):
    pass
