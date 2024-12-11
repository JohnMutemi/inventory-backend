from app import app, db
from models import User, Business, Inventory, Sales, Insights
from datetime import datetime
from werkzeug.security import generate_password_hash

def seed_data():
    with app.app_context():
        # Clear existing data (optional, for fresh seeding)
        db.drop_all()
        db.create_all()

        # Create sample users with hashed passwords
        user1 = User(username='alice', email='alice@example.com')
        user1.set_password('password123')  # Hash the password
        user2 = User(username='bob', email='bob@example.com')
        user2.set_password('password123')  # Hash the password

        # Add users to session and commit to generate user IDs
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()  # Commit here to assign user IDs

        # Create sample businesses
        business1 = Business(name='Tech Shop', user_id=user1.id, category='Technology')
        business2 = Business(name='Grocery Store', user_id=user2.id, category='Retail')

        db.session.add(business1)
        db.session.add(business2)
        db.session.commit()  # Commit businesses to generate business IDs

        # Create sample inventory and commit them
        inventory1 = Inventory(item_name='Laptop', description='High-end gaming laptop', quantity=50, price_per_unit=1000, business_id=business1.id)
        inventory2 = Inventory(item_name='Smartphone', description='Latest model', quantity=200, price_per_unit=500, business_id=business1.id)
        inventory3 = Inventory(item_name='Apple', description='Fresh apples', quantity=300, price_per_unit=1, business_id=business2.id)
        
        db.session.add(inventory1)
        db.session.add(inventory2)
        db.session.add(inventory3)
        db.session.commit()  # Commit inventories to generate inventory IDs

        # Create sample sales, ensuring inventory_id is correctly assigned
        sale1 = Sales(business_id=business1.id, inventory_id=inventory1.id, quantity_sold=5, total_price=5000, sold_at=datetime.utcnow())
        sale2 = Sales(business_id=business2.id, inventory_id=inventory3.id, quantity_sold=50, total_price=50, sold_at=datetime.utcnow())

        db.session.add(sale1)
        db.session.add(sale2)

        # Commit all sales changes
        db.session.commit()

        # Create Insights for business 1 (Tech Shop)
        total_revenue_1 = db.session.query(db.func.sum(Sales.total_price)).filter_by(business_id=business1.id).scalar()
        total_cost_of_goods_sold_1 = db.session.query(
            db.func.sum(Sales.quantity_sold * Inventory.price_per_unit)
        ).join(Inventory, Sales.inventory_id == Inventory.id).filter(Sales.business_id == business1.id).scalar()
        total_inventory_value_1 = db.session.query(
            db.func.sum(Inventory.quantity * Inventory.price_per_unit)
        ).filter_by(business_id=business1.id).scalar()

        profit_1 = total_revenue_1 - total_cost_of_goods_sold_1
        loss_1 = abs(profit_1) if profit_1 < 0 else 0.0
        average_sales_price_1 = total_revenue_1 / (db.session.query(db.func.count(Sales.id)).filter_by(business_id=business1.id).scalar() or 1)

        # Insert insights into the database for business 1
        db.session.add(Insights(business_id=business1.id, metric='total_revenue', value=total_revenue_1, recorded_at=datetime.utcnow()))
        db.session.add(Insights(business_id=business1.id, metric='total_profit', value=profit_1, recorded_at=datetime.utcnow()))
        db.session.add(Insights(business_id=business1.id, metric='total_losses', value=loss_1, recorded_at=datetime.utcnow()))
        db.session.add(Insights(business_id=business1.id, metric='inventory_value', value=total_inventory_value_1, recorded_at=datetime.utcnow()))
        db.session.add(Insights(business_id=business1.id, metric='average_sales_price', value=average_sales_price_1, recorded_at=datetime.utcnow()))

        # Create Insights for business 2 (Grocery Store)
        total_revenue_2 = db.session.query(db.func.sum(Sales.total_price)).filter_by(business_id=business2.id).scalar()
        total_cost_of_goods_sold_2 = db.session.query(
            db.func.sum(Sales.quantity_sold * Inventory.price_per_unit)
        ).join(Inventory, Sales.inventory_id == Inventory.id).filter(Sales.business_id == business2.id).scalar()
        total_inventory_value_2 = db.session.query(
            db.func.sum(Inventory.quantity * Inventory.price_per_unit)
        ).filter_by(business_id=business2.id).scalar()

        profit_2 = total_revenue_2 - total_cost_of_goods_sold_2
        loss_2 = abs(profit_2) if profit_2 < 0 else 0.0
        average_sales_price_2 = total_revenue_2 / (db.session.query(db.func.count(Sales.id)).filter_by(business_id=business2.id).scalar() or 1)

        # Insert insights into the database for business 2
        db.session.add(Insights(business_id=business2.id, metric='total_revenue', value=total_revenue_2, recorded_at=datetime.utcnow()))
        db.session.add(Insights(business_id=business2.id, metric='total_profit', value=profit_2, recorded_at=datetime.utcnow()))
        db.session.add(Insights(business_id=business2.id, metric='total_losses', value=loss_2, recorded_at=datetime.utcnow()))
        db.session.add(Insights(business_id=business2.id, metric='inventory_value', value=total_inventory_value_2, recorded_at=datetime.utcnow()))
        db.session.add(Insights(business_id=business2.id, metric='average_sales_price', value=average_sales_price_2, recorded_at=datetime.utcnow()))

        # Commit all insights
        db.session.commit()

        print("Sample data seeded successfully!")


# Run the seeding function
if __name__ == "__main__":
    seed_data()
