from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
from sqlalchemy import MetaData
from werkzeug.security import generate_password_hash, check_password_hash

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata)


# Marshmallow Schemas
class UserSchema(Schema):
    id = fields.Int()
    username = fields.Str()
    email = fields.Str()

class BusinessSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    user_id = fields.Int()

class InventorySchema(Schema):
    id = fields.Int()
    item_name = fields.Str()
    description = fields.Str()
    quantity = fields.Int()
    price_per_unit = fields.Decimal()

class SalesSchema(Schema):
    id = fields.Int()
    quantity_sold = fields.Int()
    total_price = fields.Decimal()

class InsightsSchema(Schema):
    id = fields.Int()
    metric = fields.Str()
    value = fields.Decimal()


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    businesses = db.relationship('Business', back_populates='owner', lazy=True)

    def set_password(self, password):
        """Hash the password before storing it."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the stored hash."""
        return check_password_hash(self.password, password)

class Business(db.Model):
    __tablename__ = 'business'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=True)

    owner = db.relationship('User', back_populates='businesses')
    inventory_items = db.relationship('Inventory', back_populates='business', lazy=True)
    sales_records = db.relationship('Sales', back_populates='business', lazy=True)
    insights = db.relationship('Insights', back_populates='business', lazy=True)  # Add this line


class Inventory(db.Model):
    __tablename__ = 'inventory'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    business_id = db.Column(db.Integer, db.ForeignKey('business.id'), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    quantity = db.Column(db.Integer, nullable=False)
    price_per_unit = db.Column(db.Numeric(10, 2), nullable=False)

    business = db.relationship('Business', back_populates='inventory_items')
    sales_records = db.relationship('Sales', back_populates='inventory_item', lazy=True)

class Sales(db.Model):
    __tablename__ = 'sales'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    business_id = db.Column(db.Integer, db.ForeignKey('business.id'), nullable=False)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=False)
    quantity_sold = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    sold_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    business = db.relationship('Business', back_populates='sales_records')
    inventory_item = db.relationship('Inventory', back_populates='sales_records')

class Insights(db.Model):
    __tablename__ = 'insights'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    business_id = db.Column(db.Integer, db.ForeignKey('business.id'), nullable=False)
    metric = db.Column(db.String(50), nullable=False)
    value = db.Column(db.Numeric(10, 2), nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    business = db.relationship('Business', back_populates='insights')  # This is fine
