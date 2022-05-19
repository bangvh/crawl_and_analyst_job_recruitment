# Import required libraries
import pickle
import copy
import pathlib
import urllib.request
import dash
import math
import datetime as dt
import pandas as pd
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
# Multi-dropdown options
from controls import PROVINCE, EXPERIENCE, TAG, RANGE_SALARY

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}],
)
app.title = "PHÂN TÍCH DỮ LIỆU VIỆC LÀM TỪ NGUỒN DỮ LIỆU ONLINE"
server = app.server

df = pd.read_pickle('data.pkl')

# Create global chart template
mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.Zme1-Uzoi75IaFbieBDl3A"

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Satellite Overview",
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style="light",
        center=dict(lon=-78.05, lat=42.54),
        zoom=7,
    ),
)

# Create app layout
app.layout = html.Div(
    [
        dcc.Store(id="aggregate_data"),
        # empty Div to trigger javascript file for graph resizing
        html.Div(id="output-clientside"),
        html.Div(
            [
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("logo_khtn.png"),
                            id="plotly-image",
                            style={
                                "height": "60px",
                                "width": "auto",
                                "margin-bottom": "25px",
                            },
                        )
                    ],
                    className="one-third column",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "PHÂN TÍCH NHU CẦU TUYỂN DỤNG",
                                    style={"margin-bottom": "0px"},
                                )
                            ]
                        )
                    ],
                    className="two-thirds column",
                    id="title",
                )
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.P("Lọc theo dải lương:", className="control_label"),
                        dcc.RadioItems(
                            id="salary_filter",
                            options=[{'label': x, 'value': x} for x in RANGE_SALARY],
                            value="All",
                            labelStyle={"display": "inline-block"},
                            className="dcc_control",
                        ),
                        html.P("Lọc theo số năm kinh nghiệm:", className="control_label"),
                        dcc.Checklist(
                            id="experience_filter",
                            options=[{'label': str(x) + ' năm', 'value': x} for x in EXPERIENCE],
                            className="dcc_control",
                            value=[],
                            labelStyle={"display": "inline-block"},
                        ),
                        html.P("Lọc theo kỹ năng:", className="control_label"),
                        dcc.Checklist(
                            id="tag_filter",
                            options=[{'label': x, 'value': x} for x in TAG],
                            value=[],
                            className="dcc_control",
                        ),
                        html.P("Lọc theo thành phố:", className="control_label"),
                        dcc.Dropdown(
                            id="province_filter",
                            options=[{'label': x, 'value': x} for x in PROVINCE],
                            multi=True,
                            value=[],
                            className="dcc_control",
                        ),
                    ],
                    className="pretty_container four columns",
                    id="cross-filter-options",
                )
                ,
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [html.P("Số tin tuyển dụng"), html.H6(id="totalText")],
                                    id="total",
                                    className="mini_container",
                                ), 
                                html.Div(
                                    [html.P("Mức lương thấp nhất"), html.H6(id="salaryMinText")],
                                    id="salaryMin",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.P("Mức lương cao nhất"), html.H6(id="salaryMaxText")],
                                    id="salaryMax",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.P("Mức lương trung bình"), html.H6(id="salaryMeanText"),],
                                    id="salaryMean",
                                    className="mini_container",
                                ),
                            ],
                            id="info-container",
                            className="row container-display",
                        ),
                        html.Div(
                            [dcc.Graph(id="tagSalary_graph")],
                            className="row container-display",
                ),
                    ],
                    id="right-column",
                    className="eight columns",
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="cityGraph")],
                    className="pretty_container six columns",
                ),
                html.Div(
                    [dcc.Graph(id="tagGraph")],
                    className="pretty_container six columns",
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="tagRangeSalary")],
                    className="pretty_container six columns",
                ),
                html.Div(
                    [dcc.Graph(id="tagExperienceSalary")],
                    className="pretty_container six columns",
                ),
            ],
            className="row flex-display",
        ),
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)


# Helper functions
def filter_dataframe(df, salary_filter, experience_filter, tag_filter, province_filter):
    # filter salary
    if salary_filter == '<2K': dff = df[df['salary_low'] < 2000]
    elif salary_filter == '2-5K': dff = df[(df['salary_low'] < 5000) & (df['salary_low'] >= 2000)]
    elif salary_filter == '5-10K': dff = df[(df['salary_low'] < 10000) & (df['salary_low'] >= 5000)]
    elif salary_filter == '10K+': dff = df[(df['salary_low'] >= 10000)]
    else: dff = df

    # filter exp
    if len(experience_filter) > 0: dff = dff[dff['experience_recode'].isin(experience_filter)]
    if len(tag_filter) > 0: dff = dff[dff['tag'].isin(tag_filter)]
    if len(province_filter) > 0 and 'All' not in province_filter: dff = dff[dff['province_recode'].isin(province_filter)]
    return dff


