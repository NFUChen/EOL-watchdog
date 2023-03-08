from typing import Callable, Optional
import re
import socket

class InvalidFileError(Exception):
    ...

class TestResultParser: 
    def __init__(self, test_file: str) -> None:
        self.test_file = test_file
        self.serial_number: Optional[str] = None
        self.final_result: Optional[str] = None
        self.test_start_time: Optional[str] = None 
        self.test_date: Optional[str] = None
        self.failed_items: list[str] = []
        self.host_name = socket.gethostname()

    def is_line_match(self, checked_string: str, line: str) -> bool:
        return checked_string in line

    def _handle_serial_number(self, line: str) -> None:
        self.serial_number =  line.split(",").pop().strip()

        if len(self.serial_number) >= 10:
            return
        self.serial_number =  re.search('\d{10}', line)

        if self.serial_number is not None:
            self.serial_number = self.serial_number.group()
    
    def _handle_final_result(self, line: str) -> None:
        self.final_result = re.search("PASS|FAIL|ERROR|NG", line)

        if self.final_result is not None:
            self.final_result = self.final_result.group()

    
    def _handle_failed_items(self, line: str) -> None:
        self.failed_items.append(line.strip())
    
    def _handle_test_start_time(self, line: str) -> None:
        self.test_start_time = line.split(",").pop().strip().replace('"',"")
    
    def _handle_test_date(self, line: str) -> None:
        self.test_date = line.split(",").pop().strip().replace('"',"")

    def parse(self) -> dict[str, str]:
        checked_strings_with_handlers: dict[bool, Callable] = {
            "Serial Number": self._handle_serial_number,
            "FinalResult": self._handle_final_result,
            "FAIL": self._handle_failed_items,
            "NG": self._handle_failed_items,
            "Test Date": self._handle_test_date,
            "Test Start Time": self._handle_test_start_time, 
        }

        with open(self.test_file, "r") as file:
            for line in file:
                for checked_string, handler in checked_strings_with_handlers.items():
                    if self.is_line_match(checked_string, line):
                        handler(line)
                        continue
        if self.serial_number is None:
            raise InvalidFileError(f"[{self.host_name}] Invalid file format, receiveing file named: {self.test_file}")

        return {  
            'host': self.host_name,
            'file_name': self.test_file,
            'date': self.test_date,
            'time': self.test_start_time,
            'serial_number': self.serial_number,
            'final_result': self.final_result,
            'failed_items': self.failed_items,
        }

