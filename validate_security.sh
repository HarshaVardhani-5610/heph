#!/bin/bash
"""
Security Check Script for API Keys
Validates environment setup and prevents accidental key exposure
"""

echo "🔒 API KEY SECURITY CHECK"
echo "========================"
echo ""

# Function to check if a file exists in git tracking
check_git_tracked() {
    local file=$1
    if git ls-files --error-unmatch "$file" >/dev/null 2>&1; then
        return 0  # File is tracked
    else
        return 1  # File is not tracked
    fi
}

# Function to scan for potential API keys in tracked files
scan_for_keys() {
    echo "🔍 Scanning for potential API keys in tracked files..."
    echo ""
    
    # Common API key patterns
    patterns=(
        "PERPLEXITY_API_KEY"
        "pplx-[a-zA-Z0-9]"
        "sk-[a-zA-Z0-9]"
        "Bearer [a-zA-Z0-9]"
        "api_key.*=.*['\"][a-zA-Z0-9]{20,}['\"]"
        "secret.*=.*['\"][a-zA-Z0-9]{20,}['\"]"
    )
    
    found_issues=false
    
    for pattern in "${patterns[@]}"; do
        if git grep -n "$pattern" -- '*.py' '*.json' '*.txt' '*.md' '*.sh' 2>/dev/null; then
            echo "⚠️  Found potential API key pattern: $pattern"
            found_issues=true
        fi
    done
    
    if [ "$found_issues" = false ]; then
        echo "✅ No API key patterns found in tracked files"
    fi
    
    echo ""
}

# Function to check environment file security
check_env_files() {
    echo "📁 Checking environment file security..."
    echo ""
    
    env_files=(".env" ".env.local" "perplexity_config.json" "*.env")
    
    for file_pattern in "${env_files[@]}"; do
        for file in $file_pattern; do
            if [ -f "$file" ]; then
                if check_git_tracked "$file"; then
                    echo "🚨 CRITICAL: $file is tracked by git!"
                    echo "   Run: git rm --cached $file"
                    echo "   Add to .gitignore: $file"
                    echo ""
                else
                    echo "✅ $file is properly ignored by git"
                fi
            fi
        done
    done
}

# Function to validate .gitignore
check_gitignore() {
    echo "📋 Validating .gitignore configuration..."
    echo ""
    
    required_ignores=(
        ".env"
        "*.env"
        "perplexity_config.json"
        "*.api_key"
    )
    
    missing_ignores=()
    
    for ignore_pattern in "${required_ignores[@]}"; do
        if ! grep -q "^$ignore_pattern$" .gitignore 2>/dev/null; then
            missing_ignores+=("$ignore_pattern")
        fi
    done
    
    if [ ${#missing_ignores[@]} -eq 0 ]; then
        echo "✅ .gitignore is properly configured"
    else
        echo "⚠️  Missing .gitignore entries:"
        for pattern in "${missing_ignores[@]}"; do
            echo "   - $pattern"
        done
        echo ""
        echo "Add these to .gitignore to prevent accidental commits"
    fi
    
    echo ""
}

# Function to check git status for staged API keys
check_git_status() {
    echo "📊 Checking git staging area..."
    echo ""
    
    # Check for staged files that might contain keys
    staged_files=$(git diff --cached --name-only 2>/dev/null || true)
    
    if [ -n "$staged_files" ]; then
        echo "Staged files:"
        for file in $staged_files; do
            echo "  - $file"
            
            # Check if staged file contains potential keys
            if git diff --cached "$file" | grep -i "api_key\|secret\|token" >/dev/null 2>&1; then
                echo "    ⚠️  Contains potential API key content!"
            fi
        done
    else
        echo "✅ No files currently staged"
    fi
    
    echo ""
}

# Function to provide setup recommendations
provide_recommendations() {
    echo "💡 SECURITY RECOMMENDATIONS"
    echo "============================"
    echo ""
    echo "1. 🔐 Store API keys as environment variables:"
    echo "   export PERPLEXITY_API_KEY_1='your-key-here'"
    echo ""
    echo "2. 📄 Use .env files for local development:"
    echo "   cp .env.template .env"
    echo "   # Edit .env with your keys"
    echo "   # .env is automatically ignored by git"
    echo ""
    echo "3. 🚫 Never commit actual API keys:"
    echo "   - Use placeholder values in templates"
    echo "   - Use environment variables in production"
    echo "   - Regularly rotate your API keys"
    echo ""
    echo "4. ✅ Before committing, always run:"
    echo "   ./validate_security.sh"
    echo ""
    echo "5. 🔄 Regular security checks:"
    echo "   git log --grep='api.*key' --oneline"
    echo "   git log --grep='secret' --oneline"
    echo ""
}

# Function to create secure environment setup
create_secure_env() {
    echo "🛠️  Creating secure environment setup..."
    echo ""
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.template" ]; then
            cp .env.template .env
            echo "✅ Created .env from template"
            echo "   Edit .env with your actual API keys"
            echo "   .env is automatically ignored by git"
        else
            echo "⚠️  .env.template not found"
            echo "   Create .env manually with your API keys"
        fi
    else
        echo "✅ .env already exists"
    fi
    
    # Ensure .env is not tracked
    if check_git_tracked ".env"; then
        echo "🚨 REMOVING .env from git tracking..."
        git rm --cached .env 2>/dev/null || true
        echo "✅ .env removed from git tracking"
    fi
    
    echo ""
}

# Main execution
main() {
    echo "Starting API key security validation..."
    echo ""
    
    # Run all checks
    scan_for_keys
    check_env_files
    check_gitignore
    check_git_status
    create_secure_env
    provide_recommendations
    
    echo "🔒 SECURITY CHECK COMPLETE"
    echo "=========================="
    echo ""
    echo "Remember: Never commit actual API keys to git!"
    echo "Use environment variables and .env files instead."
}

# Run main function
main
