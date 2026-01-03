"""
Enhanced Medical Knowledge Base

Comprehensive sample data for Global RAG and Local RAG systems.
Includes medical codes, clinical guidelines, and domain-specific knowledge.
"""

from dataclasses import dataclass
from typing import List, Dict
from mdsa.memory.dual_rag import DualRAG, RAGDocument


# ============================================================================
# Medical Codes Database (Shared across all domains - Global RAG)
# ============================================================================

@dataclass
class MedicalCode:
    """Medical code with metadata."""
    code: str
    code_type: str  # 'ICD-10', 'CPT', 'HCPCS'
    description: str
    category: str
    billable: bool = True
    requires_auth: bool = False
    typical_charge: float = 0.0
    medical_necessity: str = ""


# ICD-10 Diagnosis Codes
ICD10_CODES = [
    MedicalCode(
        code="E11.9",
        code_type="ICD-10-CM",
        description="Type 2 diabetes mellitus without complications",
        category="Endocrine",
        billable=True,
        typical_charge=0.0,
        medical_necessity="Chronic condition requiring ongoing management"
    ),
    MedicalCode(
        code="I10",
        code_type="ICD-10-CM",
        description="Essential (primary) hypertension",
        category="Cardiovascular",
        billable=True,
        medical_necessity="Chronic condition requiring monitoring and medication management"
    ),
    MedicalCode(
        code="J44.0",
        code_type="ICD-10-CM",
        description="Chronic obstructive pulmonary disease with acute lower respiratory infection",
        category="Respiratory",
        billable=True,
        medical_necessity="Acute exacerbation requiring intervention"
    ),
    MedicalCode(
        code="M79.3",
        code_type="ICD-10-CM",
        description="Panniculitis, unspecified",
        category="Musculoskeletal",
        billable=True
    ),
    MedicalCode(
        code="R07.9",
        code_type="ICD-10-CM",
        description="Chest pain, unspecified",
        category="Symptoms",
        billable=True,
        medical_necessity="Workup required to rule out cardiac or pulmonary etiology"
    ),
    MedicalCode(
        code="N18.3",
        code_type="ICD-10-CM",
        description="Chronic kidney disease, stage 3 (moderate)",
        category="Renal",
        billable=True,
        medical_necessity="Requires monitoring of renal function and potential nephrology referral"
    ),
    MedicalCode(
        code="E78.5",
        code_type="ICD-10-CM",
        description="Hyperlipidemia, unspecified",
        category="Endocrine",
        billable=True,
        medical_necessity="Cardiovascular risk reduction"
    ),
    MedicalCode(
        code="F41.1",
        code_type="ICD-10-CM",
        description="Generalized anxiety disorder",
        category="Mental Health",
        billable=True
    ),
    MedicalCode(
        code="K21.9",
        code_type="ICD-10-CM",
        description="Gastro-esophageal reflux disease without esophagitis",
        category="Digestive",
        billable=True
    ),
    MedicalCode(
        code="M54.5",
        code_type="ICD-10-CM",
        description="Low back pain",
        category="Musculoskeletal",
        billable=True
    )
]

