"""
Medical Codes Knowledge Base

Contains ICD-10, CPT, and HCPCS codes for the RAG system.

Author: MDSA Framework Team
Date: 2025-12-06
"""

from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class MedicalCode:
    """Represents a medical code with metadata."""
    code: str
    code_type: str  # 'ICD-10', 'CPT', 'HCPCS'
    description: str
    category: str
    billable: bool = True
    requires_auth: bool = False
    typical_charge: float = 0.0
    notes: str = ""


# ============================================================================
# ICD-10 Diagnostic Codes
# ============================================================================

ICD10_CODES = [
    # Diabetes
    MedicalCode(
        code="E11.9",
        code_type="ICD-10",
        description="Type 2 diabetes mellitus without complications",
        category="Endocrine, nutritional and metabolic diseases",
        billable=True
    ),
    MedicalCode(
        code="E11.65",
        code_type="ICD-10",
        description="Type 2 diabetes mellitus with hyperglycemia",
        category="Endocrine, nutritional and metabolic diseases",
        billable=True
    ),
    MedicalCode(
        code="E10.9",
        code_type="ICD-10",
        description="Type 1 diabetes mellitus without complications",
        category="Endocrine, nutritional and metabolic diseases",
        billable=True
    ),

    # Hypertension
    MedicalCode(
        code="I10",
        code_type="ICD-10",
        description="Essential (primary) hypertension",
        category="Diseases of the circulatory system",
        billable=True
    ),
    MedicalCode(
        code="I11.9",
        code_type="ICD-10",
        description="Hypertensive heart disease without heart failure",
        category="Diseases of the circulatory system",
        billable=True
    ),

    # Asthma
    MedicalCode(
        code="J45.909",
        code_type="ICD-10",
        description="Unspecified asthma, uncomplicated",
        category="Diseases of the respiratory system",
        billable=True
    ),
    MedicalCode(
        code="J45.40",
        code_type="ICD-10",
        description="Moderate persistent asthma, uncomplicated",
        category="Diseases of the respiratory system",
        billable=True
    ),

    # COVID-19
    MedicalCode(
        code="U07.1",
        code_type="ICD-10",
        description="COVID-19",
        category="Emergency use codes",
        billable=True
    ),

    # Influenza
    MedicalCode(
        code="J10.1",
        code_type="ICD-10",
        description="Influenza with other respiratory manifestations, virus identified",
        category="Diseases of the respiratory system",
        billable=True
    ),

    # Depression
    MedicalCode(
        code="F32.9",
        code_type="ICD-10",
        description="Major depressive disorder, single episode, unspecified",
        category="Mental, Behavioral and Neurodevelopmental disorders",
        billable=True
    ),

    # Migraine
    MedicalCode(
        code="G43.909",
        code_type="ICD-10",
        description="Migraine, unspecified, not intractable, without status migrainosus",
        category="Diseases of the nervous system",
        billable=True
    ),

    # Fractures
    MedicalCode(
        code="S52.501A",
        code_type="ICD-10",
        description="Unspecified fracture of the lower end of right radius, initial encounter",
        category="Injury, poisoning",
        billable=True
    ),

    # Pregnancy
    MedicalCode(
        code="Z34.90",
        code_type="ICD-10",
        description="Encounter for supervision of normal pregnancy, unspecified trimester",
        category="Factors influencing health status",
        billable=False
    ),
]

# ============================================================================
# CPT Procedure Codes
# ============================================================================

