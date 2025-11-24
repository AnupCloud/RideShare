from scipy import stats
import pandas as pd
import numpy as np

# Bonferroni correction for multiple testing
TOTAL_TESTS = 10  # Total number of hypotheses tested
BONFERRONI_ALPHA = 0.05 / TOTAL_TESTS  # Adjusted significance level (0.005)

def test_revenue_hypotheses(df: pd.DataFrame):
    """
    Test 5 revenue-related hypotheses
    Returns: List of test results with p-values, test statistics, conclusions
    """
    results = []
    
    # H1: Premium vehicles generate higher revenue
    premium_vehicles = ['Premier Sedan', 'AutoXL']
    premium_data = df[df['vehicle_type'].isin(premium_vehicles)]['booking_value'].dropna()
    non_premium_data = df[~df['vehicle_type'].isin(premium_vehicles)]['booking_value'].dropna()
    
    if len(premium_data) > 1 and len(non_premium_data) > 1:
        t_stat, p_value = stats.ttest_ind(premium_data, non_premium_data)
        results.append({
            'hypothesis': 'H1: Premium vehicles generate higher revenue',
            'test': 'Independent t-test',
            'test_statistic': float(t_stat),
            'p_value': float(p_value),
            'significant': p_value < 0.05,
            'bonferroni_significant': p_value < BONFERRONI_ALPHA,
            'bonferroni_alpha': BONFERRONI_ALPHA,
            'conclusion': f"{'Reject' if p_value < 0.05 else 'Fail to reject'} null hypothesis. Premium avg: ${premium_data.mean():.2f}, Non-premium avg: ${non_premium_data.mean():.2f}"
        })
    
    # H2: Peak hours yield higher fares
    peak = df[(df['is_peak_morning'] == True) | (df['is_peak_evening'] == True)]['booking_value'].dropna()
    non_peak = df[(df['is_peak_morning'] == False) & (df['is_peak_evening'] == False)]['booking_value'].dropna()
    
    if len(peak) > 1 and len(non_peak) > 1:
        t_stat, p_value = stats.ttest_ind(peak, non_peak)
        results.append({
            'hypothesis': 'H2: Peak hours yield higher fares',
            'test': 'Independent t-test',
            'test_statistic': float(t_stat),
            'p_value': float(p_value),
            'significant': p_value < 0.05,
            'bonferroni_significant': p_value < BONFERRONI_ALPHA,
            'bonferroni_alpha': BONFERRONI_ALPHA,
            'conclusion': f"{'Reject' if p_value < 0.05 else 'Fail to reject'} null hypothesis. Peak avg: ${peak.mean():.2f}, Non-peak avg: ${non_peak.mean():.2f}"
        })
    
    # H3: Longer distances have higher revenue
    valid_data = df[['ride_distance', 'booking_value']].dropna()
    if len(valid_data) > 2:
        corr, p_value = stats.pearsonr(valid_data['ride_distance'], valid_data['booking_value'])
        results.append({
            'hypothesis': 'H3: Longer distances have higher revenue',
            'test': 'Pearson Correlation',
            'test_statistic': float(corr),
            'p_value': float(p_value),
            'significant': p_value < 0.05,
            'bonferroni_significant': p_value < BONFERRONI_ALPHA,
            'bonferroni_alpha': BONFERRONI_ALPHA,
            'conclusion': f"Correlation: {corr:.3f}, {'Significant positive' if (p_value < 0.05 and corr > 0) else 'Not significant'} relationship"
        })
    
    # H4: Cash vs Digital payment affects revenue
    cash = df[df['payment_method'] == 'Cash']['booking_value'].dropna()
    digital = df[df['payment_method'].isin(['UPI', 'Credit Card', 'Digital Wallet'])]['booking_value'].dropna()
    
    if len(cash) > 1 and len(digital) > 1:
        t_stat, p_value = stats.ttest_ind(cash, digital)
        results.append({
            'hypothesis': 'H4: Cash vs Digital payment affects revenue',
            'test': 'Independent t-test',
            'test_statistic': float(t_stat),
            'p_value': float(p_value),
            'significant': p_value < 0.05,
            'bonferroni_significant': p_value < BONFERRONI_ALPHA,
            'bonferroni_alpha': BONFERRONI_ALPHA,
            'conclusion': f"{'Reject' if p_value < 0.05 else 'Fail to reject'} null hypothesis. Cash avg: ${cash.mean():.2f}, Digital avg: ${digital.mean():.2f}"
        })
    
    # H5: VTAT negatively affects revenue
    valid_data = df[['avg_vtat', 'booking_value']].dropna()
    if len(valid_data) > 2:
        corr, p_value = stats.pearsonr(valid_data['avg_vtat'], valid_data['booking_value'])
        results.append({
            'hypothesis': 'H5: VTAT negatively affects revenue',
            'test': 'Pearson Correlation',
            'test_statistic': float(t_stat),
            'p_value': float(p_value),
            'significant': p_value < 0.05 and corr < 0,
            'bonferroni_significant': p_value < BONFERRONI_ALPHA and corr < 0,
            'bonferroni_alpha': BONFERRONI_ALPHA,
            'conclusion': f"Correlation: {corr:.3f}, {'Negative' if corr < 0 else 'Positive'} relationship, {'Significant' if p_value < 0.05 else 'Not significant'}"
        })
    
    return results

