from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
import boto3


app = Flask(__name__)

# Configure Object Storage
ibm_cos = boto3.client(
    "s3",
    aws_access_key_id='<your-access-key>',
    aws_secret_access_key='<your-secret-key>',
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
