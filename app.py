import os

from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'my_secret_key'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:@localhost/ims"
db = SQLAlchemy(app)


class Product(db.Model):
    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(12), nullable=False)


class Location(db.Model):
    location_id = db.Column(db.Integer, primary_key=True)
    location_name = db.Column(db.String(12), nullable=False)


class Movements(db.Model):
    movement_id = db.Column(db.Integer, primary_key=True)
    from_location = db.Column(db.String(12), nullable=True)
    to_location = db.Column(db.String(12), nullable=True)
    product = db.Column(db.String(12), nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.String(20), nullable=False, default=datetime.now())


@app.route('/product', methods=['GET', 'POST'])
def product():
    if request.method == 'POST':
        product_name = request.form.get('pname')
        entry = Product(product_name=product_name)
        try:
            db.session.add(entry)
            db.session.commit()
            return redirect('/product')
        except:
            return "Database error"
    products = Product.query.all()

    return render_template('product.html', p=True, products=products)


@app.route('/p_update/<string:id>', methods=['GET', 'POST'])
def p_update(id):
    if request.method == 'POST':
        product_name = request.form.get('pname')
        products = Product.query.filter_by(product_id=id).first()
        products.product_name = product_name
        try:
            db.session.commit()
            return redirect('/p_update/' + id)
        except:
            return "Database error"
    product = Product.query.filter_by(product_id=id).first()
    return render_template('p_update.html', p=True, product=product, id=id)


@app.route('/location', methods=['GET', 'POST'])
def location():
    if request.method == 'POST':
        location_name = request.form.get('lname')
        entry = Location(location_name=location_name)
        try:
            db.session.add(entry)
            db.session.commit()
            return redirect('/location')
        except:
            return "Database error"
    locations = Location.query.all()

    return render_template('location.html', l=True, locations=locations)


@app.route('/l_update/<string:id>', methods=['GET', 'POST'])
def l_update(id):
    if request.method == 'POST':
        location_name = request.form.get('lname')
        locations = Location.query.filter_by(location_id=id).first()
        locations.location_name = location_name
        try:
            db.session.commit()
            return redirect('/l_update/' + id)
        except:
            return "Database error"
    location = Location.query.filter_by(location_id=id).first()
    return render_template('l_update.html', l=True, location=location, id=id)


@app.route('/movement', methods=['GET', 'POST'])
def movement():
    if request.method == 'POST':
        # date = datetime.now()
        from_location = request.form.get('f_location')
        to_location = request.form.get('t_location')
        product = request.form.get('product')
        qty = request.form.get('qty')
        if from_location == "" or int(qty) < get_quantity(from_location, product):
            entry = Movements(from_location=from_location, to_location=to_location, product=product,
                              qty=qty)
        else:
            flash('Not enough quantity is available')
            return redirect('/movement')
        try:
            db.session.add(entry)
            db.session.commit()
        except:
            return "Database error"

        return redirect('/movement')

    movements = Movements.query.all()
    products = Product.query.all()
    locations = Location.query.all()
    return render_template('movement.html', m=True, products=products, locations=locations, movements=movements)


@app.route('/update_movement/<string:id>', methods=['GET', 'POST'])
def update_movement(id):
    if request.method == 'POST':
        date = datetime.now()
        from_location = request.form.get('f_location')
        to_location = request.form.get('t_location')
        product = request.form.get('product')
        qty = request.form.get('qty')
        movements = Movements.query.filter_by(movement_id=id).first()
        movements.date = date
        movements.from_location = from_location
        movements.to_location = to_location
        movements.product = product
        movements.qty = qty
        try:
            db.session.commit()
            flash('Movement Updated Successfully!')
            return redirect('/update_movement/' + id)
        except:
            return "Database error"
    movements = Movements.query.filter_by(movement_id=id).first()
    locations = Location.query.all()
    products = Product.query.all()
    return render_template('update_movement.html', m=True, movements=movements, id=id, locations=locations,
                           products=products)


@app.route('/')
def report():
    locations = Location.query.all()
    products = Product.query.all()
    report = []
    for location in locations:
        for product in products:
            row = {}
            row["location"] = location.location_name
            row["product"] = product.product_name
            row["quantity"] = get_quantity(location.location_name, product.product_name)
            report.append(row)

    return render_template('report.html', r=True, report=report)


def get_quantity(location, product):
    qty = 0
    add_entries = Movements.query.filter_by(to_location=location, product=product).all()
    sub_entries = Movements.query.filter_by(from_location=location, product=product).all()
    for entry in add_entries:
        qty += entry.qty
    for entry in sub_entries:
        qty -= entry.qty

    return qty


app.run(debug=True)
