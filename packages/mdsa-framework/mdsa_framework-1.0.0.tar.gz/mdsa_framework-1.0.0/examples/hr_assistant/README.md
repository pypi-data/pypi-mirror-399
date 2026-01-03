# HR Assistant Example

Demonstrates MDSA framework's domain-agnostic capability for Human Resources industry.

## Overview

Four specialized HR domains:
- **recruitment**: Job postings, applications, interviews, hiring
- **onboarding**: New hire documentation, orientation, training
- **benefits**: Health insurance, 401k, PTO, perks
- **payroll**: Salary, taxes, deductions, compensation

## Benchmark Results

**Routing Accuracy**: 74.2% (MEDIUM semantic overlap) ✅
**Median Latency**: 14ms
**Status**: Production-ready

HR domains have distinct enough concepts (hiring vs. payroll vs. benefits) for good routing accuracy.

## Quick Start

```bash
# Run the assistant
python workflows/hr_assistant.py
```

## Sample Queries

```
User: Post a job opening for software engineer
→ Routes to: recruitment

User: Send welcome email to new hire
→ Routes to: onboarding

User: Enroll in health insurance
→ Routes to: benefits

User: View my pay stub
→ Routes to: payroll
```

## Performance

| Metric | Value | Status |
|--------|-------|--------|
| Routing Accuracy | 74.2% | ✅ PASS (MEDIUM overlap) |
| Median Latency | 14ms | ✅ PASS |
| Consistency | Same framework as medical/e-commerce | ✅ Domain-agnostic |

---

**Framework**: MDSA v1.0.0
**Industry**: Human Resources
**License**: Apache 2.0
