from flask import Flask, render_template, request, send_file, jsonify
import psycopg2

app = Flask(__name__)

# =========================
# DATABASE CONNECTION
# =========================

DATABASE_URL = "postgresql://zimstat_user:4ylHgll26POSbsqHLunNM48roLTOyKse@dpg-d8akaa0js32c7399ii70-a.virginia-postgres.render.com/zimstat_db"

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

# =========================
# HOME PAGE
# =========================

@app.route('/')
def index():
    return render_template('index.html')

# =========================
# MAP PAGE
# =========================

@app.route('/map')
def map_view():
    return render_template('map.html')

# =========================
# SINGLE EA GEOJSON (MAP LAYER)
# =========================

@app.route("/map/<geocode>")
def get_ea(geocode):

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        query = """
        SELECT json_build_object(
            'type', 'FeatureCollection',
            'features', json_agg(
                json_build_object(
                    'type', 'Feature',
                    'geometry', ST_AsGeoJSON(geom)::json,
                    'properties', json_build_object(
                        'geocode', geocode,
                        'ea_number', ea_number,
                        'population', population,
                        'households', households
                    )
                )
            )
        )
        FROM population_data
        WHERE geocode = %s;
        """

        cur.execute(query, (geocode,))
        result = cur.fetchone()[0]

        cur.close()
        conn.close()

        return jsonify(result)

    except Exception as e:
        print("MAP ERROR:", e)
        return jsonify({"error": str(e)}), 500


# =========================
# SEARCH (EA NUMBER BASED)
# =========================

@app.route('/search', methods=['POST'])
def search():

    try:
        ea_number = request.form.get('ea_number')

        if not ea_number:
            return "EA number is required", 400

        conn = get_db_connection()
        cur = conn.cursor()

        query = """
        SELECT
            geocode,
            ea_number,
            population,
            households
        FROM population_data
        WHERE ea_number = %s;
        """

        cur.execute(query, (ea_number,))
        result = cur.fetchone()

        cur.close()
        conn.close()

        # If nothing found
        if result is None:
            return render_template("result.html", result=None)

        return render_template("result.html", result=result)

    except Exception as e:
        print("SEARCH ERROR:", e)
        return f"Server Error: {str(e)}", 500


# =========================
# REPORTS PAGE
# =========================

@app.route('/reports')
def reports():

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM population_data")
        total_eas = cur.fetchone()[0]

        cur.execute("SELECT SUM(population) FROM population_data")
        total_population = cur.fetchone()[0] or 0

        cur.execute("SELECT SUM(households) FROM population_data")
        total_households = cur.fetchone()[0] or 0

        cur.close()
        conn.close()

        return render_template(
            "reports.html",
            total_eas=total_eas,
            total_population=total_population,
            total_households=total_households
        )

    except Exception as e:
        print("REPORTS ERROR:", e)
        return f"Server Error: {str(e)}", 500


# =========================
# DOWNLOAD SHAPEFILE
# =========================

@app.route('/download_shapefile')
def download_shapefile():
    try:
        shapefile_path = "static/shapefiles/kwekwe_eas.zip"
        return send_file(shapefile_path, as_attachment=True)
    except Exception as e:
        print("DOWNLOAD ERROR:", e)
        return f"File error: {str(e)}", 500


# =========================
# RUN APP
# =========================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
