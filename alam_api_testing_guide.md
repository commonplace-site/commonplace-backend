# Alam.py API Testing Guide

## Base URL
```
http://localhost:8000/api/v1/alam
```

## Testing Tools
1. Postman Collection
2. cURL Commands
3. Python Requests
4. JavaScript Fetch/Axios

## Authentication Flow

### 1. User Registration
```bash
curl -X POST http://localhost:8000/api/v1/alam/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test@123",
    "first_name": "Test",
    "last_name": "User",
    "phone_number": "+1234567890"
  }'
```

### 2. User Login
```bash
curl -X POST http://localhost:8000/api/v1/alam/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test@123"
  }'
```

Response:
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
        "id": "user_uuid",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "is_active": true
    }
}
```

## Business Management

### 1. Create Business
```bash
curl -X POST http://localhost:8000/api/v1/alam/business \
  -H "Authorization: Bearer your_access_token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Business",
    "license_key": "TEST123",
    "established_date": "2024-01-01T00:00:00Z",
    "renewal_due_date": "2025-01-01T00:00:00Z"
  }'
```

### 2. Get Business Details
```bash
curl -X GET http://localhost:8000/api/v1/alam/business/{business_id} \
  -H "Authorization: Bearer your_access_token"
```

## Learning Module Management

### 1. Create Learning Module
```bash
curl -X POST http://localhost:8000/api/v1/alam/learning-modules \
  -H "Authorization: Bearer your_access_token" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Module",
    "description": "Test Description",
    "business_id": "business_uuid",
    "content": "Test content"
  }'
```

### 2. List Business Learning Modules
```bash
curl -X GET http://localhost:8000/api/v1/alam/business/{business_id}/learning-modules \
  -H "Authorization: Bearer your_access_token"
```

## Python Integration Example

```python
import requests

BASE_URL = "http://localhost:8000/api/v1/alam"

def login(email, password):
    response = requests.post(
        f"{BASE_URL}/login",
        json={"email": email, "password": password}
    )
    return response.json()

def create_business(token, business_data):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/business",
        headers=headers,
        json=business_data
    )
    return response.json()

# Example usage
token = login("test@example.com", "Test@123")["access_token"]
business = create_business(token, {
    "name": "Test Business",
    "license_key": "TEST123",
    "established_date": "2024-01-01T00:00:00Z",
    "renewal_due_date": "2025-01-01T00:00:00Z"
})
```

## JavaScript Integration Example

```javascript
const BASE_URL = "http://localhost:8000/api/v1/alam";

