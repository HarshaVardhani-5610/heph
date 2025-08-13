# 🔒 API Key Security Guide for Heph Agent Factory

## Current Security Status

✅ **SECURED**: The Heph Agent Factory is now properly configured to prevent API key exposure:

### Protected Files
- `.env` - Environment variables (automatically ignored)
- `*.env` - All environment files 
- `perplexity_config.json` - API rotation configuration
- `api_keys/` - Any API key directories
- `secrets/` - Secret storage directories
- Various temporary and cache files

### Security Features Implemented

1. **Comprehensive .gitignore**: Prevents accidental commits of sensitive data
2. **Environment Template**: Safe template with placeholder values
3. **Rotation System**: API keys stored only in environment variables
4. **Security Validation Script**: `validate_security.sh` for ongoing checks

## 🚀 Quick Setup Guide

### Step 1: Set Up Your API Keys

```bash
# Copy the template to create your environment file
cp .env.template .env

# Edit .env with your actual Perplexity API keys
# Replace the placeholder values with your real keys
nano .env  # or use your preferred editor
```

### Step 2: Configure Your Keys in .env

```bash
# Example .env content:
PERPLEXITY_API_KEY_1=pplx-1234567890abcdef...
PERPLEXITY_API_KEY_2=pplx-abcdef1234567890...
PERPLEXITY_API_KEY_3=pplx-fedcba0987654321...
# ... up to 8 keys as you have them
# Leave empty slots as empty or with placeholder text
PERPLEXITY_API_KEY_9=
PERPLEXITY_API_KEY_10=
```

### Step 3: Start the Agent Factory

```bash
# Install dependencies
pip install -r requirements.txt

# Start the main service
cd agents
python main_service.py
```

### Step 4: Test API Rotation

```bash
# Test the rotation system
python test_perplexity_system.py

# Run comprehensive tests
python quick_test.py
```

## 🔍 Security Validation

Run the security check anytime:

```bash
./validate_security.sh
```

This script will:
- ✅ Check for API keys in tracked files
- ✅ Validate .gitignore configuration  
- ✅ Ensure environment files are protected
- ✅ Provide security recommendations

## 🏗️ Agent Factory Status

The Agent Factory is **100% COMPLETE** with:

### Core Services
- **Clarifier Agent**: Requirement analysis and clarification
- **Strategist Agent**: Strategic planning and approach design
- **Architect Agent**: Technical architecture and system design  
- **Builder Agent**: Code implementation and artifact creation

### API Features
- **Perplexity Integration**: Latest sonar model with rotation
- **10-Key Rotation**: Automatic failover when credits exhausted
- **Error Handling**: Graceful degradation and retry logic
- **Health Monitoring**: `/api-status` endpoint for system health

### Endpoints Available
```
POST /clarify     - Clarifier Agent
POST /strategize  - Strategist Agent  
POST /architect   - Architect Agent
POST /build       - Builder Agent
GET  /api-status  - API key rotation status
```

## 🔄 API Key Rotation Features

### Automatic Rotation
- Detects credit exhaustion (402 errors)
- Switches to next available key
- Tracks failures and cooldowns
- Persistent configuration storage

### Smart Handling
- Empty slots are gracefully skipped
- 24-hour cooldown for exhausted keys
- Detailed logging and error tracking
- No interruption to service

### Configuration
The system automatically creates `perplexity_config.json` to track:
- Current active key index
- Error counts per key
- Temporary disable states
- Last successful usage timestamps

## 🚨 Security Best Practices

### DO ✅
- Store API keys in environment variables only
- Use `.env` files for local development
- Run `./validate_security.sh` before commits
- Rotate your API keys regularly
- Keep `.env` files local only

### DON'T ❌
- Never commit actual API keys to git
- Don't hardcode keys in source files
- Don't share `.env` files
- Don't store keys in configuration files that get committed

## 🐛 Troubleshooting

### No API Keys Working
```bash
# Check your .env file
cat .env

# Test individual keys
curl -H "Authorization: Bearer YOUR_KEY" \
     https://api.perplexity.ai/chat/completions \
     -d '{"model":"sonar","messages":[{"role":"user","content":"test"}]}'
```

### Service Not Starting
```bash
# Check dependencies
pip install -r requirements.txt

# Check port availability
lsof -i :8000

# Check logs
cd agents && python main_service.py
```

### Rotation Not Working
```bash
# Check configuration
cat perplexity_config.json

# Reset rotation state
rm perplexity_config.json

# Run rotation tests
python test_perplexity_system.py
```

## 📚 Next Steps

1. **Production Deployment**: Consider Docker deployment with docker-compose.yml
2. **Monitoring**: Add logging and monitoring for production use
3. **Scaling**: Add load balancing if needed
4. **Security Audit**: Regular security reviews and key rotation

---

## 🎉 You're All Set!

Your Heph Agent Factory is now:
- ✅ Fully functional with 4 AI agents
- ✅ Secured against API key exposure  
- ✅ Configured with automatic key rotation
- ✅ Ready for production use

Run `python agents/main_service.py` to start the factory! 🚀
