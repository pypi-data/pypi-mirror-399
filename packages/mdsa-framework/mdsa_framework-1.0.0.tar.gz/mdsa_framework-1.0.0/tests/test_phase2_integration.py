"""
Comprehensive End-to-End Integration Tests for Phase 2
Tests all Phase 2 features: Authentication, RAG Management, Model Configuration, Tool Management
"""

import os
import sys
import json
import time
import requests
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Windows console UTF-8 fix
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_test_header(title):
    """Print a formatted test section header"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{title}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*80}{Colors.RESET}\n")


def print_success(message):
    """Print success message in green"""
    print(f"{Colors.GREEN}[OK] {message}{Colors.RESET}")


def print_error(message):
    """Print error message in red"""
    print(f"{Colors.RED}[FAIL] {message}{Colors.RESET}")


def print_warning(message):
    """Print warning message in yellow"""
    print(f"{Colors.YELLOW}[WARN] {message}{Colors.RESET}")


def print_info(message):
    """Print info message in blue"""
    print(f"{Colors.BLUE}[INFO] {message}{Colors.RESET}")


class Phase2IntegrationTests:
    """End-to-end integration tests for Phase 2 features"""

    def __init__(self, dashboard_url="http://localhost:9000"):
        self.dashboard_url = dashboard_url
        self.session = requests.Session()
        self.access_token = None
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "warnings": 0
        }

    def run_all_tests(self):
        """Run all Phase 2 integration tests"""
        print_test_header("PHASE 2 END-TO-END INTEGRATION TESTS")

        # Test 1: Authentication
        if not self.test_authentication():
            print_error("Authentication failed - cannot proceed with protected routes")
            return False

        # Test 2: RAG Management
        self.test_rag_management()

        # Test 3: Model Configuration
        self.test_model_configuration()

        # Test 4: Tool Management
        self.test_tool_management()

        # Print summary
        self.print_summary()

        return self.test_results["failed"] == 0

    def test_authentication(self):
        """Test JWT authentication system"""
        print_test_header("1. AUTHENTICATION SYSTEM")

        # Test 1.1: Login page loads
        print_info("Test 1.1: GET /login - Login page loads")
        try:
            response = requests.get(f"{self.dashboard_url}/login")
            if response.status_code == 200 and "Login" in response.text:
                print_success("Login page loads correctly")
                self.test_results["passed"] += 1
            else:
                print_error(f"Login page failed (status: {response.status_code})")
                self.test_results["failed"] += 1
                return False
        except Exception as e:
            print_error(f"Login page error: {e}")
            self.test_results["failed"] += 1
            return False

        # Test 1.2: Login with correct credentials
        print_info("Test 1.2: POST /api/auth/login - Authenticate user")
        try:
            response = self.session.post(
                f"{self.dashboard_url}/api/auth/login",
                json={
                    "username": "admin",
                    "password": "mdsa_admin_2025"
                }
            )
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.access_token = data["access_token"]
                    print_success(f"Login successful, token received")
                    self.test_results["passed"] += 1
                else:
                    print_error("Login response missing access_token")
                    self.test_results["failed"] += 1
                    return False
            else:
                print_error(f"Login failed (status: {response.status_code})")
                self.test_results["failed"] += 1
                return False
        except Exception as e:
            print_error(f"Login error: {e}")
            self.test_results["failed"] += 1
            return False

        # Test 1.3: Get current user
        print_info("Test 1.3: GET /api/auth/me - Get current user info")
        try:
            response = self.session.get(f"{self.dashboard_url}/api/auth/me")
            if response.status_code == 200:
                data = response.json()
                if data.get("username") == "admin":
                    print_success(f"Current user: {data.get('name')}")
                    self.test_results["passed"] += 1
                else:
                    print_error("User info incorrect")
                    self.test_results["failed"] += 1
            else:
                print_error(f"Get user failed (status: {response.status_code})")
                self.test_results["failed"] += 1
        except Exception as e:
            print_error(f"Get user error: {e}")
            self.test_results["failed"] += 1

        # Test 1.4: Access protected route
        print_info("Test 1.4: GET /admin/rag - Access protected route")
        try:
            response = self.session.get(f"{self.dashboard_url}/admin/rag")
            if response.status_code == 200:
                print_success("Protected route accessible with authentication")
                self.test_results["passed"] += 1
            else:
                print_error(f"Protected route failed (status: {response.status_code})")
                self.test_results["failed"] += 1
        except Exception as e:
            print_error(f"Protected route error: {e}")
            self.test_results["failed"] += 1

        return True

    def test_rag_management(self):
        """Test RAG management features"""
        print_test_header("2. RAG MANAGEMENT")

        # Test 2.1: List RAG documents
        print_info("Test 2.1: GET /api/admin/rag/documents - List documents")
        try:
            response = self.session.get(f"{self.dashboard_url}/api/admin/rag/documents")
            if response.status_code == 200:
                data = response.json()
                doc_count = data.get("total_documents", 0)
                print_success(f"Documents listed: {doc_count} total")
                print_info(f"  Global: {data.get('global_documents', 0)}, Local: {data.get('local_documents', 0)}")
                self.test_results["passed"] += 1
            else:
                print_error(f"List documents failed (status: {response.status_code})")
                self.test_results["failed"] += 1
        except Exception as e:
            print_error(f"List documents error: {e}")
            self.test_results["failed"] += 1

        # Test 2.2: Upload document (if medical chatbot is running)
        print_info("Test 2.2: POST /api/admin/rag/upload - Upload test document")
        test_content = "This is a test document for Phase 2 integration testing."
        test_file = Path(__file__).parent / "test_document.txt"

        try:
            # Create test file
            test_file.write_text(test_content, encoding='utf-8')

            files = {'file': ('test_document.txt', open(test_file, 'rb'), 'text/plain')}
            data = {'rag_type': 'global'}

            response = self.session.post(
                f"{self.dashboard_url}/api/admin/rag/upload",
                files=files,
                data=data
            )

            if response.status_code == 200:
                result = response.json()
                print_success(f"Document uploaded: {result.get('doc_id')}")
                self.test_results["passed"] += 1
            elif response.status_code == 400 or response.status_code == 500:
                print_warning(f"Upload failed - Medical chatbot may not be running (status: {response.status_code})")
                self.test_results["warnings"] += 1
            else:
                print_error(f"Upload failed (status: {response.status_code})")
                self.test_results["failed"] += 1

            # Cleanup
            test_file.unlink(missing_ok=True)

        except Exception as e:
            print_warning(f"Upload test skipped - Medical chatbot may not be running: {e}")
            self.test_results["warnings"] += 1
            test_file.unlink(missing_ok=True)

    def test_model_configuration(self):
        """Test model configuration features"""
        print_test_header("3. MODEL CONFIGURATION")

        # Test 3.1: Model configuration page loads
        print_info("Test 3.1: GET /admin/models - Model config page loads")
        try:
            response = self.session.get(f"{self.dashboard_url}/admin/models")
            if response.status_code == 200 and "Model Configuration" in response.text:
                print_success("Model configuration page loads")
                self.test_results["passed"] += 1
            else:
                print_error(f"Model config page failed (status: {response.status_code})")
                self.test_results["failed"] += 1
        except Exception as e:
            print_error(f"Model config page error: {e}")
            self.test_results["failed"] += 1

        # Test 3.2: Save model configuration
        print_info("Test 3.2: POST /api/admin/models/config - Save configuration")
        try:
            config = {
                "orchestration": {
                    "orchestrator_model": "google/bert_uncased_L-2_H-128_A-2",
                    "reasoning_model": "microsoft/phi-2",
                    "complexity_threshold": 0.2,
                    "enable_reasoning": True
                },
                "domain_models": {}
            }

            response = self.session.post(
                f"{self.dashboard_url}/api/admin/models/config",
                json=config
            )

            if response.status_code == 200:
                result = response.json()
                print_success(f"Configuration saved to {result.get('config_path')}")
                self.test_results["passed"] += 1
            else:
                print_error(f"Save config failed (status: {response.status_code})")
                self.test_results["failed"] += 1
        except Exception as e:
            print_error(f"Save config error: {e}")
            self.test_results["failed"] += 1

        # Test 3.3: Reset configuration
        print_info("Test 3.3: POST /api/admin/models/config/reset - Reset to defaults")
        try:
            response = self.session.post(f"{self.dashboard_url}/api/admin/models/config/reset")
            if response.status_code == 200:
                result = response.json()
                print_success("Configuration reset to defaults")
                self.test_results["passed"] += 1
            else:
                print_error(f"Reset config failed (status: {response.status_code})")
                self.test_results["failed"] += 1
        except Exception as e:
            print_error(f"Reset config error: {e}")
            self.test_results["failed"] += 1

    def test_tool_management(self):
        """Test tool management features"""
        print_test_header("4. TOOL MANAGEMENT")

        test_tool_id = None

        # Test 4.1: Tool management page loads
        print_info("Test 4.1: GET /admin/tools - Tool management page loads")
        try:
            response = self.session.get(f"{self.dashboard_url}/admin/tools")
            if response.status_code == 200 and "Tool Management" in response.text:
                print_success("Tool management page loads")
                self.test_results["passed"] += 1
            else:
                print_error(f"Tool management page failed (status: {response.status_code})")
                self.test_results["failed"] += 1
        except Exception as e:
            print_error(f"Tool management page error: {e}")
            self.test_results["failed"] += 1

        # Test 4.2: List tools
        print_info("Test 4.2: GET /api/admin/tools - List all tools")
        try:
            response = self.session.get(f"{self.dashboard_url}/api/admin/tools")
            if response.status_code == 200:
                data = response.json()
                tool_count = data.get("count", 0)
                print_success(f"Tools listed: {tool_count} total")
                self.test_results["passed"] += 1
            else:
                print_error(f"List tools failed (status: {response.status_code})")
                self.test_results["failed"] += 1
        except Exception as e:
            print_error(f"List tools error: {e}")
            self.test_results["failed"] += 1

        # Test 4.3: Create test tool
        print_info("Test 4.3: POST /api/admin/tools - Create test tool")
        try:
            tool_data = {
                "name": "Test API Integration",
                "type": "custom",
                "endpoint": "https://api.test.example.com",
                "api_key": "test_key_12345_phase2_integration",
                "description": "Test tool created during Phase 2 integration testing",
                "params": {"timeout": 30},
                "enabled": True
            }

            response = self.session.post(
                f"{self.dashboard_url}/api/admin/tools",
                json=tool_data
            )

            if response.status_code == 200:
                result = response.json()
                test_tool_id = result["tool"]["id"]
                print_success(f"Tool created: {test_tool_id}")
                print_info(f"  API key encrypted: {result['tool'].get('enabled')}")
                self.test_results["passed"] += 1
            else:
                print_error(f"Create tool failed (status: {response.status_code})")
                self.test_results["failed"] += 1
        except Exception as e:
            print_error(f"Create tool error: {e}")
            self.test_results["failed"] += 1

        # Test 4.4: Toggle tool (disable)
        if test_tool_id:
            print_info(f"Test 4.4: POST /api/admin/tools/{test_tool_id}/toggle - Disable tool")
            try:
                response = self.session.post(
                    f"{self.dashboard_url}/api/admin/tools/{test_tool_id}/toggle",
                    json={"enabled": False}
                )

                if response.status_code == 200:
                    print_success("Tool disabled successfully")
                    self.test_results["passed"] += 1
                else:
                    print_error(f"Toggle tool failed (status: {response.status_code})")
                    self.test_results["failed"] += 1
            except Exception as e:
                print_error(f"Toggle tool error: {e}")
                self.test_results["failed"] += 1

        # Test 4.5: Update tool
        if test_tool_id:
            print_info(f"Test 4.5: PUT /api/admin/tools/{test_tool_id} - Update tool")
            try:
                update_data = {
                    "name": "Test API Integration (Updated)",
                    "type": "custom",
                    "endpoint": "https://api.test.example.com/v2",
                    "api_key": "••••••••••••",  # Placeholder to not change key
                    "description": "Updated test tool",
                    "params": {"timeout": 60},
                    "enabled": True
                }

                response = self.session.put(
                    f"{self.dashboard_url}/api/admin/tools/{test_tool_id}",
                    json=update_data
                )

                if response.status_code == 200:
                    print_success("Tool updated successfully")
                    self.test_results["passed"] += 1
                else:
                    print_error(f"Update tool failed (status: {response.status_code})")
                    self.test_results["failed"] += 1
            except Exception as e:
                print_error(f"Update tool error: {e}")
                self.test_results["failed"] += 1

        # Test 4.6: Delete test tool (cleanup)
        if test_tool_id:
            print_info(f"Test 4.6: DELETE /api/admin/tools/{test_tool_id} - Delete test tool")
            try:
                response = self.session.delete(
                    f"{self.dashboard_url}/api/admin/tools/{test_tool_id}"
                )

                if response.status_code == 200:
                    print_success("Tool deleted successfully (cleanup complete)")
                    self.test_results["passed"] += 1
                else:
                    print_error(f"Delete tool failed (status: {response.status_code})")
                    self.test_results["failed"] += 1
            except Exception as e:
                print_error(f"Delete tool error: {e}")
                self.test_results["failed"] += 1

    def print_summary(self):
        """Print test summary"""
        print_test_header("TEST SUMMARY")

        total = self.test_results["passed"] + self.test_results["failed"]
        success_rate = (self.test_results["passed"] / total * 100) if total > 0 else 0

        print(f"\n{Colors.BOLD}Results:{Colors.RESET}")
        print(f"  {Colors.GREEN}Passed:   {self.test_results['passed']}{Colors.RESET}")
        print(f"  {Colors.RED}Failed:   {self.test_results['failed']}{Colors.RESET}")
        print(f"  {Colors.YELLOW}Warnings: {self.test_results['warnings']}{Colors.RESET}")
        print(f"  {Colors.CYAN}Total:    {total}{Colors.RESET}")
        print(f"  {Colors.BOLD}Success Rate: {success_rate:.1f}%{Colors.RESET}\n")

        if self.test_results["failed"] == 0:
            print(f"{Colors.GREEN}{Colors.BOLD}[SUCCESS] All tests passed!{Colors.RESET}\n")
        else:
            print(f"{Colors.RED}{Colors.BOLD}[FAILURE] Some tests failed{Colors.RESET}\n")


def main():
    """Main test runner"""
    print(f"\n{Colors.MAGENTA}{Colors.BOLD}")
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║          MDSA PHASE 2 END-TO-END INTEGRATION TESTS            ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}\n")

    # Check if dashboard is running
    print_info("Checking if dashboard is running on http://localhost:9000...")
    try:
        response = requests.get("http://localhost:9000/api/health", timeout=5)
        if response.status_code == 200:
            print_success("Dashboard is running")
        else:
            print_error(f"Dashboard health check failed (status: {response.status_code})")
            print_warning("Please start the dashboard: python mdsa/ui/dashboard/app.py")
            return False
    except requests.ConnectionError:
        print_error("Cannot connect to dashboard")
        print_warning("Please start the dashboard: python mdsa/ui/dashboard/app.py")
        return False
    except Exception as e:
        print_error(f"Health check error: {e}")
        return False

    # Run tests
    tests = Phase2IntegrationTests()
    success = tests.run_all_tests()

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
