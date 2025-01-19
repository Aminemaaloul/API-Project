from app import db, create_app
from app.models import Admin

app = create_app()

with app.app_context():
    # Create the database tables (if they don't already exist)
    db.create_all()

    # Add the first admin user
    admin1 = Admin(username="Wadie Tliche")
    admin1.set_password("Wadie123")  # Hash the password
    db.session.add(admin1)

    # Add the second admin user
    admin2 = Admin(username="Sabri Emlak")
    admin2.set_password("Sabri123")  # Hash the password
    db.session.add(admin2)

    # Commit the changes to the database
    db.session.commit()

    print("Two admin users created successfully!")