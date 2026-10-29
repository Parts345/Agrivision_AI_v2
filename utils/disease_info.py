"""Disease metadata for the Streamlit app.

The authoritative definitions live in backend/app/disease_info.py so the
FastAPI API and the Streamlit dashboard always show the same information.
"""

from backend.app.disease_info import (  # noqa: F401
    CLASS_NAMES,
    DISEASE_DETAILS,
    DISPLAY_NAMES,
    DiseaseDetails,
    get_disease_details,
)

__all__ = ["CLASS_NAMES", "DISEASE_DETAILS", "DISPLAY_NAMES", "DiseaseDetails", "get_disease_details"]
