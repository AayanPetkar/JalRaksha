# Project Analysis: JalRaksha — The Flood Relief, Reminder & Safety Expert

## Executive Summary

**JalRaksha** is an AI-powered flood safety, relief, and emergency-response platform designed to provide citizens and disaster management authorities with localized, understandable, and actionable intelligence before and during flood situations. 

JalRaksha does not aim to replace official government disaster-warning systems; rather, it serves as a **last-mile safety and intelligence layer** that converts trusted environmental, geographic, historical, and official data into personalized flood-risk scores, impact assessments, transparent explanations, safe-zone recommendations, safest-route navigation, and emergency communication.

---

## 1. What Problem JalRaksha Solves

Traditional disaster warning systems broadcast general warnings such as *"There may be a flood in District X."* While valuable, these macro-level alerts fail to solve the critical **last-mile emergency problem**:

1. **Lack of Localized Context**: Generic alerts do not inform individuals whether their specific home, farm, school, or local road is in danger.
2. **Information Ambiguity & Alert Fatigue**: Citizens receive repetitive vague warnings without understanding *why* the risk is elevated, causing apathy or panic.
3. **Unsafe Evacuation Routing**: Standard navigation apps optimize for the shortest route, which often leads evacuees directly into low-lying flooded roads, submerged bridges, or hazardous zones.
4. **Emergency Communication Gaps**: Family members outside or inside flood zones lack real-time status updates ("I'm Safe" / "Need Help"), especially when Internet connectivity deteriorates.
5. **Information Asymmetry for Administrators**: Disaster response teams lack granular ground-truth visibility into village-level infrastructure damage and citizen distress locations.

**JalRaksha solves this by executing the complete intelligence chain:**
> **Trusted Data → Flood Risk → Local Impact → Explanation → Alert → Safe Zone → Safest Route → Action → Community Feedback → Dynamic Update**

---

## 2. Target Users

JalRaksha addresses four primary user personas across rural and urban flood-prone regions:

1. **General Citizens / Local Residents**
   - People living in villages, low-lying areas, and river basins who require hyper-local risk warnings, plain-language explanations, actionable safety checklists, and safe evacuation routes.
2. **Emergency Contacts / Family Members**
   - Trusted family or friends added to a user's *Emergency Circle*. They receive automated SMS alerts during critical events even if they do not have the JalRaksha application installed.
3. **Disaster Management Administrators / Local Authorities / Relief Officers**
   - Officials who require a centralized web dashboard to monitor active flood events, assess village-level population/infrastructure exposure, track citizen distress reports, manage safe zones, and broadcast targeted emergency notifications.
4. **Community Volunteers & Field Rescuers**
   - Local responders who submit real-time ground-truth reports (photos, voice notes, GPS coordinates) and use the platform to coordinate evacuation and relief delivery.

---

## 3. Complete Feature List

Preserving all terminology and capabilities defined in `JALRAKSHA_SPEC.md`, the platform features include:

* **AI-Powered Flood Risk Assessment Engine**: Multi-factor model generating a **Flood Risk Score (%)**, **Confidence Level**, and **Data Freshness** indicator.
* **Village-Level Flood Impact Assessment**: Quantified impact metrics across population exposure, house risk, road risk, farm acreage risk, school risk, hospital risk, and critical infrastructure risk.
* **"Why Am I Getting This Warning?" (Explainable Risk UI)**: Transparent breakdown of contributing risk factors (heavy rainfall forecast, rising river levels, soil saturation, low elevation, historical flood patterns).
* **4-Tier Flood Alert Levels**:
  * 🟢 **LOW — Normal**: No immediate action required.
  * 🟡 **WATCH — Monitor**: Monitor conditions and track updates.
  * 🟠 **PREPARE — Get Ready**: Pack emergency supplies, protect documents/medicines, secure livestock.
  * 🔴 **CRITICAL — Immediate Attention**: Follow official evacuation orders and navigate to designated safe zones.
* **Three-Channel Notification System**:
  1. *App Notifications (FCM)*: Push alerts with rich details.
  2. *User SMS*: Direct SMS alerts for app users when mobile data/Internet is poor.
  3. *Emergency Contact SMS*: Automated SMS dispatched to non-app users in the user's Emergency Circle.
