from dash import Dash, dcc, html, Input, Output
import plotly.graph_objs as go
import pandas as pd
import functions  # Import our data handling functions
import os

# Initialize Dash app
app = Dash(__name__)

# Layout
app.layout = html.Div([
    # Link to Google Fonts for Roboto
    html.Link(
        href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap", 
        rel="stylesheet"
    ),

    # Navbar
    html.Nav(
        children=html.H1("Application for Plant Monitoring", style={
            "fontSize": "56px", 
            "color": "#FAF6E3", 
            "margin": "0", 
            "padding": "10px",
            "fontFamily": "Roboto, sans-serif"
        }),
        style={"backgroundColor": "#2A3663", "textAlign": "left"}
    ),

    # Main content area for timeline and speedometers
    html.Div([
        # Left side - Timeline graph
        html.Div(
            dcc.Graph(id="timeline-graph", style={"width": "100%", "height": "100%"}),
            style={
                "width": "75%", 
                "padding": "10px", 
                "backgroundColor": "#D8DBBD",
                "display": "flex",
                "flexDirection": "column",
                "justifyContent": "center",
                "fontFamily": "Roboto, sans-serif"
            }
        ),

        # Right side - Speedometers
        html.Div([
            dcc.Graph(id="current-temperature", style={"width": "100%", "height": "50%"}),
            dcc.Graph(id="current-humidity", style={"width": "100%", "height": "50%"}),
        ], style={
            "width": "25%", 
            "padding": "10px", 
            "backgroundColor": "#B59F78",
            "display": "flex",
            "flexDirection": "column",
            "justifyContent": "space-between",
            "fontFamily": "Roboto, sans-serif"
        })
    ], style={"display": "flex", "backgroundColor": "#D8DBBD", "alignItems": "stretch", "height": "80vh"}),

    # New Div below main content
    html.Div([
        # Left section - 1/3 width
        html.Div([
            html.H3("Prediction Model", style={
                "color": "#2A3663",
                "marginBottom": "10px",
                "fontFamily": "Roboto, sans-serif"
            }),
            html.P("This option will activate when the button is pressed. It generates a guideline of actions based on the plant's humidity, temperature, and the time of day. These predictions will appear in the right section.", style={
                "color": "#4A4A4A",
                "fontSize": "16px",
                "marginBottom": "20px",
                "fontFamily": "Roboto, sans-serif"
            }),
            html.Button("Activate Prediction Model", id="left-button", style={
                "padding": "10px 20px",
                "fontSize": "16px",
                "color": "#FAF6E3",
                "backgroundColor": "#2A3663",
                "border": "none",
                "cursor": "pointer",
                "fontFamily": "Roboto, sans-serif"
            })
        ], style={
            "width": "33.33%", 
            "padding": "10px", 
            "backgroundColor": "#A7B6A0",
            "textAlign": "center",
            "boxSizing": "border-box"  # Ensures padding doesn't increase width
        }),

        # Right section - 2/3 width
        html.Div(id="right-section", style={
            "width": "66.67%", 
            "padding": "10px", 
            "backgroundColor": "#C1B2A2",
            "textAlign": "center",
            "fontFamily": "Roboto, sans-serif",
            "boxSizing": "border-box"  # Ensures padding doesn't increase width
        })
    ], style={
        "display": "flex",
        "width": "100%",           # Matches width of parent container
        "maxWidth": "100%",         # Ensures container does not overflow
        "backgroundColor": "#D8DBBD",
        "alignItems": "stretch",
        "padding": "10px",
        "boxSizing": "border-box"   # Ensures padding doesn't increase width
    }),

    # Footer
    html.Footer("William A. Pabon", style={
        "fontSize": "28px",
        "textAlign": "center",
        "padding": "10px",
        "backgroundColor": "#2A3663",
        "color": "#FAF6E3",
        "fontFamily": "Roboto, sans-serif"
    }),

    # Interval for auto-update
    dcc.Interval(id="interval-update", interval=5 * 60 * 1000, n_intervals=0)
])

