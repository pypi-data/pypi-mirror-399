"""
Enhanced Medical Domain Configurations with Specialized SLMs

This module creates domain configurations using Ollama for development:
- All domains use: ollama://llama3.2:3b-instruct-q4_0

For production, replace with specialized medical SLMs:
- Meerkat-8B: Clinical reasoning and diagnosis
- MediPhi-Instruct: Medical coding and billing
- OpenBioLLM-8B: Biomedical text and entity extraction
- BioMedLM-2.7B: Radiology support
- TinyLlama-Health: Edge deployment medical assistance

Prerequisites:
    1. Start Ollama: `ollama serve`
    2. Pull model: `ollama pull llama3.2:3b-instruct-q4_0`
"""

from mdsa.domains.config import DomainConfig
from mdsa.models.config import ModelTier, QuantizationType
from typing import Optional, List

# Development model (lightweight, runs via Ollama locally)
# DEVELOPMENT_MODEL = "ollama://llama3.2:3b-instruct-q4_0"  # Local model (commented out)

# Cloud Ollama Models (optimized for each domain)
# Choose models based on domain-specific capabilities
CLOUD_MEDICAL_CODING_MODEL = "ollama://kimi-k2-thinking:cloud"  # Precise reasoning for coding
CLOUD_CLINICAL_MODEL = "ollama://deepseek-v3.1:671b-cloud"  # Complex medical reasoning
CLOUD_BIOMEDICAL_MODEL = "ollama://qwen3-coder:480b-cloud"  # Structured extraction
CLOUD_RADIOLOGY_MODEL = "ollama://qwen3-vl:235b-instruct-cloud"  # Vision-language for imaging
CLOUD_QA_LITE_MODEL = "ollama://gpt-oss:120b-cloud"  # General medical Q&A

# Production models (specialized medical SLMs - for future deployment)
# PROD_CLINICAL_MODEL = "dmis-lab/llama-3-meerkat-8b-v1.0"
# PROD_CODING_MODEL = "microsoft/MediPhi-Instruct"
# PROD_BIOMEDICAL_MODEL = "aaditya/Llama3-OpenBioLLM-8B"
# PROD_RADIOLOGY_MODEL = "stanford-crfm/BioMedLM"
# PROD_QA_LITE_MODEL = "selinazarzour/healthgpt-tinyllama"


def create_clinical_diagnosis_domain(
    prefer_gpu: bool = True,
    force_device: str = None
) -> DomainConfig:
    """
    Clinical Diagnosis Domain.

    Specialized for:
    - Differential diagnosis
    - Clinical Q&A (USMLE-style)
    - Provider-facing decision support

    Development: Uses Ollama llama3.2:3b-instruct-q4_0
    Production: Replace with dmis-lab/llama-3-meerkat-8b-v1.0
    """
    # Ollama handles device placement server-side
    device = "ollama"

    return DomainConfig(
        domain_id="clinical_diagnosis",
        name="Clinical Diagnosis",
        description="Patient symptoms analysis, disease diagnosis, differential diagnosis, and clinical decision support for medical conditions",
        keywords=[
            "diagnosis", "differential", "symptoms", "clinical", "disease",
            "patient", "condition", "medical reasoning", "USMLE", "exam",
            "explain", "what causes", "how to diagnose", "signs"
        ],
        model_name=CLOUD_CLINICAL_MODEL,  # Using deepseek-v3.1:671b-cloud for complex reasoning
        model_tier=ModelTier.TIER1,  # Cloud model is high-tier (671B parameters)
        device=device,
        quantization=QuantizationType.NONE,  # Ollama handles quantization
        system_prompt="""You are a clinical diagnosis assistant.

Your expertise:
- Differential diagnosis based on symptoms
- Clinical reasoning and decision support
- USMLE-style medical Q&A
- Evidence-based medical guidance

Guidelines:
1. Always consider multiple differential diagnoses
2. Ask clarifying questions when needed
3. Cite medical evidence when available
4. Recommend appropriate diagnostic tests
5. Emphasize when physician consultation is needed

Remember: This is for educational and support purposes only. Always recommend consulting a licensed healthcare provider for actual diagnosis and treatment.""",
        max_tokens=512,
        temperature=0.3,  # Low temperature for accurate medical reasoning
        use_model_validation=True
    )


