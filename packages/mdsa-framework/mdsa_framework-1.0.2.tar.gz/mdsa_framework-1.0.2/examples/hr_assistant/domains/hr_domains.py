"""HR Domain Definitions for MDSA"""

def get_hr_domains():
    return [
        {
            "name": "recruitment",
            "description": "Job postings, candidate applications, interviews, hiring decisions",
            "keywords": ["job", "hire", "candidate", "interview", "recruit", "applicant", "position", "resume", "application", "offer"]
        },
        {
            "name": "onboarding",
            "description": "New employee onboarding, orientation, training, documentation",
            "keywords": ["onboard", "new hire", "orientation", "training", "welcome", "first day", "paperwork", "setup", "introduction", "probation"]
        },
        {
            "name": "benefits",
            "description": "Employee benefits, health insurance, retirement, PTO, perks",
            "keywords": ["benefits", "insurance", "401k", "retirement", "pto", "vacation", "medical", "dental", "health", "leave"]
        },
        {
            "name": "payroll",
            "description": "Salary, compensation, tax withholding, payroll processing",
            "keywords": ["payroll", "salary", "pay", "wage", "tax", "withhold", "deduction", "bonus", "compensation", "paycheck"]
        }
    ]

def register_domains(mdsa):
    domains = get_hr_domains()
    for domain in domains:
        mdsa.register_domain(domain["name"], domain["description"], domain["keywords"])
        print(f"✓ Registered: {domain['name']}")
    print(f"\n{len(domains)} HR domains registered!")
    return domains
