// slot-sorter/slot_sorter/static/js/main.js
document.addEventListener('DOMContentLoaded', () => {
    const addBtn = document.getElementById('add-btn');
    const submitBtn = document.getElementById('submit-btn');
    const recordsContainer = document.getElementById('records-container');
    const resultsContainer = document.getElementById('results');
    const permCountEl = document.getElementById('permutation-count');

    const createRecordRow = () => {
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
            <button class="remove-btn">Remove</button>
        `;
        recordsContainer.appendChild(newRow);

        newRow.querySelector('.remove-btn').addEventListener('click', () => {
            if (document.querySelectorAll('.record-row').length > 1) {
                newRow.remove();
            } else {
                alert("You must have at least one record.");
            }
        });
    };

    addBtn.addEventListener('click', createRecordRow);

    submitBtn.addEventListener('click', async () => {
        const records = [];
        let isValid = true;
        const maxSlot = 9;

        document.querySelectorAll('.record-row').forEach(row => {
            const nameInput = row.querySelector('.name');
            const genreInput = row.querySelector('.genre');
            const slotsInput = row.querySelector('.slots');
            
            nameInput.classList.remove('error');
            genreInput.classList.remove('error');
            slotsInput.classList.remove('error');

            const name = nameInput.value.trim();
            const genre = genreInput.value.trim();
            const slotString = slotsInput.value.trim();
            const slots = Array.from(new Set(slotString.match(/\d/g) || []))
                               .map(d => parseInt(d))
                               .filter(n => n >= 1 && n <= maxSlot);

            let hasError = false;
            if (!name) { nameInput.classList.add('error'); hasError = true; }
            if (!genre) { genreInput.classList.add('error'); hasError = true; }
            if (slots.length === 0) { slotsInput.classList.add('error'); hasError = true; }
            
            if (hasError) {
                isValid = false;
            } else {
                records.push({ name, genre, slots });
            }
        });

        if (!isValid) {
            alert('Please fill all fields and provide at least one valid slot per record.');
            return;
        }

        if (records.length === 0) {
            alert('No valid records to submit.');
            return;
        }

        try {
            // Step 1: Submit records to the backend
            const postResponse = await fetch('/api/records', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(records)
            });

            if (!postResponse.ok) {
                const errorData = await postResponse.json();
                throw new Error(errorData.error || 'Failed to submit records.');
            }

            // Step 2: Fetch permutations
            const permResponse = await fetch('/api/permutations');
            if (!permResponse.ok) {
                const errorData = await permResponse.json();
                throw new Error(errorData.error || 'Failed to get permutations.');
            }
            
            const data = await permResponse.json();
            displayResults(data.permutations);

        } catch (error) {
            console.error('Error:', error);
            resultsContainer.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
            permCountEl.textContent = '0 permutations';
        }
    });

    const displayResults = (permutations) => {
        resultsContainer.innerHTML = '';
        permCountEl.textContent = `${permutations.length} permutation${permutations.length !== 1 ? 's' : ''} found`;

        if (permutations.length === 0) {
            resultsContainer.innerHTML = '<p>No valid permutations could be generated with the given records.</p>';
            return;
        }

        permutations.forEach((perm, index) => {
            const permDiv = document.createElement('div');
            permDiv.className = 'permutation-item';
            let permHTML = `<div class="permutation-header">Permutation ${index + 1}</div>`;
            
            perm.forEach(assignment => {
                permHTML += `
                    <div class="slot-assignment">
                        <div class="slot-number">Slot ${assignment.slot}:</div>
                        <div class="assignment-value">${assignment.name} (${assignment.genre})</div>
                    </div>`;
            });

            permDiv.innerHTML = permHTML;
            resultsContainer.appendChild(permDiv);
        });
    };

    // Initialize with one record row
    createRecordRow();
});