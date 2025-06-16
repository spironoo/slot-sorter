# slot-sorter/slot_sorter/routes.py
from flask import Blueprint, render_template, request, jsonify, current_app
from .logic import calculate_permutations

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

@main_bp.route('/api/records', methods=['POST'])
def handle_post_records():
    """Receives and stores records from the user."""
    records = request.get_json()
    if not isinstance(records, list):
        return jsonify({"error": "Expected an array of records"}), 400

    processed_records = []
    for record in records:
        if not all(k in record for k in ['name', 'slots', 'genre']):
            return jsonify({"error": "A record is missing a required field (name, slots, genre)"}), 400
        
        # Simple validation and cleaning
        processed_records.append({
            'name': str(record['name']).strip(),
            'genre': str(record['genre']).strip(),
            'slots': sorted(list(set(int(s) for s in record['slots'] if 1 <= int(s) <= 9)))
        })
    
    # Ensure all names are unique after processing
    names = [rec['name'] for rec in processed_records]
    if len(names) != len(set(names)):
        return jsonify({"error": "All record names must be unique"}), 400

    # Store the processed records in the app's config
    current_app.config['RECORDS_STORE'] = processed_records
    
    return jsonify({"message": f"{len(processed_records)} records stored successfully"}), 201

@main_bp.route('/api/permutations', methods=['GET'])
def handle_get_permutations():
    """Calculates and returns the permutations based on stored records."""
    records = current_app.config.get('RECORDS_STORE', [])
    try:
        permutations = calculate_permutations(records)
        return jsonify({"permutations": permutations})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        # Catch-all for other unexpected errors
        return jsonify({"error": "An internal error occurred."}), 500