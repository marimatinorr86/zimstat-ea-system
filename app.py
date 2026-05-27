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
# HOME MAP PAGE
# =========================

@app.route('/map')
def map_view():
    return render_template('map.html')

# =========================
# SINGLE EA MAP (FILTERED POLYGON)
# =========================

@app.route("/map/<geocode>")
def get_ea(geocode):

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT json_build_object(
        'type', 'FeatureCollection',
        'features', json_agg(
            json_build_object(
                'type', 'Feature',
                'geometry', ST_AsGeoJSON(geom)::json,
                'properties', json_build_object(
                    'geocode', geocode,
                    'ea_number', ea_number
                )
            )
        )
    )
    FROM population_data
    WHERE geocode = %s;
    """

    cursor.execute(query, (geocode,))
    result = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return jsonify(result)

# =========================
# SEARCH PAGE (FIXED)
# =========================

@app.route('/search', methods=['POST'])
def search():

    geocode = request.form.get('geocode')  # FIXED

    if not geocode:
        return "No geocode provided", 400

    conn = get_db_connection()
    cur = conn.cursor()

    query = """
    SELECT
        geocode,
        ea_number,
        population,
        households
    FROM population_data
    WHERE geocode = %s;
    """

    cur.execute(query, (geocode,))
    result = cur.fetchone()

    cur.close()
    conn.close()

    if result is None:
        return render_template("result.html", result=None)

    return render_template('result.html', result=result)

# =========================
# REPORTS PAGE
# =========================

@app.route('/reports')
def reports():

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM population_data")
    total_eas = cur.fetchone()[0]

    cur.execute("SELECT SUM(population) FROM population_data")
    total_population = cur.fetchone()[0]

    cur.execute("SELECT SUM(households) FROM population_data")
    total_households = cur.fetchone()[0]

    cur.close()
    conn.close()

    return render_template(
        'reports.html',
        total_eas=total_eas,
        total_population=total_population,
        total_households=total_households
    )

# =========================
# DOWNLOAD SHAPEFILE
# =========================

@app.route('/download_shapefile')
def download_shapefile():
    shapefile_path = "static/shapefiles/kwekwe_eas.zip"
    return send_file(shapefile_path, as_attachment=True)

# =========================
# RUN APP
# =========================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
