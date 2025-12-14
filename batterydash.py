import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from plotly.subplots import make_subplots

# Page configuration
st.set_page_config(
    page_title="Battery Analytics Dashboard",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Main background */
    .main, .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%) !important;
    }
    
    /* Block container background */
    .block-container {
        background: transparent !important;
    }
    
    /* Metrics styling */
    .stMetric {
        background-color: rgba(30, 41, 59, 0.8) !important;
        padding: 15px !important;
        border-radius: 10px !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(148, 163, 184, 0.3) !important;
    }
    
    /* Metric labels and values */
    .stMetric label {
        color: #94a3b8 !important;
        font-size: 14px !important;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 24px !important;
        font-weight: 600 !important;
    }
    
    .stMetric [data-testid="stMetricDelta"] {
        color: #fbbf24 !important;
    }
    
    /* All headings white */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }
    
    /* All text white */
    .stMarkdown, .stMarkdown p, .stMarkdown span, .stMarkdown div {
        color: #ffffff !important;
    }
    
    /* Labels white */
    label, .stSelectbox label, .stSlider label, .stRadio label {
        color: #ffffff !important;
    }
    
    /* Info/success/warning boxes */
    .stAlert {
        color: #000000 !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    /* Selectbox text visible */
    .stSelectbox > div > div {
        background-color: rgba(30, 41, 59, 0.9) !important;
        color: #ffffff !important;
    }
    
    .stSelectbox option {
        background-color: #1e293b !important;
        color: #ffffff !important;
    }
    
    /* Dropdown menu items */
    [data-baseweb="select"] > div {
        background-color: #1e293b !important;
        color: #ffffff !important;
    }
    
    [role="option"] {
        background-color: #1e293b !important;
        color: #ffffff !important;
    }
    
    [role="option"]:hover {
        background-color: #334155 !important;
    }
</style>
""", unsafe_allow_html=True)

class BatteryAPI:
    """Client for accessing Battery Cycle Data API"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    @st.cache_data(ttl=300)
    def get_summary(_self):
        """Get summary of all accessible batteries"""
        url = f"{_self.base_url}/api/snapshots/summary"
        try:
            response = _self.session.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Error fetching summary: {e}")
            return {}
    
    @st.cache_data(ttl=300)
    def get_snapshots(_self, imei: str, limit: int = 1000):
        """Get cycle snapshots for a specific battery"""
        url = f"{_self.base_url}/api/snapshots"
        params = {'imei': imei, 'limit': limit, 'offset': 0}
        try:
            response = _self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data if isinstance(data, list) else data.get('snapshots', data.get('data', []))
        except Exception as e:
            st.error(f"Error fetching snapshots: {e}")
            return []

def format_datetime(dt_str):
    """Format datetime string for display"""
    if dt_str and dt_str != 'N/A':
        try:
            dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M')
        except:
            return dt_str
    return 'N/A'

def main():
    BASE_URL = "https://zenfinity-intern-api-104290304048.europe-west1.run.app"
    AUTHORIZED_IMEIS = ["865044073967657", "865044073949366"]
    
    # Initialize API
    api = BatteryAPI(BASE_URL)
    
    # Sidebar
    with st.sidebar:
        # Battery Icon SVG
        st.markdown("""
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #10b981 0%, #059669 100%); border-radius: 15px; margin-bottom: 20px;">
            <svg width="150" height="80" viewBox="0 0 150 80" xmlns="http://www.w3.org/2000/svg">
                <!-- Battery Body -->
                <rect x="10" y="20" width="120" height="60" rx="8" fill="#ffffff" stroke="#0f172a" stroke-width="3"/>
                <!-- Battery Terminal -->
                <rect x="130" y="35" width="15" height="30" rx="3" fill="#ffffff" stroke="#0f172a" stroke-width="3"/>
                <!-- Battery Fill (Green) -->
                <rect x="15" y="25" width="90" height="50" rx="5" fill="#10b981"/>
                <!-- Lightning Bolt -->
                <path d="M 70 35 L 60 50 L 68 50 L 58 65 L 68 52 L 60 52 Z" fill="#fbbf24" stroke="#f59e0b" stroke-width="1.5"/>
            </svg>
            <h2 style="color: white; margin-top: 10px; font-size: 24px;">🔋 Battery Monitor</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.title("🔋 Battery Analytics")
        
        selected_imei = st.selectbox("Select Battery IMEI", AUTHORIZED_IMEIS)
        
        st.markdown("---")
        st.markdown("### 📊 Dashboard Features")
        st.markdown("""
        - Real-time cycle monitoring
        - Temperature analysis (4 rates)
        - Health tracking (SOC/SOH)
        - Charging insights
        - Long-term trends
        - Alerts & safety
        """)
    
    # Main title
    st.title("⚡ Battery Cycle Analytics Dashboard")
    st.markdown("Real-time monitoring and analysis of battery performance")
    
    # Load data
    with st.spinner("Loading battery data..."):
        snapshots = api.get_snapshots(selected_imei)
    
    if not snapshots:
        st.error("No data available for this IMEI")
        return
    
    st.success(f"✅ Loaded {len(snapshots)} cycles")
    
    # 1. CYCLE NAVIGATION
    st.markdown("---")
    st.markdown("## 🔄 Cycle Navigation")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        cycle_idx = st.slider("Select Cycle", 0, len(snapshots) - 1, len(snapshots) - 1)
    with col2:
        cycle_numbers = [s.get('cycle_number', i) for i, s in enumerate(snapshots)]
        selected = st.selectbox("Quick Jump", cycle_numbers, index=len(cycle_numbers) - 1)
        if selected in cycle_numbers:
            cycle_idx = cycle_numbers.index(selected)
    
    snapshot = snapshots[cycle_idx]
    
    # 2. CYCLE STATISTICS
    st.markdown("---")
    st.markdown("## 📈 Cycle Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Cycle Number", snapshot.get('cycle_number', 'N/A'))
    with col2:
        st.metric("Duration (hrs)", f"{snapshot.get('cycle_duration_hours', 0):.2f}")
    with col3:
        st.metric("Start Time", format_datetime(snapshot.get('cycle_start_time')))
    with col4:
        st.metric("End Time", format_datetime(snapshot.get('cycle_end_time')))
    
    # 3. PERFORMANCE METRICS
    st.markdown("---")
    st.markdown("## 🚗 Performance Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Distance (km)", f"{snapshot.get('total_distance', 0):.2f}")
    with col2:
        st.metric("Avg Speed (km/h)", f"{snapshot.get('average_speed', 0):.1f}")
    with col3:
        st.metric("Max Speed (km/h)", f"{snapshot.get('max_speed', 0):.0f}")
    with col4:
        st.metric("Data Points", f"{snapshot.get('data_points_count', 0):,}")
    
    if snapshot.get('total_distance', 0) == 0:
        st.info("ℹ️ GPS data may have gaps - zero distance recorded for this cycle")
    
    # 4. TEMPERATURE DISTRIBUTION
    st.markdown("---")
    st.markdown("## 🌡️ Temperature Distribution")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        temp_range = st.radio(
            "Sampling Rate",
            ['5deg', '10deg', '15deg', '20deg'],
            format_func=lambda x: f"±{x.replace('deg', '°C')}",
            horizontal=True
        )
    with col2:
        st.metric("Avg Temp", f"{snapshot.get('average_temperature', 0):.1f}°C")
    
    dist_key = f'temperature_dist_{temp_range}'
    temp_dist = snapshot.get(dist_key, {})
    
    if temp_dist and any(v > 0 for v in temp_dist.values()):
        df_temp = pd.DataFrame(list(temp_dist.items()), columns=['Range', 'Minutes'])
        df_temp['Minutes'] = pd.to_numeric(df_temp['Minutes'])
        df_temp = df_temp[df_temp['Minutes'] > 0]
        
        fig = px.bar(df_temp, x='Range', y='Minutes',
                     title='Time in Temperature Ranges',
                     color='Minutes', color_continuous_scale='RdYlBu_r')
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                         font=dict(color='white'), height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No temperature distribution data")
    
    # 5. BATTERY HEALTH
    st.markdown("---")
    st.markdown("## 🔋 Battery Health (SOC & SOH)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### State of Charge (SOC)")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Avg SOC", f"{snapshot.get('average_soc', 0):.1f}%")
        with c2:
            st.metric("Min SOC", f"{snapshot.get('min_soc', 0):.1f}%")
        with c3:
            st.metric("Max SOC", f"{snapshot.get('max_soc', 0):.1f}%")
        
        fig_soc = go.Figure(go.Indicator(
            mode="gauge+number",
            value=snapshot.get('average_soc', 0),
            title={'text': "Avg SOC", 'font': {'color': 'white'}},
            gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "lightgreen"}}
        ))
        fig_soc.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': 'white'}, height=250)
        st.plotly_chart(fig_soc, use_container_width=True)
    
    with col2:
        st.markdown("### State of Health (SOH)")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Avg SOH", f"{snapshot.get('average_soh', 100):.2f}%")
        with c2:
            soh_drop = snapshot.get('soh_drop', 0)
            st.metric("SOH Drop", f"{soh_drop:.3f}%")
        with c3:
            st.metric("Min SOH", f"{snapshot.get('min_soh', 100):.2f}%")
        
        fig_soh = go.Figure(go.Indicator(
            mode="gauge+number",
            value=snapshot.get('average_soh', 100),
            title={'text': "Avg SOH", 'font': {'color': 'white'}},
            gauge={'axis': {'range': [90, 100]}, 'bar': {'color': "cyan"}}
        ))
        fig_soh.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': 'white'}, height=250)
        st.plotly_chart(fig_soh, use_container_width=True)
    
    # Voltage/Current
    st.markdown("### ⚡ Electrical Parameters")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Voltage Avg", f"{snapshot.get('voltage_avg', 0):.2f} V")
    with col2:
        st.metric("Voltage Range", f"{snapshot.get('voltage_min', 0):.1f} - {snapshot.get('voltage_max', 0):.1f} V")
    with col3:
        st.metric("Current Avg", f"{snapshot.get('current_avg', 0):.2f} A")
    
    # 6. ALERTS & SAFETY
    st.markdown("---")
    st.markdown("## 🚨 Alerts & Safety")
    
    col1, col2 = st.columns(2)
    alert_details = snapshot.get('alert_details', {})
    
    with col1:
        st.markdown("### Warnings")
        warnings = alert_details.get('warnings', [])
        if warnings:
            for w in warnings:
                st.warning(w)
        else:
            st.success("No warnings")
    
    with col2:
        st.markdown("### Protections")
        protections = alert_details.get('protections', [])
        if protections:
            for p in protections:
                st.error(p)
        else:
            st.success("No protections triggered")
    
    # 7. CHARGING INSIGHTS
    st.markdown("---")
    st.markdown("## ⚡ Charging Insights")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Charge Events", snapshot.get('charging_instances_count', 0))
    with col2:
        st.metric("Avg Start SOC", f"{snapshot.get('average_charge_start_soc', 0):.1f}%")
    with col3:
        charging = snapshot.get('charging_instances_count', 0)
        pattern = "Deep Discharge" if charging > 0 and snapshot.get('average_charge_start_soc', 0) < 30 else "Normal"
        st.metric("Pattern", pattern)
    
    # 9. LONG-TERM TRENDS
    st.markdown("---")
    st.markdown("## 📊 Long-term Trends & Advanced Analysis")
    
    df_trends = pd.DataFrame(snapshots)
    
    if not df_trends.empty and len(df_trends) > 1:
        
        st.markdown("---")
        
        # Energy Efficiency Analysis
        st.markdown("### ⚡ Energy Efficiency & Performance Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Distance vs Energy Consumption Pattern**")
            
            # Calculate energy efficiency proxy (distance per SOC used)
            soc_consumed = df_trends['max_soc'] - df_trends['min_soc']
            # Avoid division by zero
            efficiency = df_trends['total_distance'] / soc_consumed.replace(0, 1)
            efficiency = efficiency.replace([float('inf'), -float('inf')], 0)
            
            fig_efficiency = go.Figure()
            
            # Scatter plot with size representing cycle duration
            fig_efficiency.add_trace(go.Scatter(
                x=soc_consumed,
                y=df_trends['total_distance'],
                mode='markers',
                marker=dict(
                    size=df_trends['cycle_duration_hours'].clip(upper=50) / 2,  # Scale for visibility
                    color=df_trends['average_temperature'],
                    colorscale='RdYlBu_r',
                    showscale=True,
                    colorbar=dict(title="Temp (°C)", titlefont=dict(color='white'), tickfont=dict(color='white')),
                    line=dict(width=1, color='white')
                ),
                text=[f"Cycle {c}" for c in df_trends['cycle_number']],
                hovertemplate='<b>Cycle %{text}</b><br>SOC Used: %{x:.1f}%<br>Distance: %{y:.2f} km<extra></extra>'
            ))
            
            fig_efficiency.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', size=11),
                xaxis_title='SOC Consumed (%)',
                yaxis_title='Distance Traveled (km)',
                height=400
            )
            
            st.plotly_chart(fig_efficiency, use_container_width=True)
            
            st.caption("💡 Bubble size = cycle duration, Color = temperature")
        
        with col2:
            st.markdown("**Voltage Stability Analysis**")
            
            # Voltage range per cycle (max - min)
            voltage_range = df_trends['voltage_max'] - df_trends['voltage_min']
            
            fig_voltage_stability = go.Figure()
            
            # Line chart with filled area
            fig_voltage_stability.add_trace(go.Scatter(
                x=df_trends['cycle_number'],
                y=voltage_range,
                mode='lines+markers',
                line=dict(color='#06b6d4', width=2),
                marker=dict(size=5, color='#06b6d4'),
                fill='tozeroy',
                name='Voltage Range'
            ))
            
            # Add average line
            avg_range = voltage_range.mean()
            fig_voltage_stability.add_hline(
                y=avg_range, 
                line_dash="dash", 
                line_color="#fbbf24",
                annotation_text=f"Avg: {avg_range:.2f}V",
                annotation_position="right",
                annotation_font_color="white"
            )
            
            fig_voltage_stability.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', size=11),
                xaxis_title='Cycle Number',
                yaxis_title='Voltage Range (V)',
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig_voltage_stability, use_container_width=True)
            
            st.caption("📊 Lower variance = better cell balance & health")
        
        # Summary Statistics
        st.markdown("### Summary Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Cycles", len(df_trends))
        with col2:
            st.metric("Avg Temperature", f"{df_trends['average_temperature'].mean():.1f}°C")
        with col3:
            st.metric("Total Distance", f"{df_trends['total_distance'].sum():.2f} km")

if __name__ == "__main__":
    main()