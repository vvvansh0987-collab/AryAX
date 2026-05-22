import requests
import time
import sys

URL = "http://127.0.0.1:5054"

def test_endpoints():
    print(f"Testing AryaX system at {URL}...")
    endpoints = [
        ("/", 200),
        ("/admin-portal/", 200),
        ("/api/history/load?username=test", 404),
        ("/api/user/credits?username=test", 200),
    ]
    
    passed = 0
    for path, expected in endpoints:
        try:
            r = requests.get(f"{URL}{path}", timeout=5)
            if r.status_code == expected:
                print(f"[OK] {path} returned {r.status_code}")
                passed += 1
            else:
                print(f"[FAIL] {path} returned {r.status_code} (expected {expected})")
        except Exception as e:
            print(f"[FAIL] {path} failed: {e}")
            
    print(f"\nResults: {passed}/{len(endpoints)} passed.")
    if passed == len(endpoints):
        print("System is stable and ready for production! [READY]")
        sys.exit(0)
    else:
        print("System has errors!")
        sys.exit(1)

if __name__ == "__main__":
    test_endpoints()
