from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

import traceback

from dto.string_dto import StringDto
from error.app_warning import AppWarning
from web.events.app_events import EAppEvents
from dto.response_dto import ResponseDto, EStatusCode

flask_app = Flask(__name__)

CORS(flask_app)

flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///demo.db"
flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


#db_app.init_app(flask_app)

# Create SocketIO server (using asyncio) , async_mode="asgi"
socketio = SocketIO(flask_app, cors_allowed_origins="*")

@socketio.on_error_default
def global_socketio_error_handler(e):
    print("Uncaught SocketIO exception: ", e)
    traceback.print_exc()
    return ResponseDto(status_code=EStatusCode.ERROR, data=StringDto("Internal server error. Please try again later.")).to_dict()

def handle_global_warning(event: AppWarning):
    print("Global Warning: ", event)
    socketio.emit(EAppEvents.WARNING, event.to_dict())





