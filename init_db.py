from app import app, db, User

# Create all database tables
with app.app_context():
    db.create_all()

    # Create an admin user if it doesn't already exist
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password='admin', is_admin=True)
        db.session.add(admin)
        db.session.commit()

