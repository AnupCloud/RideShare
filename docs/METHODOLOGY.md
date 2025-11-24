# Methodology Documentation

## 1. Data Sources & Scope

### Dataset Information
- **Source**: Ridesharing Analytics Dataset (ridesharing_analytics.csv)
- **Size**: 150,000 rides
- **Columns**: 21 features
- **Time Period**: [Based on data timestamps]
- **Geographic Scope**: Multi-city ridesharing operations

### Data Dictionary

| Column | Type | Description |
|--------|------|-------------|
| booking_id | String | Unique ride identifier |
| booking_timestamp | Datetime | Ride booking time |
| vehicle_type | Categorical | Type of vehicle (Auto, Bike, Go Sedan, etc.) |
| pickup_location | String | Pickup zone/area |
| drop_location | String | Drop zone/area |
| ride_distance | Float | Distance in kilometers |
| booking_value | Float | Revenue generated (currency) |
| booking_status | Categorical | Completed, Cancelled, Incomplete |
| driver_ratings | Float | Driver rating (1-5 scale) |
| customer_rating | Float | Customer rating (1-5 scale) |
| avg_vtat | Float | Average Vehicle Time to Arrival (minutes to pickup) |
| avg_ctat | Float | Average Customer Time at Trip (total trip duration, minutes) |
| payment_method | Categorical | Cash, UPI, Credit Card, Digital Wallet |

---

## 2. Assumptions

### Data Quality Assumptions
1. **Completeness**: Missing values are assumed to be MCAR (Missing Completely At Random)
2. **Accuracy**: Booking values, distances, and times are assumed to be accurately recorded
3. **Validity**: VTAT and CTAT values represent actual operational metrics
4. **Temporal**: Data represents typical operational periods without major anomalies (e.g., pandemic, strikes)

### Business Logic Assumptions
1. **Revenue Attribution**: booking_value represents net revenue after platform fees
2. **Rating Validity**: Ratings are genuine customer/driver feedback, not manipulated
3. **Cancellation Causes**: Cancellation by customer vs driver is accurately recorded
4. **Vehicle Availability**: All vehicle types operate in all time periods (may not be true)

### Analytical Assumptions
1. **Independence**: Individual rides are independent observations
2. **Linearity**: For correlation analysis, relationships are assumed to be linear
3. **Normality**: For parametric tests, numerical variables approximate normal distributions
4. **Homoscedasticity**: Variance is constant across groups (for ANOVA)

---

## 3. Analytical Approach

### 3.1 Data Preprocessing

**Steps**:
1. Load raw CSV data
2. Convert data types (datetime, numeric, categorical)
3. Handle missing values:
   - Columns with >30% missing → Flagged for review/drop
   - Numeric columns → Median imputation
   - Categorical columns → Mode imputation
4. Outlier detection (IQR method):
   - Q1 - 1.5×IQR and Q3 + 1.5×IQR bounds
   - Cap extreme values to bounds
5. Feature engineering (see section 3.2)

**Implementation**: `src/backend/data_loader.py`, `src/backend/data_quality.py`

### 3.2 Feature Engineering

**Temporal Features**:
- `hour`: Extracted from booking_timestamp (0-23)
- `day_of_week`: Monday-Sunday
- `day_of_week_num`: 0-6 for ML models
- `month`: 1-12
- `is_weekend`: Boolean (Saturday/Sunday)
- `is_peak_morning`: Boolean (7-10 AM)
- `is_peak_evening`: Boolean (5-8 PM)

**Derived Metrics**:
- `revenue_per_km` = booking_value / ride_distance
- `revenue_per_minute` = booking_value / avg_ctat

**Categorical Encoding**:
- `driver_rating_category`: Low (1-2), Medium (2-3.5), High (3.5-5)
- `customer_rating_category`: Same binning
- `distance_category`: Short (<5km), Medium (5-10km), Long (10-20km), Very Long (20+km)

**Flags**:
- `is_cancelled`, `cancelled_by_customer`, `cancelled_by_driver`
- `is_completed`, `is_incomplete`

**Implementation**: `src/backend/data_loader.py:47-75`

---

## 4. Statistical Methods

### 4.1 Hypothesis Testing Framework

**Significance Level**: α = 0.05 (5% false positive rate)

**Test Selection Criteria**:
- **t-test (Independent samples)**: Compare means between 2 groups (e.g., Peak vs Non-Peak revenue)
- **ANOVA (One-way)**: Compare means across 3+ groups (e.g., Payment method effect on ratings)
- **Pearson Correlation**: Linear relationship between 2 continuous variables (e.g., Distance vs Revenue)
- **Chi-square**: Independence test for categorical variables (not yet implemented)

**Hypotheses Tested**:

| ID | Hypothesis | Test | Variables |
|----|------------|------|-----------|
| H1 | Premium vehicles → Higher revenue | t-test | vehicle_type (premium vs non) → booking_value |
| H2 | Peak hours → Higher fares | t-test | is_peak → booking_value |
| H3 | Longer distances → Higher revenue | Pearson | ride_distance → booking_value |
| H4 | Cash vs Digital payment affects revenue | t-test | payment_method (cash vs digital) → booking_value |
| H5 | VTAT negatively affects revenue | Pearson | avg_vtat → booking_value |
| H6 | Higher VTAT → Lower driver rating | Pearson | avg_vtat → driver_ratings |
| H7 | Cancellations hurt ratings | t-test | is_cancelled → driver_ratings |
| H8 | Payment method affects ratings | ANOVA | payment_method → driver_ratings |
| H9 | Vehicle type affects ratings | ANOVA | vehicle_type → driver_ratings |
| H10 | Trip duration affects satisfaction | Pearson | avg_ctat → customer_rating |