* **Emergency Circle Management**: Custom list of trusted contacts with relationship details, phone numbers, verification status, and customizable alert thresholds (e.g., Prepare alerts OFF, Critical alerts ON).
* **Quick Emergency Actions**:
  * ✅ **"I'm Safe"**: One-tap status update dispatched to Emergency Circle.
  * 🆘 **"Need Help"**: One-tap distress signal sending GPS coordinates via SMS/App and flagging the user on the Admin Dashboard.
* **Safe Zone Detection**: Automated calculation of the nearest verified safe areas (official shelters, relief centers, community halls, evacuation centers) displaying distance and estimated travel time.
* **Safest Available Route Navigation**: Navigation weighted against flood risk zones, road closures, water levels, bridge status, elevation, and citizen reports (never claiming "100% safe").
* **Dynamic Safe Route Recalculation**: Live re-routing triggered when new flood hazards or road closures intersect an active evacuation path.
* **Village Digital Twin & Flood Simulation**: Spatial visualizer representing houses, roads, farms, schools, hospitals, and rivers with interactive flood simulations (e.g., *"Simulate River Level +1m"*).
* **Citizen Flood Reporting**: Ground-truth submissions capturing photos, GPS coordinates, voice recordings, text descriptions, timestamps, and disaster categories.
* **Community Intelligence Engine**: Data fusion layer integrating official weather/hydrological data with ground citizen feedback.
* **Personalized Flood Actions (Checklists)**: Dynamic, step-by-step guidance tailored to the active alert level.
* **Multilingual Support**: Full internationalization for **Marathi**, **Hindi**, and **English**.
* **Offline-Friendly Emergency Support**: Cached safety rules, emergency contacts, shelter coordinates, and last-known risk data with SMS failover.
* **Admin / Disaster Management Dashboard**: Web console for real-time monitoring of active flood events, population exposure, risk maps, citizen report triage, and alert dispatch delivery tracking.
* **Relief & Safety Support**: Last-mile guidance transitioning users smoothly from *Warning → Safety → Relief → Recovery*.

---

## 4. Core User Journeys

### Journey 1: Pre-Flood Preparation & Monitoring (Watch / Prepare State)
1. **Alert Receipt**: User receives a 🟡 **WATCH** or 🟠 **PREPARE** push notification or SMS.
2. **Risk Inspection**: User opens the app, views their village's **Flood Risk Score (e.g., 78%)**, and taps **"Why?"** to see contributing factors (heavy rainfall + saturated soil).
3. **Impact Review**: User checks local impact predictions (e.g., 185 acres of farmland at risk, local Road B at watch level).
4. **Action Readiness**: User opens **Personalized Flood Actions** checklist and completes prep steps (securing livestock, packing medicines/documents).
5. **Emergency Circle Check**: User confirms that their Emergency Circle settings are configured to notify family members if the alert escalates to 🔴 **CRITICAL**.

### Journey 2: Evacuation & Safest Route Navigation (Critical State)
1. **Critical Warning**: Risk model escalates status to 🔴 **CRITICAL**. User receives high-priority app alert and SMS.
2. **Safe Zone Selection**: App automatically displays **Nearest Safe Zone** (e.g., *Community Hall — 2.4 km away*).
3. **Route Request**: User taps **"VIEW SAFEST ROUTE"**. The platform compares available paths, rejects shorter flooded roads, and highlights **Route B (Safest Available Route)**.
4. **Active Navigation**: User begins traveling along Route B.
5. **Dynamic Recalculation**: Mid-journey, a citizen reports rising water on Route B. JalRaksha instantly alerts the user ( *"⚠️ Route Updated"* ) and shifts navigation to Route C.
6. **Arrival**: User arrives at the shelter safely.

