"""
Protocol configuration routes blueprint.

Handles protocol-specific configuration pages and form submissions.
"""
from flask import Blueprint, render_template, request, redirect, url_for
from typing import Dict, Any
import os
from services.protocol_service import ProtocolService


protocols_bp = Blueprint('protocols', __name__)


@protocols_bp.route('/protocol/<slug>', methods=['GET', 'POST'])
def protocol_page(slug: str) -> str:
    """
    Render or process a dedicated configuration page for a selected protocol.

    When a user clicks on a protocol card, they are redirected here. On
    GET requests, a form tailored to the given protocol is rendered. On
    POST requests, the submitted data is parsed and a summary of the
    configuration is appended to a persistent file.
    """
    # Determine device context (router, switch, firewall) from query or form
    device = request.args.get('device') or request.form.get('device') or None

    # On POST, process form submission
    if request.method == 'POST':
        # Ensure data directory exists
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        os.makedirs(data_dir, exist_ok=True)

        # Collect form data
        form_data: Dict[str, Any] = request.form.to_dict(flat=False)

        # Generate configuration using service layer
        config_entry = ProtocolService.generate_config(slug, form_data)

        # Determine filename based on device
        safe_device = device.lower().replace(' ', '_') if device else 'generated_config'
        filename = f"{safe_device}_config"
        file_path = os.path.join(data_dir, f"{filename}.txt")

        # Write to file
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(config_entry + "\n")

        # Redirect back to GET view after adding, preserving device param
        return redirect(url_for('protocols.protocol_page', slug=slug, device=device))

    # GET: render template
    template_name = ProtocolService.get_template_name(slug)
    if template_name:
        return render_template(template_name, slug=slug, device=device)

    # Fallback page if protocol not implemented
    return render_template('protocol_coming_soon.html', slug=slug, device=device)
