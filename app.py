from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_migrate import Migrate
from flask_restful import Api, Resource
from dotenv import load_dotenv
from datetime import datetime

# Import configurations and models
from config import Config  
from models import db, User, Business, Inventory, Sales, Insights
from auth import auth_bp  

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

api = Api(app)

db.init_app(app)
migrate = Migrate(app, db)

# Register authentication blueprint
app.register_blueprint(auth_bp, url_prefix='/auth')

# Flask-RESTful Resources
class UserResource(Resource):
    def get(self):
        users = User.query.all()
        return jsonify([user.to_dict() for user in users])

    def post(self):
        data = request.get_json()
        new_user = User(username=data['username'], email=data['email'], password=data['password'])
        db.session.add(new_user)
        db.session.commit()
        return jsonify(new_user.to_dict()), 201

class BusinessResource(Resource):
    def get(self, user_id):
        businesses = Business.query.filter_by(user_id=user_id).all()
        return jsonify([business.to_dict() for business in businesses])

    def post(self):
        data = request.get_json()
        new_business = Business(name=data['name'], user_id=data['user_id'], category=data.get('category'))
        db.session.add(new_business)
        db.session.commit()
        return jsonify(new_business.to_dict()), 201

class InventoryResource(Resource):
    def get(self, business_id):
        inventory_items = Inventory.query.filter_by(business_id=business_id).all()
        return jsonify([item.to_dict() for item in inventory_items])

    def post(self):
        data = request.get_json()
        new_inventory = Inventory(
            item_name=data['item_name'], 
            description=data.get('description'),
            quantity=data['quantity'],
            price_per_unit=data['price_per_unit'],
            business_id=data['business_id']
        )
        db.session.add(new_inventory)
        db.session.commit()
        return jsonify(new_inventory.to_dict()), 201

class SalesResource(Resource):
    def post(self):
        data = request.get_json()
        new_sale = Sales(
            business_id=data['business_id'], 
            inventory_id=data['inventory_id'],
            quantity_sold=data['quantity_sold'],
            total_price=data['total_price'],
            sold_at=data.get('sold_at', datetime.utcnow())
        )
        db.session.add(new_sale)
        db.session.commit()
        return jsonify(new_sale.to_dict()), 201

class InsightsResource(Resource):
    def get(self, business_id):
        insights = Insights.query.filter_by(business_id=business_id).all()
        return jsonify([insight.to_dict() for insight in insights])

class RevenueResource(Resource):
    def get(self, business_id):
        total_revenue = db.session.query(func.sum(Sales.total_price)).filter_by(business_id=business_id).scalar() or 0.0
        new_insight = Insights(
            business_id=business_id,
            metric='total_revenue',
            value=total_revenue,
            recorded_at=datetime.utcnow()
        )
        db.session.add(new_insight)
        db.session.commit()
        return jsonify(new_insight.to_dict()), 201

class ProfitResource(Resource):
    def get(self, business_id):
        total_revenue = db.session.query(func.sum(Sales.total_price)).filter_by(business_id=business_id).scalar() or 0.0
        total_cogs = db.session.query(
            func.sum(Sales.quantity_sold * Inventory.price_per_unit)
        ).join(Inventory, Sales.inventory_id == Inventory.id).filter(Sales.business_id == business_id).scalar() or 0.0

        profit = total_revenue - total_cogs
        new_insight = Insights(
            business_id=business_id,
            metric='total_profit',
            value=profit,
            recorded_at=datetime.utcnow()
        )
        db.session.add(new_insight)
        db.session.commit()
        return jsonify(new_insight.to_dict()), 201

class InventoryValueResource(Resource):
    def get(self, business_id):
        total_inventory_value = db.session.query(
            func.sum(Inventory.quantity * Inventory.price_per_unit)
        ).filter_by(business_id=business_id).scalar() or 0.0

        new_insight = Insights(
            business_id=business_id,
            metric='inventory_value',
            value=total_inventory_value,
            recorded_at=datetime.utcnow()
        )
        db.session.add(new_insight)
        db.session.commit()
        return jsonify(new_insight.to_dict()), 201

class ComprehensiveInsightsResource(Resource):
    def get(self, business_id):
        total_revenue = db.session.query(func.sum(Sales.total_price)).filter_by(business_id=business_id).scalar() or 0.0
        total_cogs = db.session.query(
            func.sum(Sales.quantity_sold * Inventory.price_per_unit)
        ).join(Inventory, Sales.inventory_id == Inventory.id).filter(Sales.business_id == business_id).scalar() or 0.0
        total_inventory_value = db.session.query(
            func.sum(Inventory.quantity * Inventory.price_per_unit)
        ).filter_by(business_id=business_id).scalar() or 0.0
        total_transactions = db.session.query(func.count(Sales.id)).filter_by(business_id=business_id).scalar() or 1

        profit = total_revenue - total_cogs
        loss = abs(profit) if profit < 0 else 0.0
        average_sales_price = total_revenue / total_transactions

        insights = [
            {'metric': 'total_revenue', 'value': total_revenue},
            {'metric': 'total_profit', 'value': profit},
            {'metric': 'total_losses', 'value': loss},
            {'metric': 'inventory_value', 'value': total_inventory_value},
            {'metric': 'average_sales_price', 'value': average_sales_price}
        ]
        return jsonify(insights)

# Register API resources
api.add_resource(UserResource, '/users')
api.add_resource(BusinessResource, '/businesses/<int:user_id>', '/business')
api.add_resource(InventoryResource, '/inventory/<int:business_id>', '/inventory')
api.add_resource(SalesResource, '/sales')
api.add_resource(InsightsResource, '/insights/<int:business_id>')
api.add_resource(RevenueResource, '/insights/total_revenue/<int:business_id>')
api.add_resource(ProfitResource, '/insights/total_profit/<int:business_id>')
api.add_resource(InventoryValueResource, '/insights/inventory_value/<int:business_id>')
api.add_resource(ComprehensiveInsightsResource, '/insights/comprehensive/<int:business_id>')

if __name__ == '__main__':
    app.run(debug=True)
