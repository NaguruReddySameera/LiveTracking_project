# Admin Login Guide

## ✅ Admin Login Works with Same Endpoint

All users (Admin, Analyst, Operator) use the **same login endpoint** and **same authentication flow**.

---

## 🔑 Login Endpoint

**URL**: `POST /api/auth/login/`

**No special endpoint needed** - Admin uses the same endpoint as all other users.

---

## 📋 Login Request

```bash
curl -X POST 'http://localhost:8000/api/auth/login/' \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "sameerareddy583@gmail.com",
    "password": "admin"
  }'
```

---

## ✅ Response

```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "Bearer",
    "expires_in": 86400,
    "user": {
      "id": 1,
      "email": "sameerareddy583@gmail.com",
      "first_name": "Admin",
      "last_name": "User",
      "full_name": "Admin User",
      "role": "admin",
      "is_verified": true
    }
  }
}
```

---

## 🔐 Admin Credentials

**Email**: `sameerareddy583@gmail.com`  
**Password**: `admin`

**Status**: ✅ Active and Verified

---

## 📋 Demo Users

All demo users use the same login endpoint:

| Role | Email | Password |
|------|-------|----------|
| **Admin** | `sameerareddy583@gmail.com` | `admin` |
| **Analyst** | `analyst@maritimetracking.com` | `Analyst@123` |
| **Operator** | `operator@maritimetracking.com` | `Operator@123` |

---

## 🎯 Key Points

1. ✅ **Same Endpoint**: All users use `/api/auth/login/`
2. ✅ **Same Flow**: Email + Password authentication
3. ✅ **Same Response**: JWT tokens + user profile
4. ✅ **Role in Response**: User role is included in response (`"role": "admin"`)

---

## 🔒 Authentication Flow

1. Send email and password to `/api/auth/login/`
2. System validates credentials
3. Checks if account is active
4. Verifies password
5. Generates JWT tokens
6. Returns tokens + user profile (including role)

---

## ✅ Summary

**Admin login works exactly the same as other users!**

- Same endpoint: `/api/auth/login/`
- Same credentials format: email + password
- Same response format: tokens + user data
- Role is included in user data

**No special admin login endpoint needed!** 🎉


