from flask_wtf import FlaskForm
from wtforms import TextField, SubmitField, SelectField, IntegerField, BooleanField
from wtforms.validators import DataRequired, ValidationError, Length
from flask import flash

"""
FlashForm: Adds a flash_errors function that will flash errors on the screen
Parent: flask.ext.wft.Form
"""
class FormFlash(FlaskForm):

    """flash_errors: iterate through form errors and flash them to the screen"""
    def flash_errors(self):
        for field, errors in self.errors.items():
            for error in errors:
                flash("{} - {}".format(field, error), category="error")


"""
ExampleForm: an example form showing different input types and validators
Parent: .FlashForm
"""
class ExampleForm(FormFlash):
    user = SelectField('User', choices=[])
    anumber = IntegerField('A number', validators=[DataRequired()], default="")
    text = TextField('Enter some text!', default="this is the default", validators=[Length(min=3, max=50)])
    checkbox = BooleanField('Checkbox!')
    submit = SubmitField('submit')

    """custom validation example for anumber field
       this validation could be done with the NumberRange validator,
       although this example is important. Validators have to be called
       validate_<attribute_name> and take two args: self and the field
       Validation succeeds unless a ValidationError is raised
    """
    def validate_anumber(self, field):
        if field.data < 0:
            raise ValidationError("Try positive numbers ONLY!")
