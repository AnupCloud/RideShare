# Limitations & Caveats

This document outlines known limitations, potential biases, and caveats of the Ridesharing Analytics analysis. **Critical for interpreting results correctly**.

---

## 1. Data Quality Limitations

### 1.1 Missing Values

**Issue**: Significant missing data in key columns

| Column | Missing % | Impact |
|--------|-----------|--------|
| payment_method | ~40% (cancelled rides) | Payment analysis biased toward completed rides |
| driver_ratings | ~25% (cancelled/incomplete) | Rating analysis excludes problem rides |
| customer_rating | ~25% (cancelled/incomplete) | Customer satisfaction analysis incomplete |
| drop_location | ~15% | Location analysis may miss key zones |

**Implication**: 
- Payment method analysis is **biased toward completed, successful rides**
- True driver rating distribution may be **lower** if cancelled rides had been rated
- Recommendation: Collect ratings even for cancelled rides

### 1.2 Outliers & Data Entry Errors

**Identified Issues**:
1. **Impossible Values**: Some rides show booking_value >> expected for distance
   - Example: $5000 for 2km ride (likely data entry error or surge pricing not flagged)
   - Treatment: Capped using IQR method, but may mask legitimate surge pricing

2. **VTAT/CTAT Anomalies**: 
   - Some VTAT > 120 minutes (unlikely for urban ridesharing)
   - Some CTAT < 1 minute (impossible for completed rides)
   - Recommendation: Validate with operational teams

3. **Distance = 0**: Some completed rides show 0 km distance
   - Likely data recording issues
   - Filtered out in analysis, may underestimate revenue

**Impact**: Revenue and time-based analysis may be **less accurate** than reported

### 1.3 Duplicate & Inconsistent Records

- **Duplicates**: < 1% of rides (likely re-bookings, not actual duplicates)
- **Inconsistencies**: Some rides marked "Completed" with booking_value = 0
  - May be promotional/free rides or data errors

---

## 2. Model Limitations

### 2.1 Revenue Prediction Model (R² = 0.05)

**Performance**: Extremely low R² indicates model explains only **5% of revenue variance**

**Possible Reasons**:
1. **Missing Features**: True revenue drivers not in dataset
   - Surge pricing multipliers
   - Driver experience/tenure
   - Customer loyalty tier  
   - Traffic conditions
   - Weather
   - Special events (concerts, sports)

2. **Revenue is Inherently Random**: Significant portion determined by:
   - Dynamic pricing algorithms (not in data)
   - Customer willingness to pay
   - External factors (competition, market conditions)

3. **Model Simplicity**: Random Forest with 11 features may be too simple

**Implication**: **Do NOT use this model for actual revenue prediction** without significant enhancement

**Future Work**: 
- Collect surge pricing data
- Add driver/customer history features
- Try deep learning models
- Consider it's fundamentally a pricing problem, not predictable from ride characteristics

###2.2 Rating Prediction Model (92% Accuracy)

**Performance**: High accuracy, but **potentially misleading**

**Issues**:
1. **Class Imbalance**: 
   - High ratings: ~85% of data
   - Medium ratings: ~12%
   - Low ratings: ~3%
   - Model achieves 92% by **mostly predicting "High"**

2. **Missing Low-Rating Rides**: Cancelled rides (likely to be low-rated) are excluded

3. **Overfitting Risk**: May not generalize to new drivers/locations

**Implication**: Model is **good at identifying "High" ratings**, but **poor at detecting "Low" ratings** (which are most actionable)

**Recommendation**: 
- Use precision/recall metrics for Low class
- Consider SMOTE or oversampling for imbalanced classes
- Most value is in predicting Low ratings → needs separate model

---

## 3. Statistical Testing Limitations

### 3.1 Multiple Comparisons Problem

**Issue**: Testing 10 hypotheses increases false positive rate

- With α = 0.05, expected 0.5 false positives (Type I errors)
- **No Bonferroni correction applied**