# Callback to run ETL when the page is first loaded
@app.callback(
    Output("timeline-graph", "figure"),  # Returning something to trigger the page load
    Output("current-temperature", "figure"),
    Output("current-humidity", "figure"),
    Input("interval-update", "n_intervals")
)
def run_etl_on_page_load(n):
    # Run ETL process when the page loads or refreshes
    functions.run_etl()

    # Fetch historical data
    df = functions.fetch_historical_data()

    # Plot both temperature and humidity over time with specified colors
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["timestamp"], 
        y=df["humidity"], 
        mode="lines", 
        name="Humidity",
        line=dict(color="blue")  # Set humidity line color to blue
    ))
    fig.add_trace(go.Scatter(
        x=df["timestamp"], 
        y=df["temperature"], 
        mode="lines", 
        name="Temperature",
        line=dict(color="red")  # Set temperature line color to red
    ))

    # Update layout with increased font sizes for title, axes, legend, and background color
    fig.update_layout(
        title="Temperature and Humidity Over Time",
        xaxis_title="Time",
        yaxis_title="Value",
        title_font=dict(size=32),  # Increase title font size
        xaxis=dict(title_font=dict(size=24)),  # Increase x-axis title font size
        yaxis=dict(title_font=dict(size=24)),  # Increase y-axis title font size
        legend=dict(font=dict(size=14)),  # Increase legend font size
        paper_bgcolor="#D8DBBD",  # Set background color of the figure
        plot_bgcolor="#D8DBBD"   # Set background color for the plotting area
    )

    # Update current temperature and humidity speedometers
    latest_data = functions.fetch_latest_data()

    # Create the humidity gauge with background color and white needle line
    humidity_fig = go.Figure(go.Indicator(
        mode="gauge+number",  # Exclude 'delta' to avoid displaying a delta with fill
        value=latest_data["humidity"],
        title={"text": "Current Humidity (%)", "font": {"size": 24}},  # Increase title font size
        gauge={
            "axis": {"range": [0, 100], "tickfont": {"size": 18}},  # Increase tick labels font size
            "bar": {"color": "#AF1740"},  # Set needle color
            "steps": [
                {"range": [0, 30], "color": "lightblue"},
                {"range": [30, 60], "color": "blue"},
                {"range": [60, 100], "color": "darkblue"}
            ]
        },
        domain={'x': [0, 1], 'y': [0, 1]}  # Expand to fit the full height of the div
    ))

    # Set the background color
    humidity_fig.update_layout(
        paper_bgcolor="#B59F78",
        plot_bgcolor="#B59F78"
    )

    # Create the temperature gauge with background color and white needle line
    temp_fig = go.Figure(go.Indicator(
        mode="gauge+number",  # Exclude 'delta' to avoid displaying a delta with fill
        value=latest_data["temperature"],
        title={"text": "Current Temperature (°C)", "font": {"size": 24}},  # Increase title font size
        gauge={
            "axis": {"range": [0, 85], "tickfont": {"size": 18}},  # Increase tick labels font size
            "bar": {"color": "#7AB2D3"},  # Set needle color
            "steps": [
                {"range": [0, 30], "color": "lightgreen"},
                {"range": [30, 60], "color": "yellow"},
                {"range": [60, 85], "color": "red"}
            ]
        },
        domain={'x': [0, 1], 'y': [0, 1]}  # Expand to fit the full height of the div
    ))

    # Set the background color
    temp_fig.update_layout(
        paper_bgcolor="#B59F78",
        plot_bgcolor="#B59F78"
    )

    return fig, temp_fig, humidity_fig


# Callback for button press (only generating recommendations now)
@app.callback(
    Output("right-section", "children"),
    Input("left-button", "n_clicks"),
)
def update_predictions(n_clicks):
    """Handles button press and runs the generate_recommendations"""
    if n_clicks is None:
        return "Click the button to activate the prediction model."

    # Generate recommendations
    recommendations = functions.generate_recommendations()

    # Display recommendations in the right section
    return html.Div([
        html.H4("Recommended Actions for Your Plant", style={"color": "#2A3663"}),
        html.P(recommendations, style={"color": "#4A4A4A", "fontSize": "16px", "fontFamily": "Roboto, sans-serif"})
    ])


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050, debug=True)
