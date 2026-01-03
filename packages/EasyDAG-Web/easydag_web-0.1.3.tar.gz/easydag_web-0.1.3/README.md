# EasyDAG Web

**EasyDAG Web** is an optional companion package for **EasyDAG** that adds real-time event streaming, WebSocket integration, and browser-based monitoring.

It provides a lightweight event bus and emitter system designed to sit **on top of EasyDAG’s interface API**, enabling live DAG visualization, control, and external integrations.

---

## What This Package Is

EasyDAG Web is:

* 🌐 A WebSocket-friendly event layer for EasyDAG
* 📡 A publish/subscribe event bus
* 🧩 A clean adapter between EasyDAG and web UIs
* 🖥 A reference implementation for live DAG monitoring

---

## What This Package Is *Not*

* ❌ Not a DAG engine (that’s EasyDAG)
* ❌ Not required to use EasyDAG
* ❌ Not tied to any frontend framework
* ❌ Not a scheduler or persistence layer

---

## Installation

```bash
pip install easydag-web
```

You must also install the core engine:

```bash
pip install easydag
```

---

## Package Overview

This package provides:

* **DagEventBus**
  A simple async-safe event bus supporting multiple subscribers.

* **DagEventEmitter**
  A convenience wrapper for emitting structured DAG and node events.

* **WebSocketManager**
  A helper for broadcasting events to connected WebSocket clients.

---

## Example

**Full Web Demo:** \
A complete FastAPI + WebSocket example is available on GitHub, showing:
  * DAG execution
  * Live event streaming
  * Run / cancel controls
  * Browser-based monitoring

---

## Basic Usage

### Create an Event Bus and Emitter

```python
from EasyDAGWeb import DagEventBus, DagEventEmitter

bus = DagEventBus()
emitter = DagEventEmitter(bus)
```

---

### Attach an Interface to EasyDAG

```python
from EasyDAG import EasyInterface

class MyInterface(EasyInterface):
    def __init__(self, dag, emitter):
        self.emitter = emitter
        super().__init__(dag)

    def dag_started(self, dag_id, metadata=None):
        self.emitter.emit({
            "type": "dag_started",
            "dagId": dag_id,
        })

    def node_finished(self, node_id, metadata=None):
        self.emitter.node_finished(node_id)
```

This keeps your DAG logic and your presentation layer completely separate.

---

## WebSocket Integration (FastAPI)

```python
from fastapi import FastAPI, WebSocket
from EasyDAGWeb import DagEventBus

app = FastAPI()
bus = DagEventBus()

@app.websocket("/ws/dag")
async def dag_ws(ws: WebSocket):
    await ws.accept()

    async def sender(event):
        await ws.send_json(event)

    bus.register_sender(sender)
    try:
        while True:
            await ws.receive_json()
    finally:
        bus.unregister_sender(sender)
```

Any event emitted on the bus is broadcast to all connected clients.

---

## Full Web Demo

This package includes a complete working example:

```
examples/
└── full_web_demo/
    ├── dag.py
    ├── index.html
    ├── interface.py
    └── server.py
```

### Run the demo

```bash
uvicorn examples.full_web_demo.server:app --reload
```

Open:

```
http://localhost:8000
```

### Demo Features

* Run / cancel DAG execution
* Live DAG lifecycle events
* Node progress and completion events
* WebSocket-driven control
* Browser console or UI-based monitoring
* Designed to pair with Vue Flow or similar libraries

---

## Intended Use Cases

EasyDAG Web is ideal when you want to:

* Visualize DAG execution in real time
* Control DAG runs from a UI
* Stream DAG events to external systems
* Build dashboards or monitoring tools
* Integrate EasyDAG into web services
