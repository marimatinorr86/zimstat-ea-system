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

@app.route('/')
def home():

    cur = conn.cursor()

    # TOTAL EAs
    cur.execute("SELECT COUNT(*) FROM population_data")
    total_eas = cur.fetchone()[0]

    # TOTAL IMAGES
    cur.execute("SELECT COUNT(*) FROM ea_images")
    total_images = cur.fetchone()[0]

    # TOTAL DISTRICTS
    total_districts = 1

    cur.close()

    return render_template(
        'index.html',
        total_eas=total_eas,
        total_images=total_images,
        total_districts=total_districts
    )

# =========================
# SEARCH PAGE
# =========================

@app.route('/search', methods=['POST'])
def search():

    ea_number = request.form['ea_number']

    cur = conn.cursor()

    query = """

SELECT

    p.ea_number,
    p.population,
    p.households,
    i.image_path

FROM population_data p

LEFT JOIN ea_images i
ON p.ea_number = i.ea_number

WHERE p.ea_number = %s

"""
    cur.execute(query, (ea_number,))

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
