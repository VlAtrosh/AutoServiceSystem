import requests
import sys

def test_health():
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            print('✅ Health check: OK')
            return True
        else:
            print(f'❌ Health check: status {response.status_code}')
            return False
    except Exception as e:
        print(f'❌ Health check failed: {e}')
        return False

def test_main_page():
    try:
        response = requests.get('http://localhost:8000/', timeout=5)
        if response.status_code == 200:
            print('✅ Main page: OK')
            return True
        else:
            print(f'❌ Main page: status {response.status_code}')
            return False
    except Exception as e:
        print(f'❌ Main page failed: {e}')
        return False

def test_swagger():
    try:
        response = requests.get('http://localhost:8000/docs', timeout=5)
        if response.status_code == 200:
            print('✅ Swagger UI: OK')
            return True
        else:
            print(f'❌ Swagger UI: status {response.status_code}')
            return False
    except Exception as e:
        print(f'❌ Swagger UI failed: {e}')
        return False

def test_login_success():
    try:
        response = requests.post(
            'http://localhost:8000/api/v1/auth/login',
            json={'username': 'client1', 'password': '123456'},
            timeout=5
        )
        if response.status_code == 200 and 'access_token' in response.json():
            print('✅ Login (success): OK')
            return True
        else:
            print(f'❌ Login (success): status {response.status_code}')
            return False
    except Exception as e:
        print(f'❌ Login (success) failed: {e}')
        return False

def test_login_fail():
    try:
        response = requests.post(
            'http://localhost:8000/api/v1/auth/login',
            json={'username': 'wrong', 'password': 'wrong'},
            timeout=5
        )
        if response.status_code == 401:
            print('✅ Login (fail): OK')
            return True
        else:
            print(f'❌ Login (fail): status {response.status_code} (expected 401)')
            return False
    except Exception as e:
        print(f'❌ Login (fail) failed: {e}')
        return False

if __name__ == '__main__':
    print('=' * 50)
    print('SMOKE-TESTS for AutoServiceSystem')
    print('=' * 50)
    print()
    
    results = []
    results.append(test_health())
    results.append(test_main_page())
    results.append(test_swagger())
    results.append(test_login_success())
    results.append(test_login_fail())
    
    print()
    print('=' * 50)
    if all(results):
        print('✅ ALL TESTS PASSED!')
        sys.exit(0)
    else:
        print('❌ SOME TESTS FAILED!')
        sys.exit(1)