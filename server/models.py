from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


class Sweet(db.Model, SerializerMixin):
    __tablename__ = "sweets"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    # Add relationship
    vendors = db.relationship(
        "Vendor",
        secondary="vendor_sweets",
        back_populates="sweets",
        overlaps="vendor_sweets",
    )
    vendor_sweets = db.relationship(
        "VendorSweet",
        back_populates="sweet",
    )
    # Add serialization
    serialize_rules = "-vendor_sweets.sweet"

    def __repr__(self):
        return f"<Sweet {self.id}>"


class Vendor(db.Model, SerializerMixin):
    __tablename__ = "vendors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    # Add relationship
    sweets = db.relationship(
        "Sweet",
        secondary="vendor_sweets",
        back_populates="vendors",
        overlaps="vendor_sweets",
    )
    vendor_sweets = db.relationship(
        "VendorSweet",
        back_populates="vendor",
    )

    # Add serialization
    serialize_rules = "-vendor_sweets.sweet"

    def __repr__(self):
        return f"<Vendor {self.id}>"


class VendorSweet(db.Model, SerializerMixin):
    __tablename__ = "vendor_sweets"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    sweet_id = db.Column(db.Integer, db.ForeignKey("sweets.id"))
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendors.id"))

    # Add relationships
    sweet = db.relationship(
        "Sweet", back_populates="vendor_sweets", overlaps="sweets,vendors"
    )
    vendor = db.relationship(
        "Vendor", back_populates="vendor_sweets", overlaps="sweets,vendors"
    )

    # Add serialization
    serialize_rules = ("-sweet.vendor_sweets", "-vendor.vendor_sweets")

    # Add validation
    @validates("price")
    def validate_price(self, key, price):
        if price is None or price < 0:
            raise ValueError("Price must have a value and be a non-negative number.")
        return price

    def __repr__(self):
        return f"<VendorSweet {self.id}>"
