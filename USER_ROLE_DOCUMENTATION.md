# 📚 User & Role Management API Documentation

## Overview
Dokumentasi ini menjelaskan endpoints untuk mengelola Users, Roles, dan relasi Role-User dalam sistem.

---

## 🔐 Authentication
Beberapa endpoint memerlukan JWT token. Sertakan token di header:
```
Authorization: Bearer <your_token>
```

---

## 📑 Table of Contents
- [User Management](#user-management)
- [Role Management](#role-management)
- [Role-User Management](#role-user-management)

---

## 👤 User Management

Base URL: `/users`

### 1. Get All Users
**Endpoint:** `GET /users/`  
**Description:** Mengambil daftar semua users (untuk dropdown/selection di frontend)  
**Auth Required:** No

**Response Success:**
```json
{
  "status": "success",
  "message": "All users retrieved successfully",
  "data": [
    {
      "id": "uuid-string",
      "username": "john_doe",
      "email": "john@example.com",
      "is_active": true
    }
  ]
}
```

**Example Usage (JavaScript):**
```javascript
const response = await fetch('/users/', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json'
  }
});
const result = await response.json();
const users = result.data;
```

---

### 2. Get User by ID
**Endpoint:** `GET /users/{user_id}`  
**Description:** Mengambil detail user berdasarkan ID  
**Auth Required:** No

**Path Parameters:**
- `user_id` (UUID) - ID dari user yang ingin diambil

**Response Success:**
```json
{
  "status": "success",
  "message": "User retrieved successfully",
  "data": {
    "id": "uuid-string",
    "username": "john_doe",
    "email": "john@example.com",
    "is_active": true
  }
}
```

**Response Error (404):**
```json
{
  "status": "error",
  "message": "User not found"
}
```

**Example Usage (JavaScript):**
```javascript
const userId = "550e8400-e29b-41d4-a716-446655440000";
const response = await fetch(`/users/${userId}`, {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json'
  }
});
const result = await response.json();
```

---

## 🎭 Role Management

Base URL: `/roles`

### 1. Get All Roles
**Endpoint:** `GET /roles/`  
**Description:** Mengambil daftar semua roles (untuk dropdown/selection di frontend)  
**Auth Required:** No

**Response Success:**
```json
{
  "status": "success",
  "message": "Roles retrieved successfully",
  "data": [
    {
      "id": "uuid-string",
      "name": "admin"
    },
    {
      "id": "uuid-string",
      "name": "mechanic"
    },
    {
      "id": "uuid-string",
      "name": "cashier"
    }
  ]
}
```

**Example Usage (JavaScript):**
```javascript
const response = await fetch('/roles/', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json'
  }
});
const result = await response.json();
const roles = result.data;

// Untuk populate dropdown
roles.forEach(role => {
  console.log(`Role: ${role.name} (ID: ${role.id})`);
});
```

---

### 2. Get Role by ID
**Endpoint:** `GET /roles/{role_id}`  
**Description:** Mengambil detail role berdasarkan ID  
**Auth Required:** No

**Path Parameters:**
- `role_id` (UUID) - ID dari role yang ingin diambil

**Response Success:**
```json
{
  "status": "success",
  "message": "Role retrieved successfully",
  "data": {
    "id": "uuid-string",
    "name": "admin"
  }
}
```

**Response Error (404):**
```json
{
  "status": "error",
  "message": "Role not found"
}
```

---

### 3. Create New Role
**Endpoint:** `POST /roles/`  
**Description:** Membuat role baru  
**Auth Required:** No (tapi sebaiknya Yes untuk production)

**Request Body:**
```json
{
  "name": "warehouse_manager"
}
```

**Response Success:**
```json
{
  "status": "success",
  "message": "Role created successfully",
  "data": {
    "id": "uuid-string",
    "name": "warehouse_manager"
  }
}
```

**Example Usage (JavaScript):**
```javascript
const response = await fetch('/roles/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'warehouse_manager'
  })
});
const result = await response.json();
```

---

### 4. Update Role
**Endpoint:** `PUT /roles/{role_id}`  
**Description:** Mengupdate nama role  
**Auth Required:** No (tapi sebaiknya Yes untuk production)

**Path Parameters:**
- `role_id` (UUID) - ID dari role yang ingin diupdate

**Request Body:**
```json
{
  "name": "senior_mechanic"
}
```

**Response Success:**
```json
{
  "status": "success",
  "message": "Role updated successfully",
  "data": {
    "id": "uuid-string",
    "name": "senior_mechanic"
  }
}
```

---

### 5. Delete Role
**Endpoint:** `DELETE /roles/{role_id}`  
**Description:** Menghapus role  
**Auth Required:** No (tapi sebaiknya Yes untuk production)

**Path Parameters:**
- `role_id` (UUID) - ID dari role yang ingin dihapus

**Response Success:**
```json
{
  "status": "success",
  "message": "Role deleted successfully"
}
```

**Response Error (404):**
```json
{
  "status": "error",
  "message": "Role not found"
}
```

---

## 🔗 Role-User Management

Base URL: `/role-user`

### 1. Assign Role to User
**Endpoint:** `POST /role-user/assign?user_id={user_id}`  
**Description:** Menambahkan role ke user  
**Auth Required:** No

**Query Parameters:**
- `user_id` (UUID) - ID dari user yang akan diberi role

**Request Body:**
```json
{
  "role_id": "uuid-string"
}
```

**Response Success:**
```json
{
  "status": "success",
  "message": "Role assigned successfully"
}
```

**Response Error (400):**
```json
{
  "status": "error",
  "message": "Failed to assign role or role already assigned"
}
```

**Example Usage (JavaScript):**
```javascript
const userId = "550e8400-e29b-41d4-a716-446655440000";
const roleId = "660e8400-e29b-41d4-a716-446655440001";

const response = await fetch(`/role-user/assign?user_id=${userId}`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    role_id: roleId
  })
});
const result = await response.json();
```

---

### 2. Remove Role from User
**Endpoint:** `DELETE /role-user/remove?user_id={user_id}`  
**Description:** Menghapus role dari user  
**Auth Required:** No

**Query Parameters:**
- `user_id` (UUID) - ID dari user yang akan dihapus role-nya

**Request Body:**
```json
{
  "role_id": "uuid-string"
}
```

**Response Success:**
```json
{
  "status": "success",
  "message": "Role removed successfully"
}
```

**Response Error (404):**
```json
{
  "status": "error",
  "message": "Role not assigned to user"
}
```

**Example Usage (JavaScript):**
```javascript
const userId = "550e8400-e29b-41d4-a716-446655440000";
const roleId = "660e8400-e29b-41d4-a716-446655440001";

const response = await fetch(`/role-user/remove?user_id=${userId}`, {
  method: 'DELETE',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    role_id: roleId
  })
});
const result = await response.json();
```

---

### 3. Get User with Roles
**Endpoint:** `GET /role-user/user/{user_id}/roles`  
**Description:** Mengambil user beserta semua roles yang dimilikinya  
**Auth Required:** No

**Path Parameters:**
- `user_id` (UUID) - ID dari user

**Response Success:**
```json
{
  "status": "success",
  "message": "User roles retrieved successfully",
  "data": {
    "id": "uuid-string",
    "username": "john_doe",
    "email": "john@example.com",
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
```

**Response Error (404):**
```json
{
  "status": "error",
  "message": "User not found"
}
```

**Example Usage (JavaScript):**
```javascript
const userId = "550e8400-e29b-41d4-a716-446655440000";
const response = await fetch(`/role-user/user/${userId}/roles`, {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json'
  }
});
const result = await response.json();
const userWithRoles = result.data;
```

---

### 4. Get Users for Role
**Endpoint:** `GET /role-user/role/{role_id}/users`  
**Description:** Mengambil semua users yang memiliki role tertentu  
**Auth Required:** No

**Path Parameters:**
- `role_id` (UUID) - ID dari role

**Response Success:**
```json
{
  "status": "success",
  "message": "Role users retrieved successfully",
  "data": [
    {
      "id": "user-uuid-1",
      "username": "john_doe",
      "email": "john@example.com"
    },
    {
      "id": "user-uuid-2",
      "username": "jane_smith",
      "email": "jane@example.com"
    }
  ]
}
```

**Example Usage (JavaScript):**
```javascript
const roleId = "660e8400-e29b-41d4-a716-446655440001";
const response = await fetch(`/role-user/role/${roleId}/users`, {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json'
  }
});
const result = await response.json();
const usersWithThisRole = result.data;
```

---

### 5. Update User Roles (Replace All)
**Endpoint:** `PUT /role-user/user/{user_id}/roles`  
**Description:** Replace semua roles user dengan roles baru (menghapus roles lama)  
**Auth Required:** Yes (JWT Token required)

**Path Parameters:**
- `user_id` (UUID) - ID dari user

**Request Body:**
```json
{
  "role_ids": [
    "role-uuid-1",
    "role-uuid-2",
    "role-uuid-3"
  ]
}
```

**Response Success:**
```json
{
  "status": "success",
  "message": "User roles updated successfully",
  "data": {
    "id": "user-uuid",
    "username": "john_doe",
    "email": "john@example.com",
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
```

**Response Error (404):**
```json
{
  "status": "error",
  "message": "User not found or update failed"
}
```

**Example Usage (JavaScript):**
```javascript
const userId = "550e8400-e29b-41d4-a716-446655440000";
const token = "your-jwt-token";

const response = await fetch(`/role-user/user/${userId}/roles`, {
  method: 'PUT',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    role_ids: [
      "role-uuid-1",
      "role-uuid-2"
    ]
  })
});
const result = await response.json();
```

---

### 6. Get All Roles (Simplified)
**Endpoint:** `GET /role-user/roles`  
**Description:** Mengambil daftar semua roles (versi simplified untuk dropdown)  
**Auth Required:** No

**Response Success:**
```json
{
  "status": "success",
  "message": "All roles retrieved successfully",
  "data": [
    {
      "id": "uuid-string",
      "name": "admin"
    },
    {
      "id": "uuid-string",
      "name": "mechanic"
    }
  ]
}
```

**Example Usage (JavaScript):**
```javascript
const response = await fetch('/role-user/roles', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json'
  }
});
const result = await response.json();
const roles = result.data;
```

---

### 7. Get All Users with Roles
**Endpoint:** `GET /role-user/users-with-roles`  
**Description:** Mengambil semua users beserta roles masing-masing  
**Auth Required:** No

**Response Success:**
```json
{
  "status": "success",
  "message": "All users with roles retrieved successfully",
  "data": [
    {
      "id": "user-uuid-1",
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
    },
    {
      "id": "user-uuid-2",
      "username": "jane_smith",
      "email": "jane@example.com",
      "is_active": true,
      "roles": [
        {
          "id": "role-uuid-3",
          "name": "cashier"
        }
      ]
    }
  ]
}
```

**Example Usage (JavaScript):**
```javascript
const response = await fetch('/role-user/users-with-roles', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json'
  }
});
const result = await response.json();
const allUsersWithRoles = result.data;
```

---

## 💡 Common Use Cases

### Use Case 1: Create Role Assignment Form (Frontend)

```javascript
// Step 1: Load users and roles for dropdowns
async function loadFormData() {
  const [usersRes, rolesRes] = await Promise.all([
    fetch('/users/'),
    fetch('/roles/')
  ]);
  
  const users = (await usersRes.json()).data;
  const roles = (await rolesRes.json()).data;
  
  // Populate dropdowns
  populateUserDropdown(users);
  populateRoleDropdown(roles);
}

// Step 2: Assign role when form submitted
async function assignRole(userId, roleId) {
  const response = await fetch(`/role-user/assign?user_id=${userId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ role_id: roleId })
  });
  
  const result = await response.json();
  if (result.status === 'success') {
    alert('Role assigned successfully!');
  } else {
    alert(`Error: ${result.message}`);
  }
}
```

---

### Use Case 2: Display User with Roles (User Management Page)

```javascript
async function loadUserManagementTable() {
  const response = await fetch('/role-user/users-with-roles');
  const result = await response.json();
  const users = result.data;
  
  // Display in table
  users.forEach(user => {
    const roleNames = user.roles.map(r => r.name).join(', ');
    console.log(`${user.username} - Roles: ${roleNames}`);
    // Add to table...
  });
}
```

---

### Use Case 3: Edit User Roles (Multi-select)

```javascript
async function editUserRoles() {
  const userId = "550e8400-e29b-41d4-a716-446655440000";
  
  // Step 1: Load current user roles
  const userRes = await fetch(`/role-user/user/${userId}/roles`);
  const userData = (await userRes.json()).data;
  
  console.log('Current roles:', userData.roles);
  
  // Step 2: Load all available roles
  const rolesRes = await fetch('/roles/');
  const allRoles = (await rolesRes.json()).data;
  
  // Step 3: User selects new roles (multi-select UI)
  const selectedRoleIds = ["role-uuid-1", "role-uuid-2"]; // From UI
  
  // Step 4: Update roles
  const updateRes = await fetch(`/role-user/user/${userId}/roles`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer your-token'
    },
    body: JSON.stringify({
      role_ids: selectedRoleIds
    })
  });
  
  const result = await updateRes.json();
  console.log('Updated user:', result.data);
}
```

---

### Use Case 4: Filter Users by Role

```javascript
async function getUsersByRole(roleName) {
  // Get all users with roles
  const response = await fetch('/role-user/users-with-roles');
  const result = await response.json();
  const allUsers = result.data;
  
  // Filter users who have the specific role
  const filteredUsers = allUsers.filter(user => 
    user.roles.some(role => role.name === roleName)
  );
  
  return filteredUsers;
}

