"""
Python class for the DS18B20 temperature sensor, based on code by Adafruit Industries by ThreeSixes (https://github.com/ThreeSixes/py-ds18b20)

Original Adafruit Code:
https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/software
"""

import glob
import time
import subprocess

class ds18b20:

    def __init__(self):
        """
        Class for the DS18B20 temperature sensor module, based on caode from Adafruit Industries:
        https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/software
        """
        # Minimum time we can wait before polling again is 0.750 seconds.
        self.minPoll = 0.750
        
        # Configuration for the /sys nodes
        self.__baseDir = '/sys/bus/w1/devices/'

   
    def __readTempRaw(self, address):
        """
        Read raw temperature values from the /sys node for the sensor.
        """
        
        devicePath = self.__baseDir + address + '/w1_slave'
        
        # Read data from the nodes
        try:
            catData = subprocess.Popen(['cat', devicePath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out,err = catData.communicate()
        except Exception as e:
            raise e
        
        # Encode as UTF-8 and split into an array.
        outDecode = out.decode('utf-8')
        lines = outDecode.split('\n')
        
        return lines
 
    def readTemp(self, address):
        """
        Read temperature value from the sensor. Returns a float representing teperature in degrees Celcius.
        """
        
        lines = self.__readTempRaw(address)
        tempC = -9999.9
        
        # Raise an exception if we have bad CRC data.
        if lines[0].find('YES') < 0:
            raise ValueError("Bad CRC value from DS18B20 at " + address)
        
        # Find the chunk of the second line that represents the temperature.
        equalsPos = lines[1].find('t=')
        
        # If the temperature isn't missing read the data.
        if equalsPos != -1:
            tempString = lines[1][equalsPos+2:]
            tempC = float(tempString) / 1000.0
        else:
            raise IOError("Missing temperature data from DS18B20 at " + address)
        
        return tempC
