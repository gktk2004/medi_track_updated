# 🩸 Admin Blood Donation Admin Management - Quick Reference

## What Was Implemented

The system now allows regular admins to **create, view, and manage** blood donation admin accounts through REST API endpoints.

---

## API Endpoints Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/admin-create-blood-donation-admin/` | Create new blood donation admin |
| GET | `/admin-manage-blood-donation-admins/` | View all blood donation admins |
| POST | `/admin-deactivate-blood-donation-admin/` | Deactivate blood donation admin |

---

## Complete Workflow

### Step 1: Admin Creates a Blood Donation Admin
```
Admin sends POST request to /admin-create-blood-donation-admin/
↓
System verifies admin credentials (admin_id + admin_email)
↓
System validates all required fields
↓
System checks for duplicate username/email
↓
System validates location (Thrissur/Ernakulam/Palakkad)
↓
System creates BloodDonationAdmin record
↓
Returns: New blood admin details with ID
```

### Step 2: Admin Views All Blood Donation Admins
```
Admin sends GET request to /admin-manage-blood-donation-admins/
with query params: admin_id, admin_email
↓
System verifies admin credentials
↓
System fetches all BloodDonationAdmin records
↓
Returns: Complete list with all details
```

### Step 3: Admin Deactivates a Blood Donation Admin
```
Admin sends POST request to /admin-deactivate-blood-donation-admin/
with: admin_id, admin_email, blood_admin_id
↓
System verifies admin credentials
↓
System finds blood donation admin by ID
↓
System sets is_active = False
↓
Returns: Confirmation of deactivation
```

---

## Request & Response Examples

### 1️⃣ CREATE Blood Donation Admin

**Request:**
```json
POST /admin-create-blood-donation-admin/
{
  "admin_id": 1,
  "admin_email": "admin@meditrack.com",
  "username": "blood_admin_thrissur",
  "email": "blood_thrissur@hospital.com",
  "password": "secure_password",
  "phone_number": "+91-9876543210",
  "hospital_name": "Thrissur Medical Center",
  "location": "Thrissur"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Blood Donation Admin created successfully",
  "blood_admin": {
    "id": 5,
    "username": "blood_admin_thrissur",
    "email": "blood_thrissur@hospital.com",
    "hospital_name": "Thrissur Medical Center",
    "location": "Thrissur",
    "is_active": true
  }
}
```

---

### 2️⃣ VIEW All Blood Donation Admins

**Request:**
```
GET /admin-manage-blood-donation-admins/?admin_id=1&admin_email=admin@meditrack.com
```

**Response (200 OK):**
```json
{
  "success": true,
  "total_blood_admins": 3,
  "blood_admins": [
    {
      "id": 1,
      "username": "blood_admin_001",
      "email": "thrissur@bloodbank.com",
      "hospital_name": "Thrissur Blood Bank",
      "location": "Thrissur",
      "phone_number": "9876543210",
      "is_active": true
    },
    {
      "id": 2,
      "username": "blood_admin_002",
      "email": "ernakulam@bloodbank.com",
      "hospital_name": "Ernakulam Blood Bank",
      "location": "Ernakulam",
      "phone_number": "9876543211",
      "is_active": true
    },
    {
      "id": 3,
      "username": "blood_admin_003",
      "email": "palakkad@bloodbank.com",
      "hospital_name": "Palakkad Blood Bank",
      "location": "Palakkad",
      "phone_number": "9876543212",
      "is_active": false
    }
  ]
}
```

---

### 3️⃣ DEACTIVATE Blood Donation Admin

**Request:**
```json
POST /admin-deactivate-blood-donation-admin/
{
  "admin_id": 1,
  "admin_email": "admin@meditrack.com",
  "blood_admin_id": 2
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Blood Donation Admin 'blood_admin_002' deactivated",
  "blood_admin_id": 2
}
```

---

## Error Scenarios

### Missing Required Fields
```json
{
  "error": "All fields are required"
}
// HTTP 400
```

### Invalid Admin Credentials
```json
{
  "error": "Invalid admin credentials"
}
// HTTP 401
```

### Duplicate Username
```json
{
  "error": "Username already exists"
}
// HTTP 400
```

### Invalid Location
```json
{
  "error": "Location must be one of: Thrissur, Ernakulam, Palakkad"
}
// HTTP 400
```

### Blood Admin Not Found (Deactivation)
```json
{
  "error": "Blood Donation Admin not found"
}
// HTTP 404
```

---

## Valid Locations
- `Thrissur`
- `Ernakulam`
- `Palakkad`

---

## Security Features

✅ **Admin-Only Access** - All endpoints require valid admin credentials
✅ **Email Verification** - Admin email must match recorded email in database
✅ **Duplicate Prevention** - Prevents duplicate usernames and emails
✅ **Location Validation** - Ensures only valid locations are used
✅ **Soft Delete** - Deactivation doesn't delete records, just sets `is_active=false`
✅ **Audit Trail** - `created_at` timestamp tracks creation

---

## Integration Points

1. **Blood Donation Admin Login** `/blood-admin-login/`
   - Blood admins created here can authenticate using their credentials

2. **Blood Request Management** `/blood-admin-view-requests/`, `/blood-admin-approve-request/`
   - Blood admins manage blood requests in their locations

3. **Donor Management** `/blood-admin-view-accepted-donors/`, `/blood-admin-complete-donation/`
   - Blood admins manage donation records

---

## Database Impact

**Table Modified:** None (All operations use existing BloodDonationAdmin model)

**Records Created:** New BloodDonationAdmin entries when admin creates new admins

**No Data Loss:** Deactivation uses soft-delete (only sets `is_active=false`)

---

## Testing Instructions

1. Ensure you have admin credentials (admin_id and admin_email)
2. Use a REST client (Postman, Thunder Client, or similar)
3. Call the endpoints with the proper HTTP methods
4. Verify responses match expected format

---

## Related Features

- 🏥 **Slot Management** - 80 slots/day (40 morning + 40 evening)
- 🔄 **Appointment Rescheduling** - 5-day rule enforcement
- 🩸 **Blood Donation System** - Blood request management and tracking
- 👤 **Blood Donation Admin** - Dedicated admin for blood operations
- 🔔 **Notifications** - Auto-notification system for all operations

---

**Status:** ✅ Ready for Production
**Last Updated:** 2024
**API Version:** v1