def test_rating_hypotheses(df: pd.DataFrame):
    """Test 5 rating-related hypotheses"""
    results = []
    
    # H6: Higher VTAT reduces driver rating
    valid_data = df[['avg_vtat', 'driver_ratings']].dropna()
    if len(valid_data) > 2:
        corr, p_value = stats.pearsonr(valid_data['avg_vtat'], valid_data['driver_ratings'])
        results.append({
            'hypothesis': 'H6: Higher VTAT reduces driver rating',
            'test': 'Pearson Correlation',
            'test_statistic': float(corr),
            'p_value': float(p_value),
            'significant': p_value < 0.05 and corr < 0,
            'bonferroni_significant': p_value < BONFERRONI_ALPHA and corr < 0,
            'bonferroni_alpha': BONFERRONI_ALPHA,
            'conclusion': f"Correlation: {corr:.3f}, {'Confirmed' if (p_value < 0.05 and corr < 0) else 'Not confirmed'} - {'Negative' if corr < 0 else 'Positive'} relationship"
        })
    
    # H7: Cancellations hurt ratings
    completed = df[df['is_completed'] == True]['driver_ratings'].dropna()
    cancelled = df[df['is_cancelled'] == True]['driver_ratings'].dropna()
    
    if len(completed) > 1 and len(cancelled) > 1:
        t_stat, p_value = stats.ttest_ind(completed, cancelled)
        results.append({
            'hypothesis': 'H7: Cancellations hurt driver ratings',
            'test': 'Independent t-test',
            'test_statistic': float(t_stat),
            'p_value': float(p_value),
            'significant': p_value < 0.05,
            'conclusion': f"{'Confirmed' if p_value < 0.05 else 'Not confirmed'}. Completed avg: {completed.mean():.2f}, Cancelled avg: {cancelled.mean():.2f}"
        })
    
    # H8: Payment method affects ratings (ANOVA)
    groups = [group['driver_ratings'].dropna() for name, group in df.groupby('payment_method') if len(group['driver_ratings'].dropna()) > 0]
    if len(groups) > 1:
        f_stat, p_value = stats.f_oneway(*groups)
        results.append({
            'hypothesis': 'H8: Payment method affects driver ratings',
            'test': 'One-way ANOVA',
            'test_statistic': float(f_stat),
            'p_value': float(p_value),
            'significant': p_value < 0.05,
            'conclusion': f"{'Significant' if p_value < 0.05 else 'No significant'} effect of payment method on ratings"
        })
    
    # H9: Vehicle type affects ratings (ANOVA)
    groups = [group['driver_ratings'].dropna() for name, group in df.groupby('vehicle_type') if len(group['driver_ratings'].dropna()) > 0]
    if len(groups) > 1:
        f_stat, p_value = stats.f_oneway(*groups)
        results.append({
            'hypothesis': 'H9: Vehicle type affects driver ratings',
            'test': 'One-way ANOVA',
            'test_statistic': float(f_stat),
            'p_value': float(p_value),
            'significant': p_value < 0.05,
            'conclusion': f"{'Significant' if p_value < 0.05 else 'No significant'} effect of vehicle type on ratings"
        })
    
    # H10: Trip duration affects customer satisfaction
    valid_data = df[['avg_ctat', 'customer_rating']].dropna()
    if len(valid_data) > 2:
        corr, p_value = stats.pearsonr(valid_data['avg_ctat'], valid_data['customer_rating'])
        results.append({
            'hypothesis': 'H10: Trip duration affects customer satisfaction',
            'test': 'Pearson Correlation',
            'test_statistic': float(corr),
            'p_value': float(p_value),
            'significant': p_value < 0.05,
            'conclusion': f"Correlation: {corr:.3f}, {'Significant' if p_value < 0.05 else 'Not significant'} relationship"
        })
    
    return results
