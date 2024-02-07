import asyncio
import webbrowser
import threading
from os.path import dirname, exists
import websockets
from screens.screen import Screen
from werkzeug.serving import make_server
from flask import Flask, send_file, redirect


class FlaskThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.app = Flask("GPS")
        self.server = make_server("0.0.0.0", port=5000, app=self.app)
        ALLOWED_ASSET_TYPES = {"js": "application/js", "css": "text/css", "ico": "image/ico", "png": "image/png"}

        @self.app.route("/")
        def serve_index():
            content = open(FlaskThread._get_full_path("index.html"), "r").read()
            return content

        @self.app.route("/start")
        def serve_start_page():
            content = open(FlaskThread._get_full_path("starting_gps.html"), "r").read()
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

        @self.app.route("/assets/images/<path>")
        def serve_images(path):
            return redirect(f"/assets/{path}")

    @staticmethod
    def _get_full_path(path):
        return dirname(dirname(dirname(__file__))) + "/assets/web/" + path

    def run(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()


class WebsocketThread(threading.Thread):
    def __init__(self):
        super(WebsocketThread, self).__init__()
        self.message = ""

    async def _websocket_entrypoint(self):
        async def websocket_server(websocket: websockets.WebSocketServerProtocol):
            while True:
                if self.message != "":
                    await websocket.send(self.message)
                await asyncio.sleep(0.5)

        async with websockets.serve(websocket_server, "0.0.0.0", 5678):
            await asyncio.Future()

    def send(self, message):
        self.message = message

    def run(self):
        asyncio.run(self._websocket_entrypoint())

    def stop(self):
        asyncio.get_event_loop().stop()


class GPSScreen(Screen):
    def __init__(self, root, on_close=None):
        super().__init__(root, on_close)
        self.web_server = FlaskThread()
        self.websocket_server = WebsocketThread()
        self.root.withdraw()
        self.show()

    def show(self):
        self.visible = True
        self.web_server.start()
        self.websocket_server.start()
        webbrowser.open("http://localhost:5000/start")

    def add_result(self, packet):
        packet_length = len(packet)
        self.websocket_server.send(" ".join([str(data) for data in [packet[0], packet[packet_length-2], packet[packet_length-1]]]))

    def hide(self):
        # TODO: Send window close command
        self.visible = False

    def close(self):
        self.web_server.shutdown()
        self.websocket_server.stop()
