import threading
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

from EasyDAG import EasyDAG, MultiprocessQueue, DAGNode
from src.EasyDAG_Web import DagEventBus, DagEventEmitter

from .dag import simple_process, process_data, aggregate
from .interface import WebInterface

# DAG setup
queue = MultiprocessQueue()
queue.register_message_handler("progress", print)
queue.register_message_handler("upload", print)

dag = EasyDAG(processes=4, mp_queue=queue)

dag.add_node(DAGNode("A", process_data, args=(10,)))
dag.add_node(DAGNode("B", process_data, args=(20,)))
dag.add_node(DAGNode("C", aggregate))
dag.add_node(DAGNode("D", simple_process))

dag.add_edge("A", "C")
dag.add_edge("B", "C")
dag.add_edge("D", "C")

bus = DagEventBus()
emitter = DagEventEmitter(bus)
queue.register_message_handler("emit", emitter.emit)
interface = WebInterface(dag, emitter)

app = FastAPI()

@app.get("/")
async def index():
    return HTMLResponse(open("./example/index.html").read())

@app.websocket("/ws/dag")
async def dag_ws(ws: WebSocket):
    await ws.accept()
    async def sender(event):
        await ws.send_json(event)
    bus.register_sender(sender)
    try:
        t = None
        while True:
            msg = await ws.receive_json()
            if msg["type"] == "run":
                threading.Thread(
                    target=interface.run_dag,
                    kwargs={"dag_id": "Your_ID"},
                    daemon=True
                ).start()
            elif msg["type"] == "cancel":
                interface.cancel_dag()
    finally:
        bus.unregister_sender(sender)
