from flask import Flask, jsonify, redirect, render_template, request, send_from_directory, url_for
import os


app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config["UPLOAD_FOLDER"] = os.path.join(BASE_DIR, "uploads")
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf"}

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


def is_pdf(filename):
    return os.path.splitext(filename.lower())[1] in ALLOWED_EXTENSIONS


def clean_filename(filename):
    return filename.replace("\\", "/").split("/")[-1].strip()


def unique_filename(filename):
    name, extension = os.path.splitext(filename)
    candidate = filename
    counter = 2

    while os.path.exists(os.path.join(app.config["UPLOAD_FOLDER"], candidate)):
        candidate = f"{name}_{counter}{extension}"
        counter += 1

    return candidate


def get_report_files():
    if not os.path.exists(app.config["UPLOAD_FOLDER"]):
        return []

    return sorted(
        [filename for filename in os.listdir(app.config["UPLOAD_FOLDER"]) if is_pdf(filename)],
        reverse=True,
    )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/files")
def files_api():
    files = get_report_files()
    return jsonify({"files": files})


@app.route("/upload", methods=["POST"])
def upload_file():
    selected_files = request.files.getlist("files") or request.files.getlist("file")
    selected_files = [file for file in selected_files if file and file.filename]

    if not selected_files:
        return "파일을 선택해 주세요.", 400

    cleaned_files = []
    for file in selected_files:
        filename = clean_filename(file.filename)
        if not filename:
            return "파일명이 비어 있습니다.", 400
        if not is_pdf(filename):
            return "문서 파일만 업로드할 수 있습니다.", 400
        cleaned_files.append((file, filename))

    for file, filename in cleaned_files:
        save_name = unique_filename(filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], save_name))

    return redirect(url_for("index"))


@app.route("/uploads/<filename>")
def download_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
