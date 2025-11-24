import pandas as pd
import numpy as np
from .models import MetricsResponse, RevenueByVehicle, RevenueByTime

def calculate_metrics(df: pd.DataFrame) -> MetricsResponse:
    return MetricsResponse(
        total_revenue=df['booking_value'].sum(),
        avg_revenue_per_ride=df['booking_value'].mean(),
        total_rides=len(df),
        avg_driver_rating=df['driver_ratings'].mean(),
        avg_customer_rating=df['customer_rating'].mean()
    )

def get_revenue_by_vehicle(df: pd.DataFrame):
    grouped = df.groupby('vehicle_type')['booking_value'].agg(['sum', 'mean']).reset_index()
    return [
        RevenueByVehicle(vehicle_type=row['vehicle_type'], total_revenue=row['sum'], avg_revenue=row['mean'])
        for _, row in grouped.iterrows()
    ]

def get_revenue_by_hour(df: pd.DataFrame):
    grouped = df.groupby('hour')['booking_value'].mean().reset_index()
    return [
        RevenueByTime(hour=row['hour'], avg_revenue=row['booking_value'])
        for _, row in grouped.iterrows()
    ]

# NEW: Distance analysis
def get_distance_revenue_correlation(df: pd.DataFrame):
    """Analyze relationship between ride distance and revenue"""
    df_valid = df[df['ride_distance'].notna() & df['booking_value'].notna()].copy()
    
    if len(df_valid) == 0:
        return {'bins': [], 'avg_revenue': [], 'correlation': 0, 'count': []}
    
    # Create distance bins
    df_valid['distance_bin'] = pd.cut(df_valid['ride_distance'], 
                                       bins=[0, 5, 10, 15, 20, 50], 
                                       labels=['0-5 km', '5-10 km', '10-15 km', '15-20 km', '20+ km'])
    
    grouped = df_valid.groupby('distance_bin', observed=True).agg({
        'booking_value': ['mean', 'count']
    }).reset_index()
    
    # Calculate correlation
    correlation = df_valid[['ride_distance', 'booking_value']].corr().iloc[0, 1]
    
    return {
        'bins': grouped['distance_bin'].astype(str).tolist(),
        'avg_revenue': grouped[('booking_value', 'mean')].tolist(),
        'count': grouped[('booking_value', 'count')].tolist(),
        'correlation': float(correlation) if not pd.isna(correlation) else 0
    }

# NEW: VTAT impact on ratings
def get_vtat_rating_impact(df: pd.DataFrame):
    """Analyze how vehicle time to arrival affects ratings"""
    df_valid = df[df['avg_vtat'].notna() & 
                  (df['driver_ratings'].notna() | df['customer_rating'].notna())].copy()
    
    if len(df_valid) == 0:
        return {'vtat_bins': [], 'avg_driver_rating': [], 'avg_customer_rating': [], 'count': [], 'correlation_driver': 0, 'correlation_customer': 0}
    
    # Create VTAT bins
    df_valid['vtat_bin'] = pd.cut(df_valid['avg_vtat'], 
                                   bins=[0, 5, 10, 15, 20, 100], 
                                   labels=['0-5 min', '5-10 min', '10-15 min', '15-20 min', '20+ min'])
    
    grouped = df_valid.groupby('vtat_bin', observed=True).agg({
        'driver_ratings': 'mean',
        'customer_rating': 'mean',
        'booking_id': 'count'
    }).reset_index()
    
    # Calculate correlations
    corr_driver = df_valid[['avg_vtat', 'driver_ratings']].corr().iloc[0, 1] if df_valid['driver_ratings'].notna().any() else 0
    corr_customer = df_valid[['avg_vtat', 'customer_rating']].corr().iloc[0, 1] if df_valid['customer_rating'].notna().any() else 0
    
    return {
        'vtat_bins': grouped['vtat_bin'].astype(str).tolist(),
        'avg_driver_rating': grouped['driver_ratings'].tolist(),
        'avg_customer_rating': grouped['customer_rating'].tolist(),
        'count': grouped['booking_id'].tolist(),
        'correlation_driver': float(corr_driver) if not pd.isna(corr_driver) else 0,
        'correlation_customer': float(corr_customer) if not pd.isna(corr_customer) else 0
    }

