import os
from flask import Flask, render_template, request, jsonify

# This is a workaround for the fact that the tool sandbox does not allow relative imports
# from .layout_engine import LayoutEngine
# from .semantic_analyzer import SemanticAnalyzer
# from .smart_templates import SMART_TEMPLATES_MVP
# Instead, we will add the src directory to the path and import directly
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Now import the modules
try:
    import layout_engine
    # Test if LayoutEngine is usable
    # print(f"LayoutEngine found: {layout_engine.LayoutEngine}")
except ImportError as e:
    print(f"Error importing layout_engine: {e}", file=sys.stderr)
    layout_engine = None # Fallback

app = Flask(__name__, template_folder='templates', static_folder='static')

# Initialize LayoutEngine if successfully imported
if layout_engine:
    engine = layout_engine.LayoutEngine()
else:
    engine = None
    print("LayoutEngine could not be initialized. /render endpoint will not work correctly.", file=sys.stderr)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/render', methods=['POST'])
def render_markdown_route():
    if not engine:
        return jsonify({"error": "Layout engine not available."}), 500

    data = request.get_json()
    if not data or 'markdown' not in data:
        return jsonify({"error": "Markdown content is missing."}), 400

    markdown_text = data['markdown']

    try:
        # For now, use automatic template selection by LayoutEngine
        html_output, selected_template_name = engine.generate_layout(markdown_text)
        # print(f"Rendered with template: {selected_template_name}", file=sys.stderr) # For server-side logging
        return jsonify({"html": html_output, "template": selected_template_name})
    except Exception as e:
        print(f"Error during layout generation: {e}", file=sys.stderr) # Log the exception server-side
        return jsonify({"error": f"An error occurred during layout generation: {str(e)}"}), 500

if __name__ == '__main__':
    # Check if engine is initialized before running
    if not engine:
        print("Critical error: LayoutEngine failed to initialize. Flask app will not run.", file=sys.stderr)
    else:
        # Port 5000 is often used by default by Flask, but can be other numbers.
        # For the tool environment, we might not need to specify host/port,
        # but it's good practice for local development.
        # The tool's `run_in_web_server` will handle the actual serving.
        print("Flask app initialized. To run locally: flask --app src/app.py run --debug", file=sys.stderr)
        # app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
        # The above app.run line is for local execution, not for the tool's web server.
        # The tool will run the app in its own way.
        # For now, we just need to make sure the app object is correctly defined.

# To ensure the tool can pick up the app, it's common to have the app object
# available globally, which it is.

# Example of how to run for local testing (outside the tool environment):
# export FLASK_APP=src/app.py
# flask run --debug
# (or python src/app.py directly if app.run is uncommented and configured)
