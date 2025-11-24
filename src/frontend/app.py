import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
import pandas as pd
from api_client import api_client
from components import metric_card, custom_css

st.set_page_config(page_title="Ridesharing Analytics", layout="wide", page_icon="🚖")

# Apply Custom CSS
custom_css()

# Header
col_header_1, col_header_2 = st.columns([1, 5])
with col_header_1:
    st.image("https://cdn-icons-png.flaticon.com/512/1584/1584808.png", width=80)
with col_header_2:
    st.title("Ridesharing Analytics Dashboard")
    st.markdown("Interactive insights into revenue, ratings, and operational metrics.")

st.markdown("---")

# Sidebar - Filters
with st.sidebar:
    st.header("🔍 Filters")
    
    # Date Range
    st.subheader("Date Range")
    start_date = st.date_input("Start Date", date(2023, 1, 1))
    end_date = st.date_input("End Date", date.today())
    
    # Vehicle Type
    st.subheader("Vehicle Type")
    vehicle_types = api_client.get_vehicle_types()
    selected_vehicles = st.multiselect("Select Vehicles", vehicle_types, default=vehicle_types)
    
    st.info("Adjust filters to update the dashboard in real-time.")

    st.markdown("---")
    st.subheader("🔴 Live Operations")
    live_mode = st.toggle("Live Monitor Mode")
    if live_mode:
        st.caption("Auto-refreshing every 5s...")
        import time
        time.sleep(5)
        st.rerun()

# Fetch Data
metrics = api_client.get_metrics(selected_vehicles, str(start_date), str(end_date))

