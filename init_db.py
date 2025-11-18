#!/usr/bin/env python
"""
Initialize the database with migrations and seed data
"""
import os
import sys
from app_api import create_app
from extensions import db
from models import Organization, User
from flask_migrate import init as migrate_init, migrate as migrate_migrate, upgrade as migrate_upgrade


def init_database():
    """Initialize database with migrations"""
    app = create_app()

    with app.app_context():
        print("🔧 Initializing database...")

        # Check if migrations folder exists
        migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')

        if not os.path.exists(migrations_dir):
            print("📁 Creating migrations folder...")
            migrate_init()

        # Create migration
        print("📝 Creating migration...")
        migrate_migrate(message="Initial migration")

        # Apply migrations
        print("⬆️  Applying migrations...")
        migrate_upgrade()

        print("✅ Database initialized successfully!")

        # Create default organization and admin user
        if not Organization.query.first():
            print("👥 Creating default organization...")
            org = Organization(
                name="Default Organization",
                slug="default",
                is_active=True
            )
            db.session.add(org)
            db.session.flush()

            print("👤 Creating admin user...")
            admin = User(
                email="admin@example.com",
                username="admin",
                first_name="Admin",
                last_name="User",
                is_admin=True,
                is_active=True,
                organization_id=org.id
            )
            admin.set_password("admin123")  # Change this in production!
            db.session.add(admin)

            db.session.commit()
            print("✅ Default organization and admin user created!")
            print("\n📋 Default credentials:")
            print("   Username: admin")
            print("   Password: admin123")
            print("   ⚠️  CHANGE THIS PASSWORD IN PRODUCTION!\n")


if __name__ == '__main__':
    init_database()
