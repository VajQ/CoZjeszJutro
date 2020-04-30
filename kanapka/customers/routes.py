from flask import Blueprint, render_template, url_for, flash, redirect,\
    session
from kanapka import db
from kanapka.customers.forms import SupplyForm
from kanapka.models  import User, Category, Dish, Order, Position,\
    Menu, Company, Group
from datetime import datetime, timedelta
from sendgrid.helpers.mail import Mail
from kanapka.customers.utils import district_switch, send_email

customers = Blueprint('customers', __name__)

opening = datetime.strptime('6:00', '%H:%M').time()
closing = datetime.strptime('23:00', '%H:%M').time()
delivery_cost = 4.0



@customers.route("/")
def home():
    open = False
    now = datetime.now().time()
    
    if opening <= now and now <=closing:
        open = True
        
        #TOMORROW
        category = Category.query.join(Dish, Menu).\
            filter(Menu.date==datetime.now().date()+timedelta(days=1)).\
            all()
        menu = Menu.query.filter_by(date=datetime.now().date()+timedelta(days=1)).all()
        # NOW
       # menu = Menu.query.filter_by(date=datetime.now().date()).all()
       #category = Category.query.join(Dish, Menu).\
       #     filter(Menu.date==datetime.now().date()).\
        #    all()


        companies = Company.query.join(Dish, Menu).\
            filter(Menu.date==datetime.now().date()+timedelta(days=1)).all()

        cart = {}
        total_prize = 0.0

        if 'cart' in session:
            for d in session['cart']:
                for k, v in d.items():
                    cart[k]=v
                    if Dish.query.get(k):
                        total_prize += Dish.query.get(k).prize * v
        total_prize += delivery_cost
        total_prize = round(total_prize, 2)
        
        return render_template('home.html', open=open, menu=menu,\
             category=category, Dish=Dish, cart=cart,\
             companies=companies,\
             total_prize=total_prize,\
             delivery_cost=delivery_cost)
        
    else:
        if 'cart' in session:
            session['cart'].clear()
        return render_template('home.html', open=open)
    

@customers.route("/about")
def about():
    return render_template('about.html', title='Informacje')



@customers.route('/add_to_cart/<int:dish_id>', methods=['GET', 'POST'])
def add_to_cart(dish_id):
    dish = Dish.query.get(dish_id)
    if 'cart' in session:
        # If the product is not in the cart, then add it. 
        if not any(dish.dish_id in d for d in session['cart']):
            session['cart'].append({dish.dish_id: 1})
            

        # If the product is already in the cart, update the quantity
        elif any(dish.dish_id in d for d in session['cart']):
            for d in session['cart']:
                d.update((k, v+1) for k, v in d.items() if k == dish.dish_id)
                
    else:
        # In this block, the user has not started a cart, so we start it for them and add the product. 
        session['cart'] = [{dish.dish_id: 1}]
    return redirect(url_for('customers.home'))


@customers.route('/delete_from_cart/<int:dish_id>', methods=['GET', 'POST'])
def delete_from_cart(dish_id):
    dish = Dish.query.get(dish_id)
    cart = {}
    for d in session['cart']:
            for k, v in d.items():
                cart[k]=v 

    for d in session['cart']:
        for a in list(d):
            if cart[a] == 1 and a == dish.dish_id:
                d.pop(a, None)            
            elif cart[a] > 1:
                d.update((k, v-1) for k, v in d.items() if k == dish.dish_id)


    return redirect(url_for('customers.home'))

@customers.route('/empty_cart', methods=['POST'])
def empty_cart():
    if 'cart' in session:
        session['cart'].clear()
    return redirect(url_for('customers.home'))

