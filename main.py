from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, validators
import random
import ast


app = Flask(__name__)
app.config['SECRET_KEY'] = 'hjsbdfo8aso7df987ew4fa87w3e'
Bootstrap(app)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Table Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


# Cafe form
class CafeForm(FlaskForm):
    name = StringField('Cafe name', validators=[validators.input_required()])
    map_url = StringField('Cafe location URL (Google Maps URL)', validators=[validators.url()])
    img_url = StringField('Cafe image URL', validators=[validators.url()])
    location = StringField('Cafe street address', validators=[validators.input_required()])
    seats = StringField('Number of seats range', validators=[validators.input_required()])
    has_toilet = StringField('Has toilets available (True or False)', validators=[validators.input_required()])
    has_wifi = StringField('Has free wifi available (True or False)', validators=[validators.input_required()])
    has_sockets = StringField('Has sockets available (True or False)', validators=[validators.input_required()])
    can_take_calls = StringField('Has cell service (True or False)', validators=[validators.input_required()])
    coffee_price = StringField('Coffee price', validators=[validators.input_required()])
    submit = SubmitField('Submit')


# Used to generate new tables
# with app.app_context():
#     db.create_all()


# Home page
@app.route("/")
def home():
    return render_template("index.html")


@app.route('/cafes', methods=["GET"])
def cafes():
    all_cafes = Cafe.query.all()
    all_cafe_list = []
    for cafe in all_cafes:
        cafe_info = {
            "id": cafe.id,
            "name": cafe.name,
            "map_url": cafe.map_url,
            "img_url": cafe.img_url,
            "location": cafe.location,
            "seats": cafe.seats,
            "has_toilet": cafe.has_toilet,
            "has_wifi": cafe.has_wifi,
            "has_sockets": cafe.has_sockets,
            "can_take_calls": cafe.can_take_calls,
            "coffee_price": cafe.coffee_price,
        }
        all_cafe_list.append(cafe_info)
    return render_template('cafes.html', cafes=all_cafe_list)


# Get a random cafe
@app.route("/random", methods=["GET"])
def get_random_cafe():
    all_cafes = Cafe.query.all()
    random_choice_cafe = random.choice(all_cafes)
    cafe_id = random_choice_cafe.id
    cafe = Cafe.query.get(cafe_id)
    return render_template("random_cafe.html", cafe=cafe)


# Add cafe
@app.route("/add", methods=["GET", "POST"])
def add_cafe():
    form = CafeForm()
    try:
        if form.validate_on_submit():
            new_cafe = Cafe(
                name=request.form.get("name"),
                map_url=request.form.get("map_url"),
                img_url=request.form.get("img_url"),
                location=request.form.get("location"),
                seats=request.form.get("seats"),
                has_toilet=ast.literal_eval(request.form.get("has_toilet")),
                has_wifi=ast.literal_eval(request.form.get("has_wifi")),
                has_sockets=ast.literal_eval(request.form.get("has_sockets")),
                can_take_calls=ast.literal_eval(request.form.get("can_take_calls")),
                coffee_price=request.form.get("coffee_price"),
            )
            db.session.add(new_cafe)
            db.session.commit()
            flash(f"{new_cafe.name} has been successfully added.")
            return redirect(url_for("cafes"))
    except ValueError:
        flash(f"An error has occurred when adding the cafe. Please try again.")
        return redirect(url_for("add_cafe"))
    return render_template("add.html", form=form)


# Update cafe
@app.route("/update-cafe/<cafe_id>", methods=["GET", "POST"])
def update_cafe(cafe_id):
    cafe_info = Cafe.query.get(cafe_id)
    form = CafeForm()
    if form.validate_on_submit():
        cafe_info.name = request.form.get("name")
        cafe_info.map_url = request.form.get("map_url")
        cafe_info.img_url = request.form.get("img_url")
        cafe_info.location = request.form.get("location")
        cafe_info.seats = request.form.get("seats")
        cafe_info.has_toilet = ast.literal_eval(request.form.get("has_toilet"))
        cafe_info.has_wifi = ast.literal_eval(request.form.get("has_wifi"))
        cafe_info.has_sockets = ast.literal_eval(request.form.get("has_sockets"))
        cafe_info.can_take_calls = ast.literal_eval(request.form.get("can_take_calls"))
        cafe_info.coffee_price = request.form.get("coffee_price")
        db.session.commit()
        flash(f"{cafe_info.name} has been successfully updated.")
        return redirect(url_for("update_cafe", cafe_id=cafe_id))
    elif form.errors:
        flash(f"An error has occurred when updating this cafe. Please try again.")
        return redirect(url_for("update_cafe", cafe_id=cafe_id))
    else:
        form.name.data = cafe_info.name
        form.map_url.data = cafe_info.map_url
        form.img_url.data = cafe_info.img_url
        form.location.data = cafe_info.location
        form.seats.data = cafe_info.seats
        form.has_toilet.data = cafe_info.has_toilet
        form.has_wifi.data = cafe_info.has_wifi
        form.has_sockets.data = cafe_info.has_sockets
        form.can_take_calls.data = cafe_info.can_take_calls
        form.coffee_price.data = cafe_info.coffee_price
        return render_template("update.html", form=form, cafe_id=cafe_id)


# Delete cafe
@app.route("/delete/<cafe_id>", methods=["GET", "DELETE"])
def delete_cafe(cafe_id):
    closed_cafe = Cafe.query.get(cafe_id)
    db.session.delete(closed_cafe)
    db.session.commit()
    flash(f"{closed_cafe.name} has successfully been deleted.")
    return redirect(url_for("cafes"))


# Run the application
if __name__ == '__main__':
    app.run(debug=True)