def create_medical_coding_domain(
    prefer_gpu: bool = True,
    force_device: str = None
) -> DomainConfig:
    """
    Medical Coding & Billing Domain.

    Specialized for:
    - ICD-10, CPT, HCPCS code suggestion
    - Medical necessity documentation
    - Denial appeal assistance

    Development: Uses Ollama llama3.2:3b-instruct-q4_0
    Production: Replace with microsoft/MediPhi-Instruct
    """
    # Ollama handles device placement server-side
    device = "ollama"

    return DomainConfig(
        domain_id="medical_coding",
        name="Medical Coding & Billing",
        description="Medical coding, billing, and claims support",
        keywords=[
            "icd", "icd-10", "cpt", "hcpcs", "code", "billing", "claims",
            "procedure", "diagnosis code", "medical coding", "revenue cycle",
            "denial", "appeal", "medical necessity", "justification"
        ],
        model_name=CLOUD_MEDICAL_CODING_MODEL,  # Using kimi-k2-thinking:cloud for precise reasoning
        model_tier=ModelTier.TIER1,  # Cloud model is high-tier (thinking-optimized)
        device=device,
        quantization=QuantizationType.NONE,
        system_prompt="""You are a medical coding and billing specialist.

Your expertise:
- ICD-10-CM diagnosis coding
- CPT and HCPCS procedure coding
- Medical necessity documentation
- Claims submission guidance
- Denial management and appeals

Guidelines:
1. Suggest appropriate codes based on clinical documentation
2. Explain code selection rationale
3. Highlight bundling and modifier requirements
4. Draft medical necessity statements
5. Assist with denial appeal letters

Format: Always provide codes in standard format (e.g., ICD-10: E11.9, CPT: 99213)""",
        max_tokens=768,
        temperature=0.2,  # Very low for precise coding
        use_model_validation=True
    )


def create_biomedical_extraction_domain(
    prefer_gpu: bool = True,
    force_device: str = None
) -> DomainConfig:
    """
    Biomedical Entity Extraction Domain.

    Specialized for:
    - Clinical text analysis
    - Entity extraction (diagnoses, procedures, medications)
    - De-identification

    Development: Uses Ollama llama3.2:3b-instruct-q4_0
    Production: Replace with aaditya/Llama3-OpenBioLLM-8B
    """
    # Ollama handles device placement server-side
    device = "ollama"

    return DomainConfig(
        domain_id="biomedical_extraction",
        name="Biomedical Text Analysis",
        description="Clinical text analysis and entity extraction",
        keywords=[
            "extract", "entity", "medication", "lab", "test", "procedure",
            "clinical note", "chart", "medical record", "phi", "de-identify",
            "parse", "structure", "summarize clinical", "biomedical"
        ],
        model_name=CLOUD_BIOMEDICAL_MODEL,  # Using qwen3-coder:480b-cloud for structured extraction
        model_tier=ModelTier.TIER1,  # Cloud model is high-tier (480B parameters, optimized for structured tasks)
        device=device,
        quantization=QuantizationType.NONE,
        system_prompt="""You are a biomedical text analysis specialist.

Your expertise:
- Extract structured information from clinical notes
- Identify diagnoses, procedures, medications, and lab results
- De-identify protected health information (PHI)
- Summarize clinical documentation
- Support claims auto-population

Guidelines:
1. Extract entities with high precision
2. Maintain clinical context
3. Flag ambiguous terms
4. Preserve medical terminology accuracy
5. Remove all PHI when requested (names, dates, locations, IDs)

Output Format: Structured JSON or markdown tables for easy integration.""",
        max_tokens=1024,
        temperature=0.1,  # Very precise extraction
        use_model_validation=True
    )