CPT_CODES = [
    # Office Visits (Evaluation & Management)
    MedicalCode(
        code="99213",
        code_type="CPT",
        description="Office or other outpatient visit, established patient, 20-29 minutes",
        category="Evaluation and Management",
        typical_charge=150.00,
        notes="Requires moderate medical decision making"
    ),
    MedicalCode(
        code="99214",
        code_type="CPT",
        description="Office or other outpatient visit, established patient, 30-39 minutes",
        category="Evaluation and Management",
        typical_charge=200.00,
        notes="Requires moderate to high medical decision making"
    ),
    MedicalCode(
        code="99203",
        code_type="CPT",
        description="Office or other outpatient visit, new patient, 30-44 minutes",
        category="Evaluation and Management",
        typical_charge=175.00
    ),

    # Laboratory
    MedicalCode(
        code="80053",
        code_type="CPT",
        description="Comprehensive metabolic panel",
        category="Pathology and Laboratory",
        typical_charge=75.00
    ),
    MedicalCode(
        code="85025",
        code_type="CPT",
        description="Complete blood count (CBC) with differential",
        category="Pathology and Laboratory",
        typical_charge=50.00
    ),
    MedicalCode(
        code="82947",
        code_type="CPT",
        description="Glucose blood test",
        category="Pathology and Laboratory",
        typical_charge=25.00
    ),

    # Radiology
    MedicalCode(
        code="70553",
        code_type="CPT",
        description="MRI brain with and without contrast",
        category="Radiology",
        typical_charge=1200.00,
        requires_auth=True,
        notes="Prior authorization usually required"
    ),
    MedicalCode(
        code="71046",
        code_type="CPT",
        description="Chest X-ray, 2 views",
        category="Radiology",
        typical_charge=150.00
    ),

    # Surgery
    MedicalCode(
        code="29881",
        code_type="CPT",
        description="Arthroscopy, knee, surgical; with meniscectomy",
        category="Surgery",
        typical_charge=3500.00,
        requires_auth=True
    ),

    # Immunizations
    MedicalCode(
        code="90471",
        code_type="CPT",
        description="Immunization administration, first vaccine",
        category="Medicine",
        typical_charge=25.00
    ),
    MedicalCode(
        code="90686",
        code_type="CPT",
        description="Influenza virus vaccine, quadrivalent",
        category="Medicine",
        typical_charge=40.00
    ),
]

# ============================================================================
# HCPCS Codes
# ============================================================================

HCPCS_CODES = [
    # Diabetic Supplies
    MedicalCode(
        code="A4253",
        code_type="HCPCS",
        description="Blood glucose test strips, 50 count",
        category="Medical and Surgical Supplies",
        typical_charge=35.00
    ),
    MedicalCode(
        code="A4258",
        code_type="HCPCS",
        description="Spring-powered device for lancet",
        category="Medical and Surgical Supplies",
        typical_charge=10.00
    ),
    MedicalCode(
        code="E0607",
        code_type="HCPCS",
        description="Home blood glucose monitor",
        category="Durable Medical Equipment",
        typical_charge=50.00
    ),

    # Wheelchair/Mobility
    MedicalCode(
        code="E1130",
        code_type="HCPCS",
        description="Standard wheelchair, fixed full-length arms",
        category="Durable Medical Equipment",
        typical_charge=500.00,
        requires_auth=True
    ),
    MedicalCode(
        code="E0110",
        code_type="HCPCS",
        description="Crutches, forearm, includes crutches of various materials",
        category="Durable Medical Equipment",
        typical_charge=75.00
    ),

    # Oxygen Equipment
    MedicalCode(
        code="E1390",
        code_type="HCPCS",
        description="Oxygen concentrator, single delivery port",
        category="Durable Medical Equipment",
        typical_charge=800.00,
        requires_auth=True
    ),

    # Prosthetics
    MedicalCode(
        code="L3000",
        code_type="HCPCS",
        description="Foot insert, removable, molded to patient model",
        category="Orthotics and Prosthetics",
        typical_charge=200.00
    ),
]


# ============================================================================
# Knowledge Base Functions
# ============================================================================

def get_all_codes() -> List[MedicalCode]:
    """Get all medical codes."""
    return ICD10_CODES + CPT_CODES + HCPCS_CODES


