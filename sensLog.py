"""
sensLog by ThreeSixes (https://github.com/ThreeSixes)

This project is licensed under GPLv3. See COPYING for dtails.

This file was originally part of the airSuck project (https://github.com/ThreeSixes/airSuck).
"""

# Imports
import sys
import datetime
import syslog
import traceback

# Main class
class sensLog():
    """
    sensLog logging class.
    """
    
    def __init__(self, loggingMode="stdout"):
        """
        sensLog constructor
        """
        
        # Check for acceptable logging mode.
        if loggingMode in ('stdout', 'syslog', 'none'):
            # Set class-wide logging mode.
            self.mode = loggingMode
        else:
            raise ValueError("Valid loging mode not specified. Please use 'stdout', 'syslog', or 'none'.")
        
        if loggingMode == "syslog":
            syslog.openlog(logoption=syslog.LOG_PID, facility=syslog.LOG_DAEMON)
    
    def __logStdout(self, message):
        """
        Log a message to stdout with a UTC timestamp.
        """
        # Get timestamp.
        dts = str(datetime.datetime.utcnow())
        
        # Keep the log looking pretty and uniform.
        if len(dts) == 19:
            dts = dts + ".000000"
        
        # Dump the message.
        sys.stdout.write("%s - %s\n" %(dts, message))
    
    def __logSyslog(self, message, sev=syslog.LOG_NOTICE):
        """
        Log a message to syslog.
        """
        
        # Log it.
        syslog.syslog(sev, message)
    
    def log(self, message):
        """
        Log a message.
        """
        
        try:
            # If we don't want to do anything...
            if self.mode == "stdout":
                # Log to stdout.
                self.__logStdout(message)
            
            elif self.mode == "syslog":
                # Log to syslog. Not fully implemented yet.
                self.__logSyslog(message)
            
            elif self.mode == "none":
                # This logs absolutely nothing.
                None
        
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        
        except:
            tb = traceback.format_exc()
            print("sensLog logger failure:\n%s" %tb)
        