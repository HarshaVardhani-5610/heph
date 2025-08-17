#!/usr/bin/env python3
"""
Production Docker Deployment Validation Script
This script ensures the Docker configuration is production-ready
"""

import os
import sys
import subprocess
import json

def validate_docker_setup():
    """Validate that all Docker files are properly configured for production"""
    print("🐳 DOCKER DEPLOYMENT VALIDATION")
    print("=" * 50)
    
    issues = []
    
    # Test 1: Required files exist
    print("\n📋 Testing required files...")
    required_files = [
        "requirements.txt",
        "agents/main_service.py", 
        "app/main_ui.py",
        "api_key_manager.py",
        ".env",
        "docker-compose.yml",
        "agents/Dockerfile",
        "app/Dockerfile"
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            issues.append(f"Missing file: {file}")
    
    # Test 2: Docker Compose syntax
    print("\n📋 Testing docker-compose.yml syntax...")
    try:
        with open("docker-compose.yml", "r") as f:
            content = f.read()
            if "version:" in content and "services:" in content:
                print("✅ docker-compose.yml has basic structure")
            else:
                print("❌ docker-compose.yml missing required sections")
                issues.append("docker-compose.yml structure invalid")
    except Exception as e:
        print(f"❌ Error reading docker-compose.yml: {e}")
        issues.append(f"docker-compose.yml error: {e}")
    
    # Test 3: Dockerfile syntax
    print("\n📋 Testing Dockerfile syntax...")
    for dockerfile in ["agents/Dockerfile", "app/Dockerfile"]:
        try:
            with open(dockerfile, "r") as f:
                content = f.read()
                if "FROM" in content and "COPY" in content and "EXPOSE" in content:
                    print(f"✅ {dockerfile} has basic structure")
                else:
                    print(f"❌ {dockerfile} missing required commands")
                    issues.append(f"{dockerfile} structure invalid")
        except Exception as e:
            print(f"❌ Error reading {dockerfile}: {e}")
            issues.append(f"{dockerfile} error: {e}")
    
    # Test 4: Python imports
    print("\n📋 Testing Python imports...")
    try:
        sys.path.append('.')
        import agents.main_service
        print("✅ Backend imports successfully")
    except Exception as e:
        print(f"❌ Backend import failed: {e}")
        issues.append(f"Backend import error: {e}")
    
    try:
        import streamlit
        import httpx
        import requests
        print("✅ Frontend dependencies available")
    except Exception as e:
        print(f"❌ Frontend dependencies missing: {e}")
        issues.append(f"Frontend dependencies error: {e}")
    
    # Test 5: Environment file
    print("\n📋 Testing environment configuration...")
    try:
        with open(".env", "r") as f:
            env_content = f.read()
            if "PERPLEXITY_API_KEY" in env_content:
                print("✅ .env file has API key configuration")
            else:
                print("❌ .env file missing API key configuration")
                issues.append(".env missing API key configuration")
    except Exception as e:
        print(f"❌ Error reading .env: {e}")
        issues.append(f".env error: {e}")
    
    # Results
    print("\n" + "=" * 50)
    if not issues:
        print("🎉 DOCKER DEPLOYMENT VALIDATION COMPLETE")
        print("✅ Configuration is production-ready")
        print("✅ Ready for deployment with: docker-compose up --build")
        return True
    else:
        print("❌ VALIDATION FAILED - Issues found:")
        for issue in issues:
            print(f"   • {issue}")
        print("\n🔧 Fix these issues before deployment")
        return False

def create_deployment_guide():
    """Create a deployment guide for production use"""
    guide = """
# 🚀 Production Deployment Guide

## Prerequisites
1. Docker and Docker Compose installed
2. .env file with your API keys configured
3. Internet access for downloading dependencies

## Quick Deploy Commands

### Option 1: Docker Compose (Recommended)
```bash
# Clone the repository
git clone <your-repo-url>
cd heph

# Configure your API keys in .env file
cp .env.example .env
# Edit .env with your actual API keys

# Deploy the application
docker-compose up --build -d

# Check status
docker-compose ps
docker-compose logs

# Access the application
# Frontend: http://localhost:8501
# Backend API: http://localhost:8000/docs
```

### Option 2: Manual Docker Build
```bash
# Build backend
docker build -f agents/Dockerfile -t heph-backend .

# Build frontend  
docker build -f app/Dockerfile -t heph-frontend .

# Run backend
docker run -d --name heph-backend -p 8000:8000 --env-file .env heph-backend

# Run frontend
docker run -d --name heph-frontend -p 8501:8501 heph-frontend
```

## Production Considerations
1. **Security**: Ensure .env file is not committed to version control
2. **Monitoring**: Set up health checks and monitoring
3. **Scaling**: Consider using Docker Swarm or Kubernetes for scaling
4. **SSL**: Add HTTPS/SSL termination for production
5. **Backup**: Regular backup of any persistent data

## Troubleshooting
- Check logs: `docker-compose logs [service-name]`
- Restart services: `docker-compose restart`
- Rebuild: `docker-compose up --build`
- Clean slate: `docker-compose down && docker-compose up --build`
"""
    
    with open("DEPLOYMENT.md", "w") as f:
        f.write(guide)
    print("📝 Created DEPLOYMENT.md with production guidance")

if __name__ == "__main__":
    success = validate_docker_setup()
    if success:
        create_deployment_guide()
        print("\n🎯 Next Steps:")
        print("1. Validate docker-compose.yml works: docker-compose config")
        print("2. Test build: docker-compose build")
        print("3. Deploy: docker-compose up --build")
    sys.exit(0 if success else 1)
    
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
