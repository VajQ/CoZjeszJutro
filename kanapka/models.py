from kanapka import db, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.company_id'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.role_id'), nullable=False)
    def __repr__(self):
        return f"User('{self.id}', '{self.email}', '{self.password}', '{self.role_id}', '{self.company_id}')"

class Category(db.Model):
    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.company_id'), nullable=False)
    dishes = db.relationship('Dish', backref='category', lazy=True)   

    def __repr__(self):
        return f"{self.name}"

class Dish(db.Model):
    dish_id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'), nullable=False)
    name = db.Column(db.String(40), nullable=False)
    description = db.Column(db.String(300), nullable=False)
    prize = db.Column(db.Float(2), nullable=False)
    image_file = db.Column(db.String(20), nullable=False,
                          default='default.jpg')
    company_id = db.Column(db.Integer, db.ForeignKey('company.company_id'), nullable=False)
    positions = db.relationship('Position', backref='dish', lazy=True)
    menu = db.relationship('Menu', backref='dish_m', lazy=True)
    
    def __repr__(self):
        return f"Dish('{self.category}', '{self.name}', '{self.prize}')"

class Menu(db.Model):
    date = db.Column(db.Date, nullable=False, primary_key=True)
    dish_id = db.Column(db.Integer, db.ForeignKey('dish.dish_id'), 
                          primary_key=True)
    

class Order(db.Model):
    order_id = db.Column(db.Integer, primary_key=True)
    date_ordered = db.Column(db.Date, nullable=False)
    client_first_name = db.Column(db.String(20), nullable=False)
    client_second_name = db.Column(db.String(40), nullable=False)
    client_phone_number = db.Column(db.Integer, nullable=False)
    client_district = db.Column(db.String(30), nullable=False)
    client_email = db.Column(db.String(50), nullable=False)
    street_name = db.Column(db.String(50), nullable=False)
    street_number = db.Column(db.String(5), nullable=False)
    home_number = db.Column(db.Integer)
    total_value = db.Column(db.Float(2), nullable=False)
    payment = db.Column(db.String(10), nullable=False)
    time_of_delivery = db.Column(db.Time())
    positions = db.relationship('Position', backref='order', lazy=True)   

    def __repr__(self):
        return f"Order('{self.order_id}', '{self.date_ordered}', '{self.client_phone_number}', '{self.street_name}')"

class Position(db.Model):
    dish_id = db.Column(db.Integer, db.ForeignKey('dish.dish_id'), 
                          primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.order_id'), primary_key=True)
    dish_count = db.Column(db.Integer, nullable=False, default='1')

    def __repr__(self):
        return f"Position('{self.dish_id}', '{self.order_id}', '{self.dish_count}')"

class Role(db.Model):     
    role_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)

class Company(db.Model):
    company_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)


class Group(db.Model):
    group_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.order_id'), primary_key=True)
    