# dashboard.py
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash_extensions import WebSocket
import pandas as pd
import json
import plotly.graph_objects as go
import os

# --- ส่วนการตั้งค่าและการดีบัก ---
# ดึง URL ของ Backend มาเก็บไว้ก่อน
backend_ws_url = os.environ.get("BACKEND_WS_URL")

# พิมพ์ค่า URL ที่ได้รับมาออกมาใน Log อย่างชัดเจน เพื่อให้เราเห็นว่ามันถูกต้องหรือไม่
print("--- DASHBOARD STARTUP ---")
print(f"Attempting to read BACKEND_WS_URL environment variable.")
print(f"Value received: '{backend_ws_url}' (Type: {type(backend_ws_url)})")
print("-------------------------")


# สร้างแอปพลิเคชัน Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server # เปิดเผยตัวแปร server ให้ Waitress รู้จัก

# นำ Layout ทั้งหมดไปใส่ไว้ในฟังก์ชันเพื่อเพิ่มความเสถียร
def serve_layout():
    # ตรวจสอบค่า URL อย่างละเอียด
    if not backend_ws_url or not isinstance(backend_ws_url, str) or not backend_ws_url.startswith('wss://'):
        # ถ้าค่าที่ได้รับมาไม่มี, ไม่ใช่ข้อความ, หรือไม่ได้ขึ้นต้นด้วย wss:// ให้แสดงหน้า Error
        print("ERROR: BACKEND_WS_URL is invalid or not set.")
        return html.Div([
            html.H1("Configuration Error", style={'color': 'red'}),
            html.P("The BACKEND_WS_URL environment variable is either not set or invalid."),
            html.P(f"Value received was: '{backend_ws_url}'")
        ])

    # ถ้าทุกอย่างถูกต้อง ให้แสดง Dashboard ปกติ
    return dbc.Container([
        html.H1("📊 Real-time Product Review Sentiment Dashboard", className="my-4 text-center"),
        WebSocket(id="ws", url=backend_ws_url),
        dbc.Row([
            dbc.Col(dcc.Graph(id='sentiment-pie-chart'), md=4),
            dbc.Col([
                html.H4("Latest Reviews"),
                dash_table.DataTable(
                    id='live-update-table',
                    columns=[{'name': i.capitalize(), 'id': i} for i in ['text', 'label', 'score']],
                    data=[],
                    style_cell={'textAlign': 'left', 'padding': '10px'},
                    style_header={'fontWeight': 'bold'},
                    page_size=10,
                )
            ], md=8),
        ])
    ], fluid=True)

app.layout = serve_layout

# Callback สำหรับอัปเดตข้อมูล
@app.callback(
    Output('live-update-table', 'data'),
    Output('sentiment-pie-chart', 'figure'),
    Input('ws', 'message'),
    State('live-update-table', 'data')
)
def update_data(message, existing_data):
    if not message:
        raise dash.exceptions.PreventUpdate

    try:
        new_row = json.loads(message['data'])
        updated_data = [new_row] + existing_data
        df_updated = pd.DataFrame(updated_data)
        sentiment_counts = df_updated['label'].value_counts()

        fig = go.Figure(data=[go.Pie(
            labels=sentiment_counts.index,
            values=sentiment_counts.values,
            marker_colors=['#28a745', '#dc3545', '#6c757d'], # Positive, Negative, Neutral
            hole=.3
        )])
        fig.update_layout(title_text='Sentiment Distribution', legend_title_text='Sentiment')

        return updated_data, fig
    except (json.JSONDecodeError, KeyError) as e:
        print(f"ERROR: Could not process incoming WebSocket message. Error: {e}. Message: {message}")
        raise dash.exceptions.PreventUpdate

# ส่วนสำหรับรันบนเครื่อง (ไม่มีผลตอน Deploy)
if __name__ == '__main__':
    # สำหรับการทดสอบบนเครื่อง ให้เราตั้งค่า URL เองชั่วคราว
    backend_ws_url = "ws://127.0.0.1:8000/ws" 
    print(f"INFO: Running in local debug mode. Connecting to {backend_ws_url}")
    app.run(debug=True, port=8050)