def create_lightweight_medical_qa_domain(
    force_device: str = "cpu"
) -> DomainConfig:
    """
    Lightweight Medical Q&A Domain.

    Specialized for:
    - Quick medical term explanations
    - Basic medical Q&A
    - Edge deployment / on-device assistance

    Development: Uses Ollama llama3.2:3b-instruct-q4_0
    Production: Replace with selinazarzour/healthgpt-tinyllama
    """
    # Ollama handles device placement server-side
    device = "ollama"

    return DomainConfig(
        domain_id="medical_qa_lite",
        name="Medical Q&A Lite",
        description="General medical questions, symptom explanations, disease definitions, medical terminology, and basic health information",
        keywords=[
            "what is", "explain", "define", "meaning", "term", "simple",
            "basic", "quick question", "medical term", "glossary",
            "what are symptoms", "explain symptoms", "what causes", "describe"
        ],
        model_name=CLOUD_QA_LITE_MODEL,  # Using gpt-oss:120b-cloud for general medical Q&A
        model_tier=ModelTier.TIER1,  # Cloud model is high-tier (120B parameters, general purpose)
        device=device,
        quantization=QuantizationType.NONE,
        system_prompt="""You are a medical terminology assistant.

Your expertise:
- Explain medical terms in simple language
- Answer basic medical questions
- Provide quick definitions
- Help coders and billers understand medical terminology

Guidelines:
1. Keep explanations simple and concise
2. Use analogies when helpful
3. Avoid complex medical jargon
4. Provide practical examples
5. Direct users to specialized domains for complex queries

This is a lightweight assistant for quick reference only.""",
        max_tokens=256,
        temperature=0.5,
        use_model_validation=False  # Skip validation for speed
    )


def create_radiology_support_domain(
    prefer_gpu: bool = True,
    force_device: str = None
) -> DomainConfig:
    """
    Radiology Support Domain.

    Specialized for:
    - Radiology report analysis
    - Imaging findings extraction
    - Supporting coding from rad reports

    Development: Uses Ollama llama3.2:3b-instruct-q4_0
    Production: Replace with stanford-crfm/BioMedLM
    """
    # Ollama handles device placement server-side
    device = "ollama"

    return DomainConfig(
        domain_id="radiology_support",
        name="Radiology Support",
        description="Imaging report interpretation, radiology findings extraction from CT scans, MRI reports, X-rays, and ultrasound studies",
        keywords=[
            "radiology", "imaging", "x-ray", "ct", "mri", "ultrasound",
            "scan", "radiologist", "report", "findings", "impression",
            "rad report", "image", "radiologic", "ct scan", "mri scan"
        ],
        model_name=CLOUD_RADIOLOGY_MODEL,  # Using qwen3-vl:235b-instruct-cloud for vision-language capabilities
        model_tier=ModelTier.TIER1,  # Cloud model is high-tier (235B parameters, vision-language optimized)
        device=device,
        quantization=QuantizationType.NONE,
        system_prompt="""You are a radiology support assistant.

Your expertise:
- Analyze radiology reports
- Extract key findings and impressions
- Suggest relevant procedure codes
- Support medical necessity documentation for imaging

Guidelines:
1. Focus on findings and clinical significance
2. Extract anatomical locations and abnormalities
3. Identify procedures performed
4. Suggest appropriate CPT codes for imaging
5. Note follow-up recommendations

Format: Structured extraction with clinical relevance.""",
        max_tokens=512,
        temperature=0.3,
        use_model_validation=True
    )


def get_all_enhanced_medical_domains(
    prefer_gpu: bool = True,
    force_device: Optional[str] = None
) -> List[DomainConfig]:
    """
    Get all enhanced medical domain configurations.

    Args:
        prefer_gpu: Whether to prefer GPU if available
        force_device: Force specific device (overrides prefer_gpu)

    Returns:
        List of DomainConfig objects for all medical domains
    """
    return [
        create_clinical_diagnosis_domain(prefer_gpu, force_device),
        create_medical_coding_domain(prefer_gpu, force_device),
        create_biomedical_extraction_domain(prefer_gpu, force_device),
        create_lightweight_medical_qa_domain(force_device or "cpu"),
        create_radiology_support_domain(prefer_gpu, force_device)
    ]


# Domain routing priority (highest to lowest specificity)
DOMAIN_PRIORITY = [
    "medical_coding",  # Most specific keywords
    "biomedical_extraction",  # Extraction-specific
    "radiology_support",  # Radiology-specific
    "clinical_diagnosis",  # General clinical
    "medical_qa_lite"  # Fallback for simple queries
]
