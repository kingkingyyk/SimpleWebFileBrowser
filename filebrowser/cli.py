from gevent import monkey
monkey.patch_all()

import os, socket, humanize, sys, traceback
from gevent.pywsgi import WSGIServer
from flask import Flask, request, render_template, send_from_directory, abort
from pathlib import Path
from datetime import datetime

app = Flask(__name__)


class File(object):

    def __init__(self, path):
        self.path = path
        while path[-1] == os.path.sep and len(path) > 1:
            path = path[:-1]
        self.name = os.path.basename(path) if len(os.path.basename(path)) > 0 else path
        self.size = humanize.naturalsize(os.path.getsize(path)) if os.path.isfile(path) else '--'
        try:
            self.time = datetime.fromtimestamp(os.path.getmtime(path))
        except:
            self.time = datetime.fromtimestamp(0)


@app.route('/', methods=['GET'])
def index():
    path = request.args.get('path', str(Path.home()))
    try:
        if os.path.isdir(path):
            route_list = [x for x in path.split(os.path.sep) if len(x.strip()) > 0]
            if len(route_list) == 0:
                route_list.append(os.path.sep)
            if path[0] == os.path.sep and route_list[0][0] != os.path.sep:
                route_list[0] = os.path.sep + route_list[0]
            for i in range(1, len(route_list)):
                route_list[i] = route_list[i-1] + os.path.sep + route_list[i]
            if route_list[0][-1] != os.path.sep:
                route_list[0] += os.path.sep
            return render_template('browse.html',
                                   hostname=socket.gethostname(),
                                   path=path,
                                   routes=[File(x) for x in route_list],
                                   files=[File(os.path.join(path, x)) for x in os.listdir(path)])
        else:
            filename = os.path.basename(path)
            return send_from_directory(os.path.abspath(os.path.join(path, os.pardir)),
                                       filename,
                                       as_attachment=True,
                                       conditional=True)
    except:
        return render_template('error.html',
                               hostname=socket.gethostname(),
                               error=str(traceback.format_exc()))


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 80
    server = WSGIServer(('0.0.0.0', port), app)
    server.serve_forever()

main()