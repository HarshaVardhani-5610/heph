# 🔑 Perplexity API Key Rotation System

A robust, production-ready API key rotation system for Perplexity AI that automatically handles failover when credits are exhausted. Supports up to 10 API keys with intelligent rotation and comprehensive error handling.

## 🚀 Features

- **Automatic Rotation**: Seamlessly switches to the next available API key when one runs out of credits
- **10 Key Slots**: Supports up to 10 API keys with graceful handling of empty slots
- **Smart Error Handling**: Distinguishes between exhausted credits, rate limits, and other errors
- **Persistent Configuration**: Maintains key status across application restarts
- **24-Hour Retry Logic**: Automatically retries exhausted keys after cooldown period
- **Zero-Downtime Failover**: No interruption in service when keys fail
- **Production Ready**: Comprehensive logging, error tracking, and status monitoring

## 📦 Installation & Setup

### 1. Configure API Keys

**Option A: Using Environment Variables**
```bash
export PERPLEXITY_API_KEY_1="your_first_key_here"
export PERPLEXITY_API_KEY_2="your_second_key_here"
export PERPLEXITY_API_KEY_3="your_third_key_here"
# ... up to PERPLEXITY_API_KEY_10
```

**Option B: Using .env File**
```bash
# Copy the template
cp .env.template .env

# Edit .env with your actual API keys
nano .env

# Source the environment
source .env
```

**Option C: Interactive Setup**
```bash
# Run the interactive setup script
./setup_api_keys.sh
```

### 2. Install Dependencies

```bash
pip install httpx pydantic fastapi uvicorn
```

## 🔧 Usage

### Basic Usage

```python
from api_key_manager import call_perplexity_api

# Simple API call with automatic rotation
response = await call_perplexity_api(
    "What is the latest version of Python?",
    max_tokens=1000,
    temperature=0.2
)

print(response)
```

### Advanced Usage

```python
from api_key_manager import PerplexityAPIManager

# Initialize manager
manager = PerplexityAPIManager()

# Check status of all keys
status = manager.get_status()
print(f"Active keys: {status['active_keys']}/{status['total_keys']}")

# Make API call with custom parameters
response = await manager.make_api_call(
    "Explain FastAPI microservices",
    model="llama-3.1-sonar-large-128k-online",
    max_tokens=2000,
    temperature=0.1,
    return_citations=True
)

# Reset a key if needed
manager.reset_key_status("key_1")
```

### Integration with Agent Factory

The system is fully integrated with the Agent Factory FastAPI service:

```python
# All endpoints now use Perplexity API with automatic rotation
# /refine_prompt - Uses API for prompt refinement
# /feasibility - Uses API for technical analysis  
# /optimize_prompt - Uses API for architectural specifications
# /generate_code - Uses API for code generation

# Check API key status
GET /api-status
```

## 📊 Monitoring & Status

### API Status Endpoint

```bash
curl http://localhost:8000/api-status
```

Example response:
```json
{
  "total_keys": 8,
  "active_keys": 6,
  "exhausted_keys": 2,
  "current_key": 3,
  "keys": [
    {
      "key_id": "key_1",
      "is_active": true,
      "credits_exhausted": false,
      "error_count": 0,
      "last_used": "2025-08-13T10:30:00Z"
    }
  ]
}
```

### Configuration File

The system automatically maintains a `perplexity_config.json` file:

```json
{
  "api_keys": [...],
  "current_key_index": 2,
  "last_updated": "2025-08-13T10:30:00Z"
}
```

## 🔄 How Rotation Works

1. **Primary Key**: System starts with the first available key
2. **Credit Exhaustion**: When a key runs out of credits (HTTP 429), it's marked as exhausted
3. **Automatic Failover**: System immediately switches to the next available key
4. **Error Tracking**: Persistent errors temporarily disable keys (30-minute cooldown)
5. **Recovery**: Exhausted keys are retried after 24 hours
6. **Empty Slots**: System gracefully ignores empty key slots

## 🚨 Error Handling

### Credit Exhaustion (HTTP 429)
- Key marked as `credits_exhausted: true`
- 24-hour retry cooldown applied
- Immediate rotation to next available key

### Invalid API Key (HTTP 401)
- Key permanently disabled
- Rotation to next available key
- Manual reset required

### Rate Limiting
- Temporary 5-second delay
- Retry with same key
- Rotation if multiple failures

### Network/Timeout Errors
- 3 retry attempts with exponential backoff
- Error count tracking
- Temporary disable after 5 consecutive errors

## 🧪 Testing

### Basic Test
```bash
python api_key_manager.py
```

### Comprehensive Test Suite
```bash
python test_perplexity_system.py
```

### Integration Test with Agent Factory
```bash
# Start Agent Factory
cd agents && python main_service.py

# Run tests (in another terminal)
python test_perplexity_system.py
```

## 📋 API Parameters

### Supported Parameters

```python
await call_perplexity_api(
    prompt="Your question here",
    model="llama-3.1-sonar-large-128k-online",  # Latest Sonar model
    max_tokens=4000,
    temperature=0.2,
    top_p=0.9,
    return_citations=True,
    search_domain_filter=["perplexity.ai"],
    return_images=False,
    return_related_questions=False,
    search_recency_filter="month",
    top_k=0,
    presence_penalty=0,
    frequency_penalty=1
)
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `PERPLEXITY_API_KEY_1` to `PERPLEXITY_API_KEY_10` | Your Perplexity API keys | At least 1 |

### Manager Configuration

```python
manager = PerplexityAPIManager(
    config_file="custom_config.json",  # Custom config file
    max_retries=3,                     # Max retry attempts
    retry_delay=5                      # Delay between retries (seconds)
)
```

## 🐛 Troubleshooting

### No API Keys Found
```bash
# Verify environment variables
env | grep PERPLEXITY_API_KEY

# Check if keys are properly set
python -c "import os; print([k for k in os.environ if 'PERPLEXITY' in k])"
```

### All Keys Exhausted
```bash
# Check key status
curl http://localhost:8000/api-status

# Reset a key manually
python -c "from api_key_manager import get_perplexity_manager; get_perplexity_manager().reset_key_status('key_1')"
```

### Configuration Issues
```bash
# Delete config file to reset
rm perplexity_config.json

# Restart with fresh configuration
python api_key_manager.py
```

## 📈 Performance Considerations

- **Response Time**: ~1-3 seconds per API call
- **Failover Time**: <100ms when switching keys
- **Memory Usage**: ~10MB for manager + config
- **Rate Limits**: Handled automatically with backoff
- **Concurrency**: Thread-safe for multiple simultaneous requests

## 🔒 Security Best Practices

- Store API keys as environment variables, not in code
- Use `.env` files for local development only
- Rotate API keys regularly
- Monitor usage and set up alerts for exhaustion
- Use separate keys for development and production

## 📚 Dependencies

```
httpx>=0.24.0
pydantic>=2.0.0
fastapi>=0.100.0
uvicorn>=0.22.0
```

## 🤝 Contributing

1. Ensure all tests pass: `python test_perplexity_system.py`
2. Add tests for new features
3. Update documentation
4. Follow existing code style and patterns

## 📄 License

This system is part of the Agent Factory project and follows the same licensing terms.

---

**🔑 Ready to set up your API keys?** Run `./setup_api_keys.sh` to get started!