**Implication**: Some "significant" findings may be due to chance

**Recommendation**: Apply Bonferroni correction (α = 0.05/10 = 0.005) for conservative testing

### 3.2 Violated Assumptions

**Normality**: 
- Revenue and distance are **right-skewed**, not normally distributed
- t-tests and Pearson correlation assume normality
- **Mitigation**: Large sample size (n > 30,000) invokes Central Limit Theorem

**Independence**:
- Rides from same driver/customer are **not independent**
- Should use mixed-effects models or cluster by driver
- Current analysis treats all rides as independent

**Homoscedasticity**:
- Variance of revenue **not constant** across vehicle types
- ANOVA assumption violated
- **Mitigation**: Welch's ANOVA or bootstrap methods (not implemented)

---

## 4. Sampling & Selection Biases

### 4.1 Survivorship Bias

**Issue**: Analysis focuses on **completed rides only** (for revenue/rating predictions)

**Missing**:
- Cancelled rides (15-20% of bookings)
- Incomplete rides (~5%)
- Rides that were never initiated

**Impact**: 
- **Overestimates** successful ride characteristics
- **Underestimates** friction points (VTAT, cancellations)
- Recommendations may not address root causes of cancellations

### 4.2 Temporal Bias

**Issue**: Dataset may not cover all seasons or economic conditions

**Unknown**:
- Data collection period (is it 1 month? 1 year? 3 years?)
- Seasonal variations (summer vs winter, holidays)
- Economic cycles (recession vs growth)

**Impact**: Revenue and demand patterns may **not generalize** to other time periods

### 4.3 Geographic Bias

**Issue**: Unclear if data is from single city or multi-city

**If Single City**:
- Findings **do not generalize** to other cities/countries
- Optimal times, vehicle types, pricing vary by geography

**If Multi-City**:
demand patterns differ by location

**Recommendation**: Segment analysis by city if data available

---

## 5. Analytical Choices & Trade-offs

### 5.1 Feature Engineering Decisions

**Arbitrary Thresholds**:
- Peak morning: 7-10 AM (why not 6-9 or 8-11?)
- Distance categories: 5, 10, 20 km bins (culturally dependent)
- Rating categories: Low/Medium/High (loses granularity)

**Impact**: Different thresholds → different insights

### 5.2 Outlier Treatment

**Choice**: Cap outliers using IQR method (replaces values with bounds)

**Alternative**: Remove outliers entirely

**Trade-off**: 
- Capping: Retains data but **distorts distribution**
- Removing: **Loses information** but preserves true values

**Current approach**: Capping prioritizes sample size over distributional accuracy

### 5.3 Missing Value Imputation

**Choice**: Median (numeric) / Mode (categorical)

**Issue**: Imputation **reduces variance** and **introduces bias**

**Better Approaches** (not implemented):
- Multiple imputation
- ML-based imputation (k-NN, MICE)
- Treat "missing" as its own category

---

## 6. Business Logic & Domain Limitations

### 6.1 Revenue Attribution

**Assumption**: `booking_value` = gross revenue

**Reality Check**:
- Is this driver's earning or platform's gross?
- Are fees/commissions already deducted?
- Do split payments exist (partially cancelled)?

**Impact**: Revenue optimization recommendations may **not apply to driver earnings**

### 6.2 Rating Validity

**Assumptions**:
- Ratings are genuine, unbiased customer feedback
- 1-star and 5-star ratings are equally meaningful

**Concerns**:
- **Rating inflation**: Most ratings are 4-5 stars (cultural bias)
- **Response bias**: Only very satisfied or very dissatisfied riders rate
- **Gaming**: Drivers may solicit 5-star ratings

**Impact**: Rating analysis may **overvalue marginal improvements** (4.8 → 4.9)

### 6.3 Causality vs Correlation

**Critical Limitation**: All findings are **correlational, not causal**