# Live Monitor Section
if live_mode:
    st.markdown("### 📡 Live Incoming Bookings")
    recent_rides = api_client.get_recent_rides(limit=5)
    if not recent_rides.empty:
        display_cols = ['booking_id', 'vehicle_type', 'booking_status', 'booking_value', 'pickup_location']
        available_cols = [c for c in display_cols if c in recent_rides.columns]
        st.dataframe(
            recent_rides[available_cols].style.applymap(
                lambda x: 'color: red' if x == 'Cancelled' else 'color: green', subset=['booking_status']
            ),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("Waiting for live data...")
    st.markdown("---")

# Metrics Row
st.subheader("🚀 Key Performance Indicators")
m1, m2, m3, m4 = st.columns(4)
with m1:
    metric_card("Total Revenue", f"{metrics['total_revenue']:,.2f}", prefix="$")
with m2:
    metric_card("Total Rides", f"{metrics['total_rides']:,}")
with m3:
    metric_card("Avg Driver Rating", f"{metrics['avg_driver_rating']:.2f}", suffix=" ⭐")
with m4:
    metric_card("Avg Customer Rating", f"{metrics['avg_customer_rating']:.2f}", suffix=" ⭐")

st.markdown("---")

# Tabs for detailed analysis
tab_revenue, tab_ratings, tab_cancellation, tab_recommendations, tab_stats, tab_ml = st.tabs([
    "💰 Revenue Analysis", 
    "⭐ Rating Analysis", 
    "🚫 Cancellation Insights",
    "💡 Driver Recommendations",
    "📊 Statistical Tests",
    "🤖 Predictive Insights"
])

with tab_revenue:
    st.header("Revenue Insights")
    
    row1_col1, row1_col2 = st.columns(2)
    
    with row1_col1:
        st.subheader("Revenue by Vehicle Type")
        df_vehicle = api_client.get_revenue_by_vehicle(selected_vehicles, str(start_date), str(end_date))
        if not df_vehicle.empty:
            fig_vehicle = px.bar(
                df_vehicle, 
                x='vehicle_type', 
                y='total_revenue', 
                color='total_revenue',
                color_continuous_scale='Viridis',
                labels={'total_revenue': 'Revenue ($)', 'vehicle_type': 'Vehicle Type'},
                template="plotly_white"
            )
            st.plotly_chart(fig_vehicle, use_container_width=True)
        else:
            st.warning("No data available for the selected filters.")
            
    with row1_col2:
        st.subheader("Revenue Trends (Hourly)")
        df_hour = api_client.get_revenue_by_hour(selected_vehicles, str(start_date), str(end_date))
        if not df_hour.empty:
            fig_hour = px.area(
                df_hour, 
                x='hour', 
                y='avg_revenue', 
                markers=True,
                labels={'avg_revenue': 'Avg Revenue ($)', 'hour': 'Hour of Day'},
                template="plotly_white"
            )
            fig_hour.update_traces(line_color='#1f77b4')
            st.plotly_chart(fig_hour, use_container_width=True)
        else:
            st.warning("No data available.")
    
    st.markdown("---")
    
    # NEW: Distance Analysis
    row2_col1, row2_col2 = st.columns(2)
    
    with row2_col1:
        st.subheader("Distance vs Revenue Correlation")
        distance_data = api_client.get_distance_analysis(selected_vehicles, str(start_date), str(end_date))
        if distance_data.get('bins'):
            fig_distance = px.bar(
                x=distance_data['bins'],
                y=distance_data['avg_revenue'],
                labels={'x': 'Distance Range', 'y': 'Avg Revenue ($)'},
                template="plotly_white",
                color=distance_data['avg_revenue'],
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig_distance, use_container_width=True)
            st.metric("Correlation Coefficient", f"{distance_data['correlation']:.3f}", 
                     help="Positive value indicates longer distances generate more revenue")
        else:
            st.warning("No distance data available.")
    
    with row2_col2:
        st.subheader("Payment Method Revenue")
        payment_data = api_client.get_payment_insights(selected_vehicles, str(start_date), str(end_date))
        if payment_data.get('methods'):
            fig_payment = px.bar(
                x=payment_data['methods'],
                y=payment_data['avg_revenue'],
                labels={'x': 'Payment Method', 'y': 'Avg Revenue ($)'},
                template="plotly_white",
                color=payment_data['avg_revenue'],
                color_continuous_scale='Greens'
            )
            st.plotly_chart(fig_payment, use_container_width=True)
        else:
            st.warning("No payment data available.")
    
    st.markdown("---")
    
    # NEW: Top Locations
    st.subheader("Top Revenue Locations")
    location_data = api_client.get_location_insights(selected_vehicles, str(start_date), str(end_date), top_n=5)
    if location_data.get('top_pickup'):
        col_pickup, col_drop = st.columns(2)
        with col_pickup:
            st.markdown("**🚩 Top Pickup Zones**")
            pickup_df = pd.DataFrame(location_data['top_pickup'])
            st.dataframe(pickup_df[['location', 'total_revenue', 'avg_revenue']], use_container_width=True, hide_index=True)
        with col_drop:
            if location_data.get('top_drop'):
                st.markdown("**📍 Top Drop Zones**")
                drop_df = pd.DataFrame(location_data['top_drop'])
                st.dataframe(drop_df[['location', 'total_revenue', 'avg_revenue']], use_container_width=True, hide_index=True)

with tab_ratings:
    st.header("Rating Insights")
    
    row1_col1, row1_col2 = st.columns(2)
    
    with row1_col1:
        st.subheader("Rating Distribution")
        rating_dist = api_client.get_rating_distribution(selected_vehicles, str(start_date), str(end_date))
        if rating_dist.get('driver', {}).get('counts'):
            fig_rating = go.Figure()
            fig_rating.add_trace(go.Bar(
                x=rating_dist['driver']['stars'],
                y=rating_dist['driver']['counts'],
                name='Driver Ratings',
                marker_color='gold'
            ))
            fig_rating.add_trace(go.Bar(
                x=rating_dist['customer']['stars'],
                y=rating_dist['customer']['counts'],
                name='Customer Ratings',
                marker_color='lightblue'
            ))
            fig_rating.update_layout(
                barmode='group',
                title_text='Actual Rating Distribution',
                template="plotly_white",
                xaxis_title="Rating",
                yaxis_title="Count"
            )
            st.plotly_chart(fig_rating, use_container_width=True)
        else:
            st.warning("No rating data available.")
    
    with row1_col2:
        st.subheader("VTAT Impact on Ratings")
        vtat_data = api_client.get_vtat_impact(selected_vehicles, str(start_date), str(end_date))
        if vtat_data.get('vtat_bins'):
            fig_vtat = go.Figure()
            fig_vtat.add_trace(go.Scatter(
                x=vtat_data['vtat_bins'],
                y=vtat_data['avg_driver_rating'],
                mode='lines+markers',
                name='Driver Rating',
                line=dict(color='gold', width=3)
            ))
            fig_vtat.add_trace(go.Scatter(
                x=vtat_data['vtat_bins'],
                y=vtat_data['avg_customer_rating'],
                mode='lines+markers',
                name='Customer Rating',
                line=dict(color='lightblue', width=3)
            ))
            fig_vtat.update_layout(
                title_text='How Pickup Time Affects Ratings',
                template="plotly_white",
                xaxis_title="Time to Reach Pickup",
                yaxis_title="Average Rating"
            )
            st.plotly_chart(fig_vtat, use_container_width=True)
            
            col_corr1, col_corr2 = st.columns(2)
            col_corr1.metric("Driver Correlation", f"{vtat_data['correlation_driver']:.3f}",
                            help="Negative = Longer VTAT → Lower Rating")
            col_corr2.metric("Customer Correlation", f"{vtat_data['correlation_customer']:.3f}",
                            help="Negative = Longer VTAT → Lower Rating")
        else:
            st.warning("No VTAT data available.")

with tab_cancellation:
    st.header("Cancellation Insights")
    
    cancel_data = api_client.get_cancellation_metrics(selected_vehicles, str(start_date), str(end_date))
    
    if cancel_data:
        # Overview metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Cancellation Rate", f"{cancel_data.get('cancellation_rate', 0):.1f}%")
        col2.metric("Total Cancelled", f"{cancel_data.get('total_cancelled', 0):,}")
        col3.metric("By Customer", f"{cancel_data.get('by_customer', 0):,}")
        col4.metric("By Driver", f"{cancel_data.get('by_driver', 0):,}")
        
        st.markdown("---")
        
        row1_col1, row1_col2 = st.columns(2)
        
        with row1_col1:
            st.subheader("Cancellation by Hour")
            if cancel_data.get('hourly_cancellation'):
                hourly = cancel_data['hourly_cancellation']
                fig_hourly = px.line(
                    x=hourly['hours'],
                    y=hourly['rates'],
                    markers=True,
                    labels={'x': 'Hour of Day', 'y': 'Cancellation Rate (%)'},
                    template="plotly_white"
                )
                fig_hourly.update_traces(line_color='red')
                st.plotly_chart(fig_hourly, use_container_width=True)
        
        with row1_col2:
            st.subheader("Cancellation by Vehicle Type")
            if cancel_data.get('by_vehicle'):
                vehicle = cancel_data['by_vehicle']
                fig_vehicle = px.bar(
                    x=vehicle['types'],
                    y=vehicle['rates'],
                    labels={'x': 'Vehicle Type', 'y': 'Cancellation Rate (%)'},
                    template="plotly_white",
                    color=vehicle['rates'],
                    color_continuous_scale='Reds'
                )
                st.plotly_chart(fig_vehicle, use_container_width=True)
        
        st.markdown("---")
        st.metric("Estimated Revenue Loss", f"${cancel_data.get('estimated_revenue_loss', 0):,.2f}",
                 help="Potential revenue if cancelled rides were completed")

with tab_recommendations:
    st.header("💡 Actionable Insights for Drivers")
    
    recommendations = api_client.get_recommendations(selected_vehicles, str(start_date), str(end_date))
    
    if recommendations:
        for rec in recommendations:
            with st.container():
                col_icon, col_content = st.columns([1, 10])
                with col_icon:
                    st.markdown(f"# {rec['icon']}")
                with col_content:
                    st.markdown(f"**{rec['category']}**: {rec['title']}")
                    st.caption(rec['description'])
                st.markdown("---")
    else:
        st.info("No recommendations available for the selected filters.")
    
    st.markdown("### 📊 Key Takeaways")
    st.markdown("""
    Based on the data analysis, here are the main drivers of revenue and ratings:
    
    **Revenue Drivers:**
    - 🚗 Vehicle type selection
    - 📏 Ride distance (longer trips = higher revenue)
    - 🕐 Time of day (peak hours vary)
    - 📍 Pickup location (some zones are more profitable)
    
    **Rating Optimizers:**
    - ⏱️ **VTAT (Time to reach pickup)** - Keep it low!
    - 🎯 Accept rides closer to your current location
    - 💳 Payment method can influence customer satisfaction
    - 🚫 Avoid high-cancellation scenarios
    """)

with tab_stats:
    st.header("📊 Statistical Hypothesis Testing")
    st.markdown("*Rigorous statistical validation of key business questions*")
    
    stats_data = api_client.get_statistical_tests(selected_vehicles, str(start_date), str(end_date))
    
    # Overview metrics
    col1, col2 = st.columns(2)
    col1.metric("Total Tests", stats_data.get('total_tests', 0))
    col2.metric("Significant Results (p < 0.05)", stats_data.get('significant_tests', 0))
    
    st.markdown("---")
    
    # Revenue Hypotheses
    st.subheader("💰 Revenue Hypotheses")
    revenue_hyp = stats_data.get('revenue_hypotheses', [])
    
    if revenue_hyp:
        for test in revenue_hyp:
            significance_badge = "✅ Significant" if test['significant'] else "❌ Not Significant"
            with st.expander(f"{test['hypothesis']} - {significance_badge}"):
                col1, col2, col3 = st.columns(3)
                col1.metric("Test Method", test['test'])
                col2.metric("P-Value", f"{test['p_value']:.4f}")
                col3.metric("Test Statistic", f"{test['test_statistic']:.3f}")
                
                st.info(test['conclusion'])
                
                if test['p_value'] < 0.05:
                    st.success("**Result**: Statistically significant at α = 0.05 level")
                else:
                    st.warning("**Result**: Not statistically significant")
    else:
        st.info("No revenue hypothesis tests available.")
    
    st.markdown("---")
    
    # Rating Hypotheses
    st.subheader("⭐ Rating Hypotheses")
    rating_hyp = stats_data.get('rating_hypotheses', [])
    
    if rating_hyp:
        for test in rating_hyp:
            significance_badge = "✅ Significant" if test['significant'] else "❌ Not Significant"
            with st.expander(f"{test['hypothesis']} - {significance_badge}"):
                col1, col2, col3 = st.columns(3)
                col1.metric("Test Method", test['test'])
                col2.metric("P-Value", f"{test['p_value']:.4f}")
                col3.metric("Test Statistic", f"{test['test_statistic']:.3f}")
                
                st.info(test['conclusion'])
                
                if test['p_value'] < 0.05:
                    st.success("**Result**: Statistically significant at α = 0.05 level")
                else:
                    st.warning("**Result**: Not statistically significant")
    else:
        st.info("No rating hypothesis tests available.")

with tab_ml:
    st.header("🤖 Predictive Insights & Machine Learning")
    st.markdown("*ML-powered feature importance and revenue/rating prediction models*")
    
    # Model Performance
    st.subheader("Model Performance Metrics")
    perf = api_client.get_model_performance()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**💰 Revenue Prediction Model**")
        revenue_model = perf.get('revenue_model', {})
        if revenue_model:
            st.metric("Test R² Score", f"{revenue_model.get('test_r2', 0):.3f}",
                     help="Proportion of variance explained (higher is better, max 1.0)")
            st.metric("Test RMSE", f"${revenue_model.get('test_rmse', 0):.2f}",
                     help="Root Mean Squared Error (lower is better)")
            st.metric("Test MAE", f"${revenue_model.get('test_mae', 0):.2f}",
                     help="Mean Absolute Error (lower is better)")
            st.caption(f"Trained on {revenue_model.get('train_samples', 0):,} samples, tested on {revenue_model.get('test_samples', 0):,} samples")
        else:
            st.warning("Model not trained yet.")
    
    with col2:
        st.markdown("**⭐ Rating Prediction Model**")
        rating_model = perf.get('rating_model', {})
        if rating_model:
            st.metric("Test Accuracy", f"{rating_model.get('test_accuracy', 0):.3f}",
                     help="Proportion of correct predictions (higher is better, max 1.0)")
            st.caption(f"Trained on {rating_model.get('train_samples', 0):,} samples, tested on {rating_model.get('test_samples', 0):,} samples")
        else:
            st.warning("Model not trained yet.")
    
    st.markdown("---")
    
    # Feature Importance
    st.subheader("What Drives Revenue? (ML Feature Importance)")
    feat_imp = api_client.get_feature_importance()
    
    revenue_drivers = feat_imp.get('revenue_drivers', [])
    if revenue_drivers:
        # Create DataFrame for plotting
        df_importance = pd.DataFrame(revenue_drivers)
        
        fig = px.bar(
            df_importance,
            x='importance',
            y='feature',
            orientation='h',
            labels={'importance': 'Importance Score', 'feature': 'Feature'},
            title='Top 10 Revenue Drivers (Random Forest)',
            color='importance',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
        
        st.caption("**Interpretation**: Higher importance = stronger influence on revenue predictions")
    else:
        st.info("Feature importance data not available.")
    
    st.markdown("---")
    
    # Rating Drivers
    st.subheader("What Drives Ratings? (ML Feature Importance)")
    rating_drivers = feat_imp.get('rating_drivers', [])
    if rating_drivers:
        df_importance = pd.DataFrame(rating_drivers)
        
        fig = px.bar(
            df_importance,
            x='importance',
            y='feature',
            orientation='h',
            labels={'importance': 'Importance Score', 'feature': 'Feature'},
            title='Top 10 Rating Drivers (Random Forest)',
            color='importance',
            color_continuous_scale='Blues'
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
        
        st.caption("**Interpretation**: Higher importance = stronger influence on rating predictions")
    else:
        st.info("Feature importance data not available.")
