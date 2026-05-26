from flask import Flask, render_template, request, send_file
import psycopg2
import os

app = Flask(__name__)

# =========================
# RENDER POSTGRESQL CONNECTION
# =========================

DATABASE_URL = "postgresql://zimstat_user:4ylHgll26POSbsqHLunNM48roLTOyKse@dpg-d8akaa0js32c7399ii70-a.virginia-postgres.render.com/zimstat_db"

conn = psycopg2.connect(DATABASE_URL)

# =========================
# HOME PAGE
# =========================

@app.route("/map/<geocode>")
def get_ea(geocode):

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

    return jsonify(result)

# =========================
# SEARCH PAGE
# =========================
@app.route('/search', methods=['POST'])
def search():

    geocode = request.form['ea_number']

    cur = conn.cursor()

    query = """

    SELECT

        geocode,
        ea_number,
        population,
        households

    FROM population_data

    WHERE geocode = %s

    """

    cur.execute(query, (geocode,))

    result = cur.fetchone()

    cur.close()

    return render_template(
        'result.html',
        result=result
    )


# =========================
# GIS MAP PAGE
# =========================

@app.route('/map')
def map_view():

    return render_template('map.html')

# =========================
# REPORTS PAGE
# =========================

@app.route('/reports')
def reports():

    return render_template('reports.html')

# =========================
# DOWNLOAD SHAPEFILE
# =========================

@app.route('/download_shapefile')
def download_shapefile():

    shapefile_path = "static/shapefiles/kwekwe_eas.zip"

    return send_file(
        shapefile_path,
        as_attachment=True
    )

# =========================
# RUN APPLICATION
# =========================

if __name__ == '__main__':

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
