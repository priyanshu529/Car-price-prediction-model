import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time

# Page config
st.set_page_config(
    page_title="Ford Car Price Predictor",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4, #45B7D1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .price-display {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #2E8B57;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem;
    }
    .stSelectbox > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Load models with fancy loading animation
@st.cache_resource
def load_models():
    with st.spinner('🔧 Loading AI models...'):
        try:
            model = joblib.load("model_car.pkl")
            scaler = joblib.load("scaler_car.pkl")
            columns = joblib.load("columns_car.pkl")
            time.sleep(1)  # Dramatic pause
            return model, scaler, columns
        except:
            st.error("🚨 Model files not found!")
            st.stop()

model, scaler, columns = load_models()
st.success("✅ AI Models loaded successfully!")

# Header
st.markdown('<h1 class="main-header">🚗 Ford Car Price Predictor AI</h1>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar for inputs
with st.sidebar:
    st.markdown("## 🎛️ Vehicle Configuration")
    
    # Car basics
    st.markdown("### 📅 Basic Info")
    year = st.slider("Year", min_value=1990, max_value=2025, value=2018, 
                    help="Manufacturing year of the vehicle")
    
    car_age = 2025 - year
    if car_age < 3:
        age_emoji = "🆕"
    elif car_age < 7:
        age_emoji = "👌"
    else:
        age_emoji = "👴"
    
    st.info(f"{age_emoji} Car age: {car_age} years")
    
    # Performance metrics
    st.markdown("### ⚡ Performance")
    col1, col2 = st.columns(2)
    with col1:
        mileage = st.number_input("Mileage", min_value=0, max_value=300000, 
                                value=30000, step=1000, help="Total miles driven")
    with col2:
        mpg = st.number_input("MPG", min_value=0.0, max_value=150.0, 
                            value=50.0, help="Miles per gallon efficiency")
    
    # Financial
    st.markdown("### 💰 Financial")
    tax = st.number_input("Annual Tax (£)", min_value=0, max_value=1000, 
                         value=150, help="Annual road tax")
    
    # Engine
    st.markdown("### 🔧 Engine")
    engineSize = st.slider("Engine Size (L)", min_value=0.5, max_value=6.0, 
                          value=1.6, step=0.1, help="Engine displacement in liters")
    
    # Model selection with search
    st.markdown("### 🚙 Vehicle Type")
    models = ['B-MAX','C-MAX','EcoSport','Edge','Escort','Fiesta','Focus','Fusion','Galaxy',
              'Grand C-MAX','Grand Tourneo Connect','KA','Ka+','Kuga','Mondeo','Mustang',
              'Puma','Ranger','S-MAX','Streetka','Tourneo Connect','Tourneo Custom','Transit Tourneo']
    
    selected_model = st.selectbox("🏷️ Model", models, index=5, help="Ford model")
    
    col1, col2 = st.columns(2)
    with col1:
        transmissions = ['Automatic','Manual','Semi-Auto']
        selected_trans = st.selectbox("⚙️ Transmission", transmissions)
    
    with col2:
        fuels = ['Diesel','Electric','Hybrid','Other','Petrol']
        selected_fuel = st.selectbox("⛽ Fuel Type", fuels)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("## 📊 Vehicle Summary")
    
    # Create a summary card
    summary_col1, summary_col2, summary_col3 = st.columns(3)
    
    with summary_col1:
        st.metric("🗓️ Age", f"{car_age} years", delta=None)
        st.metric("🛣️ Mileage", f"{mileage:,} mi", 
                 delta=f"{'Low' if mileage < 50000 else 'High' if mileage > 100000 else 'Average'}")
    
    with summary_col2:
        st.metric("⚡ Efficiency", f"{mpg} MPG", 
                 delta=f"{'Excellent' if mpg > 50 else 'Good' if mpg > 30 else 'Poor'}")
        st.metric("🔧 Engine", f"{engineSize}L", delta=None)
    
    with summary_col3:
        st.metric("💰 Tax", f"£{tax}", delta=None)
        st.metric("⚙️ Type", f"{selected_trans}", delta=None)
    
    # Efficiency gauge
    st.markdown("### ⚡ Fuel Efficiency Gauge")
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = mpg,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Miles Per Gallon"},
        delta = {'reference': 40},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkgreen"},
            'steps': [
                {'range': [0, 25], 'color': "lightgray"},
                {'range': [25, 50], 'color': "yellow"},
                {'range': [50, 100], 'color': "green"}],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 70}}))
    
    fig_gauge.update_layout(height=300)
    st.plotly_chart(fig_gauge, use_container_width=True)

