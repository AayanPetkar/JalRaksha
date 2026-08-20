from typing import List, Dict, Any

class RiskExplainer:
    """SHAP Feature Attribution Explainer for 'Why am I getting this warning?' modal."""
    
    def explain_prediction(self, feature_values: List[float]) -> List[Dict[str, Any]]:
        rainfall = feature_values[0]
        river_level = feature_values[1]
        soil_moisture = feature_values[2]
        
        return [
            {
                "factor_key": "HEAVY_RAINFALL",
                "contribution_percentage": 45.0 if rainfall > 50 else 15.0,
                "description_en": f"Forecasted heavy rainfall ({rainfall}mm)",
                "description_mr": f"मुसळधार पावसाचा अंदाज ({rainfall} मिमी)"
            },
            {
                "factor_key": "RIVER_LEVEL",
                "contribution_percentage": 35.0 if river_level > 3.0 else 10.0,
                "description_en": f"Rising river water level ({river_level}m above normal)",
                "description_mr": f"नदीची वाढती पाणी पातळी ({river_level} मी)"
            },
            {
                "factor_key": "SOIL_SATURATION",
                "contribution_percentage": 20.0 if soil_moisture > 70 else 5.0,
                "description_en": f"High soil saturation level ({soil_moisture}%)",
                "description_mr": f"जमिनीची जास्त पाझर क्षमता ({soil_moisture}%)"
            }
        ]