### Journey 3: Emergency Distress / Safety Broadcasting
1. **Safety Broadcast**: Once safe, user taps ✅ **"I'm Safe"**. The app dispatches SMS alerts to all Emergency Circle members (*"JalRaksha: Aayan has marked himself SAFE"*).
2. **Distress Activation**: If trapped by floodwaters, user taps 🆘 **"Need Help"**.
3. **Dispatch**: The app dispatches distress SMS with precise GPS coordinates to the Emergency Circle and broadcasts a high-priority distress pin onto the **Admin Dashboard** for official rescue teams.

### Journey 4: Citizen Ground Reporting
1. **Hazard Observation**: Citizen notices river water washing over a bridge.
2. **Report Submission**: Opens JalRaksha, selects **REPORT FLOOD**, attaches a geotagged photo, records a brief voice note (*"Water has reached the road"*), and submits.
3. **System Integration**: The report enters the **Community Intelligence Engine**, raising the local road risk weight, updating the Digital Twin, and triggering route recalculations for nearby evacuees.

---

## 5. Admin Journey

1. **Dashboard Login & Overview**: Disaster management officials log into the web dashboard and view an interactive map displaying active flood regions, risk heatmaps, and aggregated population exposure.
2. **Village-Level Deep Dive**: Administrator clicks on high-risk *Village X*, viewing detailed impact metrics (320 houses, 1 school, 185 acres affected) and active citizen reports with verified photos.
3. **Emergency Alert Verification & Dispatch**: Administrator reviews AI-generated risk recommendations, validates alert parameters, and triggers broadcast push notifications and SMS dispatches across the target region.
4. **Infrastructure & Safe Zone Management**: Admin updates shelter operational statuses (capacity, supply levels) and officially marks flooded roads as blocked, automatically updating the routing engine penalties.
5. **Distress Triage & Response Tracking**: Admin monitors incoming 🆘 **"Need Help"** signals on a real-time queue, dispatches rescue teams to exact coordinates, and monitors SMS/FCM delivery completion statistics.

---

## 6. AI/ML Requirements

* **Flood Risk Assessment Model**:
  * Tabular & spatial ML model (e.g., **XGBoost / Scikit-learn**) trained on historical weather, river gauge levels, soil moisture, elevation data, and past flood events.
  * Outputs: **Flood Risk Score (0-100%)**, **Confidence Level**, and **Data Freshness**.
* **Village Impact Estimation Model**:
  * Spatial overlay analysis combining risk polygons with GIS datasets to estimate population exposure and counts of affected structures (houses, schools, hospitals, farmlands).
* **Explainable AI (XAI) Engine**:
  * Feature attribution system (e.g., **SHAP / LIME** or tree feature contributions) that translates model weights into plain-language explanations for the "Why?" button.
* **Hydraulic Simulation Engine (Digital Twin)**:
  * Elevation-based inundation projection model capable of visualizing water spread for baseline scenarios (e.g., "+1m river level").
* **Citizen Data Processing & NLP**:
  * Speech-to-Text (STT) and Natural Language Processing (NLP) models for processing voice notes and text descriptions in Marathi, Hindi, and English.
  * Image classification / de-duplication heuristics to filter spam or irrelevant citizen uploads.

---

## 7. Data Requirements

* **Environmental & Hydrological Data**: Real-time and forecasted rainfall, river water levels, streamflow rates, soil saturation indices, and temperature.
* **Geographic & Topographic Data**: Digital Elevation Models (DEM / SRTM), slope data, river baselines, village boundaries, land use/cover.
* **Infrastructure & Demographic Data**: OpenStreetMap / GIS layers for roads, bridges, buildings, houses, schools, hospitals, farmlands, official shelters, and population density.
* **Historical Flood Data**: Past inundation boundaries, flood frequency maps, historical rainfall-to-flooding correlation tables.
* **Real-Time Citizen Ground Data**: Geotagged reports (GPS coordinates, timestamp, photo URLs, voice note audio files, text strings, categories).
* **User & Operational Data**: User profiles, encrypted Emergency Circle contacts, alert delivery logs, shelter capacity states, system audit trails.

---

## 8. Map and Routing Requirements

* **Mapping Infrastructure**:
  * Interactive vector tiles powered by **Mapbox** and **OpenStreetMap**.
  * **PostGIS** spatial database for geospatial queries, buffer zones, spatial joins, and raster/vector intersections.
