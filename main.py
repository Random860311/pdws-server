import eventlet
eventlet.monkey_patch()


from flask_socketio import SocketIO
from flask import Flask

from core.di.di_container import container



from pathlib import Path
import ssl

import di_config


if __name__ == "__main__":
    print("[MAIN] Starting...")
    # cert_path = Path("web/certs/cert.pem")
    # key_path = Path("web/certs/key.pem")
    cert_path = Path("web/certs/cert_192.168.11.143.pem")
    key_path = Path("web/certs/key_192.168.11.143.pem")

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(cert_path, key_path)

    station = di_config.create_di()
    socketio = container.resolve(SocketIO)
    flask_app = container.resolve(Flask)

    # ---- SSL setup (HTTPS/WSS) ----
    has_tls = cert_path.exists() and key_path.exists()
    if has_tls:
        print(f"[TLS] Using cert: {cert_path} and key: {key_path}")
    else:
        if not cert_path.exists():
            print(f"[TLS] Missing certificate file: {cert_path}")
        if not key_path.exists():
            print(f"[TLS] Missing private key file: {key_path}")
        print("[TLS] TLS disabled (falling back to HTTP).")

    # Detect the async mode chosen by Flask-SocketIO (eventlet, gevent, threading, etc.)
    async_mode = getattr(socketio, "async_mode", None)
    print(f"[SocketIO] async_mode={async_mode}")

    run_kwargs = dict(
        host="0.0.0.0",
        port=8443,
        debug=True,
        use_reloader=False,  # optional: disable duplicate startup logs
    )

    try:
        station.start()
        if has_tls:
            if async_mode in ("eventlet", "gevent"):
                # Eventlet/Gevent expect certfile/keyfile (NOT ssl_context)
                socketio.run(
                    flask_app,
                    # certfile=str(cert_path),
                    # keyfile=str(key_path),
                    **run_kwargs,
                )
            else:
                # Werkzeug/threading: ssl_context is supported
                ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                ssl_ctx.load_cert_chain(certfile=str(cert_path), keyfile=str(key_path))
                socketio.run(
                    flask_app,
                    ssl_context=ssl_ctx,
                    **run_kwargs,
                )
        else:
            # No TLS → plain HTTP
            socketio.run(flask_app, **run_kwargs)

    except Exception as e:
        print(f"[TLS] Failed to start with TLS: {e}. Falling back to HTTP.")
        socketio.run(flask_app, **run_kwargs)