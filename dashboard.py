# dashboard.py
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash_extensions import WebSocket # ตัวสำคัญสำหรับ Real-time
import pandas as pd
import json
import plotly.graph_objects as go

# สร้าง DataFrame เริ่มต้นสำหรับเก็บข้อมูลคอมเมนต์
df = pd.DataFrame(columns=['text', 'label', 'score'])

# เริ่มต้นสร้างแอปพลิเคชัน Dash และใช้ธีม Bootstrap เพื่อความสวยงาม
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# --- กำหนดหน้าตาของ Dashboard ---
app.layout = dbc.Container([
    # ส่วนหัวของ Dashboard
    html.H1("📊 Real-time Product Review Sentiment Dashboard", className="my-4 text-center"),

    # นี่คือหัวใจของการเชื่อมต่อ! คอมโพเนนต์นี้จะ "ฟัง" ข้อมูลจาก Backend ของเรา
    # โค้ดใหม่ที่ถูกต้อง
    WebSocket(id="ws", url="wss://realtime-sentiment-app-256576118647.asia-southeast1.run.app/ws"),

    # แบ่งหน้าจอเป็นแถวและคอลัมน์
    dbc.Row([
        # คอลัมน์ซ้ายสำหรับกราฟวงกลม
        dbc.Col(
            dcc.Graph(id='sentiment-pie-chart'),
            md=4
        ),
        # คอลัมน์ขวาสำหรับตาราง
        dbc.Col([
            html.H4("Latest Reviews"),
            dash_table.DataTable(
                id='live-update-table',
                columns=[{'name': i.capitalize(), 'id': i} for i in df.columns],
                data=[], # เริ่มต้นด้วยข้อมูลว่าง
                style_cell={'textAlign': 'left', 'padding': '10px'},
                style_header={'fontWeight': 'bold'},
                page_size=10,
            )
        ], md=8),
    ])
], fluid=True)


# --- ส่วนควบคุมการทำงาน (Callback) ---
# Callback นี้จะทำงานทุกครั้งที่มี 'message' ใหม่เข้ามาจาก WebSocket
@app.callback(
    Output('live-update-table', 'data'),      # ผลลัพธ์ที่ 1: ข้อมูลใหม่สำหรับตาราง
    Output('sentiment-pie-chart', 'figure'),  # ผลลัพธ์ที่ 2: กราฟใหม่สำหรับแสดง
    Input('ws', 'message'),                   # ตัวกระตุ้น: ข้อความที่ได้รับจาก WebSocket
    State('live-update-table', 'data')        # ข้อมูลเสริม: ข้อมูลปัจจุบันที่มีอยู่ในตาราง
)
def update_data(message, existing_data):
    # ถ้ายังไม่มี message ใหม่เข้ามา ก็ไม่ต้องทำอะไร
    if message is None:
        raise dash.exceptions.PreventUpdate

    # แปลงข้อมูล JSON string ที่ได้จาก WebSocket กลับเป็น Python dictionary
    new_row = json.loads(message['data'])

    # เพิ่มข้อมูลแถวใหม่เข้าไป "ข้างบนสุด" ของข้อมูลเดิม
    updated_data = [new_row] + existing_data

    # สร้าง DataFrame จากข้อมูลที่อัปเดตแล้วเพื่อนับจำนวน label
    df_updated = pd.DataFrame(updated_data)
    sentiment_counts = df_updated['label'].value_counts()

    # สร้างกราฟวงกลมใหม่
    fig = go.Figure(data=[go.Pie(
        labels=sentiment_counts.index,
        values=sentiment_counts.values,
        marker_colors=['#28a745', '#dc3545', '#6c757d'], # สีสำหรับ positive, negative, neutral
        hole=.3
    )])
    fig.update_layout(title_text='Sentiment Distribution', legend_title_text='Sentiment')

    # ส่งข้อมูลใหม่กลับไปอัปเดตหน้าเว็บ
    return updated_data, fig


# --- ส่วนสำหรับรัน Dashboard Server ---
if __name__ == '__main__':
    app.run(debug=True, port=8050)