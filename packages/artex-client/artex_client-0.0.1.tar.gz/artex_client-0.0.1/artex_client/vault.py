# -*- coding: utf-8 -*-
"""
ARTEX Client - Python клиент для подключения к системе управления роботами
"""


import cv2
import numpy as np

class Vault:
    def __init__(self):
        self.connections = {}  # {sid: robot_data} -- s/d_meta
        self.telem = {}    # {sid: telem_data}
        self.video = {}    # {sid: dideo_data}
        self.video_decoded = {}    # {sid: dideo_data}
    
    def update_connections(self, connections_data):
        """Обновить список доступных подключений"""
        self.connections = connections_data
    
    def update_telem(self, sid, telem_data):
        """Обновить телеметрию для конкретного робота"""
        self.telem[sid] = telem_data
    
    def update_video(self, sid, video_data):
        """Обновить видео для конкретного робота"""
        self.video[sid] = {"new": True,
                          "data"  : video_data}
    
    def get_connections(self):
        """Получить список доступных подключений"""
        return self.connections
    
    def get_telem(self, sid=None):
        """Получить телеметрию (всех или конкретного робота)"""
        if sid:
            return self.telem.get(sid, {})
        return self.telem
    
    def get_video(self, sid=None):
        """Получить телеметрию (всех или конкретного робота)"""
        if sid:
            if self.video["new"]:
                self.decode_video(sid)
            return self.video_decoded[sid]
        
        if any([robot["new"] for sid, robot in self.video.items()]):
            self.decode_video()
        return self.video_decoded
    
    def decode_video(self, sid=None):
        
        if sid:
            
            self.video_decoded[sid] = {cam : cv2.imdecode(np.frombuffer(vid,
                                                                       np.uint8),
                                                         cv2.IMREAD_COLOR
                                                         )
                                      for cam, vid
                                      in self.video[sid]["data"].items()}
            self.video[sid]["new"] = False
            return self.video_decoded[sid]
        
        for sid, vid_pack in self.video.items():
            if vid_pack["new"]:
                self.decode_video(sid)