# Building Your First MDSA Application

**Version**: 1.0.0
**Estimated Time**: 30-45 minutes
**Difficulty**: Beginner

Welcome! This tutorial will guide you through building your first multi-domain AI application using the MDSA Framework. By the end, you'll have a working customer support chatbot that intelligently routes queries to specialized domains.

---

## Table of Contents

1. [What We're Building](#what-were-building)
2. [Prerequisites](#prerequisites)
3. [Step 1: Installation](#step-1-installation)
4. [Step 2: Configure Domains](#step-2-configure-domains)
5. [Step 3: Add Knowledge Bases](#step-3-add-knowledge-bases)
6. [Step 4: Create the Application](#step-4-create-the-application)
7. [Step 5: Test Your Application](#step-5-test-your-application)
8. [Step 6: Monitor with Dashboard](#step-6-monitor-with-dashboard)
9. [Next Steps](#next-steps)

---

## What We're Building

We'll build a **Customer Support Chatbot** with three specialized domains:

1. **Technical Support** - Handles product issues, troubleshooting, error codes
2. **Billing** - Answers questions about invoices, payments, refunds
3. **General Inquiries** - Handles FAQs, policies, general questions

**Key Features**:
- Automatic domain routing based on query content
- Domain-specific knowledge bases for accurate responses
- Built-in caching for fast repeated queries
- Real-time monitoring dashboard

**Architecture**:
```
User Query → TinyBERT Router → Domain Classification → RAG Retrieval → Domain Model → Response
```

---

## Prerequisites

Before starting, ensure you have:

- **Python 3.9+** installed ([download](https://www.python.org/downloads/))
- **8GB+ RAM** available
- **20GB+ disk space** for models
- **Basic Python knowledge** (variables, functions, dictionaries)
- **Command line familiarity** (cd, ls, python)

**Optional but recommended**:
- Text editor (VS Code, PyCharm, Sublime Text)
- Git for version control

---

## Step 1: Installation

### 1.1 Install Ollama

Ollama runs language models locally on your machine.

**macOS / Linux**:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows**:
Download installer from [ollama.com/download](https://ollama.com/download)

**Verify installation**:
```bash
ollama --version
# Expected output: ollama version X.X.X
```

### 1.2 Download a Language Model

We'll use Deepseek v3.1 (4.7GB):

```bash
ollama pull deepseek-v3.1
```

This downloads and caches the model locally. First time takes 5-10 minutes.

### 1.3 Install MDSA Framework

**Option A: Install from PyPI** (recommended):
```bash
pip install mdsa-framework
```

**Option B: Install from source**:
```bash
# Clone repository
git clone https://github.com/your-org/mdsa-framework.git
cd mdsa-framework

# Install in development mode
pip install -e .
```

**Verify installation**:
```bash
python -c "import mdsa; print(mdsa.__version__)"
# Expected output: 1.0.0
```

---

## Step 2: Configure Domains

Create a project directory and configuration file:

```bash
# Create project
mkdir my-first-mdsa-app
cd my-first-mdsa-app

# Create directories
mkdir -p knowledge_base/technical
mkdir -p knowledge_base/billing
mkdir -p knowledge_base/general
```

Create `config.yaml`:

```yaml
# MDSA Configuration for Customer Support Chatbot

# Domain definitions
domains:
  # Technical Support Domain
  - name: technical_support
    description: "Technical issues, troubleshooting, error codes, product malfunctions, software bugs"
    model: deepseek-v3.1
    kb_path: knowledge_base/technical/
    system_prompt: |
      You are a technical support specialist.
      Help users troubleshoot issues, explain error codes, and provide step-by-step solutions.
      Be clear, concise, and ask clarifying questions when needed.
    temperature: 0.3  # Lower = more deterministic
    max_tokens: 1024

  # Billing Domain
  - name: billing
    description: "Billing questions, invoices, payments, refunds, subscription management, pricing"
    model: deepseek-v3.1
    kb_path: knowledge_base/billing/
    system_prompt: |
      You are a billing support specialist.
      Help users with invoices, payments, refunds, and subscription questions.
      Always verify account details before discussing specific billing information.
    temperature: 0.2  # Very deterministic for financial info
    max_tokens: 512

  # General Inquiries Domain
  - name: general
    description: "General questions, FAQs, company policies, hours of operation, contact information"
    model: deepseek-v3.1
    kb_path: knowledge_base/general/
    system_prompt: |
      You are a helpful customer service representative.
      Answer general questions about our company, policies, and services.
      Be friendly and redirect complex issues to appropriate specialists.
    temperature: 0.5  # Balanced
    max_tokens: 512

# Router configuration
router:
  model: TinyBERT  # Fast domain classification
  cache_embeddings: true  # 80% faster

# RAG configuration
rag:
  chunk_size: 500
  chunk_overlap: 50
  top_k: 3  # Retrieve top 3 relevant documents
  similarity_threshold: 0.7

# Performance settings
performance:
  enable_cache: true
  cache_size: 100
  max_workers: 4

# Dashboard configuration
dashboard:
  enabled: true
  host: 0.0.0.0
  port: 9000

# Logging
logging:
  level: INFO
  file: logs/mdsa.log
```

**Understanding the configuration**:

- **domains**: Each domain has its own model, knowledge base, and system prompt
- **description**: Used by router to classify queries (be specific!)
- **temperature**: Controls randomness (0.0 = deterministic, 1.0 = creative)
- **kb_path**: Path to domain-specific documents
- **system_prompt**: Instructions that define agent behavior

---

## Step 3: Add Knowledge Bases

Knowledge bases provide domain-specific information for RAG (Retrieval-Augmented Generation).

### 3.1 Technical Support Knowledge Base

Create `knowledge_base/technical/common_issues.txt`:

```text
# Common Technical Issues

## Error Code 404 - Page Not Found
This error occurs when trying to access a non-existent page or resource.

Solution:
1. Check the URL for typos
2. Clear browser cache (Ctrl+Shift+Delete)
3. Try accessing from a different browser
4. Contact support if issue persists

## Error Code 500 - Internal Server Error
Server-side error preventing request completion.

Solution:
1. Refresh the page (F5)
2. Wait 5 minutes and try again
3. Check our status page at status.example.com
4. Contact support with error details

## Application Won't Start
Common causes and solutions:

1. Insufficient RAM - Close other applications
2. Outdated version - Update to latest version
3. Corrupted installation - Reinstall application
4. Firewall blocking - Add exception in firewall settings

## Slow Performance
Troubleshooting steps:

1. Close unused browser tabs
2. Clear application cache
3. Check internet speed (minimum 5 Mbps recommended)
4. Restart application
5. Update to latest version
```

Create `knowledge_base/technical/product_specs.txt`:

```text
# Product Specifications

## System Requirements
- Operating System: Windows 10/11, macOS 12+, Linux (Ubuntu 20.04+)
- RAM: Minimum 8GB, Recommended 16GB
- Storage: 20GB available space
- Internet: Broadband connection (5 Mbps minimum)
- Browser: Chrome 90+, Firefox 88+, Safari 14+

## Supported File Formats
- Documents: PDF, DOCX, TXT, MD
- Images: PNG, JPG, GIF, SVG
- Video: MP4, WEBM, MOV (max 500MB)
- Audio: MP3, WAV, OGG (max 100MB)

## API Rate Limits
- Free Tier: 100 requests/hour
- Basic Plan: 1,000 requests/hour
- Pro Plan: 10,000 requests/hour
- Enterprise: Unlimited (with SLA)
```

### 3.2 Billing Knowledge Base

Create `knowledge_base/billing/pricing.txt`:

```text
# Pricing Information

## Subscription Plans

### Free Plan - $0/month
- 100 API calls/hour
- 1 GB storage
- Email support
- Community access

### Basic Plan - $29/month
- 1,000 API calls/hour
- 50 GB storage
- Email support (24h response)
- Basic analytics

### Pro Plan - $99/month
- 10,000 API calls/hour
- 500 GB storage
- Priority support (4h response)
- Advanced analytics
- Custom domains

### Enterprise Plan - Custom pricing
- Unlimited API calls
- Unlimited storage
- Dedicated support (1h SLA)
- Custom integrations
- On-premise deployment option

## Billing Cycle
- Monthly plans: Billed on subscription date each month
- Annual plans: Billed upfront, 20% discount
- Usage-based: Billed at end of month
```

Create `knowledge_base/billing/refund_policy.txt`:

```text
# Refund Policy

## Money-Back Guarantee
30-day money-back guarantee on all paid plans.

Conditions:
- Must request within 30 days of purchase
- Applies to first-time customers only
- No refunds for annual plans after 30 days
- Usage-based charges are non-refundable

## How to Request Refund
1. Email billing@example.com with:
   - Account email
   - Order number
   - Reason for refund (optional)
2. Refund processed within 5-7 business days
3. Refunded to original payment method

## Pro-Rated Refunds
- Downgrade: Receive pro-rated credit for unused period
- Upgrade: Pay pro-rated difference
- Cancellation: No refund, access until period end

## Dispute Resolution
For billing disputes:
1. Contact billing@example.com
2. Include invoice number and dispute details
3. Response within 48 hours
4. Escalate to manager if unresolved
```

### 3.3 General Inquiries Knowledge Base

Create `knowledge_base/general/company_info.txt`:

```text
# Company Information

## About Us
We provide cutting-edge AI solutions for businesses worldwide.
Founded in 2020, we serve over 10,000 customers across 50 countries.

## Contact Information
- Email: support@example.com
- Phone: +1-800-123-4567
- Hours: Monday-Friday, 9 AM - 6 PM EST
- Address: 123 Tech Street, San Francisco, CA 94105

## Support Channels
- Email: support@example.com (24h response)
- Live Chat: Available 9 AM - 6 PM EST
- Phone: +1-800-123-4567 (9 AM - 6 PM EST)
- Community Forum: forum.example.com
- Documentation: docs.example.com

## Social Media
- Twitter: @example
- LinkedIn: linkedin.com/company/example
- GitHub: github.com/example
```

Create `knowledge_base/general/faq.txt`:

```text
# Frequently Asked Questions

## How do I create an account?
1. Visit example.com
2. Click "Sign Up" in top-right corner
3. Enter email and create password
4. Verify email address
5. Complete profile setup

## Can I change my plan later?
Yes! You can upgrade or downgrade anytime from your account settings.
Changes take effect immediately for upgrades, at next billing cycle for downgrades.

## Is my data secure?
Yes. We use:
- AES-256 encryption at rest
- TLS 1.3 for data in transit
- SOC 2 Type II certified
- GDPR compliant
- Regular security audits

## Do you offer free trials?
Yes! All paid plans include a 14-day free trial. No credit card required.

## What payment methods do you accept?
- Credit/Debit cards (Visa, Mastercard, Amex)
- PayPal
- Wire transfer (Enterprise plans)
- Cryptocurrency (Bitcoin, Ethereum)

## Can I cancel anytime?
Yes, cancel anytime from account settings. No cancellation fees.
Access continues until end of current billing period.
```

---

## Step 4: Create the Application

Create `app.py` in your project root:

```python
"""
Customer Support Chatbot - First MDSA Application
A multi-domain chatbot that routes queries to specialized support domains.
"""

from mdsa import MDSA
import sys


def main():
    """Main application entry point."""
    print("=" * 60)
    print("Customer Support Chatbot")
    print("Powered by MDSA Framework v1.0.0")
    print("=" * 60)
    print("\nInitializing chatbot... This may take a moment.\n")

    # Initialize MDSA with configuration
    mdsa = MDSA(config_path="config.yaml")

    print("✓ MDSA Framework initialized")
    print("✓ 3 domains loaded: technical_support, billing, general")
    print("✓ Knowledge bases indexed")
    print("✓ Ready to assist!\n")
    print("Dashboard: http://localhost:9000")
    print("Type 'quit' or 'exit' to end session.\n")
    print("-" * 60)

    # Chat loop
    while True:
        try:
            # Get user input
            query = input("\nYou: ").strip()

            # Check for exit command
            if query.lower() in ['quit', 'exit', 'bye']:
                print("\nThank you for using our support chatbot. Goodbye!")
                break

            # Skip empty queries
            if not query:
                continue

            # Process query
            print("\nAgent: Thinking...")
            response = mdsa.query(query)

            # Display response
            print(f"\n[Domain: {response.domain}]")
            print(f"Agent: {response.text}")

            # Display performance metrics
            print(f"\n[Processed in {response.latency:.2f}ms | "
                  f"Cache: {'HIT' if response.cached else 'MISS'}]")

        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            break

        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again or contact support.")


if __name__ == "__main__":
    main()
```

**Code explanation**:

1. **Import MDSA**: `from mdsa import MDSA`
2. **Initialize**: `mdsa = MDSA(config_path="config.yaml")`
3. **Query**: `response = mdsa.query(query)`
4. **Access results**: `response.text`, `response.domain`, `response.latency`

---

## Step 5: Test Your Application

### 5.1 Start Ollama (if not already running)

```bash
ollama serve
```

Keep this terminal open.

### 5.2 Run Your Application

In a new terminal:

```bash
python app.py
```

**Expected output**:
```
============================================================
Customer Support Chatbot
Powered by MDSA Framework v1.0.0
============================================================

Initializing chatbot... This may take a moment.

✓ MDSA Framework initialized
✓ 3 domains loaded: technical_support, billing, general
✓ Knowledge bases indexed
✓ Ready to assist!

Dashboard: http://localhost:9000
Type 'quit' or 'exit' to end session.

------------------------------------------------------------

You:
```

### 5.3 Test Queries

Try these queries to test domain routing:

**Technical Support**:
```
You: I'm getting error code 404
```

Expected: Routed to `technical_support` domain, provides troubleshooting steps.

**Billing**:
```
You: How much does the Pro plan cost?
```

Expected: Routed to `billing` domain, explains Pro plan pricing ($99/month).

**General**:
```
You: What are your business hours?
```

Expected: Routed to `general` domain, provides hours (Monday-Friday, 9 AM - 6 PM EST).

**Test Caching**:
```
You: How much does the Pro plan cost?
```

Run this query again. Second time should show "Cache: HIT" and much faster latency (<10ms vs 500+ms).

---

## Step 6: Monitor with Dashboard

### 6.1 Open Dashboard

While chatbot is running, open browser to:
```
http://localhost:9000
```

### 6.2 Explore Dashboard Features

**Home Page**:
- Total requests processed
- Average latency
- Cache hit rate
- Domain distribution pie chart

**Request Timeline**:
- Real-time request tracking
- Query text and domain classification
- Response time for each request
- Cache status (hit/miss)

**Domain Analytics**:
- Requests per domain
- Average latency per domain
- Popular queries by domain

**Performance Metrics**:
- Latency histogram
- Cache performance over time
- Memory usage
- Throughput (requests/second)

---

## Next Steps

Congratulations! You've built your first MDSA application. Here's what to explore next:

### 1. Add More Domains

Expand your chatbot with additional specialized domains:

```yaml
domains:
  - name: sales
    description: "Product demos, pricing comparisons, sales inquiries"
    model: deepseek-v3.1
    kb_path: knowledge_base/sales/
    system_prompt: "You are a sales consultant..."
```

### 2. Integrate Tools

Add external tool calls (database queries, API calls, calculations):

```python
from mdsa.tools import Tool

def check_order_status(order_id: str) -> str:
    """Check status of an order."""
    # Your database logic here
    return f"Order {order_id} status: Shipped"

mdsa.add_tool(Tool(
    name="check_order_status",
    func=check_order_status,
    description="Check the status of an order by ID"
))
```

See [docs/USER_GUIDE.md#8-tools-integration](../USER_GUIDE.md#8-tools-integration).

### 3. Build a Web UI

Replace command-line interface with Gradio or Streamlit:

```python
import gradio as gr

def chat(message, history):
    response = mdsa.query(message)
    return response.text

gr.ChatInterface(chat).launch()
```

### 4. Deploy to Production

Deploy your chatbot to the cloud:

- **Docker**: Containerize your application
- **Cloud**: Deploy to AWS/Azure/GCP
- **Kubernetes**: Scale horizontally

See [examples/medical_chatbot/DEPLOYMENT.md](../../examples/medical_chatbot/DEPLOYMENT.md) for deployment guides.

### 5. Advanced Features

Explore advanced MDSA capabilities:

- **Multi-step reasoning** with Phi-2
- **Agent chains** for complex workflows
- **Guardrails** for input/output filtering
- **Streaming responses** for real-time output
- **Custom routers** for specialized classification

See [docs/USER_GUIDE.md](../USER_GUIDE.md) for comprehensive feature documentation.

---

## Troubleshooting

### "Ollama connection failed"

**Solution**:
```bash
# Start Ollama in separate terminal
ollama serve
```

### "No module named 'mdsa'"

**Solution**:
```bash
# Reinstall MDSA
pip install --upgrade mdsa-framework
```

### "Out of memory"

**Solution**:
1. Close other applications
2. Use smaller model: `ollama pull llama3.1:8b`
3. Reduce cache size in `config.yaml`

### Dashboard not accessible

**Solution**:
1. Check dashboard is enabled in `config.yaml`
2. Verify port 9000 is not blocked by firewall
3. Try accessing `http://127.0.0.1:9000` instead

---

## Additional Resources

- **[Setup Guide](../SETUP_GUIDE.md)** - Comprehensive installation guide
- **[User Guide](../USER_GUIDE.md)** - Complete feature documentation
- **[Examples](../../examples/)** - More example applications
- **[FAQ](../FAQ.md)** - Frequently asked questions
- **[API Reference](../FRAMEWORK_REFERENCE.md)** - Complete API documentation

---

## Summary

In this tutorial, you:

✅ Installed MDSA Framework and Ollama
✅ Configured three specialized domains
✅ Created domain-specific knowledge bases
✅ Built a working chatbot application
✅ Tested domain routing and caching
✅ Explored the monitoring dashboard

You now have a solid foundation to build sophisticated multi-domain AI applications with MDSA!

---

**Need Help?**
- GitHub Issues: https://github.com/your-org/mdsa-framework/issues
- Documentation: https://docs.mdsa-framework.com
- Community Forum: https://forum.mdsa-framework.com

**Last Updated**: December 2025
**Version**: 1.0.0
**Tutorial Difficulty**: Beginner
