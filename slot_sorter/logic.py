# slot-sorter/slot_sorter/logic.py

def calculate_permutations(records):
    """
    Calculates all valid permutations for a given set of records.
    Raises ValueError if constraints are not met.
    """
    if not records:
        return []

    # Get all unique slots from all records
    all_slots = set()
    for record in records:
        all_slots.update(record['slots'])

    if not all_slots:
        return []

    max_slot = max(all_slots)
    required_slots = list(range(1, max_slot + 1))

    # Verify all required slots are covered by at least one record
    missing_slots = [s for s in required_slots if s not in all_slots]
    if missing_slots:
        raise ValueError(f"Missing coverage for slots: {', '.join(map(str, missing_slots))}")

    # Create a mapping of slots to records that can fill them
    slot_options = {slot: [r for r in records if slot in r['slots']] for slot in required_slots}
    
    # Generate all possible assignments
    assignments = []
    _generate_assignments_recursive({}, 1, max_slot, slot_options, set(), assignments)

    # Format assignments for the final response
    formatted_permutations = []
    for assignment in assignments:
        perm_list = [
            {
                "slot": slot,
                "name": record['name'],
                "genre": record['genre']
            }
            for slot, record in sorted(assignment.items())
        ]
        formatted_permutations.append(perm_list)
            
    return formatted_permutations

def _generate_assignments_recursive(current_assignment, current_slot, max_slot, slot_options, used_names, results):
    """
    Recursively generate valid slot assignments where each record is used at most once.
    This is a helper function for calculate_permutations.
    """
    if current_slot > max_slot:
        results.append(current_assignment.copy())
        return

    # Try each candidate record for the current slot
    for record in slot_options.get(current_slot, []):
        if record['name'] in used_names:
            continue  # Skip if this record is already used in this permutation

        # Assign record to this slot and mark its name as used
        current_assignment[current_slot] = record
        used_names.add(record['name'])

        # Recurse to the next slot
        _generate_assignments_recursive(
            current_assignment, current_slot + 1, max_slot, slot_options, used_names, results
        )

        # Backtrack: un-assign the record and un-mark its name
        del current_assignment[current_slot]
        used_names.remove(record['name'])