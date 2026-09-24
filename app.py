import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# Khởi tạo App Dash
app = dash.Dash(__name__)
server = app.server  # Biến server phục vụ triển khai cloud

# Bộ nhớ đệm dữ liệu (Sliding window)
MAX_LEN = 30
data = {
    "time": [],
    "temp": [],
    "forecast": []
}

current_temp = 26.0
current_forecast = 26.0

# Giao diện ứng dụng Dash
app.layout = html.Div(style={"fontFamily": "Segoe UI, sans-serif", "padding": "25px", "backgroundColor": "#f8f9fa"}, children=[
    html.H2("🔬 REAL-TIME SENSOR STREAM & PREDICTIVE ANALYTICS", style={"textAlign": "center", "color": "#1e3d59"}),
    html.P("Hệ thống giám sát tín hiệu cảm biến thời gian thực kết hợp thuật toán khử nhiễu & mô hình dự báo Exponential Smoothing.",
           style={"textAlign": "center", "color": "#666"}),
    
    # Thẻ hiển thị KPI động
    html.Div(id="kpi-panel", style={"display": "flex", "justifyContent": "center", "gap": "20px", "margin": "20px 0"}),
    
    # Biểu đồ Plotly động
    html.Div(dcc.Graph(id="live-chart"), style={"backgroundColor": "#fff", "borderRadius": "8px", "boxShadow": "0 2px 4px rgba(0,0,0,0.1)"}),
    
    # dcc.Interval: Cơ chế trigger cập nhật dữ liệu Real-Time (1500ms = 1.5 giây)
    dcc.Interval(
        id="interval-clock",
        interval=1500,
        n_intervals=0
    )
])

# Callback xử lý Real-Time
@app.callback(
    [Output("live-chart", "figure"),
     Output("kpi-panel", "children")],
    [Input("interval-clock", "n_intervals")]
)
def stream_data(n):
    global current_temp, current_forecast, data
    
    # 1. Mô phỏng quá trình ngẫu nhiên cảm biến (Stochastic Gaussian Process)
    noise = np.random.normal(0, 0.45)
    current_temp = float(np.clip(current_temp + noise, 18.0, 36.0))
    
    # 2. Thuật toán dự báo Exponential Smoothing: S_t = alpha * Y_t + (1 - alpha) * S_{t-1}
    alpha = 0.35
    current_forecast = alpha * current_temp + (1 - alpha) * current_forecast
    
    # Ghi nhận mốc thời gian
    t_now = datetime.now().strftime("%H:%M:%S")
    data["time"].append(t_now)
    data["temp"].append(round(current_temp, 2))
    data["forecast"].append(round(current_forecast, 2))
    
    # Giới hạn kích thước mảng trượt
    if len(data["time"]) > MAX_LEN:
        data["time"].pop(0)
        data["temp"].pop(0)
        data["forecast"].pop(0)
        
    # Tính độ lệch chuẩn động (Dynamic Standard Deviation)
    current_std = np.std(data["temp"]) if len(data["temp"]) > 1 else 0.0

    # 3. Trực quan hóa Plotly Multi-layer
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data["time"], y=data["temp"],
        mode="lines+markers", name="Tín hiệu đo (°C)",
        line=dict(color="#007bff", width=2)
    ))
    fig.add_trace(go.Scatter(
        x=data["time"], y=data["forecast"],
        mode="lines", name="Dự báo (Exp Smoothing)",
        line=dict(color="#ff5722", width=2, dash="dash")
    ))
    fig.update_layout(
        title="Biểu đồ giám sát & dự báo nhiệt độ theo thời gian thực",
        xaxis_title="Thời gian thực (hh:mm:ss)",
        yaxis_title="Nhiệt độ (°C)",
        template="plotly_white",
        yaxis=dict(range=[16, 38]),
        margin=dict(l=30, r=30, t=50, b=30)
    )
    
    # Card KPI
    card_style = {"padding": "12px 20px", "backgroundColor": "#fff", "borderRadius": "6px", "border": "1px solid #e0e0e0"}
    cards = [
        html.Div([html.Div("Nhiệt độ hiện tại", style={"fontSize": "12px", "color": "#777"}), 
                  html.B(f"{current_temp:.2f} °C", style={"fontSize": "20px", "color": "#007bff"})], style=card_style),
        html.Div([html.Div("Dự báo tiếp theo", style={"fontSize": "12px", "color": "#777"}), 
                  html.B(f"{current_forecast:.2f} °C", style={"fontSize": "20px", "color": "#ff5722"})], style=card_style),
        html.Div([html.Div("Độ lệch chuẩn (Std Dev)", style={"fontSize": "12px", "color": "#777"}), 
                  html.B(f"{current_std:.2f}", style={"fontSize": "20px", "color": "#28a745"})], style=card_style)
    ]
    return fig, cards

if __name__ == "__main__":
    app.run_server(debug=True)
