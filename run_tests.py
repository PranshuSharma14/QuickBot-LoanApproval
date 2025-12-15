"""
Test Runner Script for NBFC Orchestration System
Provides easy commands to run different types of tests
"""

import subprocess
import sys
import argparse
import os
from pathlib import Path


class TestRunner:
    """Test runner with multiple test types and options"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_dir = self.project_root / "tests"
    
    def run_unit_tests(self, verbose=False):
        """Run unit tests"""
        print("🧪 Running Unit Tests...")
        
        cmd = [
            sys.executable, "-m", "pytest", 
            str(self.test_dir / "test_orchestration.py"),
            "-v" if verbose else "-q",
            "--tb=short"
        ]
        
        return subprocess.run(cmd, cwd=self.project_root)
    
    def run_integration_tests(self, verbose=False):
        """Run integration tests"""
        print("🔧 Running Integration Tests...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.test_dir / "test_api.py"), 
            "-v" if verbose else "-q",
            "--tb=short",
            "-m", "integration"
        ]
        
        return subprocess.run(cmd, cwd=self.project_root)
    
    def run_performance_tests(self, verbose=False):
        """Run performance tests"""
        print("⚡ Running Performance Tests...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.test_dir / "test_orchestration.py::TestPerformanceAndLoad"),
            "-v" if verbose else "-q",
            "--tb=short"
        ]
        
        return subprocess.run(cmd, cwd=self.project_root)
    
    def run_load_tests(self):
        """Run load tests"""
        print("🚀 Running Load Tests...")
        print("Note: This requires the server to be running on localhost:8000")
        
        cmd = [sys.executable, str(self.test_dir / "load_test.py")]
        
        return subprocess.run(cmd, cwd=self.project_root)
    
    def run_all_tests(self, verbose=False):
        """Run all tests"""
        print("🎯 Running All Tests...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.test_dir),
            "-v" if verbose else "-q",
            "--tb=short",
            "--cov=app",
            "--cov-report=html",
            "--cov-report=term"
        ]
        
        return subprocess.run(cmd, cwd=self.project_root)
    
    def run_demo(self):
        """Run orchestration demo"""
        print("🎭 Running Orchestration Demo...")
        
        cmd = [sys.executable, "demo_orchestration.py"]
        
        return subprocess.run(cmd, cwd=self.project_root)
    
    def check_server_health(self):
        """Check if server is running and healthy"""
        try:
            import requests
            response = requests.get("http://localhost:8000/", timeout=5)
            if response.status_code == 200:
                print("✅ Server is running and healthy")
                return True
            else:
                print(f"⚠️  Server responding but with status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Server not reachable: {e}")
            return False
    
    def setup_test_environment(self):
        """Setup test environment"""
        print("🔧 Setting up test environment...")
        
        # Install test dependencies
        cmd = [
            sys.executable, "-m", "pip", "install", "-r", 
            str(self.test_dir / "requirements-test.txt")
        ]
        
        result = subprocess.run(cmd, cwd=self.project_root)
        
        if result.returncode == 0:
            print("✅ Test environment setup complete")
        else:
            print("❌ Failed to setup test environment")
        
        return result


def main():
    """Main CLI interface"""
    
    parser = argparse.ArgumentParser(description="NBFC Test Runner")
    parser.add_argument(
        "test_type", 
        choices=["unit", "integration", "performance", "load", "all", "demo", "setup", "health"],
        help="Type of tests to run"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    runner = TestRunner()
    
    if args.test_type == "setup":
        result = runner.setup_test_environment()
    elif args.test_type == "health":
        runner.check_server_health()
        return
    elif args.test_type == "demo":
        result = runner.run_demo()
    elif args.test_type == "unit":
        result = runner.run_unit_tests(args.verbose)
    elif args.test_type == "integration":
        result = runner.run_integration_tests(args.verbose)
    elif args.test_type == "performance":
        result = runner.run_performance_tests(args.verbose)
    elif args.test_type == "load":
        if runner.check_server_health():
            result = runner.run_load_tests()
        else:
            print("❌ Cannot run load tests without server running")
            sys.exit(1)
    elif args.test_type == "all":
        result = runner.run_all_tests(args.verbose)
    
    if hasattr(result, 'returncode'):
        sys.exit(result.returncode)


if __name__ == "__main__":
    main()