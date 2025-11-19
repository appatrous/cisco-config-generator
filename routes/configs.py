"""
Configuration management routes blueprint.

Handles displaying, downloading, and clearing generated configurations.
"""
from flask import Blueprint, render_template, send_file, redirect, url_for
import os


configs_bp = Blueprint('configs', __name__)


@configs_bp.route('/generated-config/<device>')
def show_generated_config(device: str) -> str:
    """Display all configurations that have been added for the given device."""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

    # Determine filename based on device
    safe_device = device.lower().replace(' ', '_') if device else 'generated_config'
    filename = f"{safe_device}_config.txt"
    file_path = os.path.join(data_dir, filename)

    # Read file if exists
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        content = ''

    return render_template('generated_config.html', content=content, device=device)


@configs_bp.route('/clear-config/<device>', methods=['POST'])
def clear_config(device: str) -> str:
    """Clear (empty) the generated configuration file for the given device."""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    safe_device = device.lower().replace(' ', '_') if device else 'generated_config'
    file_path = os.path.join(data_dir, f"{safe_device}_config.txt")

    # Truncate the file if it exists
    try:
        with open(file_path, 'w', encoding='utf-8'):
            pass
    except Exception:
        # Ignore errors (file may not exist)
        pass

    return redirect(url_for('configs.show_generated_config', device=device))


@configs_bp.route('/download-config/<device>')
def download_config(device: str):
    """Send the generated configuration file for the device as a downloadable attachment."""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    safe_device = device.lower().replace(' ', '_') if device else 'generated_config'
    file_path = os.path.join(data_dir, f"{safe_device}_config.txt")

    # If file does not exist, create an empty one for download
    if not os.path.exists(file_path):
        os.makedirs(data_dir, exist_ok=True)
        open(file_path, 'w', encoding='utf-8').close()

    return send_file(
        file_path,
        as_attachment=True,
        download_name=f"{safe_device}_config.txt",
        mimetype='text/plain'
    )
