import json
import itertools
from http.server import HTTPServer, BaseHTTPRequestHandler
import webbrowser

class SimpleServer(BaseHTTPRequestHandler):
    records = []  # In-memory storage for records
    
    def set_headers(self, status_code=200, content_type='application/json'):
        self.send_response(status_code)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_OPTIONS(self):
        self.set_headers(200)
    
    def do_GET(self):
        if self.path == '/':
            self.serve_html()
        elif self.path == '/api/permutations':
            self.handle_get_permutations()
        else:
            self.set_headers(404)
            self.wfile.write(b'Not Found')
    
    def do_POST(self):
        if self.path == '/api/records':
            self.handle_post_records()
        else:
            self.set_headers(404)
            self.wfile.write(b'Not Found')
    
    def serve_html(self):
        self.set_headers(200, 'text/html')
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Slot Permutations Generator</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
                .container { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
                .form-container, .results-container { border: 1px solid #ddd; padding: 20px; border-radius: 5px; }
                .record-row { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 15px; padding: 10px; border: 1px solid #eee; }
                input { padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
                button { padding: 8px 15px; color: white; border: none; border-radius: 4px; cursor: pointer; }
                .remove-btn { background-color: #f44336; }
                #add-btn { background-color: #2196F3; margin-bottom: 15px; }
                #submit-btn { background-color: #4CAF50; margin-top: 10px; }
                .permutation-item { padding: 10px; margin-bottom: 15px; border: 1px solid #ddd; border-radius: 5px; background-color: #f9f9f9; }
                .slot-assignment { display: flex; justify-content: space-between; padding: 5px 0; }
                .slot-number { font-weight: bold; min-width: 60px; }
                .assignment-value { flex-grow: 1; }
                .permutation-header { font-weight: bold; margin-bottom: 8px; padding-bottom: 5px; border-bottom: 1px solid #ddd; }
                .field-group { display: flex; flex-direction: column; gap: 5px; }
                .error { border-color: red !important; }
                .note { color: #666; font-size: 0.9em; margin-top: 5px; }
                .results-header { display: flex; justify-content: space-between; margin-bottom: 10px; }
            </style>
        </head>
        <body>
            <h1>Slot Permutations Generator</h1>
            <div class="container">
                <div class="form-container">
                    <h2>Add Records</h2>
                    <div id="records-container">
                        <div class="record-row">
                            <div class="field-group">
                                <label>Name</label>
                                <input type="text" placeholder="Name" class="name">
                            </div>
                            <div class="field-group">
                                <label>Genre</label>
                                <input type="text" placeholder="Genre" class="genre">
                            </div>
                            <div class="field-group">
                                <label>Slots (single digits)</label>
                                <input type="text" placeholder="e.g., 123 for slots 1,2,3" class="slots">
                                <div class="note">Enter digits without spaces (e.g., 135)</div>
                            </div>
                            <div style="align-self: flex-end;">
                                <button class="remove-btn">Remove</button>
                            </div>
                        </div>
                    </div>
                    <button id="add-btn">+ Add Another Record</button>
                    <button id="submit-btn">Generate Permutations</button>
                </div>
                <div class="results-container">
                    <div class="results-header">
                        <h2>Permutations Results</h2>
                        <div id="permutation-count">0 permutations</div>
                    </div>
                    <div id="results"></div>
                </div>
            </div>

            <script>
                // Add new record row
                document.getElementById('add-btn').addEventListener('click', () => {
                    const container = document.getElementById('records-container');
                    const newRow = document.createElement('div');
                    newRow.className = 'record-row';
                    newRow.innerHTML = `
                        <div class="field-group">
                            <label>Name</label>
                            <input type="text" placeholder="Name" class="name">
                        </div>
                        <div class="field-group">
                            <label>Genre</label>
                            <input type="text" placeholder="Genre" class="genre">
                        </div>
                        <div class="field-group">
                            <label>Slots (single digits)</label>
                            <input type="text" placeholder="e.g., 123 for slots 1,2,3" class="slots">
                            <div class="note">Enter digits without spaces (e.g., 135)</div>
                        </div>
                        <div style="align-self: flex-end;">
                            <button class="remove-btn">Remove</button>
                        </div>
                    `;
                    container.appendChild(newRow);
                    
                    // Add event for remove button
                    newRow.querySelector('.remove-btn').addEventListener('click', function() {
                        if (document.querySelectorAll('.record-row').length > 1) {
                            newRow.remove();
                        }
                    });
                });

                // Add events for initial remove buttons
                document.querySelectorAll('.remove-btn').forEach(btn => {
                    btn.addEventListener('click', function() {
                        const row = this.closest('.record-row');
                        if (document.querySelectorAll('.record-row').length > 1) {
                            row.remove();
                        }
                    });
                });

                document.getElementById('submit-btn').addEventListener('click', async () => {
                    const records = [];
                    let isValid = true;
                    const maxSlot = 9;  // Maximum slot based on single-digit requirement
                    
                    document.querySelectorAll('.record-row').forEach(row => {
                        const nameInput = row.querySelector('.name');
                        const genreInput = row.querySelector('.genre');
                        const slotsInput = row.querySelector('.slots');
                        const name = nameInput.value.trim();
                        const genre = genreInput.value.trim();
                        const slotString = slotsInput.value.trim();
                        
                        // Process slots from string
                        const slots = [];
                        if (slotString) {
                            // Extract unique single-digit numbers
                            const digitSet = new Set(slotString.match(/\d/g) || []);
                            for (const digit of digitSet) {
                                const slotNum = parseInt(digit);
                                if (slotNum >= 1 && slotNum <= maxSlot) {
                                    slots.push(slotNum);
                                }
                            }
                        }
                        
                        // Validate fields
                        let hasError = false;
                        if (!name) {
                            nameInput.classList.add('error');
                            hasError = true;
                        } else {
                            nameInput.classList.remove('error');
                        }
                        
                        if (!genre) {
                            genreInput.classList.add('error');
                            hasError = true;
                        } else {
                            genreInput.classList.remove('error');
                        }
                        
                        if (slots.length === 0) {
                            slotsInput.classList.add('error');
                            hasError = true;
                        } else {
                            slotsInput.classList.remove('error');
                        }
                        
                        if (hasError) {
                            isValid = false;
                        } else {
                            records.push({
                                name: name,
                                slots: slots,
                                genre: genre
                            });
                        }
                    });
                    
                    if (!isValid) {
                        alert('Please fill all fields and provide at least one valid slot per record');
                        return;
                    }
                    
                    if (records.length === 0) {
                        alert('No valid records to submit');
                        return;
                    }
                    
                    try {
                        // Submit records
                        const response = await fetch('/api/records', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(records)
                        });
                        
                        if (!response.ok) {
                            const error = await response.json();
                            throw new Error(error.error || 'Failed to submit records');
                        }
                        
                        // Fetch and display permutations
                        const permResponse = await fetch('/api/permutations');
                        if (!permResponse.ok) {
                            const error = await permResponse.json();
                            throw new Error(error.error || 'Failed to get permutations');
                        }
                        
                        const data = await permResponse.json();
                        const permutations = data.permutations;
                        
                        const resultsContainer = document.getElementById('results');
                        resultsContainer.innerHTML = '';
                        document.getElementById('permutation-count').textContent = 
                            `${permutations.length} permutation${permutations.length !== 1 ? 's' : ''} found`;
                        
                        if (permutations.length === 0) {
                            resultsContainer.innerHTML = '<p>No valid permutations available</p>';
                            return;
                        }
                        
                        permutations.forEach((perm, index) => {
                            const permDiv = document.createElement('div');
                            permDiv.className = 'permutation-item';
                            
                            const header = document.createElement('div');
                            header.className = 'permutation-header';
                            header.textContent = `Permutation ${index + 1}`;
                            permDiv.appendChild(header);
                            
                            perm.forEach(assignment => {
                                const slotDiv = document.createElement('div');
                                slotDiv.className = 'slot-assignment';
                                
                                const slotLabel = document.createElement('div');
                                slotLabel.className = 'slot-number';
                                slotLabel.textContent = `Slot ${assignment.slot}:`;
                                
                                const valueDiv = document.createElement('div');
                                valueDiv.className = 'assignment-value';
                                valueDiv.textContent = `${assignment.name}(${assignment.genre})`;
                                
                                slotDiv.appendChild(slotLabel);
                                slotDiv.appendChild(valueDiv);
                                permDiv.appendChild(slotDiv);
                            });
                            
                            resultsContainer.appendChild(permDiv);
                        });
                        
                    } catch (error) {
                        console.error('Error:', error);
                        alert('Error: ' + error.message);
                    }
                });
            </script>
        </body>
        </html>
        """
        self.wfile.write(html_content.encode('utf-8'))
    
    def handle_post_records(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            self.set_headers(400)
            self.wfile.write(json.dumps({"error": "No data provided"}).encode())
            return
        
        try:
            post_data = self.rfile.read(content_length)
            records = json.loads(post_data)
            
            if not isinstance(records, list):
                self.set_headers(400)
                self.wfile.write(json.dumps({"error": "Expected array of records"}).encode())
                return
                
            # Clear existing records and store new ones
            SimpleServer.records = []
            for record in records:
                if 'name' not in record or 'slots' not in record or 'genre' not in record:
                    self.set_headers(400)
                    self.wfile.write(json.dumps({"error": "Missing required field(s) in one or more records"}).encode())
                    return
                    
                if not isinstance(record['slots'], list):
                    self.set_headers(400)
                    self.wfile.write(json.dumps({"error": "Slots must be an array"}).encode())
                    return
                    
                try:
                    # Deduplicate and validate slots
                    deduped_slots = []
                    for slot in record['slots']:
                        slot_int = int(slot)
                        if slot_int < 1 or slot_int > 9:
                            continue  # Skip invalid slots
                        if slot_int not in deduped_slots:
                            deduped_slots.append(slot_int)
                except (ValueError, TypeError):
                    self.set_headers(400)
                    self.wfile.write(json.dumps({"error": "Slots must contain integers between 1-9"}).encode())
                    return
                
                if not deduped_slots:
                    continue  # Skip records with no valid slots
                    
                SimpleServer.records.append({
                    'name': record['name'],
                    'slots': deduped_slots,
                    'genre': record['genre']
                })
            
            if not SimpleServer.records:
                self.set_headers(400)
                self.wfile.write(json.dumps({"error": "No valid records provided"}).encode())
                return
            
            # Ensure all names are unique
            names = [record['name'] for record in SimpleServer.records]
            if len(names) != len(set(names)):
                self.set_headers(400)
                self.wfile.write(json.dumps({"error": "All names must be unique"}).encode())
                return
            
            self.set_headers(201)
            self.wfile.write(json.dumps({"message": f"{len(SimpleServer.records)} records stored successfully"}).encode())
        
        except Exception as e:
            self.set_headers(500)
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def handle_get_permutations(self):
        try:
            if not SimpleServer.records:
                self.set_headers(200)
                self.wfile.write(json.dumps({"permutations": []}).encode())
                return
                
            # Get all slots from all records
            all_slots = set()
            for record in SimpleServer.records:
                all_slots.update(record['slots'])
            
            if not all_slots:
                self.set_headers(200)
                self.wfile.write(json.dumps({"permutations": []}).encode())
                return
                
            max_slot = max(all_slots)
            required_slots = list(range(1, max_slot + 1))
            
            # Verify all required slots are covered
            missing_slots = [s for s in required_slots if s not in all_slots]
            if missing_slots:
                self.set_headers(400)
                self.wfile.write(json.dumps({
                    "error": f"Missing coverage for slots: {missing_slots}"
                }).encode())
                return
            
            # Create a mapping of slots to records that can fill them
            slot_options = {}
            for slot in required_slots:
                slot_options[slot] = [r for r in SimpleServer.records if slot in r['slots']]
            
            # Generate all possible assignments where each record is used at most once
            assignments = []
            self.generate_assignments({}, 1, max_slot, slot_options, set(), assignments)
            
            # Format assignments for response
            formatted_permutations = []
            for assignment in assignments:
                # Create a list of slot assignments
                perm_list = []
                for slot in range(1, max_slot + 1):
                    if slot in assignment:
                        record = assignment[slot]
                        perm_list.append({
                            "slot": slot,
                            "name": record['name'],
                            "genre": record['genre']
                        })
                formatted_permutations.append(perm_list)
            
            self.set_headers(200)
            self.wfile.write(json.dumps({"permutations": formatted_permutations}).encode())
        
        except Exception as e:
            self.set_headers(500)
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def generate_assignments(self, current_assignment, current_slot, max_slot, slot_options, used_names, results):
        """Recursively generate valid slot assignments with no duplicate records"""
        if current_slot > max_slot:
            results.append(current_assignment.copy())
            return
            
        # Try each candidate record for this slot
        for record in slot_options[current_slot]:
            if record['name'] in used_names:
                continue  # Skip if record already used
                
            # Assign record to this slot
            current_assignment[current_slot] = record
            used_names.add(record['name'])
            
            # Recurse to next slot
            self.generate_assignments(
                current_assignment,
                current_slot + 1,
                max_slot,
                slot_options,
                used_names,
                results
            )
            
            # Backtrack: remove assignment
            del current_assignment[current_slot]
            used_names.remove(record['name'])

def run_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, SimpleServer)
    print("Server running on http://localhost:8000")
    httpd.serve_forever()

if __name__ == '__main__':
    webbrowser.open('http://localhost:8000')
    run_server()
