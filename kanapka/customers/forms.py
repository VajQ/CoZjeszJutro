from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, \
    IntegerField, SelectField
from wtforms.validators import DataRequired, Email,\
    NumberRange, Optional

class SupplyForm(FlaskForm):
    first_name = StringField('Imię', validators=[DataRequired()])
    second_name = StringField('Nazwisko', validators=[DataRequired()])
    phone_number = IntegerField('Numer telefonu', validators=[DataRequired(), 
                                         NumberRange(min=10000000, max=999999999)])
    email = StringField('Adres email',
                validators=[DataRequired(), Email()])                                    
    street_name = StringField('Nazwa ulicy', validators=[DataRequired()])
    district = SelectField('Dzielnica', choices=[
        ('Bemowo', 'Bemowo'),
        ('Białołęka', 'Białołęka'),
        ('Bielany', 'Bielany'),
        ('Mokotów', 'Mokotów'),
        ('Ochota', 'Ochota'),
        ('Praga-Południe', 'Praga-Południe'),
        ('Praga-Północ', 'Praga-Północ'),
        ('Rembertów', 'Rembertów'),
        ('Śródmieście', 'Śródmieście'),
        ('Targówek', 'Targówek'),
        ('Ursus', 'Ursus'),
        ('Ursynów', 'Ursynów'),
        ('Wawer', 'Wawer'),
        ('Wesoła', 'Wesoła'),
        ('Wilanów', 'Wilanów'),
        ('Włochy', 'Włochy'),
        ('Wola', 'Wola'),
        ('Żoliborz', 'Żoliborz')
    ])
    
    street_number = StringField('Numer domu', validators=[DataRequired()])
    flat_number = IntegerField('Numer mieszkania', validators=[Optional()])    
    payment = SelectField('Forma płatnośći', choices=[
        ('Karta', 'Karta'),
        ('Gotówka', 'Gotówka')
        
    ])
    submit = SubmitField('Zamów')