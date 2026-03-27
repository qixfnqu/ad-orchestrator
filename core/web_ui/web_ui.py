from flask import Flask, render_template
from werkzeug.serving import make_server
import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)  # solo errores
app = Flask(__name__, static_folder="static", template_folder="templates")
session = None
_server = None

@app.route("/")
def index():
    global session
    return render_template("index.html", session=session)

class WebUIThread:
    def __init__(self, current_session, host="0.0.0.0", port=5000, debug=False, threaded=False):
        global session
        session = current_session
        self.host = host
        self.port = port
        self.server = make_server(self.host, self.port, app)
        self.ctx = app.app_context()
        self.ctx.push()
        self.thread = None

    def start(self):
        from threading import Thread
        self.thread = Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.server.shutdown()
        if self.thread:
            self.thread.join()