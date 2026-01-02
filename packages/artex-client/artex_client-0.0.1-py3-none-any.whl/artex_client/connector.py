# -*- coding: utf-8 -*-
"""
ARTEX Client - Python клиент для подключения к системе управления роботами
"""


import socketio
from time import sleep as zzz

class Connector:
    def __init__(self, vault, server_url):
        self.vault = vault
        self.server_url = server_url
        self.namespace = "/client"
        self.sio = socketio.Client()
        self.connected = False
        
        self._setup_handlers()
        
    def connect(self):
        """Подключиться к серверу"""
        try:
            self.sio.connect(
                self.server_url + self.namespace,   # ← ОБЯЗАТЕЛЬНО !!!
                auth={"name": "python_client", "type": "pc"},
            )
            self.connected = True
            zzz(.5)
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def _setup_handlers(self):
        """Настроить обработчики событий"""

        @self.sio.event(namespace=self.namespace)
        def connect():
            print("✅ Python client connected:", self.sio.sid)

        @self.sio.event(namespace=self.namespace)
        def disconnect():
            print("⚠️ Python client disconnected")


        @self.sio.on("token_ask", namespace=self.namespace)
        def on_token_ask(data):
            return self.sio.sid

        @self.sio.on("heartbeat", namespace=self.namespace)
        def on_heartbeat(data):
            response = {}
            for key in data:
                if key == "d_meta":
                    response[key] = {"sid": self.sio.sid, "ready": True}
                elif key == "Ready":
                    response[key] = "ok"
            return response
        
        
        @self.sio.on("overview", namespace=self.namespace)
        def on_overview(data):
            author  =  data.get("author", {})
            payload =  data.get("payload", {})
            self.vault.update_connections(payload.get("robots", {}))
        
        
        
        @self.sio.on("telem", namespace=self.namespace)
        def on_telem(data):
            robot_sid =  data.get("author", {})
            payload   =  data.get("payload", {})
            self.vault.update_telem(robot_sid, payload)
        
        
        @self.sio.on("video", namespace=self.namespace)
        def on_video(data):
            robot_sid =  data.get("author", {})
            payload   =  data.get("payload", {})
            self.vault.update_video(robot_sid, payload)
        
    
    def subscribe(self, robot_sid):
        if self.connected:
            self.sio.emit("subscribe_ask", [robot_sid], namespace=self.namespace)
    
    def send_command(self, robot_sid, command, args=None):
        if self.connected:
            payload = {
                "to_sid": robot_sid,
                "com": command
            }
            if args:
                payload["args"] = args

            self.sio.emit("command", payload, namespace=self.namespace)

    def disconnect(self):
        if self.connected:
            self.sio.disconnect()
            self.connected = False