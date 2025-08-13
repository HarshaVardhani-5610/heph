#!/bin/bash
"""
Secure Setup Script for Heph Agent Factory
Guides users through safe API key configuration
"""

echo "🏭 HEPH AGENT FACTORY - SECURE SETUP"
echo "====================================="
echo ""
echo "This script will help you securely configure your Perplexity API keys"
echo "for the Heph Agent Factory's automatic rotation system."
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to create secure .env file
setup_env_file() {
    echo "📄 Setting up environment file..."
    echo ""
    
    if [ -f ".env" ]; then
        echo "⚠️  .env file already exists."
        read -p "Do you want to overwrite it? (y/N): " overwrite
        if [[ ! $overwrite =~ ^[Yy]$ ]]; then
            echo "Keeping existing .env file."
            return
        fi
    fi
    
    # Copy template to .env
    if [ -f ".env.template" ]; then
        cp .env.template .env
        echo "✅ Created .env from template"
        echo ""
        echo "📝 Next steps:"
        echo "   1. Edit .env with your actual Perplexity API keys"
        echo "   2. Replace placeholder values with real keys"
        echo "   3. You can leave empty slots for future expansion"
        echo ""
        echo "🔓 Example API key format: pplx-1234567890abcdef..."
        echo ""
        
        if command_exists nano; then
            read -p "Would you like to edit .env now with nano? (y/N): " edit_now
            if [[ $edit_now =~ ^[Yy]$ ]]; then
                nano .env
            fi
        else
            echo "Edit .env with your preferred text editor:"
            echo "   vim .env"
            echo "   code .env"
            echo "   cat > .env  # then paste and Ctrl+D"
        fi
    else
        echo "❌ .env.template not found!"
        echo "Creating basic .env file..."
        
        cat > .env << EOF
# Perplexity AI API Keys
PERPLEXITY_API_KEY_1=your-first-api-key-here
PERPLEXITY_API_KEY_2=your-second-api-key-here
PERPLEXITY_API_KEY_3=your-third-api-key-here
PERPLEXITY_API_KEY_4=your-fourth-api-key-here
PERPLEXITY_API_KEY_5=your-fifth-api-key-here
PERPLEXITY_API_KEY_6=your-sixth-api-key-here
PERPLEXITY_API_KEY_7=your-seventh-api-key-here
PERPLEXITY_API_KEY_8=your-eighth-api-key-here
PERPLEXITY_API_KEY_9=
PERPLEXITY_API_KEY_10=
EOF
        echo "✅ Created basic .env file"
        echo "   Edit it with your actual API keys"
    fi
    
    echo ""
}

# Function to validate dependencies
check_dependencies() {
    echo "📦 Checking dependencies..."
    echo ""
    
    if [ ! -f "requirements.txt" ]; then
        echo "❌ requirements.txt not found!"
        return 1
    fi
    
    if command_exists python3; then
        PYTHON_CMD="python3"
    elif command_exists python; then
        PYTHON_CMD="python"
    else
        echo "❌ Python not found! Please install Python 3.8+"
        return 1
    fi
    
    if command_exists pip3; then
        PIP_CMD="pip3"
    elif command_exists pip; then
        PIP_CMD="pip"
    else
        echo "❌ pip not found! Please install pip"
        return 1
    fi
    
    echo "✅ Found Python: $($PYTHON_CMD --version)"
    echo "✅ Found pip: $($PIP_CMD --version)"
    echo ""
    
    read -p "Install Python dependencies? (Y/n): " install_deps
    if [[ ! $install_deps =~ ^[Nn]$ ]]; then
        echo "Installing dependencies..."
        $PIP_CMD install -r requirements.txt
        echo ""
    fi
}

# Function to run security validation
run_security_check() {
    echo "🔒 Running security validation..."
    echo ""
    
    if [ -x "./validate_security.sh" ]; then
        ./validate_security.sh
    else
        echo "⚠️  Security validation script not found or not executable"
        echo "Make sure validate_security.sh exists and is executable:"
        echo "   chmod +x validate_security.sh"
    fi
    
    echo ""
}

# Function to test the setup
test_setup() {
    echo "🧪 Testing setup..."
    echo ""
    
    if [ ! -f ".env" ]; then
        echo "❌ .env file not found! Please create it first."
        return 1
    fi
    
    # Source the environment variables
    set -o allexport
    source .env
    set +o allexport
    
    # Check if at least one API key is set
    if [ -z "$PERPLEXITY_API_KEY_1" ] || [ "$PERPLEXITY_API_KEY_1" = "your-first-api-key-here" ]; then
        echo "⚠️  No valid API key found in .env"
        echo "Please edit .env with your actual Perplexity API keys"
        return 1
    fi
    
    echo "✅ Environment file configured"
    
    # Test if we can run the test scripts
    if [ -f "test_perplexity_system.py" ]; then
        read -p "Run API rotation tests? (y/N): " run_tests
        if [[ $run_tests =~ ^[Yy]$ ]]; then
            echo "Running tests..."
            $PYTHON_CMD test_perplexity_system.py
        fi
    fi
    
    echo ""
}

# Function to start the service
start_service() {
    echo "🚀 Starting Heph Agent Factory..."
    echo ""
    
    if [ -d "agents" ] && [ -f "agents/main_service.py" ]; then
        echo "Service will start on http://localhost:8000"
        echo "Available endpoints:"
        echo "  POST /clarify     - Clarifier Agent"
        echo "  POST /strategize  - Strategist Agent"
        echo "  POST /architect   - Architect Agent"
        echo "  POST /build       - Builder Agent"
        echo "  GET  /api-status  - API rotation status"
        echo ""
        
        read -p "Start the service now? (Y/n): " start_now
        if [[ ! $start_now =~ ^[Nn]$ ]]; then
            cd agents
            echo "Starting service... (Press Ctrl+C to stop)"
            $PYTHON_CMD main_service.py
        else
            echo "To start the service later, run:"
            echo "   cd agents && python main_service.py"
        fi
    else
        echo "❌ Service files not found!"
        echo "Make sure agents/main_service.py exists"
    fi
    
    echo ""
}

# Function to show final instructions
show_final_instructions() {
    echo "🎉 SETUP COMPLETE!"
    echo "=================="
    echo ""
    echo "Your Heph Agent Factory is ready! Here's what to do next:"
    echo ""
    echo "1. 🔑 Verify your API keys in .env are correct"
    echo "2. 🏃 Start the service: cd agents && python main_service.py"
    echo "3. 🧪 Test endpoints: curl http://localhost:8000/api-status"
    echo "4. 📖 Read SECURITY_SETUP.md for detailed documentation"
    echo "5. 🔒 Run ./validate_security.sh periodically"
    echo ""
    echo "🚨 IMPORTANT SECURITY REMINDERS:"
    echo "   - Never commit your .env file to git"
    echo "   - Keep your API keys private"
    echo "   - Rotate keys regularly"
    echo "   - Run security checks before any commits"
    echo ""
    echo "Happy coding! 🚀"
}

# Main setup workflow
main() {
    echo "Starting secure setup process..."
    echo ""
    
    # Step 1: Set up environment file
    setup_env_file
    
    # Step 2: Check dependencies
    check_dependencies
    
    # Step 3: Run security check
    run_security_check
    
    # Step 4: Test the setup
    test_setup
    
    # Step 5: Offer to start service
    start_service
    
    # Step 6: Show final instructions
    show_final_instructions
}

# Execute main function
main
