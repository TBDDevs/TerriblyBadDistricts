from flask import Flask, render_template
import dem_gen


app = Flask(__name__)


@app.before_first_request
def start():
    dem_gen.generate()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/democratic_map')
def dem_map():
    return render_template('democratic_map.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0')