# NEW: Cancellation metrics
def get_cancellation_analysis(df: pd.DataFrame):
    """Analyze cancellation patterns and revenue loss"""
    total_rides = len(df)
    cancelled = df[df['is_cancelled'] == True]
    completed = df[df['is_completed'] == True]
    
    # Basic metrics
    cancellation_rate = (len(cancelled) / total_rides * 100) if total_rides > 0 else 0
    
    # Cancellation by type
    by_customer = len(df[df['cancelled_by_customer'] == True])
    by_driver = len(df[df['cancelled_by_driver'] == True])
    
    # Revenue loss (estimated based on completed rides avg)
    avg_completed_revenue = completed['booking_value'].mean() if len(completed) > 0 else 0
    estimated_loss = avg_completed_revenue * len(cancelled)
    
    # Cancellation by hour
    hourly = df.groupby('hour').agg({
        'is_cancelled': lambda x: (x.sum() / len(x) * 100) if len(x) > 0 else 0
    }).reset_index()
    
    # Cancellation by vehicle type
    by_vehicle = df.groupby('vehicle_type').agg({
        'is_cancelled': lambda x: (x.sum() / len(x) * 100) if len(x) > 0 else 0,
        'booking_id': 'count'
    }).reset_index()
    
    return {
        'cancellation_rate': float(cancellation_rate),
        'total_cancelled': int(len(cancelled)),
        'by_customer': int(by_customer),
        'by_driver': int(by_driver),
        'estimated_revenue_loss': float(estimated_loss),
        'hourly_cancellation': {
            'hours': hourly['hour'].tolist(),
            'rates': hourly['is_cancelled'].tolist()
        },
        'by_vehicle': {
            'types': by_vehicle['vehicle_type'].tolist(),
            'rates': by_vehicle['is_cancelled'].tolist(),
            'counts': by_vehicle['booking_id'].tolist()
        }
    }

# NEW: Payment method analysis
def get_payment_method_analysis(df: pd.DataFrame):
    """Analyze revenue and cancellation patterns by payment method"""
    df_valid = df[df['payment_method'].notna()].copy()
    
    if len(df_valid) == 0:
        return {'methods': [], 'avg_revenue': [], 'cancellation_rate': [], 'count': []}
    
    grouped = df_valid.groupby('payment_method').agg({
        'booking_value': 'mean',
        'is_cancelled': lambda x: (x.sum() / len(x) * 100) if len(x) > 0 else 0,
        'booking_id': 'count',
        'driver_ratings': 'mean'
    }).reset_index()
    
    return {
        'methods': grouped['payment_method'].tolist(),
        'avg_revenue': grouped['booking_value'].tolist(),
        'cancellation_rate': grouped['is_cancelled'].tolist(),
        'count': grouped['booking_id'].tolist(),
        'avg_rating': grouped['driver_ratings'].tolist()
    }

# NEW: Location insights
def get_location_insights(df: pd.DataFrame, top_n=10):
    """Identify top revenue locations"""
    df_valid = df[df['pickup_location'].notna() & df['booking_value'].notna()].copy()
    
    if len(df_valid) == 0:
        return {'top_pickup': [], 'top_drop': []}
    
    # Top pickup locations by revenue
    pickup_grouped = df_valid.groupby('pickup_location').agg({
        'booking_value': ['sum', 'mean', 'count']
    }).reset_index()
    pickup_grouped.columns = ['location', 'total_revenue', 'avg_revenue', 'ride_count']
    pickup_grouped = pickup_grouped.nlargest(top_n, 'total_revenue')
    
    # Top drop locations
    df_drop = df[df['drop_location'].notna() & df['booking_value'].notna()].copy()
    if len(df_drop) > 0:
        drop_grouped = df_drop.groupby('drop_location').agg({
            'booking_value': ['sum', 'mean', 'count']
        }).reset_index()
        drop_grouped.columns = ['location', 'total_revenue', 'avg_revenue', 'ride_count']
        drop_grouped = drop_grouped.nlargest(top_n, 'total_revenue')
    else:
        drop_grouped = pd.DataFrame(columns=['location', 'total_revenue', 'avg_revenue', 'ride_count'])
    
    return {
        'top_pickup': pickup_grouped.to_dict('records'),
        'top_drop': drop_grouped.to_dict('records')
    }

