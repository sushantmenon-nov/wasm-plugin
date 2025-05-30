from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import extism
import json
from pathlib import Path
import hashlib
import shutil

app = FastAPI()


# Request model
class EvalRequest(BaseModel):
    expression: str


@app.post("/evaluate")
async def evaluate(data: EvalRequest):
    expression = data.expression
    try:
        shutil.copy("wasi_eval.wasm", "/tmp/wasi_eval.wasm")
        wasm = Path("/tmp/wasi_eval.wasm").read_bytes()
        hash = hashlib.sha256(wasm).hexdigest()
        manifest = {"wasm": [{"data": wasm, "hash": hash}]}

        with extism.Plugin(manifest, wasi=True) as plugin:
            result = plugin.call(
                "exec",
                json.dumps({"expression": expression, "envInput": {}}),
                parse=lambda output: json.loads(bytes(output).decode("utf-8")),
            )

        return {"result": result}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/")
def home():
    return {"message": "Extism API Running!"}
