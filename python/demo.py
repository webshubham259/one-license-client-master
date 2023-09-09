from one_license_client import OneLicenceClient
from flask import Flask, jsonify
import time
import threading

app = Flask(__name__)


@app.route('/consume')
def hello_world():
    try:
        license.consume()
        # Import your business logic here
        return 'success'
    except Exception as err:
        return jsonify({"error": str(err)})


if __name__ == '__main__':
    global license
    license = OneLicenceClient({
        "server_url": "http://localhost:4000/api/v1",
        "product_id": "5edb10fecc150913cb7640f6",
        "version_id": "5edb1105cc150913cb7640f7",
        "license_id": "5edb1264cc150913cb7640f8",
    })
    loopThread = threading.Thread(
        target=license.sync_at_interval, args=())
    loopThread.start()
    # Ensure that use_reloader is set to False, else reloader starts
    # its own thread which leads to 2 separate connection IDs. The client
    # will crash if sync happens with different connection IDs
    app.run(port=8002, debug=True, use_reloader=False)
    loopThread.join()