@customers.route('/add_order', methods=['GET', 'POST'])
def add_order():
    cart={}
    total_prize=0
    if 'cart' in session:
            for d in session['cart']:
                for k, v in d.items():
                    cart[k]=v
                    total_prize += Dish.query.get(k).prize * v
    total_prize += delivery_cost
    total_prize = round(total_prize, 2)
    companies = Company.query.join(Dish, Menu).\
            filter(Menu.date==datetime.now().date()+timedelta(days=1)).all()
    form=SupplyForm()
    if form.submit.data and form.validate_on_submit():
        datetime_now = datetime.now()
        date_now = datetime_now.date()
        order = Order(date_ordered=date_now,\
            client_first_name=form.first_name.data,\
            client_second_name=form.second_name.data,\
            client_phone_number=form.phone_number.data,\
            client_district=form.district.data,\
            street_name=form.street_name.data,\
            street_number=form.street_number.data,\
            payment=form.payment.data,\
            total_value=total_prize,\
            client_email=form.email.data
            )
        
        if form.flat_number.data:
            order.home_number=form.flat_number.data
        db.session.add(order)
        db.session.commit()
        for k in cart.keys():
            position = Position(dish_id=k, order_id=order.order_id, dish_count=cart[k])
            db.session.add(position)
            db.session.commit()

        #flash('Zlecenie zostało złożone.', 'success')

        return redirect(url_for('customers.group_choice', district=order.client_district, order_id=order.order_id))
    return render_template('add_order.html', title='Złóż zamówienie',\
        form=form, cart=cart, total_prize=total_prize,\
        Dish=Dish, companies=companies, delivery_cost=delivery_cost)






@customers.route('/group_choice/<string:district>/<int:order_id>', methods=['GET', 'POST'])
def group_choice(district, order_id):
    now = datetime.now().time()    
    #if now <= closing:
    #    date_orders = datetime.now().date() - timedelta(days=1)
   # else:
    date_orders = datetime.now().date()  
    print(order_id)
    
    orders = Order.query.filter_by(date_ordered=date_orders).\
            filter_by(client_district=district).all()
    groups = Group.query.outerjoin(Order).filter(Order.date_ordered==date_orders).\
        filter(Order.client_district==district).all()

    group_dict = {}
    for group in groups:
        if group.group_id in group_dict:
            group_dict[group.group_id].append(group.order_id)
        else:
            group_dict[group.group_id] = [group.order_id]

    print(group_dict)

    return render_template('group_choice.html', orders=orders, order_id=order_id, group_dict=group_dict, date=date_orders, Dish=Dish)

@customers.route('/add_group/<int:group_id>/<int:order_id>')
def add_group(group_id, order_id):

    order = Order.query.filter_by(order_id=order_id).first()
    if group_id == 0:
        group = Group(order_id=order_id)
    else:
        group = Group(group_id=group_id, order_id=order_id)        
        order.total_value -= delivery_cost
    if 'cart' in session:
            session['cart'].clear()
    db.session.add(group)
    db.session.commit()
    positions = Position.query.filter_by(order_id=order.order_id).all()
    
    msg = '''Witaj,
Twoje zamówienie z dnia {date} zostało złożone.

Skład zamówienia:

'''.format(date=order.date_ordered)
    value = 0.0
    for position in positions:
        dish = Dish.query.filter_by(dish_id=position.dish_id).first()
        msg = msg + dish.name + " x" + str(position.dish_count) + " " + str(dish.prize * position.dish_count) + "zł \n"    
        value += dish.prize * position.dish_count
        value = round(value, 2)
    if value < order.total_value:
        msg+= 'Dostawa: ' + str(delivery_cost) + " zł\n"

    msg+='''
Dane zamawiającego:

Nazwisko: {second_name}
'''.format(second_name=order.client_second_name)

    if order.home_number:
        msg+='''Adres: {street_name} {street_number}/{home_number}
'''.format(street_name=order.street_name, street_number=order.street_number, home_number=order.home_number)

    else:
        msg+='''Adres: {street_name} {street_number}
'''.format(street_name=order.street_name, street_number=order.street_number)

    msg+='''Całkowita kwota: {total_value} zł
Płatność: {payment}
'''.format(total_value=order.total_value, payment=order.payment)
    print(msg)

    subject = 'Potwierdzenie zamówienia #' + str(order.order_id)




    flash("Zlecenie zostało złożone, na podanego maila zostało wysłane potwierdzenie", "success")
    send_email(order.client_email, subject, msg)
    return redirect(url_for('customers.home'))
