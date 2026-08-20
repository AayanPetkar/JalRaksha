from typing import Dict, Any, List

class FeatureEngine:
    """Feature Extraction and Normalization for XGBoost Flood Risk Model."""
    
    FEATURE_NAMES: List[str] = [
        "rainfall_24h_mm",
        "river_water_level_m",
        "soil_moisture_index",
        "temperature_celsius",
        "mean_elevation_m",
        "distance_to_river_m",
        "historical_flood_freq"
    ]
    
    def extract_features(self, raw_data: Dict[str, Any]) -> List[float]:
        return [
            float(raw_data.get("rainfall_24h_mm", 0.0)),
            float(raw_data.get("river_water_level_m", 0.0)),
            float(raw_data.get("soil_moisture_index", 0.0)),
            float(raw_data.get("temperature_celsius", 25.0)),
            float(raw_data.get("mean_elevation_m", 50.0)),
            float(raw_data.get("distance_to_river_m", 1000.0)),
            float(raw_data.get("historical_flood_freq", 0))
        ]
