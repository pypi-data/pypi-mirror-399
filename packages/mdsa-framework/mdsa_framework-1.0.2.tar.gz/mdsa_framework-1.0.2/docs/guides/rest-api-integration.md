# REST API Integration Guide

**Version**: 1.0.0
**Last Updated**: December 2025

This guide explains how to integrate MDSA Framework into your applications using the REST API. You'll learn how to make HTTP requests to MDSA, handle responses, and implement common integration patterns.

---

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [API Endpoints](#api-endpoints)
4. [Request Format](#request-format)
5. [Response Format](#response-format)
6. [Authentication](#authentication)
7. [Client Examples](#client-examples)
8. [Integration Patterns](#integration-patterns)
9. [Error Handling](#error-handling)
10. [Rate Limiting](#rate-limiting)
11. [Best Practices](#best-practices)
12. [Troubleshooting](#troubleshooting)

---

## Overview

The MDSA REST API allows you to:

- Submit queries for domain-specific processing
- Retrieve domain classifications
- Access knowledge base information
- Monitor request status and performance
- Configure runtime settings

**Base URL**: `http://localhost:9000/api/v1`

**Supported Methods**: GET, POST, PUT, DELETE

**Data Format**: JSON

**Authentication**: API Key (optional) or Basic Auth

---

## Getting Started

### Prerequisites

- MDSA Framework installed and running
- Dashboard enabled in configuration
- Basic HTTP client (curl, Postman, or programming language HTTP library)

### Enable API Access

Edit `mdsa_config.yaml`:

```yaml
dashboard:
  enabled: true
  host: 0.0.0.0  # Listen on all interfaces
  port: 9000
  api:
    enabled: true
    cors_enabled: true  # Allow cross-origin requests
    rate_limit: 100  # requests per minute
```

Restart MDSA to apply changes:

```bash
python -m mdsa.ui.dashboard.app
```

### Verify API is Accessible

```bash
curl http://localhost:9000/api/v1/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": 3600,
  "timestamp": "2025-12-25T10:30:00Z"
}
```

---

## API Endpoints

### Core Endpoints

#### 1. Health Check

**GET** `/api/v1/health`

Check if MDSA is running and responsive.

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": 3600,
  "domains": 3,
  "cached_responses": 45
}
```

---

#### 2. Query Processing

**POST** `/api/v1/query`

Submit a query for processing.

**Request Body**:
```json
{
  "query": "What are symptoms of diabetes?",
  "domain": null,  // Optional: force specific domain
  "context": {},  // Optional: additional context
  "options": {
    "use_cache": true,
    "include_sources": true,
    "max_tokens": 1024
  }
}
```

**Response**:
```json
{
  "request_id": "req_abc123",
  "query": "What are symptoms of diabetes?",
  "response": {
    "text": "Common symptoms of diabetes include...",
    "domain": "clinical_diagnosis",
    "confidence": 0.94,
    "sources": [
      {
        "document": "diabetes_overview.txt",
        "chunk": "Symptoms of diabetes...",
        "relevance": 0.89
      }
    ]
  },
  "performance": {
    "latency_ms": 625,
    "cached": false,
    "classification_ms": 45,
    "rag_retrieval_ms": 60,
    "inference_ms": 520
  },
  "timestamp": "2025-12-25T10:30:00Z"
}
```

---

#### 3. Domain Classification Only

**POST** `/api/v1/classify`

Classify query without generating response (useful for routing decisions).

**Request Body**:
```json
{
  "query": "How do I reset my password?"
}
```

**Response**:
```json
{
  "query": "How do I reset my password?",
  "domain": "technical_support",
  "confidence": 0.92,
  "all_scores": {
    "technical_support": 0.92,
    "billing": 0.05,
    "general": 0.03
  },
  "latency_ms": 38
}
```

---

#### 4. List Domains

**GET** `/api/v1/domains`

Retrieve all configured domains.

**Response**:
```json
{
  "domains": [
    {
      "name": "technical_support",
      "description": "Technical issues and troubleshooting",
      "model": "deepseek-v3.1",
      "kb_documents": 42,
      "total_queries": 1250
    },
    {
      "name": "billing",
      "description": "Billing and payment questions",
      "model": "deepseek-v3.1",
      "kb_documents": 28,
      "total_queries": 687
    }
  ]
}
```

---

#### 5. Get Domain Details

**GET** `/api/v1/domains/{domain_name}`

Get detailed information about a specific domain.

**Response**:
```json
{
  "name": "technical_support",
  "description": "Technical issues and troubleshooting",
  "model": "deepseek-v3.1",
  "kb_path": "knowledge_base/technical/",
  "kb_documents": 42,
  "configuration": {
    "temperature": 0.3,
    "max_tokens": 1024,
    "system_prompt": "You are a technical support specialist..."
  },
  "statistics": {
    "total_queries": 1250,
    "avg_latency_ms": 580,
    "cache_hit_rate": 0.65
  }
}
```

---

#### 6. Get Request Status

**GET** `/api/v1/requests/{request_id}`

Track status of a specific request.

**Response**:
```json
{
  "request_id": "req_abc123",
  "status": "completed",  // or "processing", "failed"
  "query": "What are symptoms of diabetes?",
  "domain": "clinical_diagnosis",
  "created_at": "2025-12-25T10:30:00Z",
  "completed_at": "2025-12-25T10:30:01Z",
  "latency_ms": 625
}
```

---

#### 7. Metrics and Analytics

**GET** `/api/v1/metrics`

Retrieve system performance metrics.

**Query Parameters**:
- `period`: Time period (hour, day, week, month)
- `domain`: Filter by specific domain

**Response**:
```json
{
  "period": "day",
  "total_requests": 3542,
  "avg_latency_ms": 612,
  "cache_hit_rate": 0.68,
  "domains": {
    "technical_support": {
      "requests": 1250,
      "avg_latency_ms": 580
    },
    "billing": {
      "requests": 687,
      "avg_latency_ms": 490
    }
  },
  "latency_percentiles": {
    "p50": 520,
    "p95": 1200,
    "p99": 2100
  }
}
```

---

## Request Format

### Headers

All requests should include:

```
Content-Type: application/json
Accept: application/json
X-API-Key: your-api-key-here  (if authentication enabled)
```

### Request Body Structure

**Query Request**:
```json
{
  "query": "string (required)",
  "domain": "string (optional)",
  "context": {
    "user_id": "string",
    "session_id": "string",
    "metadata": {}
  },
  "options": {
    "use_cache": true,
    "include_sources": true,
    "max_tokens": 1024,
    "temperature": 0.7,
    "stream": false
  }
}
```

**Field Descriptions**:

- **query** (required): User's question or request
- **domain** (optional): Force specific domain (skip classification)
- **context** (optional): Additional context for personalization
- **options** (optional): Override default processing options

---

## Response Format

### Success Response

```json
{
  "request_id": "string",
  "query": "string",
  "response": {
    "text": "string",
    "domain": "string",
    "confidence": 0.0-1.0,
    "sources": []
  },
  "performance": {
    "latency_ms": 0,
    "cached": false
  },
  "timestamp": "ISO8601"
}
```

### Error Response

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "Additional error context"
    }
  },
  "request_id": "string",
  "timestamp": "ISO8601"
}
```

**Common Error Codes**:

- `INVALID_REQUEST`: Malformed request body
- `MISSING_FIELD`: Required field not provided
- `DOMAIN_NOT_FOUND`: Specified domain doesn't exist
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INTERNAL_ERROR`: Server-side error
- `UNAUTHORIZED`: Invalid API key

---

## Authentication

MDSA supports multiple authentication methods:

### 1. API Key Authentication (Recommended)

**Generate API Key**:
```bash
python -m mdsa.tools.generate_api_key
# Output: mdsa_1a2b3c4d5e6f7g8h9i0j
```

**Configure**:
```yaml
dashboard:
  api:
    auth_enabled: true
    api_keys:
      - key: mdsa_1a2b3c4d5e6f7g8h9i0j
        name: Production App
        rate_limit: 1000  # per hour
```

**Usage**:
```bash
curl -H "X-API-Key: mdsa_1a2b3c4d5e6f7g8h9i0j" \
     http://localhost:9000/api/v1/query \
     -d '{"query": "test"}'
```

### 2. Basic Authentication

**Configure**:
```yaml
dashboard:
  auth:
    enabled: true
    username: admin
    password: ${API_PASSWORD}
```

**Usage**:
```bash
curl -u admin:password \
     http://localhost:9000/api/v1/query \
     -d '{"query": "test"}'
```

### 3. No Authentication (Development Only)

```yaml
dashboard:
  api:
    auth_enabled: false  # Not recommended for production
```

---

## Client Examples

### Python (requests library)

```python
import requests
import json

# Configuration
API_URL = "http://localhost:9000/api/v1"
API_KEY = "mdsa_1a2b3c4d5e6f7g8h9i0j"

# Headers
headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

# Submit query
def query_mdsa(query_text):
    payload = {
        "query": query_text,
        "options": {
            "use_cache": True,
            "include_sources": True
        }
    }

    response = requests.post(
        f"{API_URL}/query",
        headers=headers,
        json=payload
    )

    if response.status_code == 200:
        data = response.json()
        return data["response"]["text"]
    else:
        raise Exception(f"API Error: {response.text}")

# Usage
result = query_mdsa("What are the symptoms of diabetes?")
print(result)
```

### JavaScript (fetch API)

```javascript
const API_URL = "http://localhost:9000/api/v1";
const API_KEY = "mdsa_1a2b3c4d5e6f7g8h9i0j";

async function queryMDSA(query) {
  const response = await fetch(`${API_URL}/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY
    },
    body: JSON.stringify({
      query: query,
      options: {
        use_cache: true,
        include_sources: true
      }
    })
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.statusText}`);
  }

  const data = await response.json();
  return data.response.text;
}

// Usage
queryMDSA("What are the symptoms of diabetes?")
  .then(result => console.log(result))
  .catch(error => console.error(error));
```

### cURL

```bash
curl -X POST http://localhost:9000/api/v1/query \
  -H "Content-Type: application/json" \
  -H "X-API-Key: mdsa_1a2b3c4d5e6f7g8h9i0j" \
  -d '{
    "query": "What are the symptoms of diabetes?",
    "options": {
      "use_cache": true,
      "include_sources": true
    }
  }'
```

### Java (HttpClient)

```java
import java.net.http.*;
import java.net.URI;
import com.google.gson.Gson;

public class MDSAClient {
    private static final String API_URL = "http://localhost:9000/api/v1";
    private static final String API_KEY = "mdsa_1a2b3c4d5e6f7g8h9i0j";

    public static String queryMDSA(String query) throws Exception {
        HttpClient client = HttpClient.newHttpClient();

        String json = new Gson().toJson(Map.of(
            "query", query,
            "options", Map.of(
                "use_cache", true,
                "include_sources", true
            )
        ));

        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(API_URL + "/query"))
            .header("Content-Type", "application/json")
            .header("X-API-Key", API_KEY)
            .POST(HttpRequest.BodyPublishers.ofString(json))
            .build();

        HttpResponse<String> response = client.send(
            request,
            HttpResponse.BodyHandlers.ofString()
        );

        if (response.statusCode() == 200) {
            Map result = new Gson().fromJson(
                response.body(),
                Map.class
            );
            return (String) ((Map) result.get("response")).get("text");
        } else {
            throw new Exception("API Error: " + response.body());
        }
    }
}
```

---

## Integration Patterns

### Pattern 1: Simple Query-Response

Use for basic chatbot or Q&A integration:

```python
def handle_user_query(user_input):
    response = requests.post(
        f"{API_URL}/query",
        headers=headers,
        json={"query": user_input}
    )
    return response.json()["response"]["text"]
```

### Pattern 2: Classification-Based Routing

Use MDSA for classification, handle responses in your app:

```python
def route_user_query(user_input):
    # Get domain classification
    classification = requests.post(
        f"{API_URL}/classify",
        headers=headers,
        json={"query": user_input}
    ).json()

    domain = classification["domain"]
    confidence = classification["confidence"]

    # Route based on domain
    if domain == "technical_support" and confidence > 0.8:
        return handle_technical_query(user_input)
    elif domain == "billing":
        return handle_billing_query(user_input)
    else:
        return handle_general_query(user_input)
```

### Pattern 3: Async Processing

For long-running queries:

```python
import time

def async_query(user_input):
    # Submit query
    response = requests.post(
        f"{API_URL}/query",
        headers=headers,
        json={
            "query": user_input,
            "options": {"async": True}
        }
    )

    request_id = response.json()["request_id"]

    # Poll for completion
    while True:
        status = requests.get(
            f"{API_URL}/requests/{request_id}",
            headers=headers
        ).json()

        if status["status"] == "completed":
            return status["response"]["text"]
        elif status["status"] == "failed":
            raise Exception(status["error"])

        time.sleep(1)  # Wait 1 second before polling again
```

### Pattern 4: Batch Processing

Process multiple queries efficiently:

```python
def batch_query(queries):
    results = []
    for query in queries:
        response = requests.post(
            f"{API_URL}/query",
            headers=headers,
            json={"query": query}
        )
        results.append(response.json())
    return results
```

---

## Error Handling

### Retry Logic

```python
import time
from requests.exceptions import RequestException

def query_with_retry(query, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{API_URL}/query",
                headers=headers,
                json={"query": query},
                timeout=30
            )
            response.raise_for_status()
            return response.json()

        except RequestException as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt  # Exponential backoff
            time.sleep(wait_time)
```

### Timeout Handling

```python
try:
    response = requests.post(
        f"{API_URL}/query",
        headers=headers,
        json={"query": query},
        timeout=30  # 30 second timeout
    )
except requests.Timeout:
    print("Request timed out. MDSA may be overloaded.")
```

---

## Rate Limiting

MDSA enforces rate limits to prevent abuse:

### Rate Limit Headers

Response includes:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
```

### Handle Rate Limit Errors

```python
response = requests.post(...)

if response.status_code == 429:  # Too Many Requests
    reset_time = int(response.headers["X-RateLimit-Reset"])
    wait_seconds = reset_time - time.time()
    print(f"Rate limited. Retry in {wait_seconds} seconds")
```

---

## Best Practices

1. **Always use HTTPS in production** - Encrypt API communication
2. **Store API keys securely** - Use environment variables, not code
3. **Implement retry logic** - Handle transient network failures
4. **Cache responses client-side** - Reduce API calls
5. **Use batch requests** - When processing multiple queries
6. **Monitor rate limits** - Track usage to avoid hitting limits
7. **Handle errors gracefully** - Provide fallback responses
8. **Log requests for debugging** - Include request_id for tracing

---

## Troubleshooting

### Connection Refused

**Cause**: MDSA dashboard not running
**Solution**: Start dashboard with `python -m mdsa.ui.dashboard.app`

### 401 Unauthorized

**Cause**: Invalid or missing API key
**Solution**: Check X-API-Key header matches configured key

### 429 Rate Limit Exceeded

**Cause**: Too many requests
**Solution**: Implement backoff and respect rate limit headers

### 500 Internal Server Error

**Cause**: MDSA encountered an error
**Solution**: Check MDSA logs for details, report issue with request_id

---

## Additional Resources

- **[User Guide](../USER_GUIDE.md)** - Complete MDSA feature documentation
- **[API Reference](../FRAMEWORK_REFERENCE.md)** - Detailed API documentation
- **[First Application Tutorial](../getting-started/first-application.md)** - Building your first MDSA app
- **[Examples](../../examples/)** - Working example applications

---

**Need Help?**
- GitHub Issues: https://github.com/your-org/mdsa-framework/issues
- Documentation: https://docs.mdsa-framework.com
- API Status: https://status.mdsa-framework.com

**Last Updated**: December 2025
**Version**: 1.0.0
