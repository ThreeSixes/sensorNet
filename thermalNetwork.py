#!/usr/bin/python

"""
Simple temperature-based monitoring and control system for the Raspberry Pi.
"""

###########
# Imports #
###########

import time
import traceback
import threading
import random
import datetime
from ds18b20 import ds18b20

class thermalNetwork:
    def __init__(self, logger):
        """
        Class responsible for cummunicating with the temperature sensor network for data acquisition.
        This expects a sensLog instance called logger to exist when runnig.
        """
        
        # For some reason we aren't inheriting this globally so instead we'll override it.
        self.__logger = logger
        
        self.__logger.log("Init thermalNetwork...")
        
        # Debug?
        self.__debugOn = False
        
        # Temperature sensor support
        self.__tempSens = ds18b20()
        
        # Temperature sensor registry
        self.__sensorSet = {}
        
        # Store readings and sensor data globally.
        self.__sensorReadings = {}
        
        # Running flag. Set to false when we should die.
        self.__keepRunning = True
    
    def setDebug(self, debugOn):
        """
        Activates or deactivates debugging. Accepts one boolean argument.
        """
        
        self.__logger.log("Set debug %s" %debugOn)
        
        # Set master debug flag.
        self.__debugOn = debugOn
        
        return
    
    def registerSensor(self, generalLoc, locDetail, address):
        """
        Register a new temperature sensor
        Accepts a sensor name and address.
        """
        
        try:
            # Register the sensor in the dictionary.
            self.__sensorSet.update({address: {'loc': generalLoc, 'locDetail': locDetail}})
            
            # Debug?
            if self.__debugOn:
                self.__logger.log("Registered new temp sensor %s, @ %s: %s" %(address, generalLoc, locDetail))
        
        except Exception as e:
            # Just pass whatever happened back up.
            raise e
    
    def getReadings(self):
        """
        Get a dictionary containg sensor readings.
        """
        
        # Send all the readings!
        return self.__sensorReadings
    
    def showReadingsCont(self):
        """
        Show temperature readings continuously.
        """
        
        try:
            while True:
                pass
        
        except Exception as e:
            # Pass exception up.
            raise e

    def __takeReadings(self):
        """
        Take readings from sensors.
        """
        
        # Hold readings.
        readings = {}
        
        try:
            # Attempt to take readings.
            for tgtSens in self.__sensorSet:
                # Get timestamp.
                dts = str(datetime.datetime.utcnow())
                
                # Keep the log looking pretty and uniform.
                if len(dts) == 19:
                    dts = dts + ".000000"
                
                # Update local readings.
                readings.update({
                    tgtSens: {
                        'dts': dts,
                        'tempReading': self.__tempSens.readTemp(tgtSens),
                        'loc': self.__sensorSet[tgtSens]['loc'],
                        'locDetail': self.__sensorSet[tgtSens]['locDetail']
                    }
                })
            
            # Set global readings from new values.
            # Note: this is designed to be atomic so both old and new data don't coexist globally.
            self.__sensorReadings = readings
        
        except Exception as e:
            raise e
    
    def __fakeReadings(self):
        """
        Fake readings from sensors.
        """
        
        # Hold readings.
        readings = {}
        
        try:
            # Attempt to take readings.
            for tgtSens in self.__sensorSet:
                # Get timestamp.
                dts = str(datetime.datetime.utcnow())
                
                # Keep the log looking pretty and uniform.
                if len(dts) == 19:
                    dts = dts + ".000000"
                
                # Update local readings.
                readings.update({
                    tgtSens: {
                        'time': dts,
                        'tempReading': random.randint(-10, 125),
                        'loc': self.__sensorSet[tgtSens]['loc'],
                        'locDetail': self.__sensorSet[tgtSens]['locDetail']
                    }
                })
            
            # Set global readings from new values.
            # Note: this is designed to be atomic so both old and new data don't coexist globally.
            self.__sensorReadings = readings
        
        except Exception as e:
            raise e
    
    def __worker(self):
        """
        thermalNetwork worker.
        """
        
        if self.__debugOn:
            self.__logger.log("In worker...")
        
        try:
            while self.__keepRunning:
                # Grab all our readings.
                self.__takeReadings()
                
                # Wait for sensor refresh timing to do it again.
                time.sleep(self.__tempSens.minPoll)
        
        except KeyboardInterrupt:
            # Flag to shut down.
            self.__keepRunning = False
            
            # pass it up the stack.
            raise KeyboardInterrupt
        
        except Exception as e:
            # Flag to shut down.
            self.__keepRunning = False
            
            # Figure out what happened.
            tb = traceback.format_exc()
            
            # Log it.
            self.__logger.log("Exception in worker:\n%s" %tb)
            
            # Pass it up the stack
            raise e

    def __dummyWorker(self):
        """
        thermalNetwork worker that creates fake data..
        """
        
        if self.__debugOn:
            self.__logger.log("In dummy worker...")
        
        # Long hair, don't care.
        random.seed(395803958)
        
        try:
            while self.__keepRunning:
                # Grab all our readings.
                self.__fakeReadings()
                
                # Wait for sensor refresh timing to do it again.
                time.sleep(self.__tempSens.minPoll)
        
        except KeyboardInterrupt:
            # Flag to shut down.
            self.__keepRunning = False
            
            # pass it up the stack.
            raise KeyboardInterrupt
        
        except Exception as e:
            # Flag to shut down.
            self.__keepRunning = False
            
            # Figure out what happened.
            tb = traceback.format_exc()
            
            # Log it.
            self.__logger.log("Exception in dummyWorker:\n%s" %tb)
            
            # Pass it up the stack
            raise e

    def __contiuous(self):
        """
        thermalNetwork continuous measurement mode.
        """
        if self.__debugOn:
            self.__logger.log("In continuous mode...")
        
        try:
            while self.__keepRunning:
                # Grab all our readings.
                self.__takeReadings()
                
                # Dump the readings.
                for reading in self.__sensorReadings:
                    if reading:
                        self.__logger.log("[%s] %s (%s) is %s C" %(reading, self.__sensorReadings[reading]['loc'], self.__sensorReadings[reading]['locDetail'], self.__sensorReadings[reading]['tempReading']))
                
                # Wait for sensor refresh timing to do it again.
                time.sleep(self.__tempSens.minPoll)
        
        except KeyboardInterrupt:
            # Flag to shut down.
            self.__keepRunning = False
            
            # pass it up the stack.
            raise KeyboardInterrupt
        
        except Exception as e:
            # Flag to shut down.
            self.__keepRunning = False
            
            # Figure out what happened.
            tb = traceback.format_exc()
            
            # Log it.
            self.__logger.log("Exception in worker:\n%s" %tb)
            
            # Pass it up the stack
            raise e
    
    def run(self, mode='worker'):
        """
        The runner continuously monitors temperaure sensors for new data. In 'worker' mode this just runs in the background. In 'continuous' mode it runs continuously printing out its readings.
        """
        
        if mode == 'worker':
            try:
                if self.__debugOn:
                    self.__logger.log("Entering worker mode.")
                
                # Start the sensor worker.
                self.__worker()
            
            except Exception as e:
                # If we explode just fire the exception.
                raise e
        
        elif mode == 'dummy':
            try:
                if self.__debugOn:
                    self.__logger.log("Entering dummy worker mode.")
                
                # Start the sensor worker.
                self.__dummyWorker()
                
            except Exception as e:
                # If we explode just fire the exception.
                raise e
            
        elif mode == 'continuous':
            try:
                if self.__debugOn:
                    self.__logger.log("Entering continuous mode.")
                
                # Start continuous mode.
                self.__contiuous()
            
            except Exception as e:
                # If we explode just fire the exception.
                raise e
        
        else:
            raise RuntimeError("Unable to run thermalNetwork in %s mode. Valid modes are 'worker' and 'continuous'." %mode)


