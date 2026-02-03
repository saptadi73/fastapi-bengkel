# 🔐 Login with Roles Documentation

## Overview
Endpoint login sekarang mengembalikan data roles user untuk mengetahui role apa saja yang dimiliki user tersebut.

---

## Login Endpoint

**Endpoint:** `POST /auth/login`  
**Description:** Login user dan mendapatkan access token beserta data user termasuk roles  
**Auth Required:** No

### Request Body
```json
{
  "username": "john_doe",
  "password": "your_password"
}
```

### Response Success
```json
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "username": "john_doe",
      "email": "john@example.com",
      "is_active": true,
      "roles": [
        {
          "id": "role-uuid-1",
          "name": "admin"
        },
        {
          "id": "role-uuid-2",
          "name": "mechanic"
        }
      ]
    }
  }
}
```

### Response Error (401)
```json
{
  "status": "error",
  "message": "Invalid username or password"
}
```

---

## Frontend Implementation

### 1. Login Function (JavaScript/TypeScript)

```javascript
async function login(username, password) {
  try {
    const response = await fetch('/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        username: username,
        password: password
      })
    });

    const result = await response.json();

    if (result.status === 'success') {
      const { access_token, user } = result.data;
      
      // Store token
      localStorage.setItem('token', access_token);
      
      // Store user data including roles
      localStorage.setItem('user', JSON.stringify(user));
      
      // Get role names
      const roleNames = user.roles.map(role => role.name);
      console.log('User roles:', roleNames);
      
      return {
        success: true,
        token: access_token,
        user: user,
        roles: roleNames
      };
    } else {
      return {
        success: false,
        message: result.message
      };
    }
  } catch (error) {
    console.error('Login error:', error);
    return {
      success: false,
      message: 'Network error'
    };
  }
}

// Usage
const loginResult = await login('john_doe', 'password123');
if (loginResult.success) {
  console.log('Logged in as:', loginResult.user.username);
  console.log('With roles:', loginResult.roles);
}
```

---

### 2. React Login Component

```jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function LoginForm() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const response = await fetch('/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
      });

      const result = await response.json();

      if (result.status === 'success') {
        const { access_token, user } = result.data;
        
        // Store in localStorage
        localStorage.setItem('token', access_token);
        localStorage.setItem('user', JSON.stringify(user));
        
        // Check user roles and redirect accordingly
        const roleNames = user.roles.map(r => r.name);
        
        if (roleNames.includes('admin')) {
          navigate('/admin/dashboard');
        } else if (roleNames.includes('mechanic')) {
          navigate('/mechanic/dashboard');
        } else if (roleNames.includes('cashier')) {
          navigate('/cashier/dashboard');
        } else {
          navigate('/dashboard');
        }
      } else {
        setError(result.message);
      }
    } catch (err) {
      setError('Network error. Please try again.');
    }
  };

  return (
    <form onSubmit={handleLogin}>
      <h2>Login</h2>
      
      {error && <div className="error">{error}</div>}
      
      <input
        type="text"
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        required
      />
      
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />
      
      <button type="submit">Login</button>
    </form>
  );
}

export default LoginForm;
```

---

### 3. Role-Based Access Control (RBAC)

```javascript
// auth-utils.js

// Get current user from localStorage
export function getCurrentUser() {
  const userStr = localStorage.getItem('user');
  return userStr ? JSON.parse(userStr) : null;
}

// Get user roles
export function getUserRoles() {
  const user = getCurrentUser();
  return user ? user.roles.map(role => role.name) : [];
}

// Check if user has specific role
export function hasRole(roleName) {
  const roles = getUserRoles();
  return roles.includes(roleName);
}

// Check if user has any of the specified roles
export function hasAnyRole(roleNames) {
  const roles = getUserRoles();
  return roleNames.some(roleName => roles.includes(roleName));
}

// Check if user has all of the specified roles
export function hasAllRoles(roleNames) {
  const roles = getUserRoles();
  return roleNames.every(roleName => roles.includes(roleName));
}

// Usage examples:
if (hasRole('admin')) {
  console.log('User is admin');
}

if (hasAnyRole(['admin', 'mechanic'])) {
  console.log('User is admin or mechanic');
}

if (hasAllRoles(['admin', 'manager'])) {
  console.log('User has both admin and manager roles');
}
```

