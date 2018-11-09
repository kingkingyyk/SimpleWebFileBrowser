from gevent import monkey
monkey.patch_all()

import os, socket, humanize, sys, traceback, mimetypes, platform, string
from gevent.pywsgi import WSGIServer
from flask import Flask, request, render_template, send_from_directory
from flask_httpauth import HTTPBasicAuth
from pathlib import Path
from datetime import datetime

mimetypes.init()


def get_extensions_for_type(type):
    return [x for x in mimetypes.types_map if mimetypes.types_map[x].split('/')[0] == type]


non_attachment = get_extensions_for_type('video') + \
                 get_extensions_for_type('audio') + \
                 get_extensions_for_type('image') + \
                 ['.pdf', '.html', '.log', '.json', '.txt']

html_media = {'.mp4': 'video/mp4', '.mkv': 'video/mp4',
              '.webm': 'video/webm', '.ogg': 'video/ogg',
              '.mp3': 'audio/mpeg', '.wav': 'audio/wav',
              'm4a': 'audio/mp4'}

app = Flask(__name__)
auth = HTTPBasicAuth()
login_dict = {'admin': 'admin'}


class File(object):

    def __init__(self, path):
        self.path = path
        self.name = os.path.basename(path) if len(os.path.basename(path)) > 0 else path
        self.is_file = os.path.isfile(path)
        self.size = humanize.naturalsize(os.path.getsize(path)) if self.is_file else '--'
        try:
            self.time = datetime.fromtimestamp(os.path.getmtime(path))
        except:
            self.time = datetime.fromtimestamp(0)
        ext = [x for x in html_media.keys() if self.path.endswith(x)]
        self.playable = os.path.isfile(path) and len(ext) > 0
        self.playable_tag = html_media[ext[0]] if self.playable else None


@auth.get_password
def get_pw(username):
    return login_dict.get(username, None)


@app.route('/', methods=['GET'])
@auth.login_required
def index():
    path = request.args.get('path', '')
    force_attachment = request.args.get('download', 'false') == 'true'
    try:
        if path == '':
            root_drives = []
            if platform.system() == 'Windows':
                from ctypes import windll
                bitmask = windll.kernel32.GetLogicalDrives()
                for letter in string.ascii_uppercase:
                    if bitmask & 1:
                        root_drives.append(letter)
                    bitmask >>= 1
                root_drives = [x + ':' for x in root_drives]
            elif platform.system() == 'Linux':
                root_drives = ['/' + x for x in os.listdir('/')]
            return render_template('browse.html',
                                   hostname=socket.gethostname(),
                                   path='',
                                   files=[File(x) for x in root_drives])
        elif os.path.isdir(path):
            route_list = list(Path(path).parts)
            if not route_list[0].endswith(os.path.sep):
                route_list[0] += os.path.sep
            for i in range(1, len(route_list)):
                route_list[i] = os.path.join(route_list[i-1], route_list[i])
            return render_template('browse.html',
                                   hostname=socket.gethostname(),
                                   path=path,
                                   routes=[File(x) for x in route_list],
                                   files=[File(os.path.join(path, x)) for x in os.listdir(path)])
        else:
            filename = os.path.basename(path)
            return send_from_directory(os.path.abspath(os.path.join(path, os.pardir)),
                                       filename,
                                       as_attachment=len([x for x in non_attachment if filename.lower().endswith(x)]) == 0 or force_attachment,
                                       conditional=True)
    except:
        return render_template('error.html',
                               hostname=socket.gethostname(),
                               error=str(traceback.format_exc()))


def main():
    server = WSGIServer(('0.0.0.0', port), app)
    server.serve_forever()

port = int(sys.argv[1])
login_dict = {sys.argv[2]: sys.argv[3]}
main()