async function login(email, password) {
    const response = await fetch(`${BASE_URL}/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
    });
    return response.json();
}

async function createBusiness(token, businessData) {
    const response = await fetch(`${BASE_URL}/business`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(businessData)
    });
    return response.json();
}

// Example usage
async function main() {
    const { access_token } = await login("test@example.com", "Test@123");
    const business = await createBusiness(access_token, {
        name: "Test Business",
        license_key: "TEST123",
        established_date: "2024-01-01T00:00:00Z",
        renewal_due_date: "2025-01-01T00:00:00Z"
    });
}
```

## Postman Collection

```json
{
  "info": {
    "name": "Alam API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Authentication",
      "item": [
        {
          "name": "Register",
          "request": {
            "method": "POST",
            "url": "http://localhost:8000/api/v1/alam/register",
            "body": {
              "mode": "raw",
              "raw": "{\n    \"email\": \"test@example.com\",\n    \"password\": \"Test@123\",\n    \"first_name\": \"Test\",\n    \"last_name\": \"User\",\n    \"phone_number\": \"+1234567890\"\n}",
              "options": {
                "raw": {
                  "language": "json"
                }
              }
            }
          }
        },
        {
          "name": "Login",
          "request": {
            "method": "POST",
            "url": "http://localhost:8000/api/v1/alam/login",
            "body": {
              "mode": "raw",
              "raw": "{\n    \"email\": \"test@example.com\",\n    \"password\": \"Test@123\"\n}",
              "options": {
                "raw": {
                  "language": "json"
                }
              }
            }
          }
        }
      ]
    }
  ]
}
```

## Testing Checklist

1. Authentication
   - [ ] Register new user
   - [ ] Login with credentials
   - [ ] Verify token expiration
   - [ ] Test refresh token

2. Business Management
   - [ ] Create business
   - [ ] Get business details
   - [ ] Update business
   - [ ] List user's businesses

3. Learning Modules
   - [ ] Create module
   - [ ] Get module details
   - [ ] Update module
   - [ ] List business modules

4. Error Handling
   - [ ] Test invalid credentials
   - [ ] Test missing required fields
   - [ ] Test invalid data types
   - [ ] Test unauthorized access

## Common Test Cases

1. Authentication
```python
def test_registration():
    response = requests.post(
        f"{BASE_URL}/register",
        json={
            "email": "test@example.com",
            "password": "Test@123",
            "first_name": "Test",
            "last_name": "User",
            "phone_number": "+1234567890"
        }
    )
    assert response.status_code == 200
    assert "id" in response.json()

def test_login():
    response = requests.post(
        f"{BASE_URL}/login",
        json={
            "email": "test@example.com",
            "password": "Test@123"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
```

2. Business Management
```python
def test_create_business():
    token = login("test@example.com", "Test@123")["access_token"]
    response = requests.post(
        f"{BASE_URL}/business",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Test Business",
            "license_key": "TEST123",
            "established_date": "2024-01-01T00:00:00Z",
            "renewal_due_date": "2025-01-01T00:00:00Z"
        }
    )
    assert response.status_code == 200
    assert "id" in response.json()
```

## Environment Variables

```bash
# .env file
ALAM_API_URL=http://localhost:8000/api/v1/alam
ALAM_TEST_EMAIL=test@example.com
ALAM_TEST_PASSWORD=Test@123
```

## Rate Limiting Test

```python
def test_rate_limiting():
    for _ in range(101):  # Should fail on 101st request
        response = requests.post(
            f"{BASE_URL}/login",
            json={
                "email": "test@example.com",
                "password": "Test@123"
            }
        )
    assert response.status_code == 429  # Too Many Requests
```

## Security Testing

1. Token Validation
```python
def test_invalid_token():
    response = requests.get(
        f"{BASE_URL}/profile",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
```

2. Password Requirements
```python
def test_password_requirements():
    response = requests.post(
        f"{BASE_URL}/register",
        json={
            "email": "test@example.com",
            "password": "weak",  # Too short
            "first_name": "Test",
            "last_name": "User",
            "phone_number": "+1234567890"
        }
    )
    assert response.status_code == 422
```

## Integration Testing

```python
def test_full_flow():
    # 1. Register
    register_response = requests.post(
        f"{BASE_URL}/register",
        json={
            "email": "test@example.com",
            "password": "Test@123",
            "first_name": "Test",
            "last_name": "User",
            "phone_number": "+1234567890"
        }
    )
    assert register_response.status_code == 200
    
    # 2. Login
    login_response = requests.post(
        f"{BASE_URL}/login",
        json={
            "email": "test@example.com",
            "password": "Test@123"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # 3. Create Business
    business_response = requests.post(
        f"{BASE_URL}/business",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Test Business",
            "license_key": "TEST123",
            "established_date": "2024-01-01T00:00:00Z",
            "renewal_due_date": "2025-01-01T00:00:00Z"
        }
    )
    assert business_response.status_code == 200
    business_id = business_response.json()["id"]
    
    # 4. Create Learning Module
    module_response = requests.post(
        f"{BASE_URL}/learning-modules",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test Module",
            "description": "Test Description",
            "business_id": business_id,
            "content": "Test content"
        }
    )
    assert module_response.status_code == 200
``` 