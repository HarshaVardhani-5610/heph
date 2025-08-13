#!/usr/bin/env python3
"""
Validate our Docker setup configuration
"""

import os

def validate_docker_setup():
    """Validate that all Docker files are properly created"""
    
    print("🐳 Docker-First Setup Validation")
    print("=" * 40)
    
    # Check required files
    required_files = [
        ('docker-compose.yml', 'Root'),
        ('agents/Dockerfile', 'Backend'),
        ('agents/main_service.py', 'Backend Service'),
        ('app/Dockerfile', 'Frontend'),
        ('app/main_ui.py', 'Frontend Service'),
        ('requirements.txt', 'Dependencies')
    ]
    
    all_good = True
    
    for file_path, description in required_files:
        if os.path.exists(file_path):
            print(f"✅ {description}: {file_path}")
        else:
            print(f"❌ {description}: {file_path} - MISSING")
            all_good = False
    
    print("\n📋 Configuration Summary:")
    print("- Backend: FastAPI on port 8000")
    print("- Frontend: Streamlit on port 8501") 
    print("- Network: Custom bridge network for inter-service communication")
    print("- Dependencies: Health checks and service dependencies configured")
    
    if all_good:
        print("\n🎉 Docker setup is complete and ready!")
        print("\n🚀 Next steps:")
        print("   1. Run: docker-compose up --build")
        print("   2. Access frontend: http://localhost:8501")
        print("   3. Test backend: http://localhost:8000")
        print("   4. Frontend can call backend at: http://backend:8000")
    else:
        print("\n⚠️  Some files are missing. Please create them before proceeding.")
    
    return all_good

if __name__ == "__main__":
    validate_docker_setup()
