from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error, accuracy_score, classification_report
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

class RevenuePredictionModel:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
        self.feature_importances_ = None
        self.label_encoders = {}
        self.metrics = {}
        self.feature_names = []
        
    def prepare_features(self, df):
        """Encode categorical features and select relevant columns"""
        feature_cols = [
            'hour', 'day_of_week_num', 'month', 
            'is_weekend', 'is_peak_morning', 'is_peak_evening',
            'ride_distance', 'avg_vtat', 'avg_ctat',
            'vehicle_type', 'payment_method'
        ]
        
        # Filter to only include columns that exist
        existing_cols = [col for col in feature_cols if col in df.columns]
        df_features = df[existing_cols].copy()
        
        # Encode categorical variables
        for col in ['vehicle_type', 'payment_method']:
            if col in df_features.columns:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    df_features[col] = self.label_encoders[col].fit_transform(df_features[col].astype(str).fillna('unknown'))
                else:
                    # Handle new categories in test data
                    known_classes = set(self.label_encoders[col].classes_)
                    df_features[col] = df_features[col].astype(str).fillna('unknown').apply(
                        lambda x: x if x in known_classes else 'unknown'
                    )
                    df_features[col] = self.label_encoders[col].transform(df_features[col])
        
        self.feature_names = df_features.columns.tolist()
        return df_features
    
    def train(self, df):
        """Train the revenue prediction model"""
        # Filter to completed rides with valid booking values
        df_clean = df[(df['is_completed'] == True) & (df['booking_value'].notna())].copy()
        
        if len(df_clean) < 100:
            return {'error': 'Insufficient data for training'}
        
        X = self.prepare_features(df_clean)
        y = df_clean['booking_value']
        
        # Remove rows with any NaN values
        valid_idx = X.notna().all(axis=1) & y.notna()
        X = X[valid_idx]
        y = y[valid_idx]
        
        if len(X) < 100:
            return {'error': 'Insufficient valid data after cleaning'}
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.model.fit(X_train, y_train)
        
        # Calculate metrics
        train_pred = self.model.predict(X_train)
        test_pred = self.model.predict(X_test)
        
        self.metrics = {
            'train_r2': float(r2_score(y_train, train_pred)),
            'test_r2': float(r2_score(y_test, test_pred)),
            'train_rmse': float(np.sqrt(mean_squared_error(y_train, train_pred))),
            'test_rmse': float(np.sqrt(mean_squared_error(y_test, test_pred))),
            'train_mae': float(mean_absolute_error(y_train, train_pred)),
            'test_mae': float(mean_absolute_error(y_test, test_pred)),
            'train_samples': int(len(X_train)),
            'test_samples': int(len(X_test))
        }
        
        # Feature importance
        self.feature_importances_ = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        return self.metrics
    
    def get_feature_importance(self):
        """Get top 10 features"""
        if self.feature_importances_ is not None:
            return self.feature_importances_.head(10).to_dict('records')
        return []

class RatingPredictionModel:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
        self.feature_importances_ = None
        self.label_encoders = {}
        self.metrics = {}
        self.feature_names = []
        
    def prepare_features(self, df):
        """Same feature preparation as revenue model"""
        feature_cols = [
            'hour', 'day_of_week_num', 'month', 
            'is_weekend', 'is_peak_morning', 'is_peak_evening',
            'ride_distance', 'avg_vtat', 'avg_ctat',
            'vehicle_type', 'payment_method', 'booking_value'
        ]
        
        existing_cols = [col for col in feature_cols if col in df.columns]
        df_features = df[existing_cols].copy()
        
        # Encode categorical variables
        for col in ['vehicle_type', 'payment_method']:
            if col in df_features.columns:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    df_features[col] = self.label_encoders[col].fit_transform(df_features[col].astype(str).fillna('unknown'))
                else:
                    known_classes = set(self.label_encoders[col].classes_)
                    df_features[col] = df_features[col].astype(str).fillna('unknown').apply(
                        lambda x: x if x in known_classes else 'unknown'
                    )
                    df_features[col] = self.label_encoders[col].transform(df_features[col])
        
        self.feature_names = df_features.columns.tolist()
        return df_features
    
    def train(self, df):
        """Train the rating prediction model (classify into Low/Medium/High)"""
        df_clean = df[(df['is_completed'] == True) & (df['driver_rating_category'].notna())].copy()
        
        if len(df_clean) < 100:
            return {'error': 'Insufficient data for training'}
        
        X = self.prepare_features(df_clean)
        y = df_clean['driver_rating_category']
        
        # Remove rows with any NaN values
        valid_idx = X.notna().all(axis=1) & y.notna()
        X = X[valid_idx]
        y = y[valid_idx]
        
        if len(X) < 100:
            return {'error': 'Insufficient valid data after cleaning'}
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.model.fit(X_train, y_train)
        
        # Calculate metrics
        train_pred = self.model.predict(X_train)
        test_pred = self.model.predict(X_test)
        
        self.metrics = {
            'train_accuracy': float(accuracy_score(y_train, train_pred)),
            'test_accuracy': float(accuracy_score(y_test, test_pred)),
            'train_samples': int(len(X_train)),
            'test_samples': int(len(X_test))
        }
        
        # Feature importance
        self.feature_importances_ = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        return self.metrics
    
    def get_feature_importance(self):
        """Get top 10 features"""
        if self.feature_importances_ is not None:
            return self.feature_importances_.head(10).to_dict('records')
        return []

# Global model instances
revenue_model = RevenuePredictionModel()
rating_model = RatingPredictionModel()
