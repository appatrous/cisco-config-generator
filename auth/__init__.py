"""
Authentication and authorization utilities
"""
from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from models import User, Organization
from extensions import db


def admin_required():
    """Decorator to require admin privileges"""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if not claims.get('is_admin'):
                return jsonify({'error': 'Admin privileges required'}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper


def organization_required():
    """Decorator to ensure user belongs to an organization"""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if not claims.get('organization_id'):
                return jsonify({'error': 'Organization membership required'}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper


def get_current_user():
    """Get the current authenticated user"""
    verify_jwt_in_request()
    user_id = get_jwt_identity()
    return User.query.get(user_id)


def get_current_organization():
    """Get the current user's organization"""
    user = get_current_user()
    if user and user.organization_id:
        return Organization.query.get(user.organization_id)
    return None


def filter_by_organization(query, model):
    """Filter query by current user's organization"""
    from config_enhanced import Config

    if not Config.MULTI_TENANT_ENABLED:
        return query

    org = get_current_organization()
    if not org:
        return query.filter(model.organization_id.is_(None))

    return query.filter(model.organization_id == org.id)
