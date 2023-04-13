from flask import Flask, request
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy import or_
from flask_migrate import Migrate
from decouple import config
import shortuuid


app = Flask(__name__)
app.secret_key = config('APP.SECRET_KEY')
db_user = config('DB_USER')
db_pass = config('DB_PASS')
db_port = config('DB_PORT')
db_name = config('DB_NAME')
token_to_medicine_id = {}

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


def generate_token_and_store_data(medicine_id, quantity, price, expiry_date, batch_number, supplier_code):
    token = shortuuid.uuid()
    token_to_medicine_id[token] = {
        "medicine_id": medicine_id,
        "quantity": quantity,
        "price": price,
        "expiry_date": expiry_date,
        "batch_number": batch_number,
        "supplier_code": supplier_code
    }
    return token


class PurchaseResource(Resource):
    @staticmethod
    def create_or_update_inventory(medicine_id, price, quantity, expiry_date):
        existing_inventory = Inventory.query.filter_by(medicine_id=medicine_id).first()
        if existing_inventory:
            existing_inventory.quantity += quantity
        else:
            inventory = Inventory(
                medicine_id=medicine_id,
                price=price,
                quantity=quantity,
                expiry_date=expiry_date
            )
            db.session.add(inventory)

    def post(self):
        data = request.get_json()
        medicines = data.get('medicines')
        response = []
        has_errors = False

        for medicine_data in medicines:
            medicine_name = medicine_data.get('medicine_name')

            medicine = MedicineDetail.query.filter(
                or_(
                    MedicineDetail.medicine_name_bg == medicine_name,
                    MedicineDetail.medicine_name == medicine_name
                )
            ).first()

            if not medicine:
                new_medicine = MedicineDetail(medicine_name=medicine_name)
                db.session.add(new_medicine)
                db.session.commit()
                medicine = new_medicine

            medicine_barcode = MedicineBarcode.query.filter_by(medicine_id=medicine.medicine_id).first()

            if not medicine_barcode:
                details = {key: medicine_data.get(key) for key in
                           ["quantity", "price", "expiry_date", "batch_number", "supplier_code"]}
                token = generate_token_and_store_data(medicine.medicine_id, **details)
                response.append({
                    "status": 400,
                    "message": f"Missing barcode for {medicine_name}. Please provide a barcode for it.",
                    "token": token
                })

            else:
                details = {key: medicine_data.get(key) for key in
                           ["quantity", "price", "expiry_date", "batch_number", "supplier_code"]}
                purchase = Purchase(medicine_id=medicine.medicine_id, verified=False, reported=False,
                                    sespa_reporting=False, purchase_order="", **details)
                db.session.add(purchase)
                self.create_or_update_inventory(medicine.medicine_id, details['price'], details['quantity'],
                                                details['expiry_date'])

                response.append({
                    "status": 201,
                    "message": f"Purchase and inventory records created successfully for {medicine_name}."})

        db.session.commit()
        return response


class BarcodeResource(Resource):
    def post(self):
        data = request.get_json()
        token = data.get('token')
        barcode = data.get('barcode')

        if not token or not barcode:
            return {"message": "Both token and barcode must be provided."}, 400

        medicine_data = token_to_medicine_id.get(token)
        if not medicine_data:
            return {"message": "Invalid token."}, 400

        medicine = MedicineDetail.query.get(medicine_data["medicine_id"])

        if not medicine:
            return {"message": "Medicine not found"}, 400

        existing_barcode = MedicineBarcode.query.filter_by(medicine_id=medicine.medicine_id).first()
        if existing_barcode:
            return {"message": "Barcode already exists for this medicine."}, 400

        new_barcode = MedicineBarcode(medicine_id=medicine.medicine_id, barcode_1=barcode)
        db.session.add(new_barcode)

        if all(key in medicine_data for key in
                ["quantity", "price", "expiry_date", "batch_number", "supplier_code"]):
            purchase = Purchase(
                medicine_id=medicine_data["medicine_id"],
                quantity=medicine_data["quantity"],
                price=medicine_data["price"],
                expiry_date=medicine_data["expiry_date"],
                batch_number=medicine_data["batch_number"],
                verified=False,
                reported=False,
                sespa_reporting=False,
                supplier_code=medicine_data["supplier_code"],
                purchase_order=""
            )

            PurchaseResource.create_or_update_inventory(medicine.medicine_id, medicine_data['price'], medicine_data['quantity'], medicine_data['expiry_date'])

            db.session.add(purchase)
        db.session.commit()
        return {"message": "Barcode added successfully"}, 201


api.add_resource(PurchaseResource, '/purchase')
api.add_resource(BarcodeResource, '/add_barcode')
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
    expiry_date = db.Column(db.String(20))
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
