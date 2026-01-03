# MDSA Framework - Comprehensive User Guide

## Table of Contents
1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Creating Domains](#creating-domains)
4. [Adding Models to Domains](#adding-models-to-domains)
5. [Creating Agents](#creating-agents)
6. [System Prompts](#system-prompts)
7. [Connecting Agents](#connecting-agents)
8. [Tools Integration](#tools-integration)
9. [MCP Integration](#mcp-integration)
10. [API Integration](#api-integration)
11. [Guardrails](#guardrails)
12. [RAG Configuration](#rag-configuration)
13. [Complete Examples](#complete-examples)

---

## 1. Installation

### Prerequisites
- Python 3.8+
- 4GB+ RAM
- Optional: NVIDIA GPU with 3GB+ VRAM

### Install from PyPI
```bash
pip install mdsa-framework
```

### Install from Source
```bash
git clone https://github.com/yourusername/mdsa.git
cd mdsa
pip install -e .
```

### Verify Installation
```python
from mdsa import ModelManager
print("MDSA installed successfully!")
```

---

## 2. Quick Start

### Hello World Example

```python
from mdsa import ModelManager, DomainExecutor, DomainConfig

# Step 1: Create model manager
manager = ModelManager(max_models=2)

# Step 2: Create domain executor
executor = DomainExecutor(manager)

# Step 3: Define a domain
domain = DomainConfig(
    domain_id="general",
    name="General Assistant",
    description="General purpose AI assistant",
    keywords=["help", "question", "what", "how"],
    model_name="gpt2",  # Any HuggingFace model
    system_prompt="You are a helpful AI assistant."
)

# Step 4: Execute a query
result = executor.execute("What is machine learning?", domain)

print(f"Response: {result['response']}")
print(f"Latency: {result['latency_ms']}ms")
print(f"Confidence: {result['confidence']}")
```

**Expected Output:**
```
Response: Machine learning is a type of artificial intelligence that allows computers to learn from data...
Latency: 152.3ms
Confidence: 0.95
```

---

## 3. Creating Domains

### What is a Domain?

A domain represents a specialized area of knowledge or functionality. Each domain has:
- **Unique ID**: Identifier
- **Name**: Human-readable name
- **Description**: What the domain does
- **Keywords**: Trigger words for routing
- **Model**: Assigned LLM
- **System Prompt**: Behavior instructions
- **Configuration**: Temperature, max tokens, etc.

### Domain Configuration

```python
from mdsa.domains import DomainConfig

# Finance Domain
finance_domain = DomainConfig(
    domain_id="finance",
    name="Financial Advisor",
    description="Expert in financial planning and investment",
    keywords=[
        "money", "finance", "investment", "stock", "portfolio",
        "savings", "budget", "401k", "retirement", "tax"
    ],
    model_name="gpt2",  # or "llama3.2:3b" for Ollama
    system_prompt="""You are an expert financial advisor with 20 years of experience.
    Provide accurate, conservative financial advice. Always mention risks.
    Use simple language and explain complex concepts clearly.""",
    max_tokens=200,
    temperature=0.5,  # Lower = more conservative
    top_p=0.9
)

# Medical Domain
medical_domain = DomainConfig(
    domain_id="medical",
    name="Medical Assistant",
    description="Medical information and health advice",
    keywords=[
        "health", "medical", "doctor", "symptom", "disease",
        "medicine", "treatment", "diagnosis", "pain", "sick"
    ],
    model_name="phi3:mini",  # Different model for medical domain
    system_prompt="""You are a medical information assistant.
    Provide accurate health information but ALWAYS recommend consulting
    a real doctor. Never diagnose. Be empathetic and clear.""",
    max_tokens=250,
    temperature=0.3  # Very low for medical accuracy
)

# Technical Support Domain
tech_domain = DomainConfig(
    domain_id="technical",
    name="Tech Support",
    description="Software and hardware troubleshooting",
    keywords=[
        "code", "programming", "error", "bug", "install",
        "debug", "software", "computer", "crash", "fix"
    ],
    model_name="qwen2.5:3b-instruct",
    system_prompt="""You are a senior software engineer.
    Provide clear, step-by-step solutions. Include code examples.
    Explain technical concepts simply.""",
    max_tokens=300,
    temperature=0.7
)
```

### Using Pre-Built Domains

```python
from mdsa.domains import create_finance_domain, create_medical_domain

# Use factory functions
finance = create_finance_domain()
medical = create_medical_domain()
```

---

## 4. Adding Models to Domains

### Supported Models

**HuggingFace Models:**
- `gpt2` (124M params) - Fast, good for testing
- `microsoft/phi-2` (2.7B params) - Balanced
- `microsoft/phi-3` (3.8B params) - High quality
- Any model on HuggingFace Hub

**Ollama Models:**
- `llama3.2:1b` - Ultra fast
- `llama3.2:3b` - Balanced
- `phi3:mini` - Efficient
- `qwen2.5:3b-instruct` - Instruction-tuned
- Any Ollama model installed locally

### Assigning Models to Domains

```python
# Method 1: Direct assignment in DomainConfig
domain = DomainConfig(
    domain_id="my_domain",
    model_name="llama3.2:3b",  # Assign specific model
    # ... other config
)

# Method 2: Change model for existing domain
domain.model_name = "phi3:mini"

# Method 3: Use tier-based configs
from mdsa.models import ModelConfig

# Tier 1: Fast, small models (GPT-2)
tier1_config = ModelConfig.for_tier1()

# Tier 2: Medium models (3B params)
tier2_config = ModelConfig.for_tier2()

# Tier 3: Large models (7B+ params)
tier3_config = ModelConfig.for_tier3()
```

### Multi-Model Setup

```python
# Different models for different domains
domains = {
    'finance': DomainConfig(
        domain_id="finance",
        model_name="llama3.2:3b",  # Larger for complex reasoning
        # ...
    ),
    'casual': DomainConfig(
        domain_id="casual",
        model_name="gpt2",  # Smaller for simple chat
        # ...
    ),
    'technical': DomainConfig(
        domain_id="technical",
        model_name="qwen2.5:3b-instruct",  # Instruction-tuned
        # ...
    )
}
```

---

## 5. Creating Agents

### What is an Agent?

An agent is a domain with additional capabilities:
- **Personality**: Unique character and tone
- **Memory**: Conversation history
- **Tools**: Function calling
- **State**: Persistent information

### Basic Agent

```python
from mdsa import DomainConfig, DomainExecutor, ModelManager

class Agent:
    """Base agent with personality and memory."""

    def __init__(self, domain_config: DomainConfig):
        self.config = domain_config
        self.memory = []  # Conversation history
        self.state = {}   # Agent state

        # Setup executor
        self.manager = ModelManager()
        self.executor = DomainExecutor(self.manager)

    def chat(self, message: str) -> str:
        """Chat with agent."""
        # Add to memory
        self.memory.append({"role": "user", "content": message})

        # Build context from memory
        context = self._build_context()

        # Execute with context
        result = self.executor.execute(context, self.config)
        response = result['response']

        # Add response to memory
        self.memory.append({"role": "assistant", "content": response})

        return response

    def _build_context(self) -> str:
        """Build context from conversation history."""
        # Last 5 messages
        recent = self.memory[-5:]
        return "\n".join([f"{m['role']}: {m['content']}" for m in recent])
```

### Agent with Personality

```python
# Financial Advisor Agent
financial_advisor = Agent(DomainConfig(
    domain_id="financial_advisor",
    name="Warren (Financial Advisor)",
    description="Conservative financial advisor",
    keywords=["money", "invest", "save", "budget"],
    model_name="llama3.2:3b",
    system_prompt="""You are Warren, a conservative financial advisor.
    Personality traits:
    - Patient and thorough
    - Risk-averse
    - Uses simple analogies
    - Always mentions downsides
    - Speaks in a fatherly tone

    Your goal: Help people make smart, safe financial decisions.""",
    temperature=0.6
))

# Technical Support Agent
tech_guru = Agent(DomainConfig(
    domain_id="tech_guru",
    name="Alex (Tech Guru)",
    description="Enthusiastic tech expert",
    keywords=["code", "bug", "error", "debug"],
    model_name="qwen2.5:3b-instruct",
    system_prompt="""You are Alex, an enthusiastic software engineer.
    Personality traits:
    - Excited about technology
    - Uses developer jargon (but explains it)
    - Loves solving problems
    - Provides code examples
    - Encouraging and supportive

    Your goal: Make coding fun and accessible.""",
    temperature=0.8  # Higher for more creativity
))
```

### Using Agents

```python
# Financial advice conversation
print(financial_advisor.chat("Should I invest in crypto?"))
print(financial_advisor.chat("What about stocks?"))
print(financial_advisor.chat("Thanks for the advice!"))

# Technical support conversation
print(tech_guru.chat("My Python script has an import error"))
print(tech_guru.chat("Here's the error: ModuleNotFoundError"))
print(tech_guru.chat("Thanks, that fixed it!"))
```

---

## 6. System Prompts

### Anatomy of a Good System Prompt

```python
system_prompt = """
[WHO YOU ARE]
You are Dr. Emily, a board-certified physician with 15 years of experience.

[YOUR EXPERTISE]
Specialties:
- Internal medicine
- Patient education
- Preventive care

[YOUR PERSONALITY]
Traits:
- Empathetic and patient
- Clear communicator
- Evidence-based
- Warm but professional

[YOUR CONSTRAINTS]
Important:
- Never diagnose or prescribe
- Always recommend seeing a real doctor
- Explain medical terms
- Be reassuring but realistic

[YOUR GOAL]
Help patients understand their health while emphasizing the importance
of professional medical care.
"""
```

### System Prompt Templates

**For Expert Domains (Finance, Medical, Legal):**
```python
expert_prompt = """You are {name}, a {credentials} with {experience}.

Expertise: {specialties}

Communication Style:
- {tone} and {manner}
- Use {language_level} language
- {additional_style_notes}

Constraints:
- {limitation_1}
- {limitation_2}
- {safety_note}

Goal: {primary_objective}
"""
```

**For Creative Domains (Writing, Art, Music):**
```python
creative_prompt = """You are {name}, an award-winning {profession}.

Creative Style:
- {style_descriptor_1}
- {style_descriptor_2}
- {unique_characteristic}

Approach:
- {method_1}
- {method_2}

Goal: {creative_objective}
"""
```

**For Technical Domains (Programming, Engineering):**
```python
technical_prompt = """You are {name}, a senior {role}.

Technical Expertise:
- {tech_stack_1}
- {tech_stack_2}
- {years_experience} of experience

Problem-Solving Approach:
1. {step_1}
2. {step_2}
3. {step_3}

Communication:
- Provide code examples
- Explain technical concepts clearly
- Suggest best practices

Goal: {technical_objective}
"""
```

---

## 7. Connecting Agents

### Agent Communication

```python
class MultiAgentSystem:
    """System for connecting multiple agents."""

    def __init__(self):
        self.agents = {}
        self.manager = ModelManager(max_models=5)

    def add_agent(self, agent_id: str, domain_config: DomainConfig):
        """Add agent to system."""
        agent = Agent(domain_config)
        agent.manager = self.manager  # Share model manager
        self.agents[agent_id] = agent

    def route_query(self, query: str) -> str:
        """Route query to appropriate agent."""
        # Simple keyword-based routing
        query_lower = query.lower()

        for agent_id, agent in self.agents.items():
            if any(kw in query_lower for kw in agent.config.keywords):
                return agent.chat(query)

        # Default to general agent
        return self.agents.get('general', list(self.agents.values())[0]).chat(query)

    def agent_collaboration(self, query: str, agent_ids: list) -> str:
        """Multiple agents collaborate on a query."""
        responses = []

        for agent_id in agent_ids:
            agent = self.agents[agent_id]
            response = agent.chat(query)
            responses.append(f"{agent.config.name}: {response}")

        # Combine responses
        combined = "\n\n".join(responses)
        return combined
```

### Example: Multi-Agent System

```python
# Create system
system = MultiAgentSystem()

# Add agents
system.add_agent('finance', DomainConfig(
    domain_id="finance",
    name="Financial Advisor",
    keywords=["money", "invest", "savings"],
    model_name="llama3.2:3b",
    system_prompt="You are a financial advisor..."
))

system.add_agent('legal', DomainConfig(
    domain_id="legal",
    name="Legal Consultant",
    keywords=["law", "legal", "contract", "rights"],
    model_name="phi3:mini",
    system_prompt="You are a legal consultant..."
))

system.add_agent('tax', DomainConfig(
    domain_id="tax",
    name="Tax Specialist",
    keywords=["tax", "deduction", "IRS", "filing"],
    model_name="qwen2.5:3b-instruct",
    system_prompt="You are a tax specialist..."
))

# Use system
query = "I'm starting a business. What should I know about taxes?"

# Option 1: Auto-route to single agent
response = system.route_query(query)

# Option 2: Get input from multiple agents
collaborative_response = system.agent_collaboration(
    query,
    agent_ids=['finance', 'legal', 'tax']
)
```

---

## 8. Tools Integration

### Built-in Tools

MDSA includes 8 built-in tools:
1. `get_current_time` - Get current time
2. `calculate` - Math calculations
3. `search_web` - Web search (simulated)
4. `get_weather` - Weather info (simulated)
5. `word_count` - Count words in text
6. `extract_urls` - Extract URLs from text
7. `convert_units` - Unit conversion
8. `generate_uuid` - Generate unique ID

### Using Tools

```python
from mdsa.tools import ToolRegistry

# Create tool registry
tools = ToolRegistry()

# List available tools
print(tools.get_available_tools())

# Execute a tool
result = tools.execute_tool('calculate', '25 * 4')
print(result)  # "100"

result = tools.execute_tool('get_current_time')
print(result)  # "2024-01-15 10:30:00"
```

### Tool-Enabled Agent

```python
from mdsa.tools import ToolRegistry

class ToolAgent(Agent):
    """Agent with tool calling capabilities."""

    def __init__(self, domain_config: DomainConfig):
        super().__init__(domain_config)
        self.tools = ToolRegistry()

    def chat(self, message: str) -> str:
        """Chat with tool calling."""
        # Add tools to context
        tools_info = self.tools.format_tools_for_prompt()
        context = f"{tools_info}\n\nUser: {message}"

        # Execute
        result = self.executor.execute(context, self.config)
        response = result['response']

        # Check for tool calls in response
        tool_result = self.tools.parse_and_execute(response)
        if tool_result:
            response += f"\n\n[Tool Result]: {tool_result}"

        return response
```

### Custom Tools

```python
from mdsa.tools import Tool

# Define custom tool
def search_database(query: str) -> str:
    """Search internal database."""
    # Your database search logic
    return f"Found 5 results for: {query}"

# Register custom tool
custom_tool = Tool(
    name="search_database",
    description="Search internal company database",
    function=search_database
)

tools.register_tool(custom_tool)

# Now available to agents
result = tools.execute_tool('search_database', 'customer orders')
```

---

## 9. MCP Integration

### What is MCP?

MCP (Model Context Protocol) allows external tools and data sources to be accessed by LLMs.

### Setting Up MCP Server

```python
# Install MCP dependencies
# pip install mcp

from mdsa.integrations import MCPServer

# Create MCP server
mcp = MCPServer(port=8080)

# Register resources
mcp.register_resource(
    name="company_data",
    uri="db://company/sales",
    description="Sales data"
)

# Start server
mcp.start()
```

### Using MCP in Agents

```python
from mdsa.integrations import MCPClient

# Create MCP client
mcp_client = MCPClient(server_url="http://localhost:8080")

# Agent with MCP access
class MCPAgent(Agent):
    def __init__(self, domain_config):
        super().__init__(domain_config)
        self.mcp = MCPClient()

    def chat_with_data(self, message: str) -> str:
        """Chat with access to MCP resources."""
        # Fetch relevant data from MCP
        if "sales" in message.lower():
            data = self.mcp.fetch_resource("company_data")
            context = f"Sales Data: {data}\n\nUser Query: {message}"
        else:
            context = message

        return self.chat(context)
```

---

## 10. API Integration

### RESTful API

```python
from flask import Flask, request, jsonify
from mdsa import ModelManager, DomainExecutor

app = Flask(__name__)
manager = ModelManager()
executor = DomainExecutor(manager)

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat endpoint."""
    data = request.json
    query = data.get('query')
    domain_id = data.get('domain', 'general')

    # Get domain config
    domain = get_domain_config(domain_id)

    # Execute
    result = executor.execute(query, domain)

    return jsonify({
        'response': result['response'],
        'confidence': result['confidence'],
        'latency_ms': result['latency_ms']
    })

@app.route('/api/domains', methods=['GET'])
def list_domains():
    """List available domains."""
    return jsonify({
        'domains': ['general', 'finance', 'medical', 'technical']
    })

if __name__ == '__main__':
    app.run(port=5000)
```

### API Usage

```bash
# Chat request
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is AI?", "domain": "general"}'

# List domains
curl http://localhost:5000/api/domains
```

---

## 11. Guardrails

### Input Validation

```python
from mdsa.validation import InputValidator

class SafeAgent(Agent):
    """Agent with input/output guardrails."""

    def __init__(self, domain_config):
        super().__init__(domain_config)
        self.validator = InputValidator()

    def chat(self, message: str) -> str:
        """Chat with guardrails."""
        # Validate input
        if not self.validator.is_safe_input(message):
            return "I cannot process that request. Please rephrase."

        # Execute
        response = super().chat(message)

        # Validate output
        if not self.validator.is_safe_output(response):
            return "I apologize, but I cannot provide that information."

        return response
```

### Content Filtering

```python
from mdsa.validation import ContentFilter

filter = ContentFilter()

# Check for harmful content
if filter.contains_harmful_content(text):
    # Block or sanitize

# Check for PII
if filter.contains_pii(text):
    # Redact or warn

# Check for profanity
if filter.contains_profanity(text):
    # Filter or reject
```

---

## 12. RAG Configuration

### Local RAG (Per-Domain)

```python
from mdsa.rag import RAGEngine

# Create RAG for finance domain
finance_rag = RAGEngine(
    collection_name="finance_kb",
    persist_directory="./rag_finance"
)

# Add documents
finance_rag.add_documents(
    documents=["Financial planning guide...", "Investment strategies..."],
    metadatas=[{"source": "guide"}, {"source": "strategies"}]
)

# Use in agent
class RAGAgent(Agent):
    def __init__(self, domain_config, rag_engine):
        super().__init__(domain_config)
        self.rag = rag_engine

    def chat(self, message: str) -> str:
        """Chat with RAG enhancement."""
        # Get relevant context
        context = self.rag.get_context(message, n_results=3)

        # Enhance query
        enhanced = f"Context: {context}\n\nQuestion: {message}"

        return super().chat(enhanced)
```

### Global RAG (Shared Knowledge)

```python
# Shared knowledge base for all agents
global_rag = RAGEngine(
    collection_name="global_kb",
    persist_directory="./rag_global"
)

# Add company-wide documents
global_rag.add_directory("./knowledge_base/")

# All agents access global RAG
finance_agent = RAGAgent(finance_config, global_rag)
medical_agent = RAGAgent(medical_config, global_rag)
```

---

## 13. Complete Examples

### Example 1: Simple Chatbot

```python
from mdsa import ModelManager, DomainExecutor, DomainConfig

manager = ModelManager()
executor = DomainExecutor(manager)

domain = DomainConfig(
    domain_id="chatbot",
    name="Friendly Chatbot",
    model_name="gpt2",
    system_prompt="You are a friendly chatbot."
)

while True:
    query = input("You: ")
    if query == "quit":
        break

    result = executor.execute(query, domain)
    print(f"Bot: {result['response']}")
```

### Example 2: Multi-Domain Assistant

```python
from mdsa import ModelManager, DomainExecutor, DomainRegistry

# Setup
manager = ModelManager(max_models=3)
registry = DomainRegistry()
executor = DomainExecutor(manager)

# Register domains
registry.register(create_finance_domain())
registry.register(create_medical_domain())
registry.register(create_technical_domain())

# Auto-route queries
def chat(query: str):
    domain = registry.select_domain(query)
    result = executor.execute(query, domain)
    return result['response']

# Use
print(chat("How should I invest $10,000?"))  # Routes to finance
print(chat("I have a headache"))  # Routes to medical
print(chat("Python import error"))  # Routes to technical
```

### Example 3: RAG-Powered Q&A

```python
from mdsa.rag import RAGEngine

# Create RAG
rag = RAGEngine("company_kb")
rag.add_directory("./company_docs/")

# RAG-powered agent
agent = RAGAgent(
    DomainConfig(
        domain_id="company_qa",
        name="Company Q&A",
        model_name="llama3.2:3b",
        system_prompt="Answer questions using company knowledge."
    ),
    rag_engine=rag
)

# Ask questions
print(agent.chat("What is our return policy?"))
print(agent.chat("How do I file a warranty claim?"))
```

### Example 4: Tool-Calling Agent

```python
# Tool-enabled assistant
assistant = ToolAgent(DomainConfig(
    domain_id="assistant",
    name="Smart Assistant",
    model_name="qwen2.5:3b-instruct",
    system_prompt="""You are a helpful assistant with access to tools.
    Use tools when appropriate."""
))

# Conversations with tool usage
print(assistant.chat("What time is it?"))
# Uses get_current_time tool

print(assistant.chat("Calculate 157 * 23"))
# Uses calculate tool

print(assistant.chat("Count words in: Hello world, this is MDSA"))
# Uses word_count tool
```

---

## Next Steps

1. **Explore Examples**: Try the example applications in `examples/`
2. **Read API Reference**: See detailed API documentation
3. **Join Community**: GitHub discussions and Discord
4. **Contribute**: Add domains, tools, or improvements

**Happy Building with MDSA!** 🚀
