#!/usr/bin/env python3
"""
Local Development Test Script
Tests the application without Docker for development purposes
"""

import subprocess
import time
import sys
import os
import signal
import requests
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

class LocalTestRunner:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.python_exec = "/workspaces/heph/.venv/bin/python"
        
    def start_backend(self):
        """Start the FastAPI backend"""
        print("🚀 Starting backend service...")
        os.environ["PYTHONPATH"] = str(project_root)
        
        cmd = [
            self.python_exec, "-m", "uvicorn", 
            "agents.main_service:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ]
        
        self.backend_process = subprocess.Popen(
            cmd, 
            cwd=project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for backend to start
        print("⏳ Waiting for backend to start...")
        for i in range(30):  # Wait up to 30 seconds
            try:
                response = requests.get("http://localhost:8000/", timeout=2)
                if response.status_code == 200:
                    print("✅ Backend started successfully!")
                    return True
            except:
                time.sleep(1)
        
        print("❌ Backend failed to start")
        return False
    
    def start_frontend(self):
        """Start the Streamlit frontend"""
        print("🚀 Starting frontend service...")
        
        # Set backend URL for local testing
        os.environ["BACKEND_URL"] = "http://localhost:8000"
        
        cmd = [
            self.python_exec, "-m", "streamlit", "run", 
            "app/main_ui.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ]
        
        self.frontend_process = subprocess.Popen(
            cmd,
            cwd=project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for frontend to start
        print("⏳ Waiting for frontend to start...")
        for i in range(30):  # Wait up to 30 seconds
            try:
                response = requests.get("http://localhost:8501/_stcore/health", timeout=2)
                if response.status_code == 200:
                    print("✅ Frontend started successfully!")
                    return True
            except:
                time.sleep(1)
        
        print("❌ Frontend failed to start")
        return False
    
    def test_endpoints(self):
        """Test backend endpoints"""
        print("🧪 Testing backend endpoints...")
        
        endpoints = [
            ("GET", "/", "Root endpoint"),
            ("GET", "/docs", "API documentation"),
        ]
        
        for method, endpoint, description in endpoints:
            try:
                url = f"http://localhost:8000{endpoint}"
                response = requests.request(method, url, timeout=5)
                if response.status_code == 200:
                    print(f"✅ {description}: {response.status_code}")
                else:
                    print(f"⚠️  {description}: {response.status_code}")
            except Exception as e:
                print(f"❌ {description}: {e}")
    
    def cleanup(self):
        """Stop all processes"""
        print("🧹 Cleaning up processes...")
        
        if self.backend_process:
            self.backend_process.terminate()
            self.backend_process.wait()
            print("✅ Backend stopped")
            
        if self.frontend_process:
            self.frontend_process.terminate()
            self.frontend_process.wait()
            print("✅ Frontend stopped")
    
    def run_test_protocol(self):
        """Run the complete test protocol"""
        print("🧪 LOCAL DEVELOPMENT TEST PROTOCOL")
        print("=" * 50)
        
        try:
            # Start services
            if not self.start_backend():
                return False
                
            if not self.start_frontend():
                return False
            
            # Test endpoints
            self.test_endpoints()
            
            print("\n🎉 LOCAL TEST SETUP COMPLETE!")
            print("🌐 Frontend: http://localhost:8501")
            print("📡 Backend: http://localhost:8000/docs")
            print("🧪 Ready for manual testing!")
            
            print("\n📋 MANUAL TEST STEPS:")
            print("1. Open http://localhost:8501 in your browser")
            print("2. Enter Alex's complex prompt about database rollback scripts")
            print("3. Navigate through all stages")
            print("4. Test the guided refinement buttons")
            print("5. Generate and verify the final code output")
            
            # Keep running until interrupted
            try:
                print("\n⌨️  Press Ctrl+C to stop the test environment...")
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Test interrupted by user")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False
        finally:
            self.cleanup()
        
        return True

def main():
    """Main test runner"""
    runner = LocalTestRunner()
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\n🛑 Stopping test environment...")
        runner.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    success = runner.run_test_protocol()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
