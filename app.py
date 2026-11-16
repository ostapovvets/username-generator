from flask import Flask, render_template, request, redirect, jsonify

from helpers import run, get_models, LIMITS
from generator import groups
from platforms import PLATFORMS

app = Flask(__name__)

@app.route("/", methods = ["GET", "POST"])
def index():
    return render_template("index.html", models = get_models(), styles = list(groups.keys()), platforms = list(PLATFORMS.keys()), limits = LIMITS)

@app.route("/generate", methods = ["POST"])
def generate():
    result = run(
        style = request.form.get("style"),
        platform = request.form.get("platform"),
        model = request.form.get("model"),
        count = request.form.get("count"),
        examples_count = request.form.get("examples"),
        temperature = request.form.get("temperature")
    )
    return jsonify(result)
