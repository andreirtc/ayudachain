"""
Known barangays for the fictional demo LGU.
Allocations and beneficiary registrations must reference one of these.
"""

DEMO_BARANGAYS = {
    "BRGY-001": "San Isidro",
    "BRGY-002": "Santa Elena",
    "BRGY-003": "San Roque",
    "BRGY-004": "Maligaya",
}


def barangay_error(barangay_id: str, barangay_name: str):
    """Return an error message if the barangay is unknown or its name does not match, else None."""
    known_name = DEMO_BARANGAYS.get(barangay_id)
    if known_name is None:
        return f"Unknown barangay {barangay_id}. Known barangays: {', '.join(DEMO_BARANGAYS)}."
    if barangay_name.strip() != known_name:
        return f"Barangay {barangay_id} is {known_name}, not {barangay_name}."
    return None
