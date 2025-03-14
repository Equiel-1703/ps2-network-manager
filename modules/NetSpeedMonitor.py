import psutil
import time
from colorama import Fore
from PyQt6.QtCore import QThread, pyqtSignal

class NetSpeedMonitor(QThread):
    """A class to monitor network speed for a given interface.
    Inherits from QThread to run in a separate thread.
    
    Attributes:
        interface (str): The network interface to monitor.
        interval (int): The interval in seconds to measure speed.
        running (bool): Flag to control the thread execution.
    """
    
    # Signal to send upload & download speeds
    speed_updated = pyqtSignal(float, float) 
    
    # Signal to notify about interface not found
    interface_not_found = pyqtSignal(str)

    def __init__(self, interface, interval=1):
        """Initializes the NetSpeedMonitor with the specified interface and interval.
        
        This class inherits from QThread to allow for concurrent execution.
        
        Args:
            interface (str): The network interface to monitor.
            interval (int): The interval in seconds to measure speed.
        """
        
        super().__init__()
        self.interface = interface
        self.interval = interval
        self.running = True  # Control flag to stop the thread

    def run(self):
        """Runs the speed measurement in a separate thread."""
        while self.running:
            net_before = psutil.net_io_counters(pernic=True).get(self.interface)

            if not net_before:
                print(f"{Fore.RED} ERROR: Interface {self.interface} not found.")
                self.running = False
                self.interface_not_found.emit(self.interface)
                return

            bytes_sent_before = net_before.bytes_sent
            bytes_recv_before = net_before.bytes_recv

            time.sleep(self.interval)

            net_after = psutil.net_io_counters(pernic=True).get(self.interface)
            if not net_after:
                print(f"{Fore.RED} ERROR: Interface {self.interface} not found.")
                self.running = False
                self.interface_not_found.emit(self.interface)
                return

            bytes_sent_after = net_after.bytes_sent
            bytes_recv_after = net_after.bytes_recv

            # Calculate speed in KB/s
            upload_speed = (bytes_sent_after - bytes_sent_before) / self.interval / 1024
            download_speed = (bytes_recv_after - bytes_recv_before) / self.interval / 1024

            # Emit signal with updated speeds
            self.speed_updated.emit(upload_speed, download_speed)

    def stop(self):
        """Stops the thread gracefully."""
        self.running = False
