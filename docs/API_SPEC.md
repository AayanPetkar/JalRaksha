# REST API Specification — JalRaksha

## 1. Base URL & Common Schemas

- **Base URL**: `https://api.jalraksha.org/api/v1` (Production) / `http://localhost:8000/api/v1` (Development)
- **Content-Type**: `application/json`
- **Authentication**: `Authorization: Bearer <JWT_TOKEN>`

### Common Error Response Format
```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested safe zone does not exist.",
    "timestamp": "2026-08-20T12:25:00Z"
  }
}
```

---

## 2. Authentication Endpoints (`/api/v1/auth`)

### 2.1 Request OTP / Sign In
- **HTTP Method**: `POST`
- **URL**: `/auth/request-otp`
- **Auth**: None (Public)
- **Request Body**:
```json
{
  "phone_number": "+919876543210"
}
```
- **Response (200 OK)**:
```json
{
  "status": "OTP_SENT",
  "message": "OTP sent successfully to +919876543210"
}
```
- **Errors**: `400 Bad Request` (Invalid phone number format).

### 2.2 Verify OTP & Login
- **HTTP Method**: `POST`
- **URL**: `/auth/verify-otp`
- **Auth**: None (Public)
- **Request Body**:
```json
{
  "phone_number": "+919876543210",
  "otp": "123456"
}
```
- **Response (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
  "token_type": "bearer",
  "user": {
    "id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
    "phone_number": "+919876543210",
    "full_name": "Aayan Sharma",
    "preferred_language": "mr"
  }
}
```
- **Errors**: `401 Unauthorized` (Invalid/Expired OTP).

---

## 3. Users Endpoints (`/api/v1/users`)

### 3.1 Get Current User Profile
- **HTTP Method**: `GET`
- **URL**: `/users/me`
- **Auth**: Bearer Token Required
- **Request Body**: None
- **Response (200 OK)**:
```json
{
  "id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
  "phone_number": "+919876543210",
  "full_name": "Aayan Sharma",
  "preferred_language": "mr"
}
```
- **Errors**: `401 Unauthorized`.

### 3.2 Update Preferred Language
- **HTTP Method**: `PATCH`
- **URL**: `/users/me/language`
- **Auth**: Bearer Token Required
- **Request Body**:
```json
{
  "preferred_language": "hi"
}
```
- **Response (200 OK)**:
```json
{
  "id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
  "preferred_language": "hi"
}
```

---

## 4. Location Endpoints (`/api/v1/locations`)

### 4.1 Post User Location Update
- **HTTP Method**: `POST`
- **URL**: `/locations/update`
- **Auth**: Bearer Token Required
- **Request Body**:
```json
{
  "latitude": 19.0760,
  "longitude": 72.8777,
  "accuracy_meters": 12.5
}
```
- **Response (200 OK)**:
```json
{
  "status": "LOCATION_UPDATED",
  "village_id": "v-1029",
  "village_name": "Sangli Rural"
}
```

---

## 5. Emergency Circle Endpoints (`/api/v1/emergency-circle`)

### 5.1 Get Emergency Circle Contacts
- **HTTP Method**: `GET`
- **URL**: `/emergency-circle`
- **Auth**: Bearer Token Required
- **Request Body**: None
- **Response (200 OK)**:
```json
[
  {
    "id": "c-1",
    "contact_name": "Father",
    "contact_phone": "+919811122233",
    "relationship": "Father",
    "is_verified": true,
    "preferences": {
      "notify_on_prepare": false,
      "notify_on_critical": true,
      "notify_on_distress": true
    }
  }
]
```

### 5.2 Add Emergency Contact
- **HTTP Method**: `POST`
- **URL**: `/emergency-circle`
- **Auth**: Bearer Token Required
- **Request Body**:
```json
{
  "contact_name": "Brother",
  "contact_phone": "+919822233344",
  "relationship": "Brother",
  "preferences": {
    "notify_on_prepare": false,
    "notify_on_critical": true,
    "notify_on_distress": true
  }
}
```
- **Response (201 Created)**: Contact object.

### 5.3 Quick Action: "I'm Safe" Broadcast
- **HTTP Method**: `POST`
- **URL**: `/emergency-circle/im-safe`
- **Auth**: Bearer Token Required
- **Request Body**:
```json
{
  "latitude": 19.0760,
  "longitude": 72.8777,
  "custom_message": "Reached Community Hall safely."
}
```
- **Response (200 OK)**:
```json
{
  "status": "SAFE_BROADCAST_SENT",
  "recipients_notified_count": 3
}
```

### 5.4 Quick Action: "Need Help" Distress Signal
- **HTTP Method**: `POST`
- **URL**: `/emergency-circle/need-help`
- **Auth**: Bearer Token Required
- **Request Body**:
```json
{
  "latitude": 19.0760,
  "longitude": 72.8777,
  "distress_type": "TRAPPED_WATER"
}
```
- **Response (200 OK)**:
```json
{
  "status": "DISTRESS_SIGNAL_BROADCAST",
  "emergency_contacts_notified": 3,
  "admin_distress_pin_created": true
}
```

---

## 6. Flood Risk & Explanation Endpoints (`/api/v1/flood-risk`)

### 6.1 Get Current Location Flood Risk Score
- **HTTP Method**: `GET`
- **URL**: `/flood-risk/current?latitude=19.0760&longitude=72.8777`
- **Auth**: Bearer Token Required
- **Request Body**: None
- **Response (200 OK)**:
```json
{
  "village_id": "v-1029",
  "village_name": "Sangli Rural",
  "flood_risk_score": 84.0,
  "risk_level": "CRITICAL",
  "confidence_score": 0.92,
  "data_freshness_minutes": 7,
  "source_tag": "AI_PREDICTION",
  "disclaimer": "AI prediction; not an official government warning.",
  "local_impact": {
    "affected_houses_count": 320,
    "affected_farmland_acres": 185.0,
    "affected_schools_count": 1,
    "affected_hospitals_count": 0
  }
}
```

### 6.2 "Why Am I Getting This Warning?" (Explainable AI)
- **HTTP Method**: `GET`
- **URL**: `/flood-risk/explain?village_id=v-1029&lang=mr`
- **Auth**: Bearer Token Required
- **Response (200 OK)**:
```json
{
  "village_id": "v-1029",
  "risk_score": 84.0,
  "confidence": "High",
  "data_updated": "7 minutes ago",
  "contributing_factors": [
    {
      "factor": "HEAVY_RAINFALL",
      "contribution_percentage": 42.0,
      "explanation": "मुसळधार पावसाचा अंदाज (Heavy rainfall forecast: 120mm)"
    },
    {
      "factor": "RIVER_LEVEL",
      "contribution_percentage": 30.0,
      "explanation": "कृष्णा नदीची पातळी वाढत आहे (Rising river level)"
    },
    {
      "factor": "SOIL_SATURATION",
      "contribution_percentage": 18.0,
      "explanation": "जमिनीची पाझर क्षमता पूर्ण झाली आहे (High soil saturation)"
    },
    {
      "factor": "LOW_ELEVATION",
      "contribution_percentage": 10.0,
      "explanation": "सखल भौगोलिक स्थान (Low-lying geographical area)"
    }
  ]
}
```

---

## 7. Safe Zones & Routes Endpoints (`/api/v1/safe-zones`, `/api/v1/routes`)

### 7.1 Get Nearest Verified Safe Zone
- **HTTP Method**: `GET`
- **URL**: `/safe-zones/nearest?latitude=19.0760&longitude=72.8777`
- **Auth**: Bearer Token Required
- **Response (200 OK)**:
```json
{
  "id": "sz-401",
  "name": "Sangli Community Hall",
  "type": "OFFICIAL_SHELTER",
  "distance_km": 2.4,
  "estimated_travel_time_minutes": 8,
  "is_verified": true,
  "latitude": 19.0850,
  "longitude": 72.8850
}
```

### 7.2 Get Safest Available Route
- **HTTP Method**: `POST`
- **URL**: `/routes/calculate-safest`
- **Auth**: Bearer Token Required
- **Request Body**:
```json
{
  "origin_latitude": 19.0760,
  "origin_longitude": 72.8777,
  "destination_safe_zone_id": "sz-401"
}
```
- **Response (200 OK)**:
```json
{
  "route_id": "rt-8821",
  "route_label": "Safest Available Route based on currently available data.",
  "is_100_percent_safe_guarantee": false,
  "total_distance_km": 2.4,
  "estimated_duration_minutes": 8,
  "risk_assessment": "LOW_FLOOD_RISK",
  "waypoints": [
    {"lat": 19.0760, "lng": 72.8777, "road_name": "Home"},
    {"lat": 19.0800, "lng": 72.8800, "road_name": "Main Road B"},
    {"lat": 19.0850, "lng": 72.8850, "road_name": "Community Hall"}
  ],
  "rejected_unsafe_routes": [
    {
      "route_label": "Route A via River Road",
      "distance_km": 1.8,
      "risk_status": "HIGH_FLOOD_RISK / ROAD_BLOCKED"
    }
  ]
}
```

---

## 8. Citizen Flood Reports (`/api/v1/reports`)

### 8.1 Submit Ground Flood Report
- **HTTP Method**: `POST`
- **URL**: `/reports`
- **Auth**: Bearer Token Required
- **Request Body**:
```json
{
  "latitude": 19.0780,
  "longitude": 72.8790,
  "photo_url": "https://storage.jalraksha.org/reports/img_991.jpg",
  "voice_note_url": null,
  "description": "Water level reaching road surface near bridge.",
  "disaster_category": "ROAD_BLOCKED"
}
```
- **Response (201 Created)**:
```json
{
  "report_id": "rep-9912",
  "verification_status": "UNVERIFIED",
  "created_at": "2026-08-20T12:26:00Z"
}
```

---

## 9. Admin Dashboard Endpoints (`/api/v1/admin`)

### 9.1 Get Regional Flood Risk Map Overview
- **HTTP Method**: `GET`
- **URL**: `/admin/map-overview?district=Sangli`
- **Auth**: Admin Bearer Token Required
- **Response (200 OK)**:
```json
{
  "district": "Sangli",
  "active_alert_level": "CRITICAL",
  "total_affected_villages": 4,
  "total_population_exposed": 14200,
  "active_citizen_reports_count": 28,
  "active_distress_signals_count": 3,
  "villages": [
    {
      "village_id": "v-1029",
      "name": "Sangli Rural",
      "risk_score": 84.0,
      "risk_level": "CRITICAL"
    }
  ]
}
```

### 9.2 Broadcast Emergency SMS / App Alert
- **HTTP Method**: `POST`
- **URL**: `/admin/broadcast-alert`
- **Auth**: Admin Bearer Token Required
- **Request Body**:
```json
{
  "village_id": "v-1029",
  "alert_level": "CRITICAL",
  "title": "CRITICAL FLOOD ALERT",
  "message_en": "Evacuate immediately to Community Hall via Main Road B.",
  "message_mr": "मुख्य मार्ग B ने तात्काळ कम्युनिटी हॉलकडे सुरक्षित स्थलांतर करा.",
  "dispatch_user_sms": true,
  "dispatch_emergency_contacts_sms": true
}
```
- **Response (200 OK)**:
```json
{
  "broadcast_id": "bc-5501",
  "fcm_dispatched_count": 1250,
  "sms_queued_count": 3400
}
```
