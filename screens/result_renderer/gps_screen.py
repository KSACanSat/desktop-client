import threading
from os.path import dirname, exists
from screens.screen import Screen
from werkzeug.serving import make_server
from flask import Flask, send_file, render_template


class FlaskThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.app = Flask("GPS")
        self.server = make_server("0.0.0.0", port=5000, app=self.app)
        ALLOWED_ASSET_TYPES = {"js": "application/js", "css": "text/css", "ico": "image/ico"}

        @self.app.route("/")
        def serve_index():
            content = open(FlaskThread._get_full_path("index.html"), "r").read()
            return content

        @self.app.route("/assets/<path>")
        def serve_assets(path):
            asset_type = path.split(".")[-1]
            if asset_type not in ALLOWED_ASSET_TYPES.keys():
                return "This asset type is not allowed!", 400
            full_path = FlaskThread._get_full_path(path)
            if not exists(full_path):
                return "Asset not found!", 404
            return send_file(full_path, ALLOWED_ASSET_TYPES[asset_type])

    @staticmethod
    def _get_full_path(path):
        return dirname(dirname(dirname(__file__)))+"/assets/web/"+path

    def run(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()


class GPSScreen(Screen):
    def __init__(self, root, on_close=None):
        super().__init__(root, on_close)
        self.server = FlaskThread()
        self.root.withdraw()
        self.show()

    def show(self):
        self.visible = True
        self.server.start()

    def hide(self):
        # TODO: Send window close command
        self.visible = False

    def close(self):
        self.server.shutdown()
