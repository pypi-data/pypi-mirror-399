import requests

url = "http://localhost:8080/compiler"

# 1. GET Request
print("Testing GET...")
try:
    r = requests.get(url)
    print(f"Status: {r.status_code}")
    if "Type your ShellLite code here" in r.text:
        print("GET Request Successful")
    else:
        print("GET Request Failed: Content mismatch")
        print(r.text[:500]) # Print first 500 chars
except Exception as e:
    print(f"Server error: {e}")

# 2. POST Request (Running Code)
print("\nTesting POST (Run Code)...")
code = 'say "Hello SSR"'
try:
    r = requests.post(url, data={'code': code})
    print(f"Status: {r.status_code}")
    if "Hello SSR" in r.text:
        print("POST Request Verified: Output found in response")
    else:
        print("POST Request Failed: Output not found")
        print(r.text[:500])
except Exception as e:
    print(f"Server error: {e}")
