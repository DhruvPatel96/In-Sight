# server.py
from flask import Flask, request
import os
import multiprocessing
from sender import process_video
from receiver import receive_results

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        print('Uploded')
        filename = file.filename
        file_path = os.path.join('uploads', filename)
        file.save(file_path)
        queue = multiprocessing.Queue()
        sender_process = multiprocessing.Process(target=process_video, args=(queue, file_path))
        receiver_process = multiprocessing.Process(target=receive_results, args=(queue,))
        sender_process.start()
        receiver_process.start()
        sender_process.join()
        receiver_process.join()
        return 'File processed successfully'

if __name__ == '__main__':
    app.run(debug=True)