with col2:
    st.markdown("## 🎯 Quick Stats")
    
    # Environmental impact
    if selected_fuel == 'Electric':
        env_score = "🌱 Excellent"
    elif selected_fuel == 'Hybrid':
        env_score = "♻️ Good"
    elif mpg > 50:
        env_score = "🌿 Good"
    else:
        env_score = "🏭 Average"
    
    st.success(f"Environmental Impact: {env_score}")
    
    # Value indicators
    if car_age < 3 and mileage < 30000:
        value_indicator = "💎 Premium"
    elif car_age < 7 and mileage < 80000:
        value_indicator = "⭐ Good Value"
    else:
        value_indicator = "💰 Budget Friendly"
    
    st.info(f"Market Position: {value_indicator}")
    
    # Popular choice indicator
    popular_models = ['Focus', 'Fiesta', 'Kuga', 'Mondeo']
    if selected_model in popular_models:
        st.success("🏆 Popular Choice")
    else:
        st.info("🔍 Unique Selection")

# Prediction section
st.markdown("---")
st.markdown("## 🔮 AI Price Prediction")

predict_col1, predict_col2, predict_col3 = st.columns([1, 2, 1])

with predict_col2:
    if st.button("🚀 Predict My Car's Value", type="primary", use_container_width=True):
        with st.spinner('🤖 AI is analyzing your vehicle...'):
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
            
            try:
                # Initialize all columns with 0
                raw_input = {col: 0 for col in columns}
                
                # Set numeric values
                raw_input['year'] = year
                raw_input['mileage'] = mileage
                raw_input['tax'] = tax
                raw_input['mpg'] = mpg
                raw_input['engineSize'] = engineSize
                
                # Set categorical features
                if selected_model == "Focus" and 'model_Focus' in columns:
                    raw_input['model_Focus'] = 1
                elif f'model_ {selected_model}' in columns:
                    raw_input[f'model_ {selected_model}'] = 1
                    
                trans_col = f'transmission_{selected_trans}'
                if trans_col in columns:
                    raw_input[trans_col] = 1
                    
                fuel_col = f'fuelType_{selected_fuel}'
                if fuel_col in columns:
                    raw_input[fuel_col] = 1
                
                # Create DataFrame and scale
                input_df = pd.DataFrame([raw_input])
                num_cols = ['year', 'mileage', 'tax', 'mpg', 'engineSize']
                input_df[num_cols] = scaler.transform(input_df[num_cols])
                
                # Predict
                prediction = model.predict(input_df)[0]
                
                # Clear progress bar
                progress_bar.empty()
                
              
                
                # Price display
                st.markdown(f"""
                <div class="price-display">
                    💰 Estimated Value: £{prediction:,.0f}
                </div>
                """, unsafe_allow_html=True)
                
                # Price analysis
                if prediction > 30000:
                    price_category = "🏆 Premium Vehicle"
                    price_color = "success"
                elif prediction > 15000:
                    price_category = "⭐ Mid-Range Vehicle"
                    price_color = "info"
                else:
                    price_category = "💰 Budget-Friendly Vehicle"
                    price_color = "warning"
                
                if price_color == "success":
                    st.success(f"Category: {price_category}")
                elif price_color == "info":
                    st.info(f"Category: {price_category}")
                else:
                    st.warning(f"Category: {price_category}")
                
                # Market comparison
                st.markdown("### 📈 Market Analysis")
                avg_price = 18000  # Approximate average
                price_diff = prediction - avg_price
                
                if price_diff > 5000:
                    st.success(f"📈 Above market average by £{price_diff:,.0f}")
                elif price_diff > -5000:
                    st.info("📊 Around market average")
                else:
                    st.warning(f"📉 Below market average by £{abs(price_diff):,.0f}")
                
                # Create price comparison chart
                categories = ['Budget', 'Your Car', 'Premium']
                prices = [8000, prediction, 35000]
                colors = ['#ff6b6b', '#4ecdc4', '#ffd93d']
                
                fig = px.bar(x=categories, y=prices, color=categories,
                           title="Price Comparison", color_discrete_sequence=colors)
                fig.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                # Confidence and tips
                st.markdown("### 💡 Pricing Insights")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.info("🎯 **Factors Boosting Value:**")
                    factors = []
                    if car_age < 5:
                        factors.append("• Recent model year")
                    if mileage < 50000:
                        factors.append("• Low mileage")
                    if mpg > 40:
                        factors.append("• Fuel efficient")
                    if selected_fuel in ['Electric', 'Hybrid']:
                        factors.append("• Eco-friendly")
                    
                    if factors:
                        for factor in factors:
                            st.write(factor)
                    else:
                        st.write("• Solid, reliable vehicle")
                
                with col2:
                    st.warning("📝 **Consider:**")
                    considerations = []
                    if car_age > 10:
                        considerations.append("• Vehicle age affects value")
                    if mileage > 100000:
                        considerations.append("• High mileage impacts price")
                    if tax > 300:
                        considerations.append("• Higher tax bracket")
                    
                    if considerations:
                        for consideration in considerations:
                            st.write(consideration)
                    else:
                        st.write("• Great overall condition!")
                
            except Exception as e:
                st.error(f"❌ Prediction Error: {e}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>🤖 Powered by Advanced Machine Learning | 📊 Based on Real Market Data</p>
    <p>⚠️ Estimates are for guidance only. Actual prices may vary based on condition, location, and market factors.</p>
</div>

""", unsafe_allow_html=True)
