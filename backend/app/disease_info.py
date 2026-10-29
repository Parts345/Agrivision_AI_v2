from __future__ import annotations

from typing import TypedDict


class DiseaseDetails(TypedDict):
    label: str
    description: str
    symptoms: list[str]
    causes: list[str]
    prevention: list[str]
    treatment: list[str]
    risk_level: str


CLASS_NAMES = [
    "Bacterialblight",
    "Blast",
    "Brownspot",
    "Healthy",
    "Sheathrot",
    "Tungro",
]

DISPLAY_NAMES = {
    "Bacterialblight": "Bacterial Blight",
    "Blast": "Blast",
    "Brownspot": "Brown Spot",
    "Healthy": "Healthy",
    "Sheathrot": "Sheath Rot",
    "Tungro": "Tungro",
}

DISEASE_DETAILS: dict[str, DiseaseDetails] = {
    "Bacterialblight": {
        "label": "Bacterial Blight",
        "description": "A serious bacterial disease causing water-soaked lesions, yellowing margins, and leaf drying in humid fields.",
        "symptoms": [
            "Yellow to white lesions along leaf margins.",
            "Leaf tip drying that can spread downward.",
            "Milky bacterial ooze may appear on fresh cuts.",
        ],
        "causes": [
            "Xanthomonas oryzae pv. oryzae infection.",
            "Rain splash, flooding, strong winds, and high humidity.",
            "Infected seed, crop residue, or susceptible varieties.",
        ],
        "prevention": [
            "Use certified seed and resistant varieties.",
            "Avoid excessive nitrogen fertilizer.",
            "Improve drainage and remove infected residues.",
        ],
        "treatment": [
            "Remove heavily infected plants where practical.",
            "Use locally recommended copper-based bactericides.",
            "Balance nitrogen with potassium and avoid late nitrogen application.",
        ],
        "risk_level": "High",
    },
    "Blast": {
        "label": "Blast",
        "description": "A destructive fungal disease that attacks leaves, collars, nodes, and panicles, often forming spindle lesions.",
        "symptoms": [
            "Diamond or spindle-shaped gray lesions with brown borders.",
            "Collar and neck infection that can cause panicle failure.",
            "Fast spotting during humid and cloudy weather.",
        ],
        "causes": [
            "Magnaporthe oryzae fungus.",
            "High humidity, long leaf wetness, and dense planting.",
            "Excess nitrogen or drought stress.",
        ],
        "prevention": [
            "Plant resistant varieties suited to your region.",
            "Maintain balanced spacing and avoid a dense canopy.",
            "Use balanced fertilization and steady irrigation.",
        ],
        "treatment": [
            "Apply recommended triazole or strobilurin fungicides early.",
            "Monitor closely around panicle initiation and booting.",
            "Reduce plant stress through consistent water management.",
        ],
        "risk_level": "High",
    },
    "Brownspot": {
        "label": "Brown Spot",
        "description": "A fungal disease linked with nutrient stress, producing oval brown lesions and reducing photosynthetic area.",
        "symptoms": [
            "Small oval brown spots on leaves.",
            "Dark margins with gray or tan centers.",
            "Seedling weakness and grain discoloration in severe cases.",
        ],
        "causes": [
            "Bipolaris oryzae fungus.",
            "Low soil fertility, especially potassium or silicon deficiency.",
            "Drought stress, infected seed, and poor water management.",
        ],
        "prevention": [
            "Use clean seed and seed treatment.",
            "Correct nutrient deficiencies after soil testing.",
            "Maintain irrigation and field sanitation.",
        ],
        "treatment": [
            "Apply a suitable fungicide when disease pressure is high.",
            "Improve nutrition with balanced NPK and micronutrients.",
            "Remove infected residues after harvest.",
        ],
        "risk_level": "Medium",
    },
    "Healthy": {
        "label": "Healthy",
        "description": "The leaf appears healthy, with no major visual disease symptoms detected by the model.",
        "symptoms": [
            "Uniform green leaf color.",
            "No visible lesions, streaks, or necrotic patches.",
            "Normal leaf structure and vigor.",
        ],
        "causes": [
            "Balanced crop health and low visible disease pressure.",
            "Good field hygiene, nutrition, and water management.",
        ],
        "prevention": [
            "Continue routine scouting.",
            "Maintain balanced fertilizer, irrigation, and weed control.",
            "Use clean seed and resistant varieties.",
        ],
        "treatment": [
            "No treatment is required from this image.",
            "Keep monitoring after rain and humidity spikes.",
            "Follow preventive integrated disease management.",
        ],
        "risk_level": "Low",
    },
    "Sheathrot": {
        "label": "Sheath Rot",
        "description": "A fungal disease of the upper leaf sheath that can block panicle emergence and reduce grain quality.",
        "symptoms": [
            "Oblong lesions on the flag leaf sheath.",
            "Panicles remain partially enclosed or emerge poorly.",
            "Whitish fungal growth may appear inside infected sheaths.",
        ],
        "causes": [
            "Sarocladium oryzae fungus.",
            "High humidity, dense canopy, and insect injury.",
            "Excess nitrogen and poor air circulation.",
        ],
        "prevention": [
            "Avoid dense planting and excess nitrogen.",
            "Control insects that wound plant tissue.",
            "Use resistant or tolerant varieties where available.",
        ],
        "treatment": [
            "Apply locally recommended fungicide at booting stage.",
            "Improve field aeration and water management.",
            "Remove infected residues and rotate crops where practical.",
        ],
        "risk_level": "Medium",
    },
    "Tungro": {
        "label": "Tungro",
        "description": "A viral disease spread by green leafhoppers, causing yellow-orange leaves, stunting, and yield loss.",
        "symptoms": [
            "Yellow to orange discoloration from the leaf tip downward.",
            "Stunted plants and reduced tillering.",
            "Delayed flowering and poor panicle development.",
        ],
        "causes": [
            "Rice tungro bacilliform and spherical viruses.",
            "Spread by green leafhopper vectors.",
            "Nearby infected plants and overlapping rice crops.",
        ],
        "prevention": [
            "Use tungro-resistant varieties and synchronized planting.",
            "Remove volunteer rice and infected plants early.",
            "Monitor green leafhopper populations.",
        ],
        "treatment": [
            "There is no direct cure for infected plants.",
            "Rogue infected plants early to reduce spread.",
            "Manage vectors when local thresholds are exceeded.",
        ],
        "risk_level": "High",
    },
}


def get_disease_details(class_name: str) -> DiseaseDetails:
    return DISEASE_DETAILS.get(
        class_name,
        {
            "label": DISPLAY_NAMES.get(class_name, class_name),
            "description": "No local disease details are configured for this class.",
            "symptoms": ["Not available."],
            "causes": ["Not available."],
            "prevention": ["Consult a local agriculture expert for field-specific guidance."],
            "treatment": ["Validate the model result before applying treatments."],
            "risk_level": "Unknown",
        },
    )
