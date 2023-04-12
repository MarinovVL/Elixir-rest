from flask import Flask
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_migrate import Migrate
from decouple import config

app = Flask(__name__)
db_user = config('DB_USER')
db_pass = config('DB_PASS')
db_port = config('DB_PORT')
db_name = config('DB_NAME')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_pass}@localhost:{db_port}/{db_name}'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
api = Api(app)


class LandingPage(Resource):
    def get(self):
        return {'message': 'Welcome to the landing page'}


class HomePage(Resource):
    def get(self):
        return {'message': 'Welcome to the homepage'}


api.add_resource(LandingPage, '/')
api.add_resource(HomePage, '/home')


class MedicineDetail(db.Model):
    __tablename__ = 'medicine_detail'
    medicine_id = db.Column(db.Integer, primary_key=True)
    medicine_name_bg = db.Column(db.String(255))
    group = db.Column(db.String(255))
    manufacturer = db.Column(db.String(255))
    sales_measure = db.Column(db.String(255))
    medicine_name = db.Column(db.String(255))
    atc_code = db.Column(db.String(50))
    opiate = db.Column(db.String(255))
    nhif_code = db.Column(db.String(50))

    medicine_barcode = db.relationship('MedicineBarcode', backref='medicine')
    inventory = db.relationship('Inventory', backref='inventory_details')
    purchase = db.relationship('Purchase', backref='purchase_details')
    sale = db.relationship('Sale', backref='sale_details')


class MedicineBarcode(db.Model):
    __tablename__ = 'medicine_barcode'
    barcode_id = db.Column(db.Integer, primary_key=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicine_detail.medicine_id'))
    barcode_1 = db.Column(db.String(255))
    barcode_2 = db.Column(db.String(255))


class Inventory(db.Model):
    __tablename__ = 'inventory'
    inventory_id = db.Column(db.Integer, primary_key=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicine_detail.medicine_id'))
    price = db.Column(db.Float)
    quantity = db.Column(db.Integer)
    expiry_date = db.Column(db.String(20))


class Purchase(db.Model):
    __tablename__ = 'purchase'
    purchase_id = db.Column(db.Integer, primary_key=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicine_detail.medicine_id'))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, server_default=func.now())
    batch_number = db.Column(db.String(255))
    verified = db.Column(db.Boolean)
    reported = db.Column(db.Boolean)
    sespa_reporting = db.Column(db.Boolean)
    supplier_code = db.Column(db.String(255))
    purchase_order = db.Column(db.String(255))


class Sale(db.Model):
    __tablename__ = 'sale'
    sale_id = db.Column(db.Integer, primary_key=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicine_detail.medicine_id'))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, server_default=func.now())
    batch_number = db.Column(db.String(255))
    verified = db.Column(db.Boolean)
    reported = db.Column(db.Boolean)


if __name__ == '__main__':
    app.run(debug=True)
