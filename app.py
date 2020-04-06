from flask import Flask, render_template
import folium as fol

app = Flask(__name__)


@app.route('/')
def index():
    base = fol.Map(location=[39.0457549, -76.6413], zoom_start=8)
    fol.GeoJson('maryland-congressional-districts.geojson').add_to(base)
    base.save('templates/base_map.html')
    return render_template('index.html')


@app.route('/base_map')
def base_map():
    return render_template('base_map.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0')
