# -*- coding: utf-8 -*-
"""
ARTEX Client - Python клиент для подключения к системе управления роботами
"""


from .vault import Vault
from .connector import Connector


class Artex:
    def __init__(self, server_url):
        self.vault = Vault()
        self.connector = Connector(self.vault, server_url)
    
    def connect(self):
        """Подключиться к серверу"""
        return self.connector.connect()
    
    def subscribe(self, robot_sid):
        """Подписаться на робота"""
        self.connector.subscribe(robot_sid)
    
    def get_telem(self, robot_sid=None):
        """Получить телеметрию робота"""
        return self.vault.get_telem(robot_sid)
    
    def get_video(self, robot_sid=None):
        """Получить телеметрию робота"""
        return self.vault.get_video(robot_sid)
    
    def send_command(self, robot_sid, command, args=None):
        """Отправить команду роботу"""
        self.connector.send_command(robot_sid, command, args)
    
    def get_connections(self):
        """Получить список доступных подключений"""
        return self.vault.get_connections()
    
    def disconnect(self):
        """Отключиться от сервера"""
        self.connector.disconnect()