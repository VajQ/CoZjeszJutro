from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, \
    DecimalField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length, Email, EqualTo
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from kanapka.models import User, Category, Company
from kanapka import db
from flask_login import current_user


class RegistrationForm(FlaskForm):
    email = StringField('Adres email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Hasło',
                             validators=[DataRequired(), Length(min=8, max=30)])
    confirm_password = PasswordField('Potwierdź hasło',
                                     validators=[DataRequired(),
                                                 EqualTo('password')])
    company_name = StringField('Nazwa firmy', validators=[DataRequired()])
    access_code = StringField('Kod dostępu', validators=[DataRequired()])
    submit = SubmitField('Zarejestruj')
    
    def validate_company_name(self, company_name):
        company_name = User.query.outerjoin(Company).filter(Company.name==company_name.data).first()
        if company_name:
            raise ValidationError('Podana nazwa firmy jest już zajęta. Wybierz inną.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Podany adres email jest już zajęty. Wybierz inny.')
    
    


class LoginForm(FlaskForm):
    email = StringField('Adres email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Hasło',
                             validators=[DataRequired(), 
                                         Length(min=8, max=30)])
    remember = BooleanField('Zapamiętaj mnie')
    submit = SubmitField('Zaloguj')



class DishForm(FlaskForm):
    name = StringField('Nazwa potrawy', validators=[DataRequired()])
    category = SelectField(coerce=int)
    description = TextAreaField('Opis potrawy', validators=[DataRequired()])
    prize = DecimalField('Cena', validators=[DataRequired()])
    picture = FileField('Zdjęcie potrawy', 
                        validators=[FileAllowed(['jpg', 'png'])])
    submit1 = SubmitField('Dodaj potrawę')

    def __init__(self):
        super(DishForm, self).__init__()
        self.category.choices = [(c.category_id, c.name) for c in Category.query.filter_by(company_id=current_user.company_id).all()]

class CategoryForm(FlaskForm):
    name_c = StringField('Nazwa kategorii', validators=[DataRequired()])
    submit2 = SubmitField('Dodaj')

    def validate_name_c(self, name_c):        
        name = Category.query.filter_by(company_id=current_user.company_id).filter_by(name=name_c.data).first()
        if name:            
            raise ValidationError('Podana kategoria już istnieje')
        