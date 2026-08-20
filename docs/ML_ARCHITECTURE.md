# AI/ML Risk Engine Architecture — JalRaksha

## 1. Overview

The JalRaksha AI/ML Risk Engine evaluates local flood risks, estimates structural and agricultural impacts, and provides plain-language explanations using SHAP (SHapley Additive exPlanations).

To ensure safety and integrity during emergencies:
1. **Model Outputs are Predictions**: Outputs are tagged as `AI_PREDICTION` and must never be presented as official government disaster warnings.
2. **Strict Data Ingestion Abstraction**: The machine learning engine uses an abstract **Data Provider Interface**, allowing seamless switching between synthetic/demo data (for development/SIH pitch) and real sensor feeds (CWC, IMD, PostGIS spatial queries).

---

## 2. ML Pipeline Architecture

```
Raw Hydrological & Spatial Data (Real or Abstracted Provider)
               ↓
    Data Preprocessing & Cleaning
               ↓
    Feature Engineering Engine
               ↓
  XGBoost Risk Scoring Regressor / Classifier
               ↓
 ┌─────────────┴─────────────┐
 ↓                           ↓
Flood Risk Score (0-100%)    SHAP Explainer Engine
Confidence Interval (%)      Feature Contribution Weights (%)
Risk Level (🟢/🟡/🟠/🔴)     "Why?" Text Generator
```

---

## 3. Input Feature Matrix

The model ingests 10 core features across environmental, spatial, and historical dimensions:

| Feature Name | Type | Description | Primary Unit / Scale |
| :--- | :--- | :--- | :--- |
| `rainfall_24h_mm` | Float | Cumulative 24-hour rainfall forecast | Millimeters (mm) |
| `river_water_level_m` | Float | Current river gauge level above baseline | Meters (m) |
| `river_discharge_rate` | Float | Estimated water discharge rate | Cubic meters/sec ($m^3/s$) |
| `soil_moisture_index` | Float | Soil saturation level | Percentage (0.0 - 100.0%) |
| `temperature_celsius` | Float | Ambient temperature | Celsius (°C) |
| `mean_elevation_m` | Float | Average village/point terrain elevation | Meters above sea level (m) |
| `distance_to_river_m` | Float | Euclidean/Spatial distance to nearest river | Meters (m) |
| `historical_flood_freq` | Float | Number of flood events in past 10 years | Integer count |
| `slope_degrees` | Float | Terrain slope steepness | Degrees (0 - 90°) |
| `recent_citizen_reports_count` | Int | Unverified citizen flood reports in past 2h | Integer count |

---

## 4. Model Architecture & Output Specifications

### Model Selection: **XGBoost (eXtreme Gradient Boosting)**
- **Regressor / Classifier**: Trained on historical flood event data to output a continuous risk index from $0.0$ to $100.0$.
- **Alert Tier Mapping**:
  - $0.0 - 29.9\%$: 🟢 **LOW — Normal**
  - $30.0 - 59.9\%$: 🟡 **WATCH — Monitor**
  - $60.0 - 79.9\%$: 🟠 **PREPARE — Get Ready**
  - $80.0 - 100.0\%$: 🔴 **CRITICAL — Immediate Attention**

### Confidence Score Calculation
$$\text{Confidence Score} = \min\left(1.0, \frac{\text{Data Freshness (mins)}}{\text{Max Stale Threshold (60 mins)}}\right) \times \text{Model Certainty Index}$$

---

## 5. Explainable AI (XAI) Engine

When a user taps **"Why am I getting this warning?"**, the SHAP engine extracts local feature attribution values ($\phi_i$) for that specific location:

$$\text{Risk Score} = \beta_0 + \sum_{i=1}^{n} \phi_i$$

### Text Generation Rules (Multilingual)
- **`HEAVY_RAINFALL`**: "Heavy rainfall forecast" / "मुसळधार पावसाचा अंदाज"
- **`RIVER_LEVEL`**: "Increasing river water level" / "कृष्णा नदीची पातळी वाढत आहे"
- **`SOIL_SATURATION`**: "High soil moisture saturation" / "जमिनीची पाझर क्षमता पूर्ण झाली आहे"
- **`LOW_ELEVATION`**: "Low-lying geographical area" / "सखल भौगोलिक स्थान"

---

## 6. Data Provider Interface Pattern (Synthetic vs Real Data)

To avoid using fake data as real disaster information during live operation while enabling offline testing/demos, the ML pipeline implements a strict Abstract Base Class (ABC):

```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseDataProvider(ABC):
    @abstractmethod
    def fetch_environmental_data(self, village_id: str) -> Dict[str, Any]:
        """Fetch rainfall, river level, soil moisture for a village."""
        pass

class SyntheticDemoDataProvider(BaseDataProvider):
    """Used strictly for development, testing, and SIH demonstration mode."""
    def fetch_environmental_data(self, village_id: str) -> Dict[str, Any]:
        return {
            "rainfall_24h_mm": 125.0,
            "river_water_level_m": 4.2,
            "soil_moisture_index": 88.5,
            "source_tag": "SIMULATED_DEMO_DATA"
        }

class RealHydrologicalDataProvider(BaseDataProvider):
    """Used for live production queries (CWC, IMD, Weather API)."""
    def fetch_environmental_data(self, village_id: str) -> Dict[str, Any]:
        # Live HTTP API fetch implementation
        return {
            "source_tag": "OFFICIAL_DATA"
        }
```

---

## 7. Operational Guidelines
- **Model Training Notice**: Model training scripts are placed in `ml/src/model_pipeline.py`. Training will be performed once verified datasets are loaded during Phase 7.
- **Safety Disclaimer**: All responses generated by the ML pipeline automatically append the mandatory `source_tag: "AI_PREDICTION"` header.