* **Risk-Weighted Safest Available Route Engine**:
  * Modified routing algorithm (custom Dijkstra/A* via OSRM or PostGIS `pgRouting`) where edge weights incorporate distance *plus* heavy penalties for high flood-risk zones, water depth, submerged bridges, road closures, and citizen hazard reports.
  * Explicit guardrail: The UI must present options as **"Safest Available Route"** and never guarantee "100% safety".
* **Dynamic Route Recalculation**:
  * Real-time routing daemon that evaluates active navigation sessions against incoming flood alerts and citizen reports, re-computing paths sub-second if hazards appear.
* **Digital Twin Visualizer**:
  * Multi-layer map rendering river networks, infrastructure nodes, hazard heatmaps, citizen pins, and inundation simulation overlays.

---

## 9. Notification Requirements

* **Three-Channel Architecture**:
  1. **In-App Push Notifications (FCM)**: Low-latency rich notifications containing risk level, safe zone location, and action triggers.
  2. **User SMS**: Direct SMS fallback for registered app users experiencing low connectivity or data loss.
  3. **Emergency Contact SMS**: Automatic SMS sent to non-app users in a citizen's Emergency Circle when critical risks or distress signals occur.
* **Priority Tiering & Anti-Fatigue Rules**:
  * 🟢 **LOW**: In-app status update only.
  * 🟡 **WATCH**: In-app alert + silent push.
  * 🟠 **PREPARE**: High-priority push notification.
  * 🔴 **CRITICAL**: Immediate high-priority push + User SMS + Emergency Contact SMS.
* **Reliability & Queue Tracking**:
  * Asynchronous message queue (e.g., Redis / Celery) with carrier delivery status tracking displayed on the Admin Dashboard.

---

## 10. Emergency Communication Requirements

* **Emergency Circle Management**:
  * CRUD interface for managing trusted contacts (Name, Phone Number, Relationship, Verification Status).
  * Granular notification preference controls per contact (e.g., Prepare alerts OFF, Critical alerts ON).
* **"I'm Safe" Mechanism**:
  * Single-tap action sending automated SMS/push broadcasts to all verified Emergency Circle contacts with time and status.
* **"Need Help" Mechanism**:
  * Single-tap distress trigger capturing current GPS location, sending emergency SMS messages to contacts, and broadcasting a distress pin to the Admin Dashboard.
* **Offline Telephony Fallback**:
  * Client-side native SMS drafting via device telephony APIs when data networks are down.

---

## 11. Database Requirements

* **Primary Relational & Geospatial Store**: **PostgreSQL** with **PostGIS** extension.
  * Stores user accounts, Emergency Circles, village metadata, infrastructure nodes, road networks with dynamic cost weights, safe zone catalogs, and spatial geometries.
* **Time-Series / Telemetry Store**:
  * PostgreSQL partitioned tables or dedicated time-series tables for environmental sensor feeds (rainfall, water levels).
* **Blob / Object Storage**:
  * **Firebase Storage** or **S3-compatible object storage** for storing citizen report photographs and voice notes.
* **Caching & High-Speed State Layer**:
  * **Redis** for session management, fast risk score lookup, active navigation session tracking, and routing penalty caches.

---

## 12. Multilingual Requirements

* **Supported Languages**: **Marathi**, **Hindi**, and **English**.
* **Internationalization (i18n)**:
  * Complete localization of application UI, alert titles, safety instructions, action checklists, and navigation directions.
* **Dynamic Localized AI Outputs**:
  * Template-driven natural language generation ensuring "Why?" explanations and SMS alerts are formatted naturally in the user's selected language.
* **Multilingual Speech & Text Processing**:
  * Support for Marathi, Hindi, and English in citizen voice notes and text report analysis.

---

## 13. Offline Requirements

* **Client-Side Persistence**:
  * Local database (**SQLite / Hive / SharedPreferences**) in the Flutter application.
  * Caches basic flood safety instructions, emergency contacts, Emergency Circle preferences, last-known risk assessment, and nearest safe zone coordinates.
