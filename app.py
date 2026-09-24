import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# Khởi tạo App Dash
app = dash.Dash(__name__)
server = app.server

# Bộ nhớ đệm dữ liệu (Sliding window)
MAX_LEN = 30
data = {
    "time": [],
    "temp": [],
    "forecast": []
}

current_temp = 26.0
current_forecast = 26.0

# Giao diện ứng dụng Dash phối màu Dark Mode chuyên nghiệp
app.layout = html.Div(
    style={
        "fontFamily": "'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
        "padding": "30px",
        "backgroundColor": "#0b0f19",      # Nền đen ánh xanh công nghệ
        "minHeight": "100vh",
        "color": "#ffffff"
    }, 
    children=[
        # Tiêu đề chính
        html.H2(
            "⚡ REAL-TIME SENSOR STREAM & PREDICTIVE ANALYTICS", 
            style={"textAlign": "center", "letterSpacing": "1.5px", "color": "#00f2fe", "margin": "0 0 10px 0"}
        ),
        html.P(
            "Hệ thống giám sát tín hiệu cảm biến IoT thời gian thực kết hợp thuật toán khử nhiễu & mô hình dự báo Exponential Smoothing.",
            style={"textAlign": "center", "color": "#8892b0", "fontSize": "15px", "marginBottom": "25px"}
        ),
        
        # Thẻ hiển thị KPI động
        html.Div(
            id="kpi-panel", 
            style={"display": "flex", "justifyContent": "center", "gap": "20px", "margin": "20px 0"}
        ),
        
        # Khung chứa biểu đồ bo góc có viền phát sáng nhẹ
        html.Div(
            dcc.Graph(id="live-chart"), 
            style={
                "backgroundColor": "#111827", 
                "borderRadius": "12px", 
                "padding": "10px",
                "boxShadow": "0 8px 24px rgba(0, 0, 0, 0.5)",
                "border": "1px solid #1f2937"
            }
        ),
        
        # Bộ kích hoạt cập nhật Real-Time (1.5 giây)
        dcc.Interval(
            id="interval-clock",
            interval=1500,
            n_intervals=0
        )
    ]
)

# Callback xử lý Real-Time
@app.callback(
    [Output("live-chart", "figure"),
     Output("kpi-panel", "children")],
    [Input("interval-clock", "n_intervals")]
)
def stream_data(n):
    global current_temp, current_forecast, data
    
    # 1. Mô phỏng quá trình ngẫu nhiên cảm biến
    noise = np.random.normal(0, 0.45)
    current_temp = float(np.clip(current_temp + noise, 18.0, 36.0))
    
    # 2. Thuật toán dự báo Exponential Smoothing (alpha = 0.35)
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
        
    # Tính độ lệch chuẩn động
    current_std = np.std(data["temp"]) if len(data["temp"]) > 1 else 0.0

    # 3. Trực quan hóa Plotly phong cách Dark Mode
    fig = go.Figure()
    
    # Đường cảm biến phát sáng màu Neon Cyan
    fig.add_trace(go.Scatter(
        x=data["time"], y=data["temp"],
        mode="lines+markers", 
        name="Tín hiệu đo (°C)",
        line=dict(color="#00f2fe", width=3),
        marker=dict(size=6, color="#4facfe")
    ))
    
    # Đường dự báo nét đứt màu Neon Orange
    fig.add_trace(go.Scatter(
        x=data["time"], y=data["forecast"],
        mode="lines", 
        name="Dự báo (Exp Smoothing)",
        line=dict(color="#ff9f43", width=2, dash="dash")
    ))
    
    fig.update_layout(
        title=dict(
            text="Biểu đồ giám sát & dự báo nhiệt độ theo thời gian thực",
            font=dict(color="#e2e8f0", size=16)
        ),
        xaxis_title="Thời gian thực (hh:mm:ss)",
        yaxis_title="Nhiệt độ (°C)",
        template="plotly_dark",             # Theme tối chuẩn Plotly
        paper_bgcolor="#111827",           # Nền ngoài của biểu đồ
        plot_bgcolor="#111827",            # Nền lưới vẽ
        font=dict(color="#94a3b8"),
        xaxis=dict(gridcolor="#1e293b", zerolinecolor="#1e293b"),
        yaxis=dict(gridcolor="#1e293b", zerolinecolor="#1e293b", range=[16, 38]),
        margin=dict(l=30, r=30, t=50, b=30),
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=1.02, 
            xanchor="right", 
            x=1,
            font=dict(color="#cbd5e1")
        )
    )
    
    # Style thẻ Card KPI phong cách Dark Glassmorphism
    card_style = {
        "padding": "16px 28px", 
        "backgroundColor": "#111827", 
        "borderRadius": "10px", 
        "border": "1px solid #1f2937",
        "boxShadow": "0 4px 12px rgba(0, 0, 0, 0.3)",
        "textAlign": "center"
    }
    
    cards = [
        html.Div([
            html.Div("Nhiệt độ hiện tại", style={"fontSize": "13px", "color": "#94a3b8", "marginBottom": "5px"}), 
            html.B(f"{current_temp:.2f} °C", style={"fontSize": "24px", "color": "#00f2fe"})
        ], style=card_style),
        
        html.Div([
            html.Div("Dự báo tiếp theo", style={"fontSize": "13px", "color": "#94a3b8", "marginBottom": "5px"}), 
            html.B(f"{current_forecast:.2f} °C", style={"fontSize": "24px", "color": "#ff9f43"})
        ], style=card_style),
        
        html.Div([
            html.Div("Độ lệch chuẩn (Std Dev)", style={"fontSize": "13px", "color": "#94a3b8", "marginBottom": "5px"}), 
            html.B(f"{current_std:.2f}", style={"fontSize": "24px", "color": "#10b981"})
        ], style=card_style)
    ]
    
    return fig, cards

if __name__ == "__main__":
    app.run_server(debug=True)