# NEW: Rating distribution
def get_rating_distribution(df: pd.DataFrame):
    """Get actual rating distribution (not dummy data)"""
    driver_dist = df['driver_ratings'].value_counts(bins=[0, 1, 2, 3, 4, 5], sort=False).to_dict() if df['driver_ratings'].notna().any() else {}
    customer_dist = df['customer_rating'].value_counts(bins=[0, 1, 2, 3, 4, 5], sort=False).to_dict() if df['customer_rating'].notna().any() else {}
    
    # Simplify to star counts
    driver_counts = [0] * 5
    customer_counts = [0] * 5
    
    for rating in df['driver_ratings'].dropna():
        idx = int(rating) - 1
        if 0 <= idx < 5:
            driver_counts[idx] += 1
    
    for rating in df['customer_rating'].dropna():
        idx = int(rating) - 1
        if 0 <= idx < 5:
            customer_counts[idx] += 1
    
    return {
        'driver': {
            'stars': ['1 Star', '2 Stars', '3 Stars', '4 Stars', '5 Stars'],
            'counts': driver_counts
        },
        'customer': {
            'stars': ['1 Star', '2 Stars', '3 Stars', '4 Stars', '5 Stars'],
            'counts': customer_counts
        }
    }

# NEW: Driver recommendations
def get_recommendations(df: pd.DataFrame):
    """Generate actionable recommendations for drivers"""
    recommendations = []
    
    # 1. Peak revenue hours
    hourly_revenue = df.groupby('hour')['booking_value'].mean()
    if not hourly_revenue.empty:
        peak_hours = hourly_revenue.nlargest(3).index.tolist()
        recommendations.append({
            'category': 'Peak Hours',
            'title': 'Drive during peak revenue hours',
            'description': f"Hours {', '.join(map(str, peak_hours))} generate the highest average revenue per ride.",
            'icon': '🕐'
        })
    
    # 2. Best vehicle type
    vehicle_revenue = df.groupby('vehicle_type')['booking_value'].mean()
    if not vehicle_revenue.empty:
        best_vehicle = vehicle_revenue.idxmax()
        best_revenue = vehicle_revenue.max()
        recommendations.append({
            'category': 'Vehicle Strategy',
            'title': f'Consider {best_vehicle}',
            'description': f"{best_vehicle} has the highest average revenue (${best_revenue:.2f} per ride).",
            'icon': '🚗'
        })
    
    # 3. VTAT impact
    vtat_corr = df[['avg_vtat', 'driver_ratings']].corr().iloc[0, 1] if df['avg_vtat'].notna().any() and df['driver_ratings'].notna().any() else None
    if vtat_corr and vtat_corr < -0.1:
        recommendations.append({
            'category': 'Rating Optimization',
            'title': 'Minimize pickup time',
            'description': f"Longer pickup times correlate with lower ratings (correlation: {vtat_corr:.2f}). Accept rides closer to you.",
            'icon': '⭐'
        })
    
    # 4. High-value locations
    location_data = get_location_insights(df, top_n=3)
    if location_data['top_pickup']:
        top_loc = location_data['top_pickup'][0]['location']
        recommendations.append({
            'category': 'Location Tips',
            'title': f'Position near {top_loc}',
            'description': f"{top_loc} is the highest revenue pickup zone.",
            'icon': '📍'
        })
    
    # 5. Avoid high-cancellation scenarios
    cancellation_data = get_cancellation_analysis(df)
    if cancellation_data['by_vehicle']['rates']:
        worst_vehicle_idx = cancellation_data['by_vehicle']['rates'].index(max(cancellation_data['by_vehicle']['rates']))
        worst_vehicle = cancellation_data['by_vehicle']['types'][worst_vehicle_idx]
        worst_rate = cancellation_data['by_vehicle']['rates'][worst_vehicle_idx]
        recommendations.append({
            'category': 'Avoid',
            'title': f'Caution with {worst_vehicle}',
            'description': f"{worst_vehicle} has the highest cancellation rate ({worst_rate:.1f}%).",
            'icon': '⚠️'
        })
    
    return recommendations
