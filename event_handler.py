from typing import Callable
import socket
import os
from test_result_parser import TestResultParser
from watchdog.events import FileSystemEvent, DirModifiedEvent
from watchdog.events import FileSystemEventHandler
from paho.mqtt.publish import single
from socket import gaierror
from logger import Logger


def single_publish(hostname: str, topic: str, payload: str):
    try:
        single(
            topic= topic, 
            payload= str(payload), 
            qos= 2, 
            hostname= hostname
        )
    except Exception as error:
        print(error)
        os._exit(1) # help docker to restart container

class InvalidLoggerError(Exception):
    pass

logger = Logger("error.log")

def publish_and_log_error(func: Callable) -> Callable:
    def wrapper(*args, **kwargs) -> None:
        try:
            return func(*args, **kwargs)
        except Exception as error:
            broker_host = os.environ.get("BROKER_HOST")
            error_topic = os.environ.get("MQTT_ERROR_TOPIC_PUBLISHED")
            self_host = socket.gethostname()
            
            single_publish(hostname= broker_host,
                           topic= f"{error_topic}/{self_host}", 
                           payload= str(error))
            global logger
            logger.error(error)
    return wrapper

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
    
    
    @publish_and_log_error
    def on_created(self, event: FileSystemEvent) -> None:

        current_file_name = os.path.basename(event.src_path)
        if not self.__is_valid_file_extension(current_file_name):
            return
        parser = TestResultParser(event.src_path)

        parsed_result = parser.parse()

        single_publish(hostname= self.broker_host,
            topic= f"{self.mqtt_topic}/{self.self_host_name}", 
            payload= str(parsed_result) )
    
        print(parsed_result)
            
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
