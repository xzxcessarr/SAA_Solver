# -- coding: utf-8 --**
from flask import Flask, render_template, request, jsonify
from flask_cors import *
from flask_sqlalchemy import SQLAlchemy
import webbrowser
import json


app = Flask(__name__, static_url_path='',
            static_folder='dist', template_folder='dist')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1641378513@localhost:5423/test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
CORS(app, supports_credentials=True)


class Product(db.Model):
    __tablename__ = 'product'
    name = db.Column(db.String(10), nullable=True, primary_key=True)
    unit = db.Column(db.String(5), nullable=True)
    price = db.Column(db.Float)


class Customer(db.Model):
    __tablename__ = 'customer'
    name = db.Column(db.String(10), nullable=True, primary_key=True)
    tel = db.Column(db.String(20), nullable=True)
    people = db.Column(db.String(10))
    credits = db.Column(db.String(10))


class Supplyer(db.Model):
    __tablename__ = 'supplyer'
    name = db.Column(db.String(10), nullable=True, primary_key=True)
    tel = db.Column(db.String(20), nullable=True)
    people = db.Column(db.String(10))


class Price(db.Model):
    __tablename__ = 'price'
    id = db.Column(db.Integer, nullable=True, primary_key=True)
    product = db.Column(db.String(10), db.ForeignKey(
        'product.name'), nullable=True)
    price = db.Column(db.Float, nullable=True)
    address = db.Column(db.String(10), nullable=True)
    people = db.Column(db.String(10))


class Inventory(db.Model):
    __tablename__ = 'inventory'
    id = db.Column(db.Integer, nullable=True, primary_key=True)
    product = db.Column(db.String(10), db.ForeignKey(
        'product.name'), nullable=True)
    amount = db.Column(db.Integer, nullable=True)
    address = db.Column(db.String(10), nullable=True)
    people = db.Column(db.String(10))
    changetype = db.Column(db.Boolean)


class Purchase(db.Model):
    __tablename__ = 'purchase'
    id = db.Column(db.Integer, nullable=True, primary_key=True)
    supplyer = db.Column(db.String(10), db.ForeignKey(
        'supplyer.name'), nullable=True)
    customer = db.Column(db.String(10), db.ForeignKey(
        'customer.name'), nullable=True)
    sentaddress = db.Column(db.String(10), nullable=True)
    sentdate = db.Column(db.Date, nullable=True)
    sentamount = db.Column(db.Integer, nullable=True)
    receiveamount = db.Column(db.Integer, nullable=True)
    apart = db.Column(db.String(10), nullable=True)
    people = db.Column(db.String(10), nullable=True)
    checkpeople = db.Column(db.String(10))

    def to_json(self):
        return {
            'id': self.id,
            'supplyer': self.supplyer,
            'customer': self.customer,
            'sentaddress': self.sentaddress,
            'sentdate': self.sentdate,
            'sentamount': self.sentamount,
            'receiveamount': self.receiveamount,
            'apart': self.apart,
            'people': self.people,
            'checkpeople': self.checkpeople,
        }


class PurchaseItem(db.Model):
    __tablename__ = 'purchaseitem'
    id = db.Column(db.Integer, nullable=True, primary_key=True)
    purchase = db.Column(db.Integer, db.ForeignKey(
        'purchase.id'), nullable=True)
    product = db.Column(db.String(10), db.ForeignKey(
        'product.name'), nullable=True)
    amount = db.Column(db.Integer, nullable=True)
    cost = db.Column(db.Float)


with app.app_context():
    db.drop_all()
    db.create_all()


@app.route('/', methods=['GET', 'POST'])
def helloPage():
    return render_template('index.html')


@app.route('/purchase', methods=['GET', 'POST'])
def purchaseForm():
    receive = request.args.get('purchaseForm')
    receive = json.loads(receive)
    with app.app_context():
        new = Purchase(supplyer=receive['supplyer'], customer=receive['customer'],
                       sentaddress=receive['sentaddress'], sentdate=receive['sentdate'], sentamount=receive['sentamount'], receiveamount=receive['receiveamount'], apart=receive['apart'], people=receive['people'], checkpeople=receive['checkpeople'])
        db.session.add(new)
        db.session.commit()
    return jsonify({"status": 200, "msg": "服务器已保存该订单"})


@app.route('/product', methods=['GET', 'POST'])
def productForm():
    receive = request.args.get('productForm')
    receive = json.loads(receive)
    with app.app_context():
        new = Product(name=receive['name'],
                      unit=receive['unit'], price=receive['price'])
        db.session.add(new)
        db.session.commit()
    return jsonify({"status": 200, "msg": "服务器已添加该产品"})


@app.route('/customer', methods=['GET', 'POST'])
def customerForm():
    receive = request.args.get('customerForm')
    receive = json.loads(receive)
    with app.app_context():
        new = Customer(name=receive['name'], tel=receive['tel'],
                       people=receive['people'], credits=receive['credit'])
        db.session.add(new)
        db.session.commit()
    return jsonify({"status": 200, "msg": "服务器已添加该顾客"})


@app.route('/supplyer', methods=['GET', 'POST'])
def supplyerForm():
    receive = request.args.get('supplyerForm')
    receive = json.loads(receive)
    with app.app_context():
        new = Supplyer(name=receive['name'],
                       tel=receive['tel'], people=receive['people'])
        db.session.add(new)
        db.session.commit()
    return jsonify({"status": 200, "msg": "服务器已添加该供应商"})


@app.route('/price', methods=['GET', 'POST'])
def priceForm():
    receive = request.args.get('priceForm')
    receive = json.loads(receive)
    with app.app_context():
        new = Price(product=receive['product'], price=receive['price'],
                    address=receive['address'], people=receive['people'])
        db.session.add(new)
        db.session.commit()
    return jsonify({"status": 200, "msg": "服务器已添加该价格记录"})


@app.route('/inventory', methods=['GET', 'POST'])
def inventoryForm():
    receive = request.args.get('inventoryForm')
    receive = json.loads(receive)
    with app.app_context():
        new = Inventory(product=receive['product'], amount=receive['amount'],
                        address=receive['address'], people=receive['people'], changetype=receive['changetype'])
        db.session.add(new)
        db.session.commit()
    return jsonify({"status": 200, "msg": "服务器已添加该库存记录"})


@app.route("/getpurchase", methods=["GET", "POST"])
def table():
    # try:
    res = Purchase.query.all()
    temp = []
    for x in res:
        temp.append(x.to_json())
    print(temp)
    return jsonify({"status": 200, "msg": "获取数据库成功", 'purchaseData': temp})


if __name__ == '__main__':
    webbrowser.open("http://127.0.0.1:5422/")
    app.run(debug=False, port=5422)