# If we're being independently executed...
if __name__ == '__main__':
    
    # Do a late import
    from sensLog import sensLog
    
    # Logger
    logger = sensLog()
    
    # Create minder instance
    thermalNet = thermalNetwork(logger)
    
    # Set debuggging.
    thermalNet.setDebug(True)
    
    try:
        # Register the water bath sensor.
        thermalNet.registerSensor('outside', 'west face', '28-000006de8409')
        thermalNet.registerSensor('basement living room', 'west wall', '28-04146918b4ff')
        thermalNet.registerSensor('basement bedroom', 'south wall', '28-041469030cff')
        thermalNet.registerSensor('basement stove', 'blower pocket', '28-0000068e7983')
        thermalNet.registerSensor('basement lab', 'south wall', '28-041469018aff')
        thermalNet.registerSensor('basement bar', 'north wall', '28-0414691c50ff')
        thermalNet.registerSensor('basement restroom', 'south wall', '28-03146444d4ff')
    
    except KeyboardInterrupt:
        self.__logger.log('Got keyboard interrupt. Quitting.')
    
    except:
        tb = traceback.format_exc()
        self.__logger.log("Exception registering snesors:\n%s" %tb)
    
    try:
        # Start monitoring.
        thermalNet.run('continuous')
    
    except KeyboardInterrupt:
        self.__logger.log('Got keyboard interrupt. Quitting.')
    
    except:
        tb = traceback.format_exc()
        self.__logger.log("Unhandled exception thrown by runner:\n%s" %tb)
    
    self.__logger.log("Done monitoring sensor network.")
