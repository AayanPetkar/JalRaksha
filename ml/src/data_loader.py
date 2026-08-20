from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseDataProvider(ABC):
    """Abstract Base Class for Data Providers (Synthetic vs Real)."""
    
    @abstractmethod
    def fetch_environmental_data(self, village_id: str) -> Dict[str, Any]:
        pass

class SyntheticDemoDataProvider(BaseDataProvider):
    """Used for development, unit testing, and SIH demonstration mode."""
    
    def fetch_environmental_data(self, village_id: str) -> Dict[str, Any]:
        return {
            "village_id": village_id,
            "rainfall_24h_mm": 120.0,
            "river_water_level_m": 4.5,
            "soil_moisture_index": 85.0,
            "temperature_celsius": 26.5,
            "mean_elevation_m": 12.0,
            "distance_to_river_m": 150.0,
            "historical_flood_freq": 3,
            "source_tag": "SIMULATED_DEMO_DATA"
        }

class RealHydrologicalDataProvider(BaseDataProvider):
    """Placeholder interface for live production data feeds (CWC, IMD, PostGIS)."""
    
    def fetch_environmental_data(self, village_id: str) -> Dict[str, Any]:
        # Interface stub to be implemented when real data pipelines are connected
        raise NotImplementedError("Real hydrological data provider requires live API keys.")

if __name__ == "__main__":
    provider = SyntheticDemoDataProvider()
    print("Demo Data Loader Output:", provider.fetch_environmental_data("v-1029"))