def search_codes(
    query: str,
    code_type: str = None,
    category: str = None
) -> List[MedicalCode]:
    """
    Search medical codes by query.

    Args:
        query: Search term
        code_type: Filter by code type ('ICD-10', 'CPT', 'HCPCS')
        category: Filter by category

    Returns:
        List of matching codes
    """
    query_lower = query.lower()
    all_codes = get_all_codes()

    results = []
    for code in all_codes:
        # Filter by type
        if code_type and code.code_type != code_type:
            continue

        # Filter by category
        if category and code.category != category:
            continue

        # Search in code and description
        if (query_lower in code.code.lower() or
            query_lower in code.description.lower()):
            results.append(code)

    return results


def get_code_by_id(code_id: str) -> MedicalCode:
    """Get specific code by ID."""
    code_id_upper = code_id.upper()
    all_codes = get_all_codes()

    for code in all_codes:
        if code.code.upper() == code_id_upper:
            return code

    return None


def format_code_for_rag(code: MedicalCode) -> str:
    """Format code for RAG system."""
    text = f"{code.code_type} code {code.code}: {code.description}"

    if code.category:
        text += f" (Category: {code.category})"

    if code.typical_charge > 0:
        text += f" Typical charge: ${code.typical_charge:.2f}"

    if code.requires_auth:
        text += " **Prior authorization required**"

    if code.notes:
        text += f" Notes: {code.notes}"

    return text


def populate_rag_system(dual_rag, domain_id: str):
    """
    Populate RAG system with medical codes.

    Args:
        dual_rag: DualRAG instance
        domain_id: Domain to populate ('medical_coding', 'medical_billing', 'claims_processing')
    """
    all_codes = get_all_codes()

    # Add to LocalRAG (domain-specific)
    for code in all_codes:
        formatted = format_code_for_rag(code)

        dual_rag.add_to_local(
            domain_id,
            formatted,
            metadata={
                'code': code.code,
                'code_type': code.code_type,
                'category': code.category,
                'typical_charge': code.typical_charge,
                'requires_auth': code.requires_auth
            }
        )

    # Add general medical knowledge to GlobalRAG
    global_knowledge = [
        "Medical coding involves assigning standardized codes to diagnoses and procedures",
        "ICD-10 codes are used for diagnoses and health conditions",
        "CPT codes are used for medical procedures and services",
        "HCPCS codes are used for equipment, supplies, and services not in CPT",
        "Prior authorization is required for certain procedures and equipment",
        "Insurance reimbursement rates vary by procedure and insurance plan",
        "Modifiers can be appended to CPT codes to indicate special circumstances",
        "Diagnosis codes must support the medical necessity of procedures",
    ]

    for knowledge in global_knowledge:
        dual_rag.add_to_global(
            knowledge,
            tags=['medical', 'coding', 'billing']
        )


# Demo
if __name__ == "__main__":
    print("=" * 70)
    print("Medical Codes Knowledge Base")
    print("=" * 70)

    # Statistics
    print(f"\nTotal codes: {len(get_all_codes())}")
    print(f"  ICD-10: {len(ICD10_CODES)}")
    print(f"  CPT: {len(CPT_CODES)}")
    print(f"  HCPCS: {len(HCPCS_CODES)}")

    # Search examples
    print("\nSearch Examples:")

    print("\n1. Search for 'diabetes':")
    results = search_codes("diabetes")
    for code in results[:3]:
        print(f"   {code.code_type} {code.code}: {code.description}")

    print("\n2. Search CPT codes:")
    results = search_codes("office visit", code_type="CPT")
    for code in results[:3]:
        print(f"   {code.code}: {code.description} (${code.typical_charge:.2f})")

    print("\n3. Get specific code:")
    code = get_code_by_id("99213")
    if code:
        print(f"   {format_code_for_rag(code)}")

    print("\n" + "=" * 70)
    print("✓ Knowledge base ready")
    print("=" * 70)
