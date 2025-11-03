#!/usr/bin/env python3
"""
Management script for Cisco Configuration Generator.

Provides CLI commands for database operations, user management,
and other administrative tasks.
"""

import click
import os
import secrets
from flask import Flask
from models import db, User, Configuration, bcrypt
from config import config
from datetime import datetime


def create_app(config_name='development'):
    """Create Flask application."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    bcrypt.init_app(app)

    return app


@click.group()
def cli():
    """Cisco Config Generator Management CLI."""
    pass


@cli.command()
@click.option('--config', default='development', help='Configuration environment')
def init_db(config):
    """Initialize the database."""
    app = create_app(config)

    with app.app_context():
        click.echo('Creating database tables...')
        db.create_all()
        click.echo('✓ Database tables created successfully!')

        # Create default admin user if it doesn't exist
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            click.echo('\nCreating default admin user...')
            admin = User(
                username='admin',
                email='admin@example.com',
                role='admin'
            )
            admin.set_password(os.environ.get('ADMIN_PASSWORD', 'changeme'))
            db.session.add(admin)
            db.session.commit()
            click.echo('✓ Admin user created!')
            click.echo('  Username: admin')
            click.echo(f'  Password: {os.environ.get("ADMIN_PASSWORD", "changeme")}')
            click.echo('  ⚠️  PLEASE CHANGE THE DEFAULT PASSWORD!')


@cli.command()
def drop_db():
    """Drop all database tables."""
    if click.confirm('Are you sure you want to drop all tables? This cannot be undone!'):
        app = create_app()
        with app.app_context():
            click.echo('Dropping all tables...')
            db.drop_all()
            click.echo('✓ All tables dropped!')


@cli.command()
def reset_db():
    """Drop and recreate database tables."""
    if click.confirm('This will delete ALL data. Are you sure?'):
        app = create_app()
        with app.app_context():
            click.echo('Dropping tables...')
            db.drop_all()
            click.echo('Creating tables...')
            db.create_all()
            click.echo('✓ Database reset complete!')


@cli.command()
@click.option('--username', prompt=True, help='Username')
@click.option('--email', prompt=True, help='Email address')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Password')
@click.option('--role', type=click.Choice(['admin', 'engineer', 'viewer']), default='engineer', help='User role')
def create_user(username, email, password, role):
    """Create a new user."""
    app = create_app()

    with app.app_context():
        # Check if user exists
        existing = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing:
            click.echo('❌ User with this username or email already exists!')
            return

        # Create user
        user = User(
            username=username,
            email=email,
            role=role
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        click.echo(f'✓ User {username} created successfully!')
        click.echo(f'  Email: {email}')
        click.echo(f'  Role: {role}')


@cli.command()
@click.option('--username', prompt=True, help='Username')
def delete_user(username):
    """Delete a user."""
    app = create_app()

    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            click.echo(f'❌ User {username} not found!')
            return

        if click.confirm(f'Delete user {username}?'):
            db.session.delete(user)
            db.session.commit()
            click.echo(f'✓ User {username} deleted!')


@cli.command()
def list_users():
    """List all users."""
    app = create_app()

    with app.app_context():
        users = User.query.all()

        if not users:
            click.echo('No users found.')
            return

        click.echo(f'\n{"ID":<5} {"Username":<20} {"Email":<30} {"Role":<10} {"Active":<8} {"Created"}')
        click.echo('-' * 100)

        for user in users:
            created = user.created_at.strftime('%Y-%m-%d') if user.created_at else 'N/A'
            active = '✓' if user.is_active else '✗'
            click.echo(f'{user.id:<5} {user.username:<20} {user.email:<30} {user.role:<10} {active:<8} {created}')


@cli.command()
@click.option('--username', prompt=True, help='Username')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='New password')
def change_password(username, password):
    """Change user password."""
    app = create_app()

    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            click.echo(f'❌ User {username} not found!')
            return

        user.set_password(password)
        db.session.commit()
        click.echo(f'✓ Password changed for user {username}')


@cli.command()
def generate_secret_key():
    """Generate a secure random secret key."""
    key = secrets.token_hex(32)
    click.echo('\nGenerated SECRET_KEY:')
    click.echo(key)
    click.echo('\nAdd this to your .env file:')
    click.echo(f'SECRET_KEY={key}')


@cli.command()
def db_stats():
    """Show database statistics."""
    app = create_app()

    with app.app_context():
        users_count = User.query.count()
        configs_count = Configuration.query.count()
        templates_count = Configuration.query.filter_by(is_template=True).count()

        click.echo('\n=== Database Statistics ===')
        click.echo(f'Users: {users_count}')
        click.echo(f'Configurations: {configs_count}')
        click.echo(f'Templates: {templates_count}')

        # Platform breakdown
        click.echo('\nConfigurations by Platform:')
        for platform in ['ios', 'nxos', 'asa']:
            count = Configuration.query.filter_by(platform=platform).count()
            if count > 0:
                click.echo(f'  {platform.upper()}: {count}')


@cli.command()
def test_db_connection():
    """Test database connection."""
    app = create_app()

    with app.app_context():
        try:
            # Try to query database
            db.session.execute(db.text('SELECT 1'))
            click.echo('✓ Database connection successful!')
        except Exception as e:
            click.echo(f'❌ Database connection failed: {str(e)}')


@cli.command()
@click.option('--output', default='backup.sql', help='Output file')
def backup_db(output):
    """Backup database to SQL file (PostgreSQL only)."""
    db_url = os.environ.get('DATABASE_URL', '')

    if not db_url.startswith('postgresql'):
        click.echo('❌ Backup only supported for PostgreSQL databases')
        return

    # Parse connection string
    # Format: postgresql://user:pass@host:port/dbname
    import re
    match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', db_url)

    if not match:
        click.echo('❌ Could not parse DATABASE_URL')
        return

    user, password, host, port, dbname = match.groups()

    # Run pg_dump
    cmd = f'PGPASSWORD={password} pg_dump -h {host} -p {port} -U {user} {dbname} > {output}'

    click.echo(f'Creating backup: {output}')
    os.system(cmd)
    click.echo('✓ Backup complete!')


@cli.command()
@click.option('--input', prompt=True, help='SQL backup file to restore')
def restore_db(input):
    """Restore database from SQL backup (PostgreSQL only)."""
    if not os.path.exists(input):
        click.echo(f'❌ File not found: {input}')
        return

    if not click.confirm(f'This will replace current database with {input}. Continue?'):
        return

    db_url = os.environ.get('DATABASE_URL', '')

    if not db_url.startswith('postgresql'):
        click.echo('❌ Restore only supported for PostgreSQL databases')
        return

    # Parse connection string
    import re
    match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', db_url)

    if not match:
        click.echo('❌ Could not parse DATABASE_URL')
        return

    user, password, host, port, dbname = match.groups()

    # Run psql
    cmd = f'PGPASSWORD={password} psql -h {host} -p {port} -U {user} {dbname} < {input}'

    click.echo(f'Restoring from backup: {input}')
    os.system(cmd)
    click.echo('✓ Restore complete!')


@cli.command()
def run_tests():
    """Run test suite."""
    click.echo('Running tests...')
    os.system('pytest -v --cov=. --cov-report=term-missing')


@cli.command()
def run_linter():
    """Run code quality checks."""
    click.echo('Running Black formatter check...')
    os.system('black --check .')

    click.echo('\nRunning Flake8...')
    os.system('flake8 .')

    click.echo('\nRunning Pylint...')
    os.system('pylint **/*.py')


if __name__ == '__main__':
    cli()
