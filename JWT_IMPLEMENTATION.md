# JWT Token Authentication and Role-Based Authorization Implementation

## Overview

This implementation adds JWT token authentication and role-based authorization to the `run_custom_product_query` endpoint in the API backend. The JWT token is passed from the frontend UI and verified on the backend to ensure only authorized users can execute product queries.

## Changes Made

### Backend Changes (`api-backend/main.py`)

1. **Added JWT Dependencies**:
   - Added `jwt` import for token verification
   - Added `Header` from FastAPI for authorization header handling
   - Added `Optional` from typing for optional parameters

2. **JWT Helper Functions**:
   - `verify_jwt_token()`: Verifies JWT token from Authorization header
   - `check_user_role()`: Checks if user has required roles

3. **Updated `run_custom_product_query` Endpoint**:
   - Added JWT token verification
   - Added role-based authorization check
   - Required roles: `["product_analyst", "admin", "data_analyst"]`
   - Added logging for security audit trail

4. **Added PyJWT Dependency** (`pyproject.toml`):
   - Added `PyJWT>=2.8.0` to dependencies

### Frontend Changes (`ui-frontend/app.py`)

1. **Updated `nlp_product_search()` Function**:
   - Modified API call to include JWT token in Authorization header
   - Added proper error handling for 401 (Unauthorized) and 403 (Forbidden) responses
   - Added automatic logout on authentication failure
   - Added user-friendly error messages for authorization failures

## Security Features

### JWT Token Verification
- Extracts token from `Authorization: Bearer <token>` header
- Decodes JWT token (currently without signature verification for Keycloak compatibility)
- Extracts user information and roles from token claims

### Role-Based Authorization
- Checks both realm roles and client-specific roles
- Required roles for product queries:
  - `product_analyst`: Users who can analyze product data
  - `admin`: System administrators
  - `data_analyst`: General data analysts

### Error Handling
- **401 Unauthorized**: Missing or invalid token
- **403 Forbidden**: Valid token but insufficient permissions
- Detailed error messages for debugging
- Security logging for audit trails

## Usage

### Setting Up User Roles in Keycloak

1. **Realm Roles**:
   - Create roles: `product_analyst`, `admin`, `data_analyst`
   - Assign appropriate roles to users

2. **Client Roles** (for `askdataclient`):
   - Create same roles at client level if needed
   - Assign to users as required

### Testing the Implementation

1. **Run the Test Script**:
   ```bash
   python test_jwt_implementation.py
   ```

2. **Manual Testing**:
   - Log in to the UI with a user having appropriate roles
   - Navigate to Product Search → Natural Language Query
   - Generate and run a SQL query
   - Verify successful execution

3. **Testing Authorization Failures**:
   - Log in with a user without required roles
   - Attempt to run a product query
   - Should receive "Access denied" error

## API Endpoint Details

### `POST /run_custom_product_query`

**Headers Required**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "sql_query": "SELECT * FROM financial_products WHERE product_type = 'credit_card'"
}
```

**Success Response (200)**:
```json
{
  "results": [
    {
      "product_id": 1,
      "product_name": "Premium Credit Card",
      "product_type": "credit_card"
    }
  ]
}
```

**Error Responses**:

**401 Unauthorized**:
```json
{
  "detail": "Authorization header missing"
}
```

**403 Forbidden**:
```json
{
  "detail": "Access denied. Required roles: ['product_analyst', 'admin', 'data_analyst']. User roles: ['user']"
}
```

## Security Considerations

### Current Implementation
- JWT signature verification is disabled for Keycloak compatibility
- Tokens are decoded without cryptographic verification

### Production Recommendations
1. **Enable Signature Verification**:
   - Obtain Keycloak's public key
   - Verify JWT signatures cryptographically
   
2. **Token Expiration**:
   - Implement token refresh mechanism
   - Handle expired tokens gracefully

3. **Rate Limiting**:
   - Add rate limiting to prevent abuse
   - Monitor failed authentication attempts

4. **Audit Logging**:
   - Log all authentication attempts
   - Monitor role-based access patterns

## Troubleshooting

### Common Issues

1. **"Authorization header missing"**:
   - Ensure frontend is passing JWT token
   - Check token is stored in session state

2. **"Access denied" with correct roles**:
   - Verify role names match exactly
   - Check both realm_access and resource_access in token

3. **"Invalid token" errors**:
   - Check token format and structure
   - Verify token hasn't expired

### Debug Steps

1. **Check Token Contents**:
   ```python
   import jwt
   decoded = jwt.decode(token, options={"verify_signature": False})
   print(decoded)
   ```

2. **Verify User Roles**:
   - Check Keycloak user role assignments
   - Verify token contains expected role claims

3. **API Logs**:
   - Check backend logs for detailed error messages
   - Look for JWT verification failures

## Future Enhancements

1. **Granular Permissions**:
   - Add table-level or column-level permissions
   - Implement query filtering based on user roles

2. **Dynamic Role Configuration**:
   - Make required roles configurable
   - Support role hierarchies

3. **Token Caching**:
   - Cache decoded tokens to improve performance
   - Implement token blacklisting for logout

4. **Multi-Factor Authentication**:
   - Add additional security layers
   - Implement step-up authentication for sensitive operations