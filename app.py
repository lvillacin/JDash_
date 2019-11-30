from flask import Flask, redirect
from flask import render_template
from flask import request
from flask import session
from bson.json_util import loads, dumps
from flask import make_response
import database as db
import authentication
import logging
import ordermanagement as om


app = Flask(__name__)

app.secret_key = b's@g@d@c0ff33'

logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.INFO)

@app.route('/api/stalls',methods=['GET'])
def api_get_stalls():
    resp = make_response( dumps(db.get_stalls()) )
    resp.mimetype = 'application/json'
    return resp

@app.route('/api/stalls/<stall_name>',methods=['GET'])
def api_get_stall(stall_name):
    resp = make_response(dumps(db.get_stall(stall_name)))
    resp.mimetype = 'application/json'
    return resp


@app.route('/')
def index():
    return render_template('index.html', page="Index")

@app.route('/stalls')
def stalls():
    stall_list = db.get_stalls()
    return render_template('stalls.html', page="Stalls", stall_list=stall_list)

@app.route('/stalldetails')
def stalldetails():
    stall_name = request.args.get('name')
    stall = db.get_stall(stall_name)

    menu = stall["menu"]

    return  render_template('stalldetails.html', stall=stall, menu=menu)

@app.route('/ourstory')
def ourstory():
    return render_template('aboutus.html')

@app.route( '/login' , methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route( '/auth' , methods = ['POST'])
def auth():
    username = request.form.get('username')
    password = request.form.get('password')

    is_successful, user = authentication.login(username, password)

    app.logger.info('%s', is_successful)

    if(is_successful):
        session["user"] = user
        session["cart"] = {}
        return redirect ('/')
    else:
        return redirect ('/login_error')

@app.route('/login_error')
def login_error():
    loginerror = "Incorrect username or password."
    return render_template('/login.html', loginerror = loginerror)

@app.route('/logout')
def logout():
    session.pop("user",None)
    session.pop("cart", None)
    return redirect ('/')

@app.route('/addtotray' , methods = ['GET', 'POST'])
def addtocart():
    qty = request.form.get('qty', '')
    stall_name = request.form.get('stall_name')
    item_name = request.form.get('item_name', '')
    food = db.get_item(stall_name, item_name)

    item=dict()

    item["stall"] = food["stall"]
    item["qty"] = int(qty)
    item["name"] = food["name"]
    item["price"] = food["price"]
    item["subtotal"] = food["price"]*item["qty"]

    if(session.get("cart") is None):
        session["cart"]={}

    cart = session["cart"]
    cart[item_name] = item
    session["cart"] = cart
    return redirect('/tray')

@app.route('/tray')
def tray():
    kusina = []
    bite = []
    kwento = []

    for item in session["cart"].values():
        if item["stall"] == "8-Bite":
            bite.append(item)
        elif item["stall"] == "Kusina":
            kusina.append(item)
        else:
            kwento.append(item)

    return render_template('tray.html', kusina=kusina, bite=bite, kwento=kwento)

@app.route('/update' , methods = ['POST'])
def updatecart():

    request_type = request.form.get('submit')
    name = request.form.get('name')
    price = float((request.form.get('price')))

    cart = session["cart"]

    if request_type == "Update":
        quantity = int(request.form.get('qty_cart'))
        cart[name]["qty"] = quantity
        cart[name]["subtotal"] = quantity * price

    else:
        del cart[name]

    session['cart'] = cart

    return redirect('/tray')

@app.route('/checkout', methods =['POST'])
def checkout():
    request_type = request.form.get('submit')
    total = request.form.get('total')
    location = request.form.get('location')

    if request_type == "Clear Cart":
        session["cart"] = {}
        return redirect('/tray')
    else:
        om.create_order_from_cart(location, total)
        session["cart"] = {}
        return render_template('/ordercomplete.html', location=location, total=total)

@app.route('/account')
def account():
    user = session["user"]
    username = user["username"]
    check_order = om.check_order(username)

    if check_order == True:
        order_list = db.get_orders(username)
        noorder = False
        return render_template('/account.html', user=user, noorder=noorder, order_list=order_list)

    else:
        noorder == True
        return render_template('/account.html', user=user, noorder=noorder)

@app.route('/accountsetting', methods = ['POST'])
def accountsetting():
    action = request.form.get('action')

    if action == "user":
        session.pop("user",None)
        session.pop("cart", None)
        return redirect ('/login')

    else:
        return redirect('/changepass')

@app.route('/changepass')
def changepass():
    return render_template('change_pw.html')

@app.route('/change', methods = ['POST'])
def change():
    oldpw = request.form.get("old")
    new1 = request.form.get("new1")
    new2 = request.form.get("new2")
    usernow1 = session["user"]
    user_user = usernow1["username"]
    user_pw = usernow1["password"]

    if oldpw != user_pw:
        change_error = "Incorrect Password"
        return render_template('/change_pw.html', change_error=change_error)
    elif new1 != new2:
        change_error = "Passwords do not match"
        return render_template('/change_pw.html', change_error=change_error)
    else:
        db.change_db(user_user, new1)
        change_error = "Change Password Success"
        return render_template('/change_pw.html', change_error=change_error)
