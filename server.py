
from __future__ import print_function

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

import logging
import os
import re
import sys
import time
import pprint
from datetime import datetime

import mimetypes
from flask import Response, render_template
from flask import Flask
from flask import send_file
from flask import request
from flask import session

LOG = logging.getLogger(__name__)
app = Flask(__name__)

VIDEO_PATH = '/video'
video_dir='/home/jose/Desktop/SampleFlask/py-flask-video-stream-master/video'
MB = 1 << 20
BUFF_SIZE = 1 * MB

@app.route('/')
def index():
    video_files = [f for f in os.listdir(video_dir) if f.endswith('mp4')]
    video_files_number = len(video_files)
    return render_template("index.html",
                        title = 'MP4',
                        video_files_number = video_files_number,
                        video_files = video_files)
@app.route('/VideoRender/<fileName>')
def home(fileName):
    LOG.info('Rendering play page for file:{0}'.format(fileName))
    response = render_template(
        'play.html', 
        time=str(datetime.now()),
        video=VIDEO_PATH, file=fileName
    )
    return response

def partial_response(path, start, end=None):
    LOG.info('Requested: %s, %s', start, end)
    file_size = os.path.getsize(path)

    # Determine (end, length)
    if end is None:
        end = start + BUFF_SIZE - 1
    end = min(end, file_size - 1)
    end = min(end, start + BUFF_SIZE - 1)
    length = end - start + 1

    # Read file
    with open(path, 'rb') as fd:
        fd.seek(start)
        bytes = fd.read(length)
    assert len(bytes) == length

    response = Response(
        bytes,
        206,
        mimetype=mimetypes.guess_type(path)[0],
        direct_passthrough=True,
    )
    response.headers.add(
        'Content-Range', 'bytes {0}-{1}/{2}'.format(
            start, end, file_size,
        ),
    )
    response.headers.add(
        'Accept-Ranges', 'bytes'
    )
    LOG.info('Response: %s', response)
    LOG.info('Response: %s', response.headers)
    return response

def get_range(request):
    range = request.headers.get('Range')
    LOG.info('Requested: %s', range)
    m = re.match('bytes=(?P<start>\d+)-(?P<end>\d+)?', range)
    if m:
        start = m.group('start')
        end = m.group('end')
        start = int(start)
        if end is not None:
            end = int(end)
        return start, end
    else:
        return 0, None
    
@app.route('/video')
def video():
    if 'file_name' in request.args:
        FileName = request.args['file_name']
        path = 'video/'+FileName
        start, end = get_range(request)
        return partial_response(path, start, end)
    else:
	LOG.info('ERROR Did not receive any fileName for streaming')
	return 'SORRY NO FILE Name Received in file_name using get'

@app.route('/video/<name>')
def video1(name):
    path = 'video/'+name
    start, end = get_range(request)
    return partial_response(path, start, end)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    HOST = '192.168.1.9'
    #http_server = HTTPServer(WSGIContainer(app))
    #http_server.listen(1000)
    #IOLoop.instance().start()

    # Standalone
    app.run(host=HOST, port=1000, debug=True)




