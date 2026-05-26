from flask import Flask, render_template, request, send_file
import psycopg2

app = Flask(__name__)

# HOME PAGE
@app.route('/')
def home():

    # DATABASE CONNECTION
    conn = psycopg2.connect(

        host="localhost",
        database="zimstat_ea",
        user="postgres",
        password="taz.mataz"

    )

    cur = conn.cursor()

    # TOTAL EAs
    cur.execute('SELECT COUNT(*) FROM kwekwe_eas')
    total_eas = cur.fetchone()[0]

    # TOTAL IMAGES
    cur.execute('SELECT COUNT(*) FROM ea_images')
    total_images = cur.fetchone()[0]

    # TOTAL DISTRICTS
    cur.execute('SELECT COUNT(DISTINCT district) FROM kwekwe_eas')
    total_districts = cur.fetchone()[0]

    conn.close()

    return render_template(

        'index.html',

        total_eas=total_eas,
        total_images=total_images,
        total_districts=total_districts

    )

# SEARCH FUNCTION
@app.route('/search', methods=['POST'])
def search():

    ea_number = request.form['ea_number']

    # DATABASE CONNECTION
    conn = psycopg2.connect(

        host="localhost",
        database="zimstat_ea",
        user="postgres",
        password="taz.mataz"

    )

    cur = conn.cursor()

    # QUERY
    query = """

    SELECT

        k."ea number",
        k.province,
        k.district,
        k.ward,
        k.sector,
        k."local auth",
        p.population,
        p.households,
        i.image_path

    FROM kwekwe_eas k

    JOIN ea_images i
    ON k."ea number" = i.ea_number

    LEFT JOIN population_data p
ON TRIM(LEADING '0' FROM k."ea number"::text)
=
TRIM(LEADING '0' FROM p.id::text)

    WHERE k."ea number" = %s

    """

    cur.execute(query, (ea_number,))

    result = cur.fetchone()

    conn.close()

    return render_template(

        'result.html',

        result=result

    )

# DOWNLOAD IMAGE
@app.route('/download/<path:image_path>')
def download_image(image_path):

    try:

        return send_file(

            image_path,

            as_attachment=True

        )

    except Exception as e:

        return str(e)

# RUN APPLICATION
# DOWNLOAD SHAPEFILE
@app.route('/download_shapefile')
def download_shapefile():

    return send_file(

        'shapefiles/kwekwe_eas.zip',

        as_attachment=True

    )
# WEB GIS MAP
@app.route('/map')
def webmap():

    return render_template('map.html')
# REPORTS PAGE
@app.route('/reports')
def reports():

    return render_template('reports.html')
if __name__ == '__main__':

    app.run(

        host='0.0.0.0',
        port=5000,
        debug=True

    )