**Examples**:
- "Longer VTAT → Lower ratings" (correlation)
  - Could be reverse: Low-rated drivers have longer VTAT (causal direction unclear)
- "Peak hours → Higher revenue" (correlation)
  - May be confounded by surge pricing, not time itself

**Implication**: **Do not interpret correlations as causal** without A/B testing

---

## 7. Scope Limitations

### 7.1 What's NOT Analyzed

- **Driver Behavior**: Driver experience, tenure, acceptance rate
- **Customer Behavior**: Repeat customers, customer lifetime value, churn
- **Competition**: Impact of other platforms (Uber, Lyft, etc.)
- **External Factors**: Weather, traffic, events, economic indicators
- **Pricing Strategy**: Surge pricing, dynamic pricing, promotions
- **Geospatial**: Route optimization, traffic patterns

### 7.2 What CAN'T Be Concluded

- **Driver Retention**: No data on driver churn
- **Customer Acquisition Cost**: No marketing data
- **Profitability**: No cost data (fuel, maintenance, driver payouts)
- **Market Share**: No competitive benchmarking data

---

## 8. Generalization & External Validity

### 8.1 Population Validity

**Question**: Do findings apply to:
- Other cities?
- Other countries?
- Other ridesharing platforms?
- Other time periods?

**Answer**: **Unknown** without external validation

### 8.2 Temporal Validity

- ML models trained on historical data → **decay over time**
- Recommendations based on past patterns → **may not hold** if market changes

**Shelf Life**: Assume findings valid for **3-6 months**, then re-validate

---

## 9. Technical Debt & Implementation Gaps

### 9.1 Not Yet Implemented (Per Flowchart)

Despite 85-100% coverage claim, **some components are simplified**:

1. **Cross-Validation**: Train-test split only (no k-fold CV)
2. **Hyperparameter Tuning**: Default Random Forest parameters (not optimized)
3. **Model Comparison**: Only Random Forest (Linear Regression, XGBoost planned)
4. **Residual Analysis**: Not performed for regression assumptions
5. **Interaction Effects**: Mentioned but not deeply analyzed
6. **Geospatial Analysis**: No mapping or route optimization

### 9.2 Code Quality

- **Test Coverage**: No unit tests (production risk)
- **Error Handling**: Minimal error handling in endpoints
- **Scalability**: In-memory data loading (won't scale to millions of rides)
- **Performance**: No caching, query optimization

---

## 10. Recommendations for Mitigating Limitations

### Immediate Actions

1. **Collect Missing Data**:
   - Ratings for cancelled rides
   - Surge pricing multipliers
   - Driver experience/history

2. **Validate Outliers**:
   - Partner with ops team to verify extreme values
   - Implement data validation at collection

3. **Address Class Imbalance**:
   - Oversample low ratings
   - Use F1 score instead of accuracy

### Medium-Term Improvements

4. **Hierarchical Modeling**:
   - Account for driver/customer clustering
   - Mixed-effects models

5. **Causal Inference**:
   - A/B test recommendations
   - Propensity score matching

6. **External Validation**:
   - Test on new data (different city, time period)
   - Compare with industry benchmarks

### Long-Term Enhancements

7. **Real-Time ML**:
   - Online learning for model updates
   - Streaming data pipelines

8. **Deep Learning**:
   - LSTM for time-series
   - Geospatial CNNs for route prediction

---

## Conclusion

This analysis provides **valuable insights** but should be interpreted with caution. Key takeaways:

✅ **Strong**: Descriptive analysis, correlation identification, hypothesis testing framework  
⚠️ **Moderate**: Revenue predictions (low R²), trade-off analysis  
❌ **Weak**: Causal claims, generalization to other markets, rating prediction for Low class  

**Use for**: Generating hypotheses, identifying areas for experimentation  
**Do NOT use for**: Production revenue forecasting, automated decision-making without human review  

**Always**: Combine with domain expertise, A/B testing, and continuous monitoring
