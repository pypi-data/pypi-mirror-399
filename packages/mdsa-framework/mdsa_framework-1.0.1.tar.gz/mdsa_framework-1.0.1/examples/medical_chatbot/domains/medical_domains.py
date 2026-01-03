"""
Medical Domain Configurations

Defines specialized domains for medical coding, billing, and claims processing.

Author: MDSA Framework Team
Date: 2025-12-06
"""

from mdsa.domains.config import DomainConfig
from mdsa.models.config import ModelTier, QuantizationType
from mdsa.utils.device_config import DeviceStrategy


def create_medical_coding_domain(
    prefer_gpu: bool = True,
    force_device: str = None
) -> DomainConfig:
    """
    Create domain for medical coding (ICD-10, CPT, HCPCS).

    This domain specializes in:
    - ICD-10 diagnostic codes
    - CPT procedure codes
    - HCPCS supply codes
    - Medical terminology
    - Code lookup and validation
    """
    device, quantization = DeviceStrategy.select_for_phi2(prefer_gpu, force_device)

    return DomainConfig(
        domain_id="medical_coding",
        name="Medical Coding",
        description="ICD-10, CPT, and HCPCS code lookup and validation",
        keywords=[
            # ICD-10
            "icd", "icd-10", "icd10", "diagnosis", "diagnostic",
            # CPT
            "cpt", "procedure", "treatment", "surgery",
            # HCPCS
            "hcpcs", "supply", "equipment", "dme",
            # General
            "code", "medical code", "lookup", "billing code",
            "coding", "encoder", "codebook"
        ],
        model_name="microsoft/phi-2",
        model_tier=ModelTier.TIER2,
        device=device,
        quantization=quantization,
        system_prompt="""You are a medical coding specialist with expertise in ICD-10, CPT, and HCPCS codes.

Your responsibilities:
- Look up diagnostic codes (ICD-10)
- Find procedure codes (CPT)
- Identify supply codes (HCPCS)
- Validate code accuracy
- Provide code descriptions
- Suggest appropriate codes based on medical documentation

Guidelines:
- Always specify the code system (ICD-10, CPT, HCPCS)
- Include complete code with description
- Mention any modifiers if applicable
- Note if code requires additional documentation
- Warn if code is outdated or deprecated

Example responses:
- "ICD-10 code E11.9: Type 2 diabetes mellitus without complications"
- "CPT code 99213: Office visit, established patient, 20-29 minutes"
- "HCPCS code A4253: Blood glucose test strips"
""",
        prompt_template="{query}",
        max_tokens=256,
        temperature=0.3,  # Low for accuracy
        use_model_validation=True
    )


def create_medical_billing_domain(
    prefer_gpu: bool = True,
    force_device: str = None
) -> DomainConfig:
    """
    Create domain for medical billing.

    This domain specializes in:
    - Billing calculations
    - Insurance claims
    - Payment processing
    - Billing rates
    - Reimbursement queries
    """
    device, quantization = DeviceStrategy.select_for_phi2(prefer_gpu, force_device)

    return DomainConfig(
        domain_id="medical_billing",
        name="Medical Billing",
        description="Medical billing, insurance claims, and payment processing",
        keywords=[
            # Billing
            "bill", "billing", "charge", "cost", "price", "rate",
            "fee", "payment", "invoice",
            # Insurance
            "insurance", "claim", "claims", "reimbursement",
            "coverage", "copay", "deductible", "coinsurance",
            # Financial
            "amount", "total", "balance", "due", "owed",
            "calculate", "estimation", "estimate"
        ],
        model_name="microsoft/phi-2",
        model_tier=ModelTier.TIER2,
        device=device,
        quantization=quantization,
        system_prompt="""You are a medical billing specialist with expertise in healthcare billing and insurance claims.

Your responsibilities:
- Calculate billing amounts
- Explain insurance coverage
- Process billing inquiries
- Estimate patient responsibility
- Handle payment questions

Guidelines:
- Always show calculation breakdown
- Specify what insurance covers vs patient responsibility
- Mention relevant CPT/HCPCS codes
- Include any applicable modifiers
- Note payment terms and due dates

Example responses:
- "CPT 99213 standard rate: $150.00. Insurance covers $120.00. Patient copay: $30.00"
- "Total charges: $450.00 (Office visit $150 + Lab work $300). Insurance pays 80% after $50 deductible"
""",
        prompt_template="{query}",
        max_tokens=256,
        temperature=0.3,
        use_model_validation=True
    )


def create_claims_processing_domain(
    prefer_gpu: bool = True,
    force_device: str = None
) -> DomainConfig:
    """
    Create domain for insurance claims processing.

    This domain specializes in:
    - Claims submission
    - Claims status
    - Claim denial handling
    - Prior authorization
    - Claims adjudication
    """
    device, quantization = DeviceStrategy.select_for_phi2(prefer_gpu, force_device)

    return DomainConfig(
        domain_id="claims_processing",
        name="Claims Processing",
        description="Insurance claims submission, status, and resolution",
        keywords=[
            # Claims
            "claim", "claims", "submission", "submit", "file",
            "adjudication", "adjudicate", "process", "processing",
            # Status
            "status", "pending", "approved", "denied", "rejected",
            "resubmit", "appeal", "review",
            # Authorization
            "authorization", "prior auth", "pa", "preauth",
            "approval", "clearance",
            # Resolution
            "denial", "rejection", "error", "correction", "fix"
        ],
        model_name="microsoft/phi-2",
        model_tier=ModelTier.TIER2,
        device=device,
        quantization=quantization,
        system_prompt="""You are a claims processing specialist with expertise in insurance claims and adjudication.

Your responsibilities:
- Track claim status
- Handle claim denials
- Process prior authorizations
- Resolve claim errors
- Guide resubmission

Guidelines:
- Always provide claim ID if available
- Explain denial reasons clearly
- Give specific steps for resolution
- Mention required documentation
- Note timelines and deadlines

Example responses:
- "Claim #12345 status: DENIED. Reason: Missing prior authorization for CPT 12345. Action: Obtain PA and resubmit within 30 days"
- "Prior authorization required for MRI (CPT 70553). Submit clinical notes + referral. Processing time: 3-5 business days"
""",
        prompt_template="{query}",
        max_tokens=256,
        temperature=0.3,
        use_model_validation=True
    )


def get_all_medical_domains(
    prefer_gpu: bool = True,
    force_device: str = None
) -> list[DomainConfig]:
    """Get all medical domain configurations."""
    return [
        create_medical_coding_domain(prefer_gpu, force_device),
        create_medical_billing_domain(prefer_gpu, force_device),
        create_claims_processing_domain(prefer_gpu, force_device)
    ]


# Demo
if __name__ == "__main__":
    print("=" * 70)
    print("Medical Domain Configurations")
    print("=" * 70)

    domains = get_all_medical_domains()

    for domain in domains:
        print(f"\nDomain: {domain.name}")
        print(f"  ID: {domain.domain_id}")
        print(f"  Model: {domain.model_name}")
        print(f"  Keywords: {', '.join(domain.keywords[:5])}...")
        print(f"  Device: {domain.device}")
        print(f"  Quantization: {domain.quantization.value}")

    print("\n" + "=" * 70)
    print("✓ Medical domains configured successfully")
    print("=" * 70)
