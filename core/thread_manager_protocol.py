from typing import Protocol, Any

from flask_socketio import SocketIO
import traceback



class ThreadManagerProtocol(Protocol):
    def start_background_task(self, target, *args, **kwargs) -> Any:
        """Start a background task using the appropriate async model.

        This is a utility function that applications can use to start a
        background task using the method that is compatible with the
        selected async mode.

        :param target: the target function to execute.
        :param args: arguments to pass to the function.
        :param kwargs: keyword arguments to pass to the function.

        This function returns an object that represents the background task,
        on which the ``join()`` method can be invoked to wait for the task to
        complete.
        """
        pass

class ThreadManager(ThreadManagerProtocol):
    def __init__(self, socketio: SocketIO):
        self.__socketio = socketio

    def start_background_task(self, target, *args, **kwargs):
        try:
            return self.__socketio.start_background_task(target, *args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            print(f"Error starting background task: {e}")
            raise