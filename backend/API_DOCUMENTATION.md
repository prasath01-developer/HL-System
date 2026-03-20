# Hostel Lock System - Complete REST API Documentation

## Base URL
```
http://127.0.0.1:8000
```

## API Endpoints Overview

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/login/` | User login |
| POST | `/api/logout/` | User logout |
| GET | `/api/csrf-token/` | Get CSRF token |

### Student Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/create-outpass/` | Create new outpass request |
| GET | `/api/my-outpasses/` | Get student's own outpasses |
| POST | `/api/mark-in/` | Mark student as "IN" (inside hostel) |

### Admin Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/dashboard/stats/` | Get dashboard statistics |
| GET | `/api/admin/dashboard/stats-complete/` | Get complete dashboard stats |
| GET | `/api/admin/outpasses/` | Get all outpasses (with filters) |
| POST | `/api/admin/approve/<id>/` | Approve outpass by ID |
| POST | `/api/admin/reject/<id>/` | Reject outpass by ID |

### Additional Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/mark-student-status/` | Mark student status (admin) |
| POST | `/api/update-outpass-status/` | Update outpass status (admin) |
| GET | `/api/chart/daily-requests/` | Get daily requests chart data |
| GET | `/api/chart/hostel-status/` | Get hostel status chart data |

---

## Authentication

### POST /api/login/

Login with username and password.

**Request:**
```json
{
    "username": "admin",
    "password": "admin123"
}
```

**Response (Success):**
```json
{
    "success": true,
    "message": "Login successful!",
    "redirect": "/admin-dashboard/",
    "user": {
        "username": "admin",
        "is_admin": true,
        "is_student": false
    }
}
```

**Response (Error):**
```json
{
    "success": false,
    "message": "Invalid username or password."
}
```

---

### POST /api/logout/

Logout the current user.

**Request:** Empty JSON `{}`

**Response:**
```json
{
    "success": true,
    "message": "Logout successful!",
    "redirect": "/login/"
}
```

---

## Student Features

### POST /api/create-outpass/

Create a new outpass request.

**Content-Type:** `multipart/form-data`

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| destination | string | Yes | Destination address |
| purpose | string | Yes | Purpose/reason for outpass |
| time_out | datetime | Yes | Departure time (YYYY-MM-DDTHH:MM) |
| return_date | datetime | Yes | Return time (YYYY-MM-DDTHH:MM) |
| image | file | No | Optional image |

**Response (Success):**
```json
{
    "success": true,
    "message": "Outpass request created successfully!",
    "outpass_id": 1,
    "status": "pending",
    "data": {
        "purpose": "Family function",
        "destination": "Home",
        "time_out": "2024-01-15 10:00",
        "return_date": "2024-01-15 18:00",
        "status": "Pending",
        "created_at": "2024-01-14 12:00:00"
    }
}
```

---

### GET /api/my-outpasses/

Get student's own outpass requests.

**Query Parameters (Optional):**
| Parameter | Description |
|-----------|-------------|
| status | Filter by status (pending, approved, rejected) |

**Response:**
```json
{
    "success": true,
    "count": 2,
    "data": [
        {
            "id": 1,
            "destination": "Home",
            "purpose": "Family function",
            "departure_date": "2024-01-15 10:00",
            "return_date": "2024-01-15 18:00",
            "status": "approved",
            "status_display": "Approved",
            "hostel_status": "outside",
            "hostel_status_display": "Outside Hostel",
            "created_at": "2024-01-14 12:00:00"
        }
    ]
}
```

---

### POST /api/mark-in/

Mark student as "IN" (inside hostel).

**Request:** Empty JSON `{}` or with specific outpass_id:
```json
{
    "outpass_id": 1
}
```

**Response:**
```json
{
    "success": true,
    "message": "Outpass #1 marked as IN successfully!",
    "data": {
        "outpass_id": 1,
        "hostel_status": "inside"
    }
}
```

---

## Admin Features

### GET /api/admin/dashboard/stats/

Get basic dashboard statistics.

**Response:**
```json
{
    "success": true,
    "data": {
        "total_students": 50,
        "total_out_students": 10,
        "total_inside_students": 40,
        "total_pending_requests": 5
    }
}
```