**Implementation**: `src/backend/statistical_tests.py`

### 4.2 Correlation Analysis

- **Method**: Pearson correlation coefficient (r)
- **Interpretation**:
  - |r| < 0.3: Weak correlation
  - 0.3 ≤ |r| < 0.7: Moderate correlation
  - |r| ≥ 0.7: Strong correlation
- **Significance**: Assessed via p-value from correlation test

---

## 5. Machine Learning Approach

### 5.1 Problem Formulation

**Revenue Prediction (Regression)**:
- **Target**: booking_value (continuous)
- **Objective**: Predict revenue for given ride characteristics
- **Use Case**: Estimate earnings for drivers pre-ride

**Rating Prediction (Classification)**:
- **Target**: driver_rating_category (Low/Medium/High)
- **Objective**: Predict rating category based on ride features
- **Use Case**: Identify at-risk rides for low ratings

### 5.2 Feature Selection

**Features Used** (11 features):
1. hour
2. day_of_week_num
3. month
4. is_weekend
5. is_peak_morning
6. is_peak_evening
7. ride_distance
8. avg_vtat
9. avg_ctat
10. vehicle_type (encoded)
11. payment_method (encoded)

**Encoding Strategy**:
- Categorical variables: LabelEncoder (scikit-learn)
- Binary flags: Already encoded as boolean (0/1)

### 5.3 Model Training Pipeline

**Data Split**:
- Training: 80% of data
- Testing: 20% of data
- Split method: Random (stratified for classification)
- Random seed: 42 (for reproducibility)

**Models Implemented**:

1. **Random Forest Regressor** (Revenue):
   - n_estimators: 100
   - max_depth: 10
   - random_state: 42
   - Rationale: Handles non-linearity, robust to outliers

2. **Random Forest Classifier** (Rating):
   - n_estimators: 100
   - max_depth: 10
   - random_state: 42
   - Classes: Low, Medium, High

**Implementation**: `src/backend/ml_models.py`

### 5.4 Model Evaluation

**Regression Metrics**:
- **R² Score**: Proportion of variance explained (0 = no fit, 1 = perfect fit)
- **RMSE**: Root Mean Squared Error (in currency units)
- **MAE**: Mean Absolute Error (average prediction error)

**Classification Metrics**:
- **Accuracy**: Proportion of correct predictions
- **Precision, Recall, F1**: Per-class performance (future enhancement)

**Validation Strategy**:
- Train-test split for initial evaluation
- 5-fold cross-validation (planned for Phase 2)

### 5.5 Feature Importance

**Method**: Random Forest feature importances (Gini importance)
- Measures average decrease in impurity when splitting on a feature
- Higher value = more important feature

**Interpretation**: Used to identify top revenue/rating drivers

---

## 6. Visualization & Dashboard Design

### 6.1 Dashboard Architecture

**Technology Stack**:
- Backend: FastAPI (Python)
- Frontend: Streamlit
- Charts: Plotly Express (interactive)
- Data Processing: pandas, numpy

**Dashboard Tabs**:
1. Revenue Analysis
2. Rating Analysis
3. Cancellation Insights
4. Driver Recommendations
5. Statistical Tests
6. Predictive Insights
7. Data Quality (new)
8. Multivariate Analysis (planned)

### 6.2 Visualization Principles

1. **Interactivity**: Plotly charts allow hover, zoom, pan
2. **Filtering**: Date range and vehicle type filters apply globally
3. **Color Coding**: Consistent color schemes (e.g., revenue = green, ratings = gold)
4. **Clarity**: Clear axis labels, titles, and legends
5. **Responsiveness**: Charts adapt to container width

---

## 7. Analysis Workflow

**Sequential Steps**:

1. **Data Ingestion** → Load CSV, validate schema
2. **Data Quality** → Missing values, outliers, duplicates
3. **Feature Engineering** → Derive new features
4. **EDA** → Univariate, bivariate, multivariate analysis
5. **Hypothesis Testing** → Validate business questions
6. **Predictive Modeling** → Train ML models, evaluate
7. **Insights Synthesis** → Identify key drivers
8. **Recommendations** → Generate actionable advice
9. **Visualization** → Interactive dashboard
10. **Documentation** → Methodology, limitations, findings

---

## 8. Reproducibility

**Code Organization**:
```
src/backend/
  - data_loader.py (data loading & preprocessing)
  - data_quality.py (quality checks)
  - analytics.py (EDA functions)
  - statistical_tests.py (hypothesis testing)
  - ml_models.py (machine learning)
  - main.py (FastAPI endpoints)
src/frontend/
  - app.py (Streamlit dashboard)
  - api_client.py (backend communication)
  - components.py (reusable UI components)
```

**Dependencies**:
- Managed via `pyproject.toml`
- Key libraries: pandas, numpy, scipy, scikit-learn, statsmodels, plotly, streamlit, fastapi

**Random Seeds**: Set to 42 for all random operations

---

## 9. Limitations of Methodology

*See [LIMITATIONS.md](LIMITATIONS.md) for comprehensive list*

Key methodological limitations:
1. Cross-sectional analysis (no time-series forecasting)
2. Assumes linear relationships for correlation
3. Does not account for hierarchical structure (drivers → rides)
4. Simple imputation for missing values (may introduce bias)

---

## 10. References & Standards

**Statistical Standards**:
- Significance testing: α = 0.05 (standard in social sciences)
- Effect size interpretation: Cohen's guidelines

**ML Best Practices**:
- Train-test split: Standard 80-20
- Cross-validation: 5-fold (industry standard)
- Feature engineering: Domain-driven

**Code Quality**:
- PEP 8 style guidelines (Python)
- Type hints where applicable
- Docstrings for all functions