# CPT Procedure Codes
CPT_CODES = [
    MedicalCode(
        code="99213",
        code_type="CPT",
        description="Office visit, established patient, 20-29 minutes",
        category="E&M",
        typical_charge=150.00,
        medical_necessity="Medical decision making of low complexity"
    ),
    MedicalCode(
        code="99214",
        code_type="CPT",
        description="Office visit, established patient, 30-39 minutes",
        category="E&M",
        typical_charge=200.00,
        medical_necessity="Medical decision making of moderate complexity"
    ),
    MedicalCode(
        code="80053",
        code_type="CPT",
        description="Comprehensive metabolic panel",
        category="Laboratory",
        typical_charge=35.00,
        medical_necessity="Monitoring chronic conditions (diabetes, renal function)"
    ),
    MedicalCode(
        code="93000",
        code_type="CPT",
        description="Electrocardiogram, routine ECG with interpretation",
        category="Cardiovascular",
        typical_charge=75.00,
        medical_necessity="Evaluation of chest pain, palpitations, or cardiac symptoms"
    ),
    MedicalCode(
        code="71046",
        code_type="CPT",
        description="Chest X-ray, 2 views",
        category="Radiology",
        typical_charge=120.00,
        medical_necessity="Evaluation of respiratory symptoms or chest pain"
    ),
    MedicalCode(
        code="36415",
        code_type="CPT",
        description="Venipuncture for collection of specimen",
        category="Laboratory",
        typical_charge=10.00
    ),
    MedicalCode(
        code="83036",
        code_type="CPT",
        description="Hemoglobin A1c level",
        category="Laboratory",
        typical_charge=30.00,
        medical_necessity="Diabetes monitoring and management"
    ),
    MedicalCode(
        code="85025",
        code_type="CPT",
        description="Complete blood count (CBC) with differential",
        category="Laboratory",
        typical_charge=25.00,
        medical_necessity="Infection workup, anemia evaluation"
    ),
    MedicalCode(
        code="90471",
        code_type="CPT",
        description="Immunization administration, first component",
        category="Preventive",
        typical_charge=25.00
    ),
    MedicalCode(
        code="96372",
        code_type="CPT",
        description="Therapeutic injection, subcutaneous or intramuscular",
        category="Procedures",
        typical_charge=50.00
    )
]

# HCPCS Codes
HCPCS_CODES = [
    MedicalCode(
        code="J3301",
        code_type="HCPCS",
        description="Injection, triamcinolone acetonide, 10 mg",
        category="Drugs",
        typical_charge=35.00,
        requires_auth=False
    ),
    MedicalCode(
        code="G0438",
        code_type="HCPCS",
        description="Annual wellness visit; includes personalized prevention plan",
        category="Preventive",
        typical_charge=175.00
    ),
    MedicalCode(
        code="A4253",
        code_type="HCPCS",
        description="Blood glucose test strips, 50 count",
        category="Supplies",
        typical_charge=45.00,
        requires_auth=False
    )
]


# ============================================================================
# Clinical Guidelines (Global RAG - Shared Knowledge)
# ============================================================================

CLINICAL_GUIDELINES = [
    {
        "title": "Diabetes Management Guidelines",
        "category": "Endocrine",
        "content": """
Key Points for Type 2 Diabetes Management:
- Target HbA1c: <7% for most adults, individualize based on patient factors
- Blood pressure target: <130/80 mmHg
- LDL cholesterol: <100 mg/dL (consider <70 mg/dL for high CV risk)
- Annual monitoring: HbA1c (quarterly if not at goal), lipid panel, urine albumin-to-creatinine ratio, foot exam, dilated eye exam
- First-line medication: Metformin (unless contraindicated)
- Consider SGLT2 inhibitor or GLP-1 agonist for patients with ASCVD or CKD
        """
    },
    {
        "title": "Hypertension Management",
        "category": "Cardiovascular",
        "content": """
ACC/AHA Blood Pressure Guidelines:
- Normal: <120/80 mmHg
- Elevated: 120-129/<80 mmHg
- Stage 1: 130-139/80-89 mmHg
- Stage 2: ≥140/≥90 mmHg

Treatment Recommendations:
- Lifestyle modifications for all patients
- Medication initiation: Stage 1 with 10-year ASCVD risk ≥10%, Stage 2 for all
- First-line medications: Thiazide diuretic, ACE inhibitor, ARB, or calcium channel blocker
- Target: <130/80 mmHg for most adults
        """
    },
    {
        "title": "COPD Exacerbation Management",
        "category": "Respiratory",
        "content": """
COPD Exacerbation Treatment:
- Bronchodilators: Increase short-acting beta-agonists and anticholinergics
- Corticosteroids: Prednisone 40 mg daily for 5 days
- Antibiotics: If purulent sputum or increased sputum volume (Azithromycin, Amoxicillin-clavulanate, or respiratory fluoroquinolone)
- Oxygen: Target SpO2 88-92%
- Consider hospitalization if: Severe symptoms, significant comorbidities, inadequate response to initial treatment
        """
    },
    {
        "title": "Chest Pain Evaluation",
        "category": "Cardiovascular",
        "content": """
Acute Chest Pain Workup:
- Vital signs including oxygen saturation
- ECG within 10 minutes
- Cardiac biomarkers (troponin) at presentation and 3-6 hours
- Risk stratification: HEART score or TIMI score
- Consider stress testing or CT angiography for intermediate risk
- Emergent cardiology consultation for STEMI or high-risk features
        """
    }
]