---

### 4. Protected Route Component (React)

```jsx
import React from 'react';
import { Navigate } from 'react-router-dom';
import { getCurrentUser, hasAnyRole } from './auth-utils';

function ProtectedRoute({ children, allowedRoles }) {
  const user = getCurrentUser();
  
  // Check if user is logged in
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  
  // If allowedRoles is specified, check if user has required role
  if (allowedRoles && allowedRoles.length > 0) {
    if (!hasAnyRole(allowedRoles)) {
      return <Navigate to="/unauthorized" replace />;
    }
  }
  
  return children;
}

// Usage in routes:
<Route 
  path="/admin" 
  element={
    <ProtectedRoute allowedRoles={['admin']}>
      <AdminDashboard />
    </ProtectedRoute>
  } 
/>

<Route 
  path="/mechanic" 
  element={
    <ProtectedRoute allowedRoles={['mechanic', 'admin']}>
      <MechanicDashboard />
    </ProtectedRoute>
  } 
/>
```

---

### 5. Conditional UI Rendering

```jsx
import { hasRole, getUserRoles } from './auth-utils';

function Dashboard() {
  const roles = getUserRoles();
  
  return (
    <div>
      <h1>Dashboard</h1>
      
      {/* Show admin panel only for admins */}
      {hasRole('admin') && (
        <div className="admin-panel">
          <h2>Admin Controls</h2>
          <button>Manage Users</button>
          <button>System Settings</button>
        </div>
      )}
      
      {/* Show mechanic tools for mechanics */}
      {hasRole('mechanic') && (
        <div className="mechanic-tools">
          <h2>Mechanic Tools</h2>
          <button>View Work Orders</button>
          <button>Update Status</button>
        </div>
      )}
      
      {/* Show cashier tools for cashiers */}
      {hasRole('cashier') && (
        <div className="cashier-tools">
          <h2>Cashier Tools</h2>
          <button>Process Payment</button>
          <button>View Invoices</button>
        </div>
      )}
      
      {/* Display all user roles */}
      <div className="user-info">
        <p>Your roles: {roles.join(', ')}</p>
      </div>
    </div>
  );
}
```

---

### 6. Vue.js Implementation

```javascript
// Vue 3 Composition API
import { ref } from 'vue';
import { useRouter } from 'vue-router';

export function useAuth() {
  const router = useRouter();
  const error = ref('');
  const user = ref(null);
  const isLoading = ref(false);

  const login = async (username, password) => {
    isLoading.value = true;
    error.value = '';

    try {
      const response = await fetch('/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
      });

      const result = await response.json();

      if (result.status === 'success') {
        const { access_token, user: userData } = result.data;
        
        localStorage.setItem('token', access_token);
        localStorage.setItem('user', JSON.stringify(userData));
        
        user.value = userData;
        
        // Redirect based on role
        const roleNames = userData.roles.map(r => r.name);
        
        if (roleNames.includes('admin')) {
          router.push('/admin/dashboard');
        } else if (roleNames.includes('mechanic')) {
          router.push('/mechanic/dashboard');
        } else {
          router.push('/dashboard');
        }
        
        return true;
      } else {
        error.value = result.message;
        return false;
      }
    } catch (err) {
      error.value = 'Network error. Please try again.';
      return false;
    } finally {
      isLoading.value = false;
    }
  };

  const hasRole = (roleName) => {
    if (!user.value) {
      const userStr = localStorage.getItem('user');
      user.value = userStr ? JSON.parse(userStr) : null;
    }
    return user.value?.roles.some(role => role.name === roleName) || false;
  };

  return {
    login,
    hasRole,
    error,
    user,
    isLoading
  };
}
```

