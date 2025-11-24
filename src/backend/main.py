from fastapi import FastAPI, Query
from typing import List, Optional
from functools import lru_cache
import random
from .data_loader import data_loader
from .analytics import (
    calculate_metrics, get_revenue_by_vehicle, get_revenue_by_hour,
    get_distance_revenue_correlation, get_vtat_rating_impact,
    get_cancellation_analysis, get_payment_method_analysis,
    get_location_insights, get_rating_distribution, get_recommendations
)
from .statistical_tests import test_revenue_hypotheses, test_rating_hypotheses
from .ml_models import revenue_model, rating_model
from .models import MetricsResponse, RevenueByVehicle, RevenueByTime, Ride

app = FastAPI(title="Ridesharing Analytics API")

@app.on_event("startup")
async def startup_event():
    """Load data and train ML models on startup"""
    print("Loading dataset...")
    df = data_loader.load_data()
    
    print("Training revenue prediction model...")
    revenue_metrics = revenue_model.train(df)
    print(f"Revenue model trained: R² = {revenue_metrics.get('test_r2', 'N/A'):.3f}")
    
    print("Training rating prediction model...")
    rating_metrics = rating_model.train(df)
    print(f"Rating model trained: Accuracy = {rating_metrics.get('test_accuracy', 'N/A'):.3f}")
    
    print("API ready!")

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api/metrics", response_model=MetricsResponse)
def get_metrics(
    vehicle_types: Optional[List[str]] = Query(None),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    df = data_loader.get_filtered_data(vehicle_types, start_date, end_date)
    return calculate_metrics(df)

@app.get("/api/revenue-by-vehicle", response_model=List[RevenueByVehicle])
def revenue_by_vehicle(
    vehicle_types: Optional[List[str]] = Query(None),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    df = data_loader.get_filtered_data(vehicle_types, start_date, end_date)
    return get_revenue_by_vehicle(df)

@app.get("/api/revenue-by-hour", response_model=List[RevenueByTime])
def revenue_by_hour(
    vehicle_types: Optional[List[str]] = Query(None),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    df = data_loader.get_filtered_data(vehicle_types, start_date, end_date)
    return get_revenue_by_hour(df)

@app.get("/api/vehicle-types")
def get_vehicle_types():
    df = data_loader.load_data()
    return df['vehicle_type'].unique().tolist()

@app.get("/api/recent-rides")
def get_recent_rides(limit: int = 10):
    """
    Simulates a live feed by returning a random sample of rides.
    In a real app, this would query the latest entries from a DB.
    """
    df = data_loader.load_data()
    # Sample random rows to simulate "new" incoming data
    sample = df.sample(n=limit).to_dict(orient='records')
    return sample

# NEW ENDPOINTS

@app.get("/api/distance-analysis")
def distance_analysis(
    vehicle_types: Optional[List[str]] = Query(None),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Analyze relationship between ride distance and revenue"""
    df = data_loader.get_filtered_data(vehicle_types, start_date, end_date)
    return get_distance_revenue_correlation(df)

@app.get("/api/vtat-impact")
def vtat_impact(
    vehicle_types: Optional[List[str]] = Query(None),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Analyze VTAT (pickup time) impact on ratings"""
    df = data_loader.get_filtered_data(vehicle_types, start_date, end_date)
    return get_vtat_rating_impact(df)

@app.get("/api/cancellation-metrics")
def cancellation_metrics(
    vehicle_types: Optional[List[str]] = Query(None),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get cancellation rates and revenue loss analysis"""
    df = data_loader.get_filtered_data(vehicle_types, start_date, end_date)
    return get_cancellation_analysis(df)

@app.get("/api/payment-insights")
def payment_insights(
    vehicle_types: Optional[List[str]] = Query(None),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Analyze revenue and cancellation patterns by payment method"""
    df = data_loader.get_filtered_data(vehicle_types, start_date, end_date)
    return get_payment_method_analysis(df)

@app.get("/api/location-insights")
def location_insights(
    vehicle_types: Optional[List[str]] = Query(None),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    top_n: int = 10
):
    """Get top revenue pickup and drop locations"""
    df = data_loader.get_filtered_data(vehicle_types, start_date, end_date)
    return get_location_insights(df, top_n=top_n)

@app.get("/api/rating-distribution")
def rating_distribution(
    vehicle_types: Optional[List[str]] = Query(None),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get actual rating distribution for drivers and customers"""
    df = data_loader.get_filtered_data(vehicle_types, start_date, end_date)
    return get_rating_distribution(df)

@app.get("/api/recommendations")
def recommendations(
    vehicle_types: Optional[List[str]] = Query(None),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get actionable recommendations for drivers"""
    df = data_loader.get_filtered_data(vehicle_types, start_date, end_date)
    return get_recommendations(df)

# STATISTICAL TESTING & ML ENDPOINTS

@app.get("/api/statistical-tests")
def get_statistical_tests(
    vehicle_types: Optional[List[str]] = Query(None),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Run all hypothesis tests and return results with p-values"""
    df = data_loader.get_filtered_data(vehicle_types, start_date, end_date)
    revenue_tests = test_revenue_hypotheses(df)
    rating_tests = test_rating_hypotheses(df)
    return {
        'revenue_hypotheses': revenue_tests,
        'rating_hypotheses': rating_tests,
        'total_tests': len(revenue_tests) + len(rating_tests),
        'significant_tests': sum(1 for t in revenue_tests + rating_tests if t['significant'])
    }

@app.get("/api/model-performance")
def get_model_performance():
    """Get ML model performance metrics"""
    return {
        'revenue_model': revenue_model.metrics,
        'rating_model': rating_model.metrics
    }

@app.get("/api/feature-importance")
def get_feature_importance():
    """Get feature importance from ML models"""
    return {
        'revenue_drivers': revenue_model.get_feature_importance(),
        'rating_drivers': rating_model.get_feature_importance()
    }