* **Offline Maps & Navigation Guidelines**:
  * Caching of local vector tile packages and static route guidance to shelters.
* **SMS Gateway Fallback**:
  * Seamless fallback from FCM push to SMS dispatch when IP networks fail.
* **Background Sync Queue**:
  * Offline-created citizen reports are stored locally and synced automatically once cellular data connection is re-established.

---

## 14. Security Requirements

* **Data Privacy & PII Protection**:
  * End-to-end encryption (TLS 1.3) in transit; AES-256 encryption at rest for sensitive PII (user phone numbers, location histories, Emergency Circle contacts).
* **Authentication & Role-Based Access Control (RBAC)**:
  * **Firebase Auth / JWT** implementation enforcing strict separation between Citizen Users, Emergency Contacts, and Disaster Management Administrators.
* **Citizen Report Verification & Anti-Spam**:
  * Geofence validation, rate limiting, and admin verification workflows to prevent false flood reports or malicious road closure submissions.
* **High Availability & Resilience**:
  * Redundant server deployment (Docker, load balancers) designed to withstand sudden traffic spikes during major flood emergencies.

---

## 15. Components That Can Be Built as an MVP

To deliver fast value while validating core concepts, the **Minimum Viable Product (MVP)** should focus on:

1. **Core AI Risk & Impact Model**: Baseline tabular risk model (XGBoost/Scikit-learn) calculating village Flood Risk Scores, Confidence Levels, and basic impact counts.
2. **Explainable Risk UI**: The **"Why?"** explanation modal displaying contributing environmental factors.
3. **4-Tier Alert System & 3-Channel Notifications**: In-app push notifications (FCM) and basic SMS dispatches for registered users and Emergency Contacts.
4. **Emergency Circle & Quick Actions**: Contact management with functional **"I'm Safe"** and **"Need Help"** SMS triggers.
5. **Safe Zone Detection & Baseline Safest Route**: Spatial lookup of nearest safe zones and static risk-weighted routing avoiding known flood polygons.
6. **Basic Citizen Flood Reporting**: Photo, text, and GPS submission interface.
7. **Multilingual Frontend**: Flutter application supporting Marathi, Hindi, and English.
8. **Admin Dashboard (MVP)**: Web console showing active alerts, risk maps, citizen report queues, and manual SMS broadcast triggers.
9. **Basic Offline Support**: Local caching of emergency contacts, safety checklists, and last-known risk state.

---

## 16. Components That Should Be Considered Advanced / Future Features

The following complex modules should be phased into future releases following MVP validation:

1. **Village Digital Twin with Interactive "+1m River Level" Simulation**: High-resolution hydraulic inundation simulation requiring fine-grained DEM data.
2. **Real-Time En-Route Dynamic Recalculation**: Sub-second active navigation re-routing daemon triggered by live ground reports.
3. **Voice Note AI Processing (STT & NLP)**: Automated transcription and sentiment/category extraction for Marathi and Hindi voice reports.
4. **Multi-Modal Satellite & Radar Fusion**: Automated ingestion of SAR (Synthetic Aperture Radar) satellite imagery for direct water-surface detection.
5. **Carrier-Level Location-Based SMS Broadcasting**: Integration with national telecom cell-broadcast systems for non-registered populations.
6. **IoT Sensor & Drone Direct Feeds**: Direct telemetry pipelines from automated water level sensors and aerial drone surveillance.

---

## Summary of Technology Stack Alignment

| Layer | Technology Choice |
| :--- | :--- |
| **Frontend Mobile App** | Flutter (Cross-platform iOS/Android) |
| **Backend API** | FastAPI (Python 3.11+) |
| **Database & GIS** | PostgreSQL + PostGIS |
| **AI / ML Engine** | Python, Pandas, Scikit-learn, XGBoost |
| **Maps & Routing** | Mapbox, OpenStreetMap, PostGIS spatial algorithms / OSRM |
| **Notifications & SMS** | Firebase Cloud Messaging (FCM), SMS Gateway API |
| **Storage & Auth** | Firebase Storage / S3, Firebase Auth / JWT |
| **Deployment** | Docker containers |
