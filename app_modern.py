"""
Modern Flask Application for Network Configuration Generator
Integrates the new rendering engine with validation and linting
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import json
import yaml
import os
from pathlib import Path
import sys

# Add engine to path
sys.path.insert(0, str(Path(__file__).parent))

from engine.renderer import ConfigRenderer, ConfigLinter, merge_configs
from engine.validator import ConfigValidator

app = Flask(__name__)
CORS(app)  # Enable CORS for API calls
app.config['JSON_SORT_KEYS'] = False

# Initialize engines
renderer = ConfigRenderer()
validator = ConfigValidator()
linter = ConfigLinter()

# Store for configuration history (in-memory, could be database)
config_history = []


@app.route('/')
def index():
    """Serve the modern UI"""
    return render_template('modern_index.html')


@app.route('/api/generate', methods=['POST'])
def generate_config():
    """
    Generate configuration from JSON data

    Request body:
    {
        "vendor": "ios|nxos|eos|junos|frr",
        "config": { ... configuration data ... }
    }

    Response:
    {
        "success": true,
        "config": "..rendered configuration..",
        "validation": {
            "is_valid": true,
            "errors": [],
            "warnings": []
        },
        "linting": {
            "errors": [],
            "warnings": [],
            "line_count": 100
        }
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        vendor = data.get('vendor', 'ios')
        config_data = data.get('config', {})

        # Validate vendor
        if vendor not in renderer.SUPPORTED_VENDORS:
            return jsonify({
                'error': f"Unsupported vendor '{vendor}'. "
                        f"Supported: {', '.join(renderer.SUPPORTED_VENDORS)}"
            }), 400

        # Step 1: Validate configuration
        is_valid, errors, warnings = validator.validate(config_data, vendor)

        validation_result = {
            'is_valid': is_valid,
            'errors': errors,
            'warnings': warnings
        }

        # If critical errors, don't render
        if not is_valid:
            return jsonify({
                'success': False,
                'error': 'Configuration validation failed',
                'validation': validation_result
            }), 400

        # Step 2: Render configuration
        try:
            rendered_config = renderer.render(vendor, config_data)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Rendering error: {str(e)}',
                'validation': validation_result
            }), 500

        # Step 3: Lint the rendered configuration
        linting_result = linter.lint(rendered_config, vendor)

        # Store in history
        config_history.append({
            'vendor': vendor,
            'config': rendered_config,
            'timestamp': __import__('datetime').datetime.now().isoformat()
        })

        return jsonify({
            'success': True,
            'config': rendered_config,
            'validation': validation_result,
            'linting': linting_result,
            'vendor': vendor
        })

    except Exception as e:
        app.logger.error(f"Error in generate_config: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-multi', methods=['POST'])
def generate_multi_vendor():
    """
    Generate configuration for multiple vendors

    Request body:
    {
        "vendors": ["ios", "nxos", "eos"],
        "config": { ... configuration data ... }
    }

    Response:
    {
        "success": true,
        "configs": {
            "ios": "...",
            "nxos": "...",
            "eos": "..."
        }
    }
    """
    try:
        data = request.get_json()
        vendors = data.get('vendors', renderer.SUPPORTED_VENDORS)
        config_data = data.get('config', {})

        # Validate once
        is_valid, errors, warnings = validator.validate(config_data)

        if not is_valid:
            return jsonify({
                'success': False,
                'error': 'Configuration validation failed',
                'validation': {'errors': errors, 'warnings': warnings}
            }), 400

        # Render for multiple vendors
        results = renderer.render_multi_vendor(config_data, vendors)

        return jsonify({
            'success': True,
            'configs': results,
            'validation': {
                'is_valid': is_valid,
                'warnings': warnings
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/validate', methods=['POST'])
def validate_config():
    """
    Validate configuration without rendering

    Request body:
    {
        "config": { ... configuration data ... },
        "vendor": "ios" (optional)
    }
    """
    try:
        data = request.get_json()
        config_data = data.get('config', {})
        vendor = data.get('vendor')

        is_valid, errors, warnings = validator.validate(config_data, vendor)

        return jsonify({
            'is_valid': is_valid,
            'errors': errors,
            'warnings': warnings
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/lint', methods=['POST'])
def lint_config():
    """
    Lint a configuration string

    Request body:
    {
        "config": "..configuration text..",
        "vendor": "ios"
    }
    """
    try:
        data = request.get_json()
        config_text = data.get('config', '')
        vendor = data.get('vendor', 'ios')

        result = linter.lint(config_text, vendor)

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/diff', methods=['POST'])
def diff_configs():
    """
    Generate diff between two configurations

    Request body:
    {
        "config1": "..old config..",
        "config2": "..new config.."
    }
    """
    try:
        import difflib
        data = request.get_json()
        config1 = data.get('config1', '').splitlines()
        config2 = data.get('config2', '').splitlines()

        diff = list(difflib.unified_diff(
            config1, config2,
            fromfile='Current',
            tofile='New',
            lineterm=''
        ))

        return jsonify({
            'diff': '\n'.join(diff),
            'changes': len(diff)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/examples', methods=['GET'])
def list_examples():
    """List available example configurations"""
    examples_dir = Path('examples/profiles')
    if not examples_dir.exists():
        return jsonify({'examples': []})

    examples = []
    for file in examples_dir.glob('*.json'):
        with open(file) as f:
            data = json.load(f)
            examples.append({
                'name': file.stem,
                'description': data.get('description', ''),
                'vendor': data.get('vendor', 'any')
            })

    return jsonify({'examples': examples})


@app.route('/api/examples/<name>', methods=['GET'])
def get_example(name):
    """Get a specific example configuration"""
    example_file = Path(f'examples/profiles/{name}.json')
    if not example_file.exists():
        return jsonify({'error': 'Example not found'}), 404

    with open(example_file) as f:
        data = json.load(f)

    return jsonify(data)


@app.route('/api/merge-profiles', methods=['POST'])
def merge_profiles():
    """
    Merge hierarchical profiles (Global → Site → Role → Device)

    Request body:
    {
        "profiles": [
            { "level": "global", "config": {...} },
            { "level": "site", "config": {...} },
            { "level": "role", "config": {...} },
            { "level": "device", "config": {...} }
        ]
    }
    """
    try:
        data = request.get_json()
        profiles = data.get('profiles', [])

        # Sort by hierarchy level
        level_order = {'global': 0, 'site': 1, 'role': 2, 'device': 3}
        profiles.sort(key=lambda p: level_order.get(p.get('level', 'device'), 99))

        # Merge from bottom to top priority
        merged = {}
        for profile in profiles:
            merged = merge_configs(merged, profile.get('config', {}))

        return jsonify({
            'success': True,
            'merged_config': merged
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/download', methods=['POST'])
def download_config():
    """
    Download rendered configuration as file

    Request body:
    {
        "config": "..configuration..",
        "hostname": "router1",
        "vendor": "ios"
    }
    """
    try:
        data = request.get_json()
        config = data.get('config', '')
        hostname = data.get('hostname', 'config')
        vendor = data.get('vendor', 'ios')

        # Extension mapping
        extensions = {
            'ios': '.cfg',
            'nxos': '.cfg',
            'eos': '.cfg',
            'junos': '.conf',
            'frr': '.conf'
        }
        ext = extensions.get(vendor, '.cfg')

        # Create temporary file
        import tempfile
        fd, path = tempfile.mkstemp(suffix=ext)
        with os.fdopen(fd, 'w') as tmp:
            tmp.write(config)

        return send_file(
            path,
            as_attachment=True,
            download_name=f'{hostname}_{vendor}{ext}',
            mimetype='text/plain'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    """Get configuration generation history"""
    return jsonify({
        'history': config_history[-10:]  # Last 10 entries
    })


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Create necessary directories
    Path('examples/profiles').mkdir(parents=True, exist_ok=True)
    Path('golden/configs').mkdir(parents=True, exist_ok=True)
    Path('engine').mkdir(exist_ok=True)

    # Create __init__.py for engine module
    (Path('engine') / '__init__.py').touch()

    print("\n" + "="*60)
    print("Network Configuration Generator - Modern Edition")
    print("="*60)
    print(f"Supported vendors: {', '.join(renderer.SUPPORTED_VENDORS)}")
    print("Starting server on http://localhost:5000")
    print("="*60 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
