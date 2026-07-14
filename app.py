from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename
import os


app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf"}

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


def is_pdf(filename):
    return os.path.splitext(filename.lower())[1] in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    files = []
    if os.path.exists(app.config["UPLOAD_FOLDER"]):
        files = sorted(
            [f for f in os.listdir(app.config["UPLOAD_FOLDER"]) if is_pdf(f)],
            reverse=True,
        )

    latest_file = files[0] if files else None
    return render_template("index.html", files=files, latest_file=latest_file)


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "파일을 선택해 주세요.", 400

    file = request.files["file"]
    if file.filename == "":
        return "파일명이 비어 있습니다.", 400

    if file and is_pdf(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        return redirect(url_for("index"))

    return "문서 파일만 업로드할 수 있습니다.", 400


@app.route("/uploads/<filename>")
def download_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
