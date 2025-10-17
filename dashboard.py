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

# <<< CHANGE 1: ดึง URL ของ Backend มาเก็บไว้ก่อน >>>
# เราจะเพิ่มการ print เพื่อให้เห็นค่าของมันใน Log ของ Google Cloud ด้วย
backend_ws_url = os.environ.get("BACKEND_WS_URL")
print(f"INFO: Dashboard is attempting to connect to WebSocket URL: {backend_ws_url}")

# สร้างแอปพลิเคชัน Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server # <<< CHANGE 2: เปิดเผยตัวแปร server ให้ Gunicorn รู้จัก >>>

# <<< CHANGE 3: นำ Layout ทั้งหมดไปใส่ไว้ในฟังก์ชัน >>>
# Dash จะเรียกฟังก์ชันนี้เมื่อมีคนเปิดหน้าเว็บ
# ซึ่งจะช่วยหน่วงเวลาการสร้าง WebSocket ที่อาจมีปัญหาออกไป
def serve_layout():
    if not backend_ws_url:
        return html.Div([
            html.H1("Configuration Error"),
            html.P("BACKEND_WS_URL environment variable is not set.")
        ])

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

# <<< CHANGE 4: บอกให้ app ใช้ layout จากฟังก์ชัน >>>
app.layout = serve_layout

# Callback ไม่มีการเปลี่ยนแปลง
@app.callback(
    Output('live-update-table', 'data'),
    Output('sentiment-pie-chart', 'figure'),
    Input('ws', 'message'),
    State('live-update-table', 'data')
)
def update_data(message, existing_data):
    if not message:
        raise dash.exceptions.PreventUpdate

    new_row = json.loads(message['data'])
    updated_data = [new_row] + existing_data
    df_updated = pd.DataFrame(updated_data)
    sentiment_counts = df_updated['label'].value_counts()

    fig = go.Figure(data=[go.Pie(
        labels=sentiment_counts.index,
        values=sentiment_counts.values,
        marker_colors=['#28a745', '#dc3545', '#6c757d'],
        hole=.3
    )])
    fig.update_layout(title_text='Sentiment Distribution', legend_title_text='Sentiment')

    return updated_data, fig

# ส่วนสำหรับรันบนเครื่อง (ไม่มีผลตอน Deploy)
if __name__ == '__main__':
    app.run(debug=True, port=8050)