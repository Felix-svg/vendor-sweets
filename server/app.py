#!/usr/bin/env python3

from models import db, Sweet, Vendor, VendorSweet
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

db.init_app(app)

migrate = Migrate(app, db)

api = Api(app)


@app.route("/")
def home():
    return "<h1>Code challenge</h1>"


class Vendors(Resource):
    def get(self):
        vendors = Vendor.query.all()
        vendor_list = []
        for vendor in vendors:
            vendor_dict = {
                "id": vendor.id,
                "name": vendor.name,
            }
            vendor_list.append(vendor_dict)

        response = make_response(vendor_list, 200)
        return response


class VendorByID(Resource):
    def get(self, id):
        vendor = Vendor.query.filter(Vendor.id == id).first()
        if vendor:
            vendor_dict = {
                "id": vendor.id,
                "name": vendor.name,
                "vendor_sweets": [
                    {
                        "id": vendor_sweet.id,
                        "price": vendor_sweet.price,
                        "sweet": {
                            "id": vendor_sweet.sweet.id,
                            "name": vendor_sweet.sweet.name,
                        },
                        "sweet_id": vendor_sweet.sweet_id,
                        "vendor_id": vendor_sweet.vendor_id,
                    }
                    for vendor_sweet in vendor.vendor_sweets
                ],
            }
            response = make_response(vendor_dict, 200)
        else:
            response = make_response({"error": "Vendor not found"}, 404)
        return response


class Sweets(Resource):
    def get(self):
        sweets = Sweet.query.all()
        sweet_list = []
        for sweet in sweets:
            sweet_dict = {
                "id": sweet.id,
                "name": sweet.name,
            }
            sweet_list.append(sweet_dict)

        response = make_response(sweet_list, 200)
        return response


class SweetsByID(Resource):
    def get(self, id):
        sweet = Sweet.query.filter(Sweet.id == id).first()
        if sweet:
            sweet_dict = {
                "id": sweet.id,
                "name": sweet.name,
            }
            response = make_response(sweet_dict, 200)
        else:
            response = make_response({"error": "Sweet not found"}, 404)
        return response


@app.route("/vendor_sweets", methods=["POST"])
def vendor_sweets():
    try:
        # Extract data from request.json
        price = request.json.get("price")
        vendor_id = request.json.get("vendor_id")
        sweet_id = request.json.get("sweet_id")

        new_vendor_sweet = VendorSweet(
            price=price,
            vendor_id=vendor_id,
            sweet_id=sweet_id,
        )

        db.session.add(new_vendor_sweet)
        db.session.commit()

        sweet = Sweet.query.get(sweet_id)
        vendor = Vendor.query.get(vendor_id)

        response_dict = {
            "id": new_vendor_sweet.id,
            "price": new_vendor_sweet.price,
            "sweet": {"id": sweet.id, "name": sweet.name},
            "sweet_id": new_vendor_sweet.sweet_id,
            "vendor": {"id": vendor.id, "name": vendor.name},
            "vendor_id": new_vendor_sweet.vendor_id,
        }

        response = make_response(response_dict, 201)
        return response
    except Exception:
        return {"errors": ["validation errors"]}, 400


@app.route("/vendor_sweets/<int:id>", methods=["DELETE"])
def vendor_sweets_by_id(id):
    vendor_sweet = VendorSweet.query.get(id)
    if vendor_sweet:
        db.session.delete(vendor_sweet)
        db.session.commit()
        response_body = {}
        response = make_response(response_body, 204)
        return response
    else:
        response_body = {"error": "VendorSweet not found"}
        response = make_response(response_body, 404)
        return response


api.add_resource(Vendors, "/vendors")
api.add_resource(VendorByID, "/vendors/<int:id>")
api.add_resource(Sweets, "/sweets")
api.add_resource(SweetsByID, "/sweets/<int:id>")
# api.add_resource(VendorSweets, "/vendor_sweets")


if __name__ == "__main__":
    app.run(port=5555, debug=True)
