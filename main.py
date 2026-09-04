import os
import pandas as pd
from flask import Flask, jsonify, request


# ==========================================
# FLASK APP
# ==========================================

app = Flask(
    __name__,
    static_folder="frontend",
    static_url_path=""
)


# ==========================================
# FRONTEND
# ==========================================

@app.route("/")
def index():
    return app.send_static_file("index.html")


# ==========================================
# LOAD ENERGY DATA
# ==========================================

def get_data():

    df = pd.read_csv(
        "data/energy_management_results.csv"
    )

    if "utc_timestamp" in df.columns:

        dt = pd.to_datetime(
            df["utc_timestamp"]
        )

        df["date"] = dt.dt.strftime(
            "%Y-%m-%d"
        )

        df["time"] = dt.dt.strftime(
            "%H:%M"
        )

    return df


# ==========================================
# ENERGY DATA
# ==========================================

@app.route("/api/energy")
def energy():

    try:

        df = get_data()

        return jsonify({
            "status": "success",
            "data": (
                df
                .fillna("")
                .to_dict(
                    orient="records"
                )
            )
        })

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ==========================================
# AVAILABLE DATES
# ==========================================

@app.route("/api/dates")
def dates():

    try:

        df = get_data()

        return jsonify({
            "status": "success",
            "count": df["date"].nunique(),
            "dates": (
                df["date"]
                .unique()
                .tolist()
            )
        })

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ==========================================
# ENERGY BY DATE
# ==========================================

@app.route("/api/energy/date")
def energy_date():

    try:

        date = request.args.get(
            "date"
        )

        df = get_data()

        df = df[
            df["date"] == date
        ]

        return jsonify({
            "status": "success",
            "data": (
                df
                .fillna("")
                .to_dict(
                    orient="records"
                )
            )
        })

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ==========================================
# ENERGY SUMMARY
# ==========================================

@app.route("/api/summary")
def summary():

    try:

        df = get_data()

        return jsonify({

            "status": "success",

            "records": len(df),

            "total_renewable": float(
                df["total_renewable"]
                .sum()
            ),

            "total_generator": float(
                df["generator"]
                .sum()
            ),

            "total_battery_used": float(
                df.get(
                    "battery_used",
                    pd.Series([0])
                ).sum()
            ),

            "total_flexible_reduction": float(
                df.get(
                    "flexible_reduction",
                    pd.Series([0])
                ).sum()
            )
        })

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ==========================================
# LATEST ENERGY DATA
# ==========================================

@app.route("/api/latest")
def latest():

    try:

        df = get_data()

        latest_row = (
            df.iloc[-1]
            .fillna("")
            .to_dict()
        )

        return jsonify({
            "status": "success",
            "data": [
                latest_row
            ]
        })

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ==========================================
# DIGITAL TWIN
# ==========================================

@app.route("/api/digital-twin")
def digital_twin():

    try:

        df = get_data()

        latest_row = (
            df.iloc[-1]
            .fillna("")
            .to_dict()
        )

        twin = {

            "timestamp":
                latest_row.get(
                    "utc_timestamp",
                    ""
                ),

            "temperature":
                latest_row.get(
                    "temperature",
                    0
                ),

            "solar":
                latest_row.get(
                    "solar_prediction",
                    latest_row.get(
                        "solar_power",
                        0
                    )
                ),

            "wind":
                latest_row.get(
                    "wind_prediction",
                    latest_row.get(
                        "wind_power",
                        0
                    )
                ),

            "load":
                latest_row.get(
                    "load_prediction",
                    latest_row.get(
                        "load_power",
                        0
                    )
                ),

            "battery_soc":
                latest_row.get(
                    "battery_soc",
                    0
                ),

            "generator":
                latest_row.get(
                    "generator",
                    0
                ),

            "battery_used":
                latest_row.get(
                    "battery_used",
                    0
                ),

            "battery_charged":
                latest_row.get(
                    "battery_charged",
                    0
                ),

            "flexible_reduction":
                latest_row.get(
                    "flexible_reduction",
                    0
                ),

            "action":
                latest_row.get(
                    "action",
                    ""
                )
        }

        return jsonify({
            "status": "success",
            "digital_twin": twin
        })

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ==========================================
# CORS
# ==========================================

@app.after_request
def add_cors_headers(response):

    response.headers[
        "Access-Control-Allow-Origin"
    ] = "*"

    response.headers[
        "Access-Control-Allow-Headers"
    ] = "Content-Type"

    response.headers[
        "Access-Control-Allow-Methods"
    ] = "GET, POST, OPTIONS"

    return response


# ==========================================
# START SERVER
# ==========================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            8000
        )
    )

    print(
        "\n========================================"
    )

    print(
        "   SMART AI ENERGY MANAGEMENT SYSTEM"
    )

    print(
        "========================================"
    )

    print(
        f"Starting Flask server on port {port}..."
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )