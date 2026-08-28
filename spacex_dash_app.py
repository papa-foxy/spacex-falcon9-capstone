import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Load the data
spacex_df = pd.read_csv("dataset_part_2.csv")
max_payload = spacex_df["PayloadMass"].max()
min_payload = spacex_df["PayloadMass"].min()

# Create the Dash app
app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1("SpaceX Launch Records Dashboard",
            style={"textAlign": "center", "color": "#503D36", "font-size": 40}),

    dcc.Dropdown(id="site-dropdown",
        options=[{"label": "All Sites", "value": "ALL"}] +
                [{"label": site, "value": site} for site in spacex_df["LaunchSite"].unique()],
        value="ALL",
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),

    html.Div(dcc.Graph(id="success-pie-chart")),
    html.Br(),

    html.P("Payload range (Kg):"),
    dcc.RangeSlider(id="payload-slider",
        min=0, max=10000, step=1000,
        marks={0: "0", 2500: "2500", 5000: "5000", 7500: "7500", 10000: "10000"},
        value=[min_payload, max_payload]
    ),

    html.Div(dcc.Graph(id="success-payload-scatter-chart")),
])


# Callback: pie chart (success counts, by site)
@app.callback(
    Output(component_id="success-pie-chart", component_property="figure"),
    Input(component_id="site-dropdown", component_property="value")
)
def get_pie_chart(entered_site):
    if entered_site == "ALL":
        fig = px.pie(spacex_df, values="Class", names="LaunchSite",
                     title="Total Successful Launches by Site")
    else:
        filtered_df = spacex_df[spacex_df["LaunchSite"] == entered_site]
        outcome_counts = filtered_df["Class"].value_counts().reset_index()
        outcome_counts.columns = ["Class", "count"]
        fig = px.pie(outcome_counts, values="count", names="Class",
                     title=f"Total Launch Outcomes for site {entered_site}")
    return fig


# Callback: scatter chart (payload vs. success, by site and payload range)
@app.callback(
    Output(component_id="success-payload-scatter-chart", component_property="figure"),
    [Input(component_id="site-dropdown", component_property="value"),
     Input(component_id="payload-slider", component_property="value")]
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    mask = (spacex_df["PayloadMass"] >= low) & (spacex_df["PayloadMass"] <= high)
    filtered_df = spacex_df[mask]

    if entered_site != "ALL":
        filtered_df = filtered_df[filtered_df["LaunchSite"] == entered_site]

    fig = px.scatter(filtered_df, x="PayloadMass", y="Class",
                      color="BoosterVersion",
                      title="Correlation between Payload and Success for " + entered_site)
    return fig


# Run the app
if __name__ == "__main__":
    app.run()
