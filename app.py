from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types
import os
import time
from werkzeug.utils import secure_filename
import logging

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Helper function to get Gemini client
def get_client():
    """Get Gemini client from request header or environment variable"""
    api_key = request.headers.get('X-API-Key') or os.environ.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("API key not provided. Please set your API key in the settings.")
    return genai.Client(api_key=api_key)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/create-store', methods=['POST'])
def create_store():
    """Create a new file search store"""
    try:
        client = get_client()
        data = request.json
        display_name = data.get('display_name', 'my-file-search-store')

        file_search_store = client.file_search_stores.create(
            config={'display_name': display_name}
        )

        return jsonify({
            'success': True,
            'store_name': file_search_store.name,
            'display_name': display_name
        })
    except Exception as e:
        logger.error(f"Error creating store: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/list-stores', methods=['GET'])
def list_stores():
    """List all file search stores"""
    try:
        client = get_client()
        stores = []
        for store in client.file_search_stores.list():
            stores.append({
                'name': store.name,
                'display_name': getattr(store, 'display_name', 'N/A'),
                'create_time': str(getattr(store, 'create_time', 'N/A'))
            })

        return jsonify({'success': True, 'stores': stores})
    except Exception as e:
        logger.error(f"Error listing stores: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/upload-to-store', methods=['POST'])
def upload_to_store():
    """Upload file directly to file search store"""
    try:
        client = get_client()
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400

        file = request.files['file']
        store_name = request.form.get('store_name')
        file_name = request.form.get('file_name', file.filename)

        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400

        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Upload to file search store
        # store_name should be the file search store name (e.g., fileSearchStores/xxx)
        # file_name is the custom display name for the file (used in citations)
        config_dict = {}
        if file_name:
            config_dict['display_name'] = file_name

        operation = client.file_search_stores.upload_to_file_search_store(
            file_search_store_name=store_name,
            file=filepath,
            config=config_dict if config_dict else None
        )

        # Wait for operation to complete (with timeout)
        max_wait = 60  # seconds
        elapsed = 0
        while not operation.done and elapsed < max_wait:
            time.sleep(2)
            operation = client.operations.get(operation)
            elapsed += 2

        # Clean up temporary file
        os.remove(filepath)

        if operation.done:
            return jsonify({
                'success': True,
                'message': 'File uploaded and imported successfully',
                'operation': str(operation)
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Operation timeout',
                'message': 'File upload may still be processing'
            }), 202

    except Exception as e:
        logger.error(f"Error uploading to store: {e}")
        # Clean up temporary file if it exists
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/upload-file', methods=['POST'])
def upload_file():
    """Upload file using Files API"""
    try:
        client = get_client()
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400

        file = request.files['file']
        file_name = request.form.get('file_name', file.filename)

        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400

        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Upload using Files API
        uploaded_file = client.files.upload(
            file=filepath,
            config={'name': file_name}
        )

        # Clean up temporary file
        os.remove(filepath)

        return jsonify({
            'success': True,
            'file_name': uploaded_file.name,
            'display_name': file_name
        })
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/import-file', methods=['POST'])
def import_file():
    """Import an uploaded file into file search store"""
    try:
        client = get_client()
        data = request.json
        store_name = data.get('store_name')
        file_name = data.get('file_name')
        custom_metadata = data.get('custom_metadata', [])

        # Import file
        operation = client.file_search_stores.import_file(
            file_search_store_name=store_name,
            file_name=file_name,
            custom_metadata=custom_metadata
        )

        # Wait for operation to complete
        max_wait = 60
        elapsed = 0
        while not operation.done and elapsed < max_wait:
            time.sleep(2)
            operation = client.operations.get(operation)
            elapsed += 2

        if operation.done:
            return jsonify({
                'success': True,
                'message': 'File imported successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Operation timeout',
                'message': 'File import may still be processing'
            }), 202

    except Exception as e:
        logger.error(f"Error importing file: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/query', methods=['POST'])
def query():
    """Query the file search store"""
    try:
        client = get_client()
        data = request.json
        query_text = data.get('query')
        store_names = data.get('store_names', [])
        metadata_filter = data.get('metadata_filter', None)

        if not query_text:
            return jsonify({'success': False, 'error': 'No query provided'}), 400

        if not store_names:
            return jsonify({'success': False, 'error': 'No store names provided'}), 400

        # Build file search configuration
        file_search_dict = {
            'file_search_store_names': store_names
        }

        if metadata_filter:
            file_search_dict['metadata_filter'] = metadata_filter

        file_search_config = types.FileSearch(**file_search_dict)

        # Generate content with file search
        # Note: Use camelCase 'fileSearch' not snake_case 'file_search'
        tool = types.Tool(fileSearch=file_search_config)
        logger.info(f"Tool created: {tool}")

        config = types.GenerateContentConfig(tools=[tool])
        logger.info(f"Config created: {config}")

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=query_text,
            config=config
        )

        # Extract grounding metadata if available
        grounding_metadata = None
        if response.candidates and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if hasattr(candidate, 'grounding_metadata'):
                grounding_metadata = str(candidate.grounding_metadata)

        return jsonify({
            'success': True,
            'response': response.text,
            'grounding_metadata': grounding_metadata
        })
    except Exception as e:
        logger.error(f"Error querying: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/delete-store', methods=['POST'])
def delete_store():
    """Delete a file search store"""
    try:
        client = get_client()
        data = request.json
        store_name = data.get('store_name')
        force = data.get('force', True)

        client.file_search_stores.delete(
            name=store_name,
            config={'force': force}
        )

        return jsonify({
            'success': True,
            'message': 'Store deleted successfully'
        })
    except Exception as e:
        logger.error(f"Error deleting store: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Gemini File Search Test Server...")
    print("Open http://localhost:3000 in your browser")
    print("Note: API Key can be set in the web interface (Settings tab)")
    app.run(debug=True, host='0.0.0.0', port=3000)
