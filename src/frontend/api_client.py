import requests
import pandas as pd
import os

API_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api")

class APIClient:
    def get_vehicle_types(self):
        try:
            response = requests.get(f"{API_URL}/vehicle-types")
            return response.json()
        except:
            return []

    def get_metrics(self, vehicle_types=None, start_date=None, end_date=None):
        params = {}
        if vehicle_types:
            params['vehicle_types'] = vehicle_types
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
            
        response = requests.get(f"{API_URL}/metrics", params=params)
        return response.json()

    def get_revenue_by_vehicle(self, vehicle_types=None, start_date=None, end_date=None):
        params = {}
        if vehicle_types:
            params['vehicle_types'] = vehicle_types
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
            
        response = requests.get(f"{API_URL}/revenue-by-vehicle", params=params)
        return pd.DataFrame(response.json())

    def get_revenue_by_hour(self, vehicle_types=None, start_date=None, end_date=None):
        params = {}
        if vehicle_types:
            params['vehicle_types'] = vehicle_types
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
            
        response = requests.get(f"{API_URL}/revenue-by-hour", params=params)
        return pd.DataFrame(response.json())

    def get_recent_rides(self, limit=10):
        try:
            response = requests.get(f"{API_URL}/recent-rides", params={"limit": limit})
            return pd.DataFrame(response.json())
        except:
            return pd.DataFrame()

    def _build_params(self, vehicle_types=None, start_date=None, end_date=None):
        """Helper method to build query parameters"""
        params = {}
        if vehicle_types:
            params['vehicle_types'] = vehicle_types
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        return params

    # NEW: Advanced analytics methods
    def get_distance_analysis(self, vehicle_types=None, start_date=None, end_date=None):
        params = self._build_params(vehicle_types, start_date, end_date)
        try:
            response = requests.get(f"{API_URL}/distance-analysis", params=params)
            return response.json()
        except:
            return {'bins': [], 'avg_revenue': [], 'correlation': 0, 'count': []}
    
    def get_vtat_impact(self, vehicle_types=None, start_date=None, end_date=None):
        params = self._build_params(vehicle_types, start_date, end_date)
        try:
            response = requests.get(f"{API_URL}/vtat-impact", params=params)
            return response.json()
        except:
            return {'vtat_bins': [], 'avg_driver_rating': [], 'avg_customer_rating': [], 'count': [], 'correlation_driver': 0, 'correlation_customer': 0}
    
    def get_cancellation_metrics(self, vehicle_types=None, start_date=None, end_date=None):
        params = self._build_params(vehicle_types, start_date, end_date)
        try:
            response = requests.get(f"{API_URL}/cancellation-metrics", params=params)
            return response.json()
        except:
            return {}
    
    def get_payment_insights(self, vehicle_types=None, start_date=None, end_date=None):
        params = self._build_params(vehicle_types, start_date, end_date)
        try:
            response = requests.get(f"{API_URL}/payment-insights", params=params)
            return response.json()
        except:
            return {'methods': [], 'avg_revenue': [], 'cancellation_rate': [], 'count': []}
    
    def get_location_insights(self, vehicle_types=None, start_date=None, end_date=None, top_n=10):
        params = self._build_params(vehicle_types, start_date, end_date)
        params['top_n'] = top_n
        try:
            response = requests.get(f"{API_URL}/location-insights", params=params)
            return response.json()
        except:
            return {'top_pickup': [], 'top_drop': []}
    
    def get_rating_distribution(self, vehicle_types=None, start_date=None, end_date=None):
        params = self._build_params(vehicle_types, start_date, end_date)
        try:
            response = requests.get(f"{API_URL}/rating-distribution", params=params)
            return response.json()
        except:
            return {'driver': {'stars': [], 'counts': []}, 'customer': {'stars': [], 'counts': []}}
    
    def get_recommendations(self, vehicle_types=None, start_date=None, end_date=None):
        params = self._build_params(vehicle_types, start_date, end_date)
        try:
            response = requests.get(f"{API_URL}/recommendations", params=params)
            return response.json()
        except:
            return []

    # STATISTICAL & ML METHODS
    def get_statistical_tests(self, vehicle_types=None, start_date=None, end_date=None):
        params = self._build_params(vehicle_types, start_date, end_date)
        try:
            response = requests.get(f"{API_URL}/statistical-tests", params=params)
            return response.json()
        except:
            return {'revenue_hypotheses': [], 'rating_hypotheses': [], 'total_tests': 0, 'significant_tests': 0}
    
    def get_model_performance(self):
        try:
            response = requests.get(f"{API_URL}/model-performance")
            return response.json()
        except:
            return {'revenue_model': {}, 'rating_model': {}}
    
    def get_feature_importance(self):
        try:
            response = requests.get(f"{API_URL}/feature-importance")
            return response.json()
        except:
            return {'revenue_drivers': [], 'rating_drivers': []}

api_client = APIClient()
