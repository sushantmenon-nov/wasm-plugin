from flask import Flask, request, jsonify
import extism
import json
from pathlib import Path
import hashlib
import shutil

app = Flask(__name__)

@app.route("/evaluate", methods=["POST"])
def evaluate():
    expression = request.json.get("expression")
    shutil.copy("wasi_eval.wasm", "/tmp/wasi_eval.wasm")
    wasm = Path("/tmp/wasi_eval.wasm").read_bytes()
    hash = hashlib.sha256(wasm).hexdigest()
    manifest = {"wasm": [{"data": wasm, "hash": hash}]}
    try:
        with extism.Plugin(manifest, wasi=True) as plugin:
            result = plugin.call("exec", json.dumps({"expression": expression, "envInput": {}}),
                                 parse=lambda output: json.loads(bytes(output).decode("utf-8")))
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    return "Extism API Running!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
