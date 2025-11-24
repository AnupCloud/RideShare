import pandas as pd
import os
from datetime import datetime

class DataLoader:
    _instance = None
    _data = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataLoader, cls).__new__(cls)
        return cls._instance

    def load_data(self):
        if self._data is not None:
            return self._data
        
        filepath = os.path.join(os.path.dirname(__file__), '../data/ridesharing.csv')
        print(f"Loading data from {filepath}...")
        try:
            df = pd.read_csv(filepath)
            
            # Clean columns
            df.columns = [col.strip().replace(' ', '_').lower() for col in df.columns]
            
            # DateTime conversion
            df['booking_timestamp'] = pd.to_datetime(df['date'].astype(str) + ' ' + df['time'].astype(str), errors='coerce')
            df['hour'] = df['booking_timestamp'].dt.hour
            df['day_of_week'] = df['booking_timestamp'].dt.day_name()
            
            # Time period classification
            df['time_period'] = pd.cut(df['hour'], bins=[0, 6, 12, 18, 24], 
                                       labels=['Night', 'Morning', 'Afternoon', 'Evening'],
                                       include_lowest=True)
            
            # Numeric conversion - expand to include all numerical columns
            numeric_cols = ['booking_value', 'driver_ratings', 'customer_rating', 
                           'ride_distance', 'avg_vtat', 'avg_ctat']
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Cancellation flags
            df['is_cancelled'] = df['booking_status'].str.contains('Cancelled', na=False, case=False)
            df['cancelled_by_customer'] = df['booking_status'].str.contains('Cancelled by Customer', na=False, case=False)
            df['cancelled_by_driver'] = df['booking_status'].str.contains('Cancelled by Driver', na=False, case=False)
            df['is_completed'] = df['booking_status'].str.contains('Completed', na=False, case=False)
            df['is_incomplete'] = df['booking_status'].str.contains('Incomplete', na=False, case=False)
            
            # Advanced feature engineering for ML
            # Temporal features
            df['day_of_week_num'] = df['booking_timestamp'].dt.dayofweek
            df['month'] = df['booking_timestamp'].dt.month
            df['is_weekend'] = df['day_of_week'].isin(['Saturday', 'Sunday'])
            df['is_peak_morning'] = df['hour'].between(7, 10)
            df['is_peak_evening'] = df['hour'].between(17, 20)
            
            # Revenue-derived features
            df['revenue_per_km'] = df['booking_value'] / df['ride_distance'].replace(0, pd.NA)
            df['revenue_per_minute'] = df['booking_value'] / df['avg_ctat'].replace(0, pd.NA)
            
            # Rating categories
            df['driver_rating_category'] = pd.cut(df['driver_ratings'], 
                                                   bins=[0, 2, 3.5, 5], 
                                                   labels=['Low', 'Medium', 'High'],
                                                   include_lowest=True)
            df['customer_rating_category'] = pd.cut(df['customer_rating'], 
                                                      bins=[0, 2, 3.5, 5], 
                                                      labels=['Low', 'Medium', 'High'],
                                                      include_lowest=True)
            
            # Distance categories
            df['distance_category'] = pd.cut(df['ride_distance'],
                                             bins=[0, 5, 10, 20, 100],
                                             labels=['Short', 'Medium', 'Long', 'Very Long'],
                                             include_lowest=True)
                
            self._data = df
            print(f"Data loaded successfully. Shape: {df.shape}")
            return self._data
        except Exception as e:
            print(f"Error loading data: {e}")
            raise e

    def get_filtered_data(self, vehicle_types=None, start_date=None, end_date=None):
        df = self.load_data()
        
        if vehicle_types:
            df = df[df['vehicle_type'].isin(vehicle_types)]
            
        if start_date:
            df = df[df['booking_timestamp'] >= pd.to_datetime(start_date)]
            
        if end_date:
            df = df[df['booking_timestamp'] <= pd.to_datetime(end_date)]
            
        return df

data_loader = DataLoader()