---

### GET /api/admin/dashboard/stats-complete/

Get complete dashboard statistics.

**Response:**
```json
{
    "success": true,
    "data": {
        "total_students": 50,
        "students_inside": 40,
        "students_outside": 10,
        "pending_requests": 5,
        "approved_requests": 20,
        "rejected_requests": 3,
        "total_requests": 28
    }
}
```

---

### GET /api/admin/outpasses/

Get all outpass requests with optional filters.

**Query Parameters (Optional):**
| Parameter | Description |
|-----------|-------------|
| status | Filter by status (pending, approved, rejected) |
| date | Filter by date (YYYY-MM-DD) |
| hostel_status | Filter by hostel status (inside, outside) |
| search | Search by student name or ID |

**Response:**
```json
{
    "success": true,
    "count": 2,
    "data": [
        {
            "id": 1,
            "student_name": "John Doe",
            "student_id": "STU001",
            "destination": "Home",
            "purpose": "Family function",
            "departure_time": "2024-01-15 10:00",
            "return_time": "2024-01-15 18:00",
            "status": "approved",
            "hostel_status": "outside",
            "created_at": "2024-01-14 12:00:00"
        }
    ]
}
```

---

### POST /api/admin/approve/<id>/

Approve an outpass request.

**Response:**
```json
{
    "success": true,
    "message": "Outpass #1 approved successfully!",
    "data": {
        "outpass_id": 1,
        "status": "approved",
        "hostel_status": "outside"
    }
}
```

---

### POST /api/admin/reject/<id>/

Reject an outpass request.

**Response:**
```json
{
    "success": true,
    "message": "Outpass #1 rejected.",
    "data": {
        "outpass_id": 1,
        "status": "rejected",
        "hostel_status": "inside"
    }
}
```

---

## Chart Endpoints

### GET /api/chart/daily-requests/

Get daily outpass requests for the last 7 days.

**Response:**
```json
{
    "success": true,
    "data": {
        "labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "counts": [5, 3, 8, 2, 6, 1, 4]
    }
}
```

---

### GET /api/chart/hostel-status/

Get students inside vs outside data.

**Response:**
```json
{
    "success": true,
    "data": {
        "labels": ["Inside Hostel", "Outside Hostel"],
        "counts": [40, 10]
    }
}
```

---

## Frontend Routes

| Route | Description |
|-------|-------------|
| `/` | Login page |
| `/login/` | Login page |
| `/dashboard/` | Student dashboard |
| `/create-pass/` | Create outpass form |
| `/admin-dashboard/` | Admin dashboard |

---

## CSRF Token Handling

JavaScript function to get CSRF token:

```javascript
function getCsrfToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    
    return cookieValue || '';
}
```

Using the token in fetch requests:

```javascript
fetch('/api/login/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
    },
    body: JSON.stringify({
        username: 'your_username',
        password: 'your_password'
    })
})
```

---

## Error Responses

All API endpoints return consistent error responses:

**400 Bad Request:**
```json
{
    "success": false,
    "message": "Validation failed.",
    "errors": {
        "field_name": "Error message"
    }
}
```

**401 Unauthorized:**
```json
{
    "success": false,
    "message": "Invalid username or password."
}
```

**403 Forbidden:**
```json
{
    "success": false,
    "message": "Access denied. Admin privileges required."
}
```

**404 Not Found:**
```json
{
    "success": false,
    "message": "Resource not found."
}
```

**500 Internal Server Error:**
```json
{
    "success": false,
    "message": "An error occurred: <error_message>"
}
```

---

## Testing with cURL

### Test Login
```bash
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### Test Get CSRF Token
```bash
curl http://127.0.0.1:8000/api/csrf-token/
```

### Test Dashboard Stats (Admin)
```bash
curl http://127.0.0.1:8000/api/admin/dashboard/stats-complete/
```

---

## Security Notes

1. **HTTPS**: Always use HTTPS in production
2. **CSRF Protection**: All POST requests require CSRF token
3. **Authentication**: Use session-based authentication
4. **Role-based Access**: Admin endpoints check `request.user.is_staff`
5. **Passwords**: Never send passwords in plain text over HTTP

