from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
import ibm_boto3
from ibm_botocore.client import Config

app = Flask(__name__)

# Configure Object Storage
cos_client = ibm_boto3.client(
    "s3",
    ibm_api_key_id="<your_api_key_id>",
    ibm_service_instance_id="<your_service_instance_id>",
    ibm_auth_endpoint="https://iam.cloud.ibm.com/identity/token",
    config=Config(signature_version="oauth"),
    endpoint_url="<cos_endpoint_url>"
)

# Configure SQLite Database
db = sqlite3.connect("media_streaming.db")
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS media (id INTEGER PRIMARY KEY, title TEXT, media_url TEXT)")
db.commit()
db.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_media():
    title = request.form.get('title')
    file = request.files['file']
    
    if title and file:
        # Save metadata to the database
        db = sqlite3.connect("media_streaming.db")
        cursor = db.cursor()
        cursor.execute("INSERT INTO media (title, media_url) VALUES (?, ?)", (title, ""))
        db.commit()
        media_id = cursor.lastrowid
        db.close()

        # Upload media file to IBM Cloud Object Storage
        file_data = file.read()
        media_url = f"media/{media_id}_{file.filename}"
        cos_client.upload_fileobj(file_data, "<your_bucket_name>", media_url)
        
        # Update the media_url in the database
        db = sqlite3.connect("media_streaming.db")
        cursor = db.cursor()
        cursor.execute("UPDATE media SET media_url = ? WHERE id = ?", (media_url, media_id))
        db.commit()
        db.close()

        return redirect(url_for('home'))
    return "Media upload failed."

if __name__ == '__main__':
    app.run(debug=True)