// Usage
const admins = await getUsersByRole('admin');
console.log('All admin users:', admins);
```

---

## 🎨 Frontend Component Example (React)

### Role Assignment Component

```jsx
import React, { useState, useEffect } from 'react';

function RoleAssignmentForm() {
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [selectedUser, setSelectedUser] = useState('');
  const [selectedRole, setSelectedRole] = useState('');

  useEffect(() => {
    // Load users and roles on component mount
    Promise.all([
      fetch('/users/').then(r => r.json()),
      fetch('/roles/').then(r => r.json())
    ]).then(([usersRes, rolesRes]) => {
      setUsers(usersRes.data);
      setRoles(rolesRes.data);
    });
  }, []);

  const handleAssignRole = async (e) => {
    e.preventDefault();
    
    const response = await fetch(`/role-user/assign?user_id=${selectedUser}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ role_id: selectedRole })
    });
    
    const result = await response.json();
    
    if (result.status === 'success') {
      alert('Role assigned successfully!');
    } else {
      alert(`Error: ${result.message}`);
    }
  };

  return (
    <form onSubmit={handleAssignRole}>
      <select 
        value={selectedUser} 
        onChange={(e) => setSelectedUser(e.target.value)}
        required
      >
        <option value="">Select User</option>
        {users.map(user => (
          <option key={user.id} value={user.id}>
            {user.username} ({user.email})
          </option>
        ))}
      </select>

      <select 
        value={selectedRole} 
        onChange={(e) => setSelectedRole(e.target.value)}
        required
      >
        <option value="">Select Role</option>
        {roles.map(role => (
          <option key={role.id} value={role.id}>
            {role.name}
          </option>
        ))}
      </select>

      <button type="submit">Assign Role</button>
    </form>
  );
}

export default RoleAssignmentForm;
```

---

## 📊 Database Schema

### Tables Structure

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR UNIQUE NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    is_active VARCHAR DEFAULT TRUE
);

-- Roles table
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR UNIQUE NOT NULL
);

-- Role-User junction table (many-to-many)
CREATE TABLE role_user (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    role_id UUID NOT NULL REFERENCES roles(id)
);
```

---

## ⚠️ Important Notes

1. **UUID Format:** Semua ID menggunakan format UUID v4
2. **Authentication:** Endpoint `PUT /role-user/user/{user_id}/roles` memerlukan JWT token
3. **Validation:** Pastikan user_id dan role_id valid sebelum melakukan assign
4. **Duplicate Prevention:** System otomatis mencegah duplicate assignment role ke user
5. **Cascade Delete:** Pertimbangkan untuk menambahkan ON DELETE CASCADE di foreign keys

---

## 🔒 Security Recommendations

1. **Production:** Tambahkan authentication untuk semua endpoints manajemen role
2. **Authorization:** Implementasikan role-based access control (RBAC)
3. **Audit Log:** Catat semua perubahan role assignment
4. **Rate Limiting:** Implementasikan rate limiting untuk prevent abuse

---

## 🐛 Error Handling

Semua endpoints menggunakan format response standard:

**Success Response:**
```json
{
  "status": "success",
  "message": "Operation successful",
  "data": { /* response data */ }
}
```

**Error Response:**
```json
{
  "status": "error",
  "message": "Error description",
  "status_code": 400
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request (validation error, duplicate, etc)
- `404` - Not Found (user/role not found)
- `401` - Unauthorized (missing/invalid token)
- `500` - Internal Server Error

---

## 📞 Support

Jika ada pertanyaan atau issue, silakan hubungi tim development.

**Last Updated:** January 4, 2026
