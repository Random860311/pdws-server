import functools
import traceback
from abc import ABC, abstractmethod
from typing import Optional, Callable

from flask_socketio import SocketIO

from core.dispatcher.event_dispatcher_protocol import EventDispatcherProtocol
from core.serializable_protocol import SerializableProtocol
from dto.string_dto import StringDto
from error.app_warning import AppWarning
from error.base_error import BaseError
from dto.response_dto import ResponseDto, EStatusCode
from web.events.web_event_protocol import WebEventProtocol


class BaseHandler(ABC):
    def __init__(self, dispatcher: EventDispatcherProtocol, socketio: SocketIO):
        self.__dispatcher = dispatcher
        self.__socketio = socketio

    @property
    def socketio(self):
        return self.__socketio

    @property
    def dispatcher(self):
        return self.__dispatcher

    def emit_event(self, event: WebEventProtocol):
        try:
            # data = BaseHandler.to_payload(event.data)
            # print("Emitting event: ", str(event.key), data)
            self.socketio.emit(event.event_name, event.data.to_dict())
        except Exception as e:
            print("Error in _emit_event: ", str(e), str(event.event_name), event.data)

    @staticmethod
    def ok(data: Optional[SerializableProtocol] = None) -> SerializableProtocol:
        return ResponseDto(status_code=EStatusCode.SUCCESS, data=data)

    @staticmethod
    def fail(data: Optional[SerializableProtocol] = None, status_code: EStatusCode = EStatusCode.ERROR) -> SerializableProtocol:
        return ResponseDto(status_code=status_code, data=data)

    def log_error(self, where: str, err: Exception, *, bad_request: bool = False):
        prefix = "[BadRequest]" if bad_request else "[Error]"
        print(f"{prefix} {self.__class__.__name__}:{where}: {err}")
        traceback.print_exc()

    @staticmethod
    def safe(fn: Optional[Callable] = None, *, error_message: Optional[str] = None):
        """
        Decorator for handler methods.
        """

        def _decorator(func: Callable):
            @functools.wraps(func)
            def _wrapped(self: "BaseHandler", *args, **kwargs):
                # Use function name as the action label
                action_label = getattr(func, "__qualname__", func.__name__)
                try:
                    return func(self, *args, **kwargs)
                except AppWarning as aw:
                    self.log_error(action_label, aw)
                    return self.fail(aw, status_code=aw.code)
                except BaseError as be:
                    self.log_error(action_label, be)
                    return self.fail(be)
                except ValueError as ve:
                    self.log_error(action_label, ve, bad_request=True)
                    return self.fail(StringDto(str(ve)))
                except Exception as e:
                    self.log_error(action_label, e)
                    return self.fail(StringDto(error_message if error_message else f"Error while trying to {func.__name__}."))

            return _wrapped

        # Support @BaseHandler.safe and @BaseHandler.safe()
        return _decorator if fn is None else _decorator(fn)

    @abstractmethod
    def register(self):
        pass