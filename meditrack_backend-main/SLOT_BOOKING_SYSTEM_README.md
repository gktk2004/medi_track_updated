# Slot Booking System Implementation - 80 Slots Per Day

## Overview
Implemented a daily slot management system with **80 slots per doctor per day**:
- **Morning Slots**: 1-40 (06:00 - 14:00)
- **Evening Slots**: 1-40 (14:00 - 22:00)

---

## Changes Made

### 1. **Model Update** - `userapp/models.py`
Added `time_slot` field to the `Appointment` model:

```python
TIME_SLOT_CHOICES = [
    ('morning', 'Morning (06:00 - 14:00)'),
    ('evening', 'Evening (14:00 - 22:00)'),
]

time_slot = models.CharField(max_length=10, choices=TIME_SLOT_CHOICES, default='morning')
```

**Features**:
- Default slot is 'morning'
- Each appointment now has a designated time slot
- Tokens reset for each time slot (1-40 for morning, 1-40 for evening)

---

### 2. **Booking Logic Update** - `AppointmentBookingView` in `userapp/views.py`

**New Booking Flow**:
```
POST /api/book_appointment/
{
    "user": 1,
    "doctor": 2,
    "date": "2026-02-10",
    "time_slot": "morning",  // or "evening"
    "symptoms": "Fever and cough"
}
```

**Key Features**:
- ✅ Validates time_slot parameter (must be "morning" or "evening")
- ✅ Checks if 40 slots are available for the selected time slot
- ✅ Returns error if time slot is fully booked
- ✅ Auto-assigns token number (1-40 per time slot)
- ✅ Separate token numbering for morning and evening

**Example Response**:
```json
{
    "message": "Appointment booked successfully",
    "token_number": 15,
    "time_slot": "morning",
    "appointment": {...}
}
```

---

### 3. **Payment Views Updated**
Both `CardPaymentView` and `UPIPaymentView` now filter token numbers by `time_slot` to ensure correct token assignment.

---

### 4. **New Utility Endpoint** - `CheckAvailableSlotsAPIView`

Get real-time slot availability for any doctor on a specific date:

```
GET /api/check_available_slots/?doctor_id=2&date=2026-02-10
```

**Response**:
```json
{
    "doctor": "Dr. Rajesh Kumar",
    "date": "2026-02-10",
    "morning_slots": {
        "available": 35,
        "booked": 5,
        "total": 40
    },
    "evening_slots": {
        "available": 40,
        "booked": 0,
        "total": 40
    },
    "total_available": 75,
    "total_slots": 80,
    "fully_booked": false
}
```

---

### 5. **Database Migration**
Created migration file: `userapp/migrations/0015_appointment_time_slot.py`
- Adds `time_slot` field to Appointment table
- Automatically applied with default value 'morning'

---

## API Usage Examples

### Example 1: Book Morning Appointment
```bash
POST /api/book_appointment/
{
    "user": 1,
    "doctor": 2,
    "date": "2026-02-10",
    "time_slot": "morning",
    "symptoms": "Routine checkup"
}
```

### Example 2: Book Evening Appointment
```bash
POST /api/book_appointment/
{
    "user": 1,
    "doctor": 2,
    "date": "2026-02-10",
    "time_slot": "evening",
    "symptoms": "Eye pain"
}
```

### Example 3: Check Available Slots
```bash
GET /api/check_available_slots/?doctor_id=2&date=2026-02-10
```

### Example 4: Book with Payment (Card)
```bash
POST /api/card_payment/
{
    "appointment_id": 100,
    "cardholder_name": "John Doe",
    "card_number": "1234567890123456",
    "expiry_date": "12/25",
    "cvv": "123"
}
```

---

## Slot Availability Logic

| Scenario | Status | Action |
|----------|--------|--------|
| Morning < 40 | Available | Slot assigned automatically (1-40) |
| Morning = 40 | Full | User must select "evening" |
| Evening < 40 | Available | Slot assigned automatically (1-40) |
| Evening = 40 | Full | Day is completely booked |
| Both = 40 | Fully Booked | No slots available |

---

## Benefits

✅ **Better Resource Management**: 80 slots per day per doctor (40 morning, 40 evening)
✅ **Load Balancing**: Morning and evening slots managed separately
✅ **Clarity**: Users know exact time period of appointment
✅ **Token Tracking**: Separate token numbers for each time slot
✅ **Real-time Availability**: Easy slot checking with new API endpoint
✅ **Backward Compatible**: Existing payments and appointments work seamlessly

---

## Files Modified

1. **userapp/models.py** - Added `time_slot` field to Appointment model
2. **userapp/views.py** - Updated AppointmentBookingView, CardPaymentView, UPIPaymentView, added CheckAvailableSlotsAPIView
3. **userapp/urls.py** - Added route for CheckAvailableSlotsAPIView
4. **userapp/migrations/0015_appointment_time_slot.py** - New migration file

---

## Next Steps (Optional)

If you want to add more features:

1. **Doctor Working Hours**: Store doctor's working hours (currently hardcoded as 06:00-22:00)
2. **Dynamic Slot Configuration**: Admin panel to adjust slots per day
3. **Bulk Time Slot Assignment**: Assign time slots based on auto-calculated appointment duration
4. **Notification**: Notify users of their time slot via SMS/Email
5. **Calendar View**: Display available slots as interactive calendar

---

## Testing

To test the system:

```bash
# 1. Create a doctor account
# 2. Book an appointment with morning slot
curl -X POST http://localhost:8000/api/book_appointment/ \
  -H "Content-Type: application/json" \
  -d '{
    "user": 1,
    "doctor": 2,
    "date": "2026-02-10",
    "time_slot": "morning",
    "symptoms": "Test"
  }'

# 3. Check available slots
curl http://localhost:8000/api/check_available_slots/?doctor_id=2&date=2026-02-10

# 4. Try booking when slots are full
# (Repeat step 2 40 times for morning, then attempt again - should fail)
```

---

**Implementation Date**: January 27, 2026
**System**: Meditrack Medical Appointment System
