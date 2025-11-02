"""
Custom Jinja2 helper functions and filters.

You can register functions here and then add them to the Jinja2
environment in ``utils/config_export.py`` or elsewhere to make
additional functionality available to your templates.  For example,
formatting IP addresses, conditionally including commands, or
calculating derived values.
"""

def format_comment(text: str) -> str:
    """Prefix a string with '! ' for use as a comment in CLI output."""
    return f'! {text}'