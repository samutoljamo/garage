from abc import ABC, abstractmethod

# Try to import RPi.GPIO, if it fails, use mock
GPIO_INSTALLED = False
try:
    import RPi.GPIO as GPIO
    GPIO_INSTALLED = True
except ImportError:
    pass

class BaseSensor(ABC):  
    @abstractmethod
    def get_status(self):
        pass
    
class MagnetSensor(BaseSensor):
    def __init__(self, pin):
        if not GPIO_INSTALLED:
            raise ImportError("RPi.GPIO is not installed, can't use MagnetSensor")
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        
    def get_status(self):
        return GPIO.input(self.pin)
    
class MockSensor(BaseSensor):
    def __init__(self):
        self.status = 0
        
    def get_status(self):
        return self.status
    
    def set_status(self, status):
        self.status = status
    