---

## Common Use Cases

### 1. Display User Info with Roles

```javascript
function displayUserInfo() {
  const user = JSON.parse(localStorage.getItem('user'));
  
  if (user) {
    console.log(`Username: ${user.username}`);
    console.log(`Email: ${user.email}`);
    console.log(`Roles:`);
    
    user.roles.forEach(role => {
      console.log(`  - ${role.name} (ID: ${role.id})`);
    });
  }
}
```

---

### 2. Role-Based Menu Items

```javascript
function getMenuItems() {
  const user = JSON.parse(localStorage.getItem('user'));
  const roleNames = user.roles.map(r => r.name);
  
  const menuItems = [
    { label: 'Dashboard', path: '/dashboard', roles: ['all'] }
  ];
  
  // Add admin menu items
  if (roleNames.includes('admin')) {
    menuItems.push(
      { label: 'User Management', path: '/admin/users', roles: ['admin'] },
      { label: 'Role Management', path: '/admin/roles', roles: ['admin'] },
      { label: 'System Settings', path: '/admin/settings', roles: ['admin'] }
    );
  }
  
  // Add mechanic menu items
  if (roleNames.includes('mechanic')) {
    menuItems.push(
      { label: 'Work Orders', path: '/mechanic/workorders', roles: ['mechanic'] },
      { label: 'Service History', path: '/mechanic/history', roles: ['mechanic'] }
    );
  }
  
  // Add cashier menu items
  if (roleNames.includes('cashier')) {
    menuItems.push(
      { label: 'Invoices', path: '/cashier/invoices', roles: ['cashier'] },
      { label: 'Payments', path: '/cashier/payments', roles: ['cashier'] }
    );
  }
  
  return menuItems;
}
```

---

### 3. API Request with Token

```javascript
async function makeAuthenticatedRequest(endpoint, options = {}) {
  const token = localStorage.getItem('token');
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(endpoint, {
    ...options,
    headers
  });
  
  // Check if token expired
  if (response.status === 401) {
    // Clear local storage and redirect to login
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login';
    return null;
  }
  
  return response.json();
}

// Usage
const data = await makeAuthenticatedRequest('/api/protected-endpoint', {
  method: 'GET'
});
```

---

## Response Structure

### Success Response
```typescript
interface LoginSuccessResponse {
  status: "success";
  message: string;
  data: {
    access_token: string;
    token_type: string;
    user: {
      id: string;
      username: string;
      email: string;
      is_active: boolean;
      roles: Array<{
        id: string;
        name: string;
      }>;
    };
  };
}
```

### Error Response
```typescript
interface LoginErrorResponse {
  status: "error";
  message: string;
}
```

---

## Security Best Practices

1. **Store Token Securely:** Gunakan httpOnly cookies jika memungkinkan
2. **Don't Store Password:** Jangan pernah simpan password di localStorage
3. **Clear on Logout:** Hapus token dan user data saat logout
4. **Validate Token:** Selalu validate token di backend untuk setiap request
5. **Role Verification:** Jangan hanya mengandalkan role dari frontend, validate juga di backend

---

## Logout Implementation

```javascript
function logout() {
  // Clear all auth data
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  
  // Redirect to login
  window.location.href = '/login';
}

// Or with React Router
import { useNavigate } from 'react-router-dom';

function LogoutButton() {
  const navigate = useNavigate();
  
  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };
  
  return <button onClick={handleLogout}>Logout</button>;
}
```

---

## Testing Login Response

### Using curl
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "john_doe", "password": "password123"}'
```

### Using Postman
1. Method: POST
2. URL: `http://localhost:8000/auth/login`
3. Body (JSON):
   ```json
   {
     "username": "john_doe",
     "password": "password123"
   }
   ```

---

**Last Updated:** January 4, 2026
