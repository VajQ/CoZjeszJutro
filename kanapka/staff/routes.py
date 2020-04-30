from flask import Blueprint, render_template, url_for, flash, redirect, request,\
    session, current_app
from kanapka import  db, bcrypt
from kanapka.staff.forms import LoginForm, RegistrationForm, \
    DishForm, CategoryForm
from kanapka.models  import User, Category, Dish, Order, Position,\
    Menu, Company, Role, Group
from flask_login import login_user, current_user, logout_user, \
    login_required
from datetime import datetime, timedelta
from PIL import Image
from sqlalchemy import not_
from sendgrid.helpers.mail import Mail
from kanapka.staff.utils import save_picture
from kanapka.customers.utils import district_switch

staff = Blueprint('staff', __name__)


opening = datetime.strptime('6:00', '%H:%M').time()
closing = datetime.strptime('23:00', '%H:%M').time()



@staff.route("/register_user", methods=['GET', 'POST'])
def register_user():
    if current_user.is_authenticated:
        return redirect(url_for('customers.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.access_code.data == current_app.config.get('ACCESS_CODE'):
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            company = Company(name=form.company_name.data)
            db.session.add(company)
            db.session.commit()
            user = User(email=form.email.data,
                        password=hashed_password,
                        role_id=2,
                        company_id=Company.query.filter_by(name=company.name).first().company_id)
            
            db.session.add(user)
            db.session.commit()
            flash('Twoje konto zostało utworzone, możesz się teraz zalogować!', 'success')
            return redirect(url_for('staff.login'))
        else :
            flash('Zły kod dostępu, spróbuj ponownie', 'danger')
        

    return render_template('register.html', title='Zarejestruj', form=form)


@staff.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('customers.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('customers.home'))
        else:
            flash('Nie udało ci się zalogować, sprawdź ponownie dane i spróbuj ponownie', 'danger')
    return render_template('login.html', title='Login', form=form)

@staff.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('customers.home'))


@staff.route("/new_dish", methods=['GET', 'POST'])
@login_required
def new_dish():

    form = DishForm()
    if form.submit1.data and form.validate_on_submit():
        prize_float = float(form.prize.data)
        
        dish = Dish(category_id=form.category.data,\
            description=form.description.data,\
            name=form.name.data,\
            prize=prize_float,\
            company_id=current_user.company_id)
        print(form.picture.data)
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            dish.image_file=picture_file
            
            
        db.session.add(dish)
        db.session.commit()
        flash('Nowa potrawa została dodana', 'success')
        return redirect(url_for("staff.new_dish"))
    c_form = CategoryForm()
    if c_form.submit2.data and c_form.validate_on_submit():        
        category = Category(name=c_form.name_c.data, company_id=current_user.company_id)
        db.session.add(category)
        db.session.commit()
        flash('Nowa kategoria została dodana', 'success')
        return redirect(url_for("staff.new_dish"))
    

    return render_template('new_dish.html', title='Dodaj nowe danie',\
         form=form, c_form=c_form)


@staff.route('/add_menu')
@login_required
def add_menu():
    datetime_now = datetime.now()
    time_now = datetime_now.time()
    date_now = datetime_now.date()
    if time_now <=opening:
        date = date_now
    else:
        date = date_now + timedelta(days=1)

    menu = Menu.query.outerjoin(Dish).filter(Menu.date==date).\
            filter(Dish.company_id==current_user.company_id).all()
    
    if len(Menu.query.filter_by(date=date).all()) == 0:
        dishes = Dish.query.\
         filter(Dish.company_id==current_user.company_id).all()
        
            
    else:      
        dishes = Dish.query.outerjoin(Menu).\
            filter(not_(Dish.menu.any(Menu.date == date and Menu.dish_id == Dish.dish_id))).\
            filter(Dish.company_id==current_user.company_id).\
            order_by(Dish.category_id).all() 
        print(dishes)
        
   
    
    return render_template('add_menu.html', title='Dodaj do menu',\
        dishes=dishes, menu=menu)

@staff.route('/add_dish/<int:dish_id>', methods=['GET', 'POST'])
@login_required
def add_dish(dish_id):
    datetime_now = datetime.now()
    time_now = datetime_now.time()
    date_now = datetime_now.date()
    
    if time_now <=opening:
        date = date_now
    else:
        date = date_now + timedelta(days=1)
    
    menu_position = Menu(date=date, dish_id=dish_id)
    db.session.add(menu_position)
    db.session.commit()
    flash('Dodano potrawę do menu', 'success')

    return redirect(url_for('staff.add_menu'))

@staff.route('/delete_dish/<int:dish_id>', methods=['GET', 'POST'])
@login_required
def delete_dish(dish_id):
    datetime_now = datetime.now()
    time_now = datetime_now.time()
    date_now = datetime_now.date()
    
    if time_now <=opening:
        date = date_now
    else:
        date = date_now + timedelta(days=1)
    
    menu_position = Menu.query.filter_by(date=date, dish_id=dish_id).first()
    db.session.delete(menu_position)
    db.session.commit()
    flash('Usunięto potrawę z menu', 'danger')

    return redirect(url_for('staff.add_menu'))



@staff.route('/production')
@login_required
def production():
    now = datetime.now().time()
    
    #if now <= closing:
    #    date_orders = datetime.now().date() - timedelta(days=1)
   # else:
    date_orders = datetime.now().date()
    positions = Position.query.join(Order).join(Dish).\
        filter(Order.date_ordered==date_orders).\
        filter(Dish.company_id==current_user.company_id).\
        all()
    for pos in positions:
        print(pos)
    
    all_dishes = {}
    for position in positions:
        if position.dish_id in all_dishes:
            all_dishes[position.dish_id] = all_dishes[position.dish_id] + position.dish_count
        else:
            all_dishes[position.dish_id] = position.dish_count

    categories = Category.query.join(Dish, Menu, Position, Order).\
            filter(Menu.date==datetime.now().date()+timedelta(days=1)).\
            filter(Category.company_id==current_user.company_id).\
            all()
            
    print(all_dishes)     

    return render_template('production.html', all_dishes=all_dishes, date=date_orders, Dish=Dish, categories=categories)



@staff.route('/orders/<int:district>')
@login_required
def orders(district):

    now = datetime.now().time()
    
    #if now <= closing:
    #    date_orders = datetime.now().date() - timedelta(days=1)
   # else:
    date_orders = datetime.now().date()


    if district == 0:
        orders = Order.query.filter_by(date_ordered=date_orders).all()
        groups = Group.query.outerjoin(Order).filter(Order.date_ordered==date_orders)
    else:
        orders = Order.query.filter_by(date_ordered=date_orders).\
            filter_by(client_district=district_switch(district)).all()
        groups = Group.query.outerjoin(Order).filter(Order.date_ordered==date_orders).\
            filter(Order.client_district==district_switch(district)).all()
    positions = Position.query.join(Order).filter_by(date_ordered=date_orders).all()

 


    group_dict = {}
    for group in groups:
        if group.group_id in group_dict:
            group_dict[group.group_id].append(group.order_id)
        else:
            group_dict[group.group_id] = [group.order_id]

    print(group_dict)


   # center = get_coordinates(API_KEY, 'WARSAW')
   # print(center)

    return render_template('orders.html', orders=orders, positions=positions,\
         group_dict=group_dict, date=date_orders, Dish=Dish)