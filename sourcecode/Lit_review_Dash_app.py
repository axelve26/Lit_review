from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import json
import os
import flask
import sys
import requests

FIELDS = [
    "Category (LLM/NLP, BKG/AOP, tox, lit)",
    "Aim of the study",
    "Methods used",
    "Data sources used",
    "Main findings",
    "Limitations",
    "Additional comments (e.g. specific technique/type of NLP, validation method, usefulness in AOP&BKG)",
    "Relevant citations",
    "What2write"
]

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


app.layout = html.Div([
    html.Div(id='page-title'),
    dcc.Store(id='pubmed-id-store'),
    dcc.Store(id='url-store'),
    html.Div([
        dbc.Row([
            dbc.Col(dbc.Label(field), width=2),
            dbc.Col(
                dbc.Textarea(
                    id=f"textarea-{i}",
                    style={"width": "100%", "height": "200px" if i >= len(FIELDS) - 2 else "35px"}
                ),
                width=10
            )
        ], className="mb-3") for i, field in enumerate(FIELDS)
    ]),

    dbc.Row([
        dbc.Col(dbc.Button("Save Progress", id="save-button", color="primary", className="mr-2"), width="auto"),
        dbc.Col(dbc.Button("Submit", id="submit-button", color="success"), width="auto")
    ], className="mb-3"),

    dcc.Store(id="stored-data"),
    html.Div(id="output")
])

@app.callback(
    Output("page-title", "children"),
    Input("pubmed-id-store", "data"),
    State("url-store", "data")
)
def update_title(pubmed_id, url):
    if pubmed_id and url:
        return html.Div([
            # html.P(f"Article Review App - PubMed ID: {pubmed_id}"),
            html.A(f"Article URL: {url}", href=url, target="_blank")
        ])
    return html.P("Article Review App")

@app.callback(
    [Output(f"textarea-{i}", "value") for i in range(len(FIELDS))],
    Input("pubmed-id-store", "data")
)
def load_progress(pubmed_id):
    try:
        if pubmed_id:
            file_path = f"./data/saved_progress/save_in_progress_{pubmed_id}.json"
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    data = json.load(f)
                return [data.get(field, "") for field in FIELDS]
    except Exception as e:
        print(f"Error loading progress: {e}")
    return [""] * len(FIELDS)


@app.callback(
    Output("stored-data", "data"),
    Input("save-button", "n_clicks"),
    State("pubmed-id-store", "data"),
    [State(f"textarea-{i}", "value") for i in range(len(FIELDS))]
)
def save_progress(n_clicks, pubmed_id, *values):
    if n_clicks is None:
        return ''
    data = {field: value for field, value in zip(FIELDS, values)}
    with open(f"./data/saved_progress/save_in_progress_{pubmed_id}.json", "w") as f:
        json.dump(data, f)
    return data

@app.callback(
    Output("output", "children"),
    Input("submit-button", "n_clicks"),
    State("pubmed-id-store", "data"),
    [State(f"textarea-{i}", "value") for i in range(len(FIELDS))]
)
def submit(n_clicks, pubmed_id, *values):
    if n_clicks is None:
        return ""
    data = {field: value for field, value in zip(FIELDS, values)}
    df = pd.DataFrame([data])
    df.to_csv("./data/saved_progress/submitted_data.csv", index=False)
    requests.get('http://127.0.0.1:8050/shutdown')
    return "Data submitted successfully!"

@app.server.route('/get_data')
def get_data():
    if os.path.exists("./data/saved_progress/submitted_data.csv"):
        return flask.send_file("./data/saved_progress/submitted_data.csv", as_attachment=True)
    else:
        return flask.Response("No data found", status=404)

@app.server.route('/check_submission')
def check_submission():
    if os.path.exists("./data/saved_progress/submitted_data.csv"):
        return flask.jsonify({'complete': True})
    else:
        return flask.jsonify({'complete': False})

@app.server.route('/shutdown', methods=['GET'])
def shutdown():
    shutdown_func = flask.request.environ.get('werkzeug.server.shutdown')
    if shutdown_func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    shutdown_func()
    return "Server shutting down..."


def main(pubmed_id, url):
    app.layout.children = [
        html.Div(id='page-title'),
        dcc.Store(id='pubmed-id-store', data=pubmed_id),
        dcc.Store(id='url-store', data=url),
        # html.Div([
        #     dbc.Row([
        #         dbc.Col(dbc.Label(field), width=2),
        #         dbc.Col(dbc.Textarea(id=f"textarea-{i}", style={"width": "100%"}), width=10)
        #     ], className="mb-3") for i, field in enumerate(FIELDS)
        # ]),
        html.Div([
            dbc.Row([
                dbc.Col(dbc.Label(field), width=2),
                dbc.Col(
                    dbc.Textarea(
                        id=f"textarea-{i}",
                        style={"width": "100%", "height": "200px" if i >= len(FIELDS) - 2 else "35px"}
                    ),
                    width=10
                )
            ], className="mb-3") for i, field in enumerate(FIELDS)
        ]),
        dbc.Row([
            dbc.Col(dbc.Button("Save Progress", id="save-button", color="primary", className="mr-2"), width="auto"),
            dbc.Col(dbc.Button("Submit", id="submit-button", color="success"), width="auto")
        ], className="mb-3"),
        dcc.Store(id="stored-data"),
        html.Div(id="output")
    ]
    app.title = f"Article Review App - PubMed ID: {pubmed_id}"
    app.run_server(debug=True, use_reloader=False)

if __name__ == '__main__':
    pubmed_id = sys.argv[1] if len(sys.argv) > 1 else '1'
    url = sys.argv[2] if len(sys.argv) > 2 else f'https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}/'
    main(pubmed_id, url)