@app.callback(
    Output("aggregate_data", "data"),
    [
        Input("salary_filter", "value"),
        Input("experience_filter", "value"),
        Input("tag_filter", "value"),
        Input("province_filter", "value"),
    ],
)
def update_production_text(salary_filter, experience_filter, tag_filter, province_filter):
    dff = filter_dataframe(df, salary_filter, experience_filter, tag_filter, province_filter)
    total = dff.shape[0]
    salary_min = dff['salary_low'].min()
    salary_max = dff['salary_up'].max()
    salary_mean = dff['salary_mean'].mean()
    result = [total, salary_min, salary_max, salary_mean]
    return [str(int(x)) for x in result]


@app.callback(
    [
        Output("totalText", "children"),
        Output("salaryMinText", "children"),
        Output("salaryMaxText", "children"),
        Output("salaryMeanText", "children"),
    ],
    [Input("aggregate_data", "data")],
)
def update_text(data):
    return data[0] + " tin", data[1] + " NDT", data[2] + " NDT", data[3] + " NDT"



@app.callback(
    Output("tagSalary_graph", "figure"),
    [
        Input("salary_filter", "value"),
        Input("experience_filter", "value"),
        Input("tag_filter", "value"),
        Input("province_filter", "value"),
    ],
)
def makeTagSalaryGraph(salary_filter, experience_filter, tag_filter, province_filter):
    dff = filter_dataframe(df, salary_filter, experience_filter, tag_filter, province_filter)
    dff = dff.groupby('tag')['salary_mean'].mean().apply(int).sort_values(ascending=False).head(5)
    dff = dff.reset_index()
    dff.columns = ['vị trí', 'mức lương']

    fig = px.bar(dff, x='vị trí', y='mức lương', title='Mức lương theo vị trí công việc', log_y=True,
                 color_discrete_sequence=['#34e3ec']*dff.shape[0])
    fig.update_layout(title_x=0.5)
    return fig


@app.callback(
    Output("cityGraph", "figure"),
    [
        Input("salary_filter", "value"),
        Input("experience_filter", "value"),
        Input("tag_filter", "value"),
        Input("province_filter", "value"),
    ],
)
def make_cityGraph(salary_filter, experience_filter, tag_filter, province_filter):
    dff = filter_dataframe(df, salary_filter, experience_filter, tag_filter, province_filter)
    dff = dff['province_recode'].value_counts().reset_index()
    dff.columns = ['thành phố', 'Số tin tuyển dụng']
    fig = px.bar(dff, y='Số tin tuyển dụng', x='thành phố', text_auto='.2s',
                 title="Số tin tuyển dụng phân theo thành phố")
    fig.update_layout(title_x=0.5)
    return fig

@app.callback(
    Output("tagGraph", "figure"),
    [
        Input("salary_filter", "value"),
        Input("experience_filter", "value"),
        Input("tag_filter", "value"),
        Input("province_filter", "value"),
    ],
)
def make_tagGraph(salary_filter, experience_filter, tag_filter, province_filter):
    dff = filter_dataframe(df, salary_filter, experience_filter, tag_filter, province_filter)
    top9 = dff['tag'].value_counts().head(9).index.to_list()
    dff = dff.where(dff['tag'].isin(top9), 'Khác')
    dff = dff['tag'].value_counts().reset_index()
    figure = go.Figure(data=[go.Pie(labels=dff['index'].values, values=dff['tag'].values, hole=.3)])
    figure.update_layout(title_text='Cơ cấu phân theo vị trí tuyển dụng', title_x=0.5)
    return figure


@app.callback(
    Output("tagRangeSalary", "figure"),
    [
        Input("salary_filter", "value"),
        Input("experience_filter", "value"),
        Input("tag_filter", "value"),
        Input("province_filter", "value"),
    ],
)
def make_tagRangeSalary(salary_filter, experience_filter, tag_filter, province_filter):
    dff = filter_dataframe(df, salary_filter, experience_filter, tag_filter, province_filter)
    fig = px.histogram(df, x="salary_mean",
                       labels={'salary_mean': 'Dải lương'},  # can specify one label per df column
                       opacity=0.8,
                       color_discrete_sequence=['indianred']  # color of histogram bars
                       )
    fig.update_layout(title_text='Biểu đồ histogram mức lương', title_x=0.5, bargap=0.05)
    return fig


@app.callback(
    Output("tagExperienceSalary", "figure"),
    [
        Input("salary_filter", "value"),
        Input("experience_filter", "value"),
        Input("tag_filter", "value"),
        Input("province_filter", "value"),
    ],
)
def make_tagExperienceSalary(salary_filter, experience_filter, tag_filter, province_filter):
    dff = filter_dataframe(df, salary_filter, experience_filter, tag_filter, province_filter)
    dff = dff.groupby('experience_recode')['salary_low'].mean()
    dff = dff.reset_index()
    dff.columns = ['số năm kinh nghiệm', 'mức lương']
    dff['số năm kinh nghiệm'] = dff['số năm kinh nghiệm'].apply(lambda x: str(x) + ' năm')

    fig = px.bar(dff, x='số năm kinh nghiệm', y='mức lương', text_auto='.2s',
                 color_discrete_sequence=['#ecac34']*dff.shape[0],
                 title="Mức lương phân theo yêu cầu năm kinh nghiệm")
    fig.update_layout(title_x=0.5)
    return fig





# Main
if __name__ == "__main__":
    app.run_server(debug=True, port=8080)
