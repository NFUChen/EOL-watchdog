from typing import Optional
import socket
import os
from test_result_parse import TestResultParser
from watchdog.events import FileSystemEvent, DirModifiedEvent
from watchdog.events import FileSystemEventHandler
from paho.mqtt.publish import single

from logger import Logger



class InvalidLoggerError(Exception):
    pass

logger = Logger("error.log")

class EventHandler(FileSystemEventHandler):
    def __init__(self, valid_extensions: list[str]) -> None:
        self.self_host_name = socket.gethostname()
        
        self.broker_host = os.environ.get("BROKER_HOST")
        self.mqtt_topic = os.environ.get("MQTT_TOPIC_PUBLISHED")
        if self.broker_host is None:
            raise ValueError("Environment variable: 'BROKER_HOST' is not given")
        
        if self.mqtt_topic is None:
            raise ValueError("Environment variable: 'MQTT_TOPIC_PUBLISHED' is not given")


        self.logger = logger
        self.valid_extensions = valid_extensions
    
    @logger.log_error
    def on_created(self, event: FileSystemEvent) -> None:

        current_file_name = os.path.basename(event.src_path)
        if not self.__is_valid_file_extension(current_file_name):
            return

        result = TestResultParser(event.src_path).parse()
        single(
            topic= f"{self.mqtt_topic}/{self.self_host_name}", 
            payload= str(result), 
            qos= 2, 
            hostname= self.broker_host
        )
        print(result)
            
    def on_moved(self, event: FileSystemEvent) -> None:
        pass

    def on_deleted(self, event: FileSystemEvent) -> None:
        pass


    
        



    def __is_valid_file_extension(self, file_name:str) -> bool:
        file_name_extension = file_name.split(".").pop()
        for extension in self.valid_extensions:
            if extension == file_name_extension:
                return True
        return False
