import os
from flask import Flask, request, send_file, abort

app = Flask(__name__)
REPORT_DIR = "/srv/reports"


@app.get("/report")
def download_report():
    name = request.args.get("name")
    if not name or not name.endswith(".pdf"):
        abort(400)
    path = os.path.join(REPORT_DIR, name)
    return send_file(path)
