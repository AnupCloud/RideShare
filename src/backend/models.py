from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Ride(BaseModel):
    booking_id: str
    booking_status: str
    booking_value: Optional[float] = None
    ride_distance: Optional[float] = None
    vehicle_type: str
    booking_timestamp: datetime
    driver_ratings: Optional[float] = None
    customer_rating: Optional[float] = None

class MetricsResponse(BaseModel):
    total_revenue: float
    avg_revenue_per_ride: float
    total_rides: int
    avg_driver_rating: float
    avg_customer_rating: float

class RevenueByVehicle(BaseModel):
    vehicle_type: str
    total_revenue: float
    avg_revenue: float

class RevenueByTime(BaseModel):
    hour: int
    avg_revenue: float

class FilterParams(BaseModel):
    vehicle_type: Optional[List[str]] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
