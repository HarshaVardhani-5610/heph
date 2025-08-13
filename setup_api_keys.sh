#!/bin/bash
"""
Perplexity API Key Setup Script
Run this to set up your environment variables for API key rotation
"""

echo "🔑 Perplexity API Key Setup"
echo "=========================="
echo ""
echo "This script will help you set up environment variables for your Perplexity API keys."
echo "You can configure up to 10 API keys for automatic rotation."
echo ""

# Function to set environment variable
set_api_key() {
    local key_number=$1
    local var_name="PERPLEXITY_API_KEY_${key_number}"
    
    echo -n "Enter API key ${key_number} (leave empty to skip): "
    read -s api_key
    echo ""
    
    if [ ! -z "$api_key" ]; then
        export $var_name="$api_key"
        echo "export $var_name=\"$api_key\"" >> ~/.bashrc
        echo "✅ Set $var_name"
    else
        echo "⏭️  Skipped $var_name"
    fi
}

echo "Please enter your Perplexity API keys:"
echo "(You need at least 1 key, but can configure up to 10)"
echo ""

# Set up API keys
for i in {1..10}; do
    set_api_key $i
done

echo ""
echo "🔄 Reloading environment..."
source ~/.bashrc

echo ""
echo "✅ Setup complete!"
echo ""
echo "Your API keys are now configured. The system will automatically:"
echo "• Rotate between keys when one runs out of credits"
echo "• Track usage and errors for each key"
echo "• Retry failed keys after a cooldown period"
echo ""
echo "To test your setup, run:"
echo "  python api_key_manager.py"
echo ""
echo "Current configured keys:"
for i in {1..10}; do
    var_name="PERPLEXITY_API_KEY_${i}"
    if [ ! -z "${!var_name}" ]; then
        echo "  ✅ $var_name: ****${!var_name: -4}"
    fi
done
