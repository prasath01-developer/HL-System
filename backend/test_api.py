"""
Test script to verify API endpoints are working
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_csrf_token():
    """Test CSRF token endpoint"""
    print("=" * 50)
    print("Testing CSRF Token Endpoint")
    print("=" * 50)
    
    session = requests.Session()
    response = session.get(f"{BASE_URL}/api/csrf-token/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    return session

def test_login(session):
    """Test login endpoint"""
    print("=" * 50)
    print("Testing Login Endpoint")
    print("=" * 50)
    
    # First, get a page to set CSRF cookie
    session.get(f"{BASE_URL}/")
    
    # Now try to login
    csrf_token = session.cookies.get('csrftoken', '')
    
    headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf_token
    }
    
    data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    response = session.post(
        f"{BASE_URL}/api/login/",
        json=data,
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    return response.json()

def test_admin_dashboard(session):
    """Test admin dashboard endpoint"""
    print("=" * 50)
    print("Testing Admin Dashboard Stats Endpoint")
    print("=" * 50)
    
    response = session.get(f"{BASE_URL}/api/admin/dashboard/stats/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_urls():
    """Test that all URLs return 200"""
    print("=" * 50)
    print("Testing URL Status Codes")
    print("=" * 50)
    
    urls = [
        "/",
        "/login/",
        "/api/csrf-token/",
    ]
    
    for url in urls:
        response = requests.get(f"{BASE_URL}{url}")
        print(f"{url}: {response.status_code}")
    print()

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("HOSTEL LOCK SYSTEM API TEST")
    print("=" * 50 + "\n")
    
    # Test URL status codes
    test_urls()
    
    # Test CSRF token
    session = test_csrf_token()
    
    # Test login
    login_result = test_login(session)
    
    # If login successful, test admin dashboard
    if login_result.get('success'):
        test_admin_dashboard(session)
    
    print("\n✅ All tests completed!")