# ============================================================================
# Domain-Specific Knowledge (Local RAG)
# ============================================================================

# Coding Domain Knowledge
CODING_DOMAIN_KNOWLEDGE = [
    {
        "title": "ICD-10 Coding Best Practices",
        "content": """
Key Coding Principles:
- Code to the highest level of specificity
- Use additional codes to fully describe the condition
- Sequence the principal diagnosis first
- Always check for excludes notes
- Use 'unspecified' only when information is truly unavailable
- Document medical necessity for all procedures
        """
    },
    {
        "title": "CPT Modifiers Quick Reference",
        "content": """
Common CPT Modifiers:
- 25: Significant, separately identifiable E&M service
- 59: Distinct procedural service
- 76: Repeat procedure by same physician
- 77: Repeat procedure by different physician
- GT: Via interactive telecommunications
- TC: Technical component only
- 26: Professional component only
        """
    },
    {
        "title": "Medical Necessity Documentation",
        "content": """
Required Elements:
1. Chief complaint and history of present illness
2. Relevant medical history
3. Physical examination findings
4. Assessment and clinical impression
5. Medical decision making rationale
6. Treatment plan and follow-up

Denial Prevention:
- Use specific diagnoses (avoid 'unspecified')
- Document symptom severity and duration
- Explain why test/procedure is medically necessary
- Link diagnosis to procedure performed
        """
    }
]

# Clinical Diagnosis Domain Knowledge
DIAGNOSIS_DOMAIN_KNOWLEDGE = [
    {
        "title": "Differential Diagnosis Approach",
        "content": """
Systematic Approach:
1. Identify presenting symptoms and chief complaint
2. Consider organ systems involved
3. Generate broad differential (common causes first)
4. Use VINDICATE mnemonic: Vascular, Infectious, Neoplastic, Degenerative, Iatrogenic, Congenital, Autoimmune, Traumatic, Endocrine
5. Narrow differentials based on history and exam
6. Order targeted diagnostic tests
7. Re-evaluate as new data becomes available
        """
    },
    {
        "title": "Red Flags in Common Presentations",
        "content": """
Chest Pain Red Flags:
- Radiating to jaw, left arm, or back
- Associated dyspnea, diaphoresis, nausea
- Worse with exertion
- History of CAD or risk factors

Headache Red Flags (SNOOP4):
- Systemic symptoms (fever, weight loss)
- Neurologic symptoms (vision changes, weakness)
- Onset sudden ("thunderclap")
- Onset after age 50
- Previous headache history changed
- Positional
- Papilledema
- Precipitated by Valsalva
        """
    }
]

# Radiology Domain Knowledge
RADIOLOGY_DOMAIN_KNOWLEDGE = [
    {
        "title": "Common Radiology Procedures and Codes",
        "content": """
Chest Imaging:
- 71046: CXR 2 views
- 71010: CXR single view
- 71020: CXR 2 views with fluoroscopy
- 71250: CT chest without contrast
- 71260: CT chest with contrast

Abdomen Imaging:
- 74000: Abdominal X-ray, single view
- 74150: CT abdomen without contrast
- 74160: CT abdomen with contrast
- 74177: CT abdomen and pelvis with contrast
        """
    },
    {
        "title": "Radiology Report Structure",
        "content": """
Standard Sections:
1. Clinical Indication
2. Technique (type of study, contrast used)
3. Comparison (prior studies)
4. Findings (organized by organ system)
5. Impression (summary and recommendations)

Coding Tips:
- Extract procedure type from technique section
- Identify anatomical areas imaged
- Note use of contrast (affects code selection)
- Check for multiple views or sequences
        """
    }
]


# ============================================================================
# RAG Population Functions
# ============================================================================

def populate_global_rag(dual_rag: DualRAG) -> None:
    """
    Populate Global RAG with shared medical knowledge.

    This knowledge is accessible to all domains.
    """
    # Add medical codes
    for code in ICD10_CODES + CPT_CODES + HCPCS_CODES:
        dual_rag.add_to_global(
            content=f"{code.code_type} {code.code}: {code.description}. "
                   f"Category: {code.category}. "
                   f"{code.medical_necessity if code.medical_necessity else ''}",
            metadata={
                "source": "system",
                "type": "medical_code",
                "code": code.code,
                "code_type": code.code_type,
                "category": code.category,
                "billable": code.billable,
                "typical_charge": code.typical_charge
            },
            doc_id=f"code_{code.code}",
            tags=[code.code_type, code.category, "medical_code"]
        )

    # Add clinical guidelines
    for i, guideline in enumerate(CLINICAL_GUIDELINES):
        dual_rag.add_to_global(
            content=f"{guideline['title']}: {guideline['content']}",
            metadata={
                "source": "system",
                "type": "clinical_guideline",
                "title": guideline['title'],
                "category": guideline['category']
            },
            doc_id=f"guideline_{i}",
            tags=["guideline", guideline['category']]
        )


def populate_local_rag(dual_rag: DualRAG, domain_id: str) -> None:
    """
    Populate Local RAG with domain-specific knowledge.

    Args:
        dual_rag: DualRAG instance
        domain_id: Domain to populate
    """
    knowledge_map = {
        "medical_coding": CODING_DOMAIN_KNOWLEDGE,
        "clinical_diagnosis": DIAGNOSIS_DOMAIN_KNOWLEDGE,
        "radiology_support": RADIOLOGY_DOMAIN_KNOWLEDGE,
        "biomedical_extraction": CODING_DOMAIN_KNOWLEDGE  # Share coding knowledge
    }

    knowledge = knowledge_map.get(domain_id, [])

    for i, item in enumerate(knowledge):
        dual_rag.add_to_local(
            domain_id=domain_id,
            content=f"{item['title']}: {item['content']}",
            metadata={
                "source": "system",
                "type": "domain_knowledge",
                "title": item['title'],
                "domain": domain_id
            },
            doc_id=f"{domain_id}_kb_{i}"
        )


def initialize_medical_knowledge_base(dual_rag: DualRAG) -> None:
    """
    Initialize complete medical knowledge base.

    Populates both Global RAG (shared) and Local RAG (domain-specific).
    """
    # Populate Global RAG
    populate_global_rag(dual_rag)

    # Populate Local RAG for all domains
    domains = [
        "medical_coding",
        "clinical_diagnosis",
        "radiology_support",
        "biomedical_extraction"
    ]

    for domain_id in domains:
        dual_rag.register_domain(domain_id)
        populate_local_rag(dual_rag, domain_id)


# ============================================================================
# Helper Functions
# ============================================================================

def get_code_by_number(code: str) -> MedicalCode:
    """Get medical code details by code number."""
    all_codes = ICD10_CODES + CPT_CODES + HCPCS_CODES
    for c in all_codes:
        if c.code == code:
            return c
    return None


def search_codes_by_description(search_term: str) -> List[MedicalCode]:
    """Search medical codes by description."""
    all_codes = ICD10_CODES + CPT_CODES + HCPCS_CODES
    results = []
    search_lower = search_term.lower()

    for code in all_codes:
        if search_lower in code.description.lower():
            results.append(code)

    return results
