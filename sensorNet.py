try:
    import config
except:
    raise IOError("No configuration present. Please make copy config/config.py to the root of the application and edit it.")

import threading
import re
import json
import traceback
import datetime
from sensLog import sensLog
from thermalNetwork import thermalNetwork
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from SocketServer import ThreadingMixIn

# Override the HTTPRequestHandler
class HTTPRequestHandler(BaseHTTPRequestHandler):
    # Do nothing if we get POST data.
    def do_POST(self):
        pass

    # Handle GETs.
    def do_GET(self):
        # Hold the data we want to try sending.
        sendData = None
        
        try:
            # If we request the proper thing send it.
            if None != re.search('^/v1/thermal(/)?$', self.path):
                try:
                    # Set our HTTP status stuff.
                    httpStatus = 200
                    sendData = json.dumps(thermalNet.getReadings()) + "\n"
                
                except KeyboardInterrupt:
                    # Pass it up.
                    raise KeyboardInterrupt
                
                except:
                    # Set 500 and dump error.
                    httpStatus = 500
                    
                    # Log the problem.
                    tb = traceback.format_exc()
                    logger.log("Failure getting data to send:\n%s" %tb)
                
                # Send the HTTP respnose code.
                self.send_response(httpStatus)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                
                # If we have data.
                if sendData != None:
                    # Send the data.
                    self.wfile.write(sendData)
            else:
                # If the request was for a URL that we're not serving return a 404.
                self.send_response(404)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
        
        except KeyboardInterrupt:
            # Pass it up.
            raise KeyboardInterrupt
        
        except:
            tb = traceback.format_exc()
            logger.log("Caught exception in do_get():\n%s" %tb)
        
        return
    
    # Override logging.
    def log_message(self, format, *args):
        # If we're debugging or the status isn't 200 log the request.
        if snConfig['debug'] or (args[1] != '200'): 
            logger.log("HTTP request: [%s] %s" %(self.client_address[0], format%args))

# Override the ThreadedHTTPServer
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    allow_reuse_address = True
    
    def shutdown(self):
        # Close the socket and shut the server down.
        self.socket.close()
        HTTPServer.shutdown(self)
    
# Override the SimpleHTTPServer
class SimpleHttpServer():
    def __init__(self, ip, port):
        try:
            # Start a server.
            self.server = ThreadedHTTPServer((ip, port), HTTPRequestHandler)
        
        except KeyboardInterrupt:
            # Pass it up.
            raise KeyboardInterrupt
        
        except:
            tb = traceback.format_exc()
            logger.log("Exception in Smiple HTTP server:\n%s" %tb)
    
    def start(self):
        try:
            logger.log('Start web server.')
            
            # Start the server thread.
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            logger.log('Start sensor monitor.')
            
            # Start the server thread.
            self.tnThread = threading.Thread(target=thermalNet.run(snConfig['sensorMode']))
            self.tnThread.daemon = True
            self.tnThread.start()
        
        except KeyboardInterrupt:
            # Pass it up.
            raise KeyboardInterrupt
        
        except:
            tb = traceback.format_exc()
            logger.log("Exception thrown in start()\n%s" %tb)
            
            # Shut down.
            self.stop()
        
    def waitForThread(self):
        try:
            # Join the thread.
            self.server_thread.join()
        
        except KeyboardInterrupt:
            # Pass it up.
            raise KeyboardInterrupt
        
        except:
            tb = traceback.format_exc()
            logger.log("Exception in waithForThread():\n%s" %tb)
    
    def stop(self):
        # Stop the server and wait for the threads to die.
        self.server.shutdown()
        self.waitForThread()


#######################
# MAIN EXECUTION BODY #
#######################

if __name__ == '__main__':
    # COnfiguration file here.
    snConfig = config.config
    
    # Create the logger.
    logger = sensLog(snConfig['logMode'])
    
    # Create instace of the thermal network handler.
    thermalNet = thermalNetwork(logger)
    
    # Set debuggging.
    thermalNet.setDebug(snConfig['debug'])
    
    try:
        # Register each configured sensor.
        for sensor in snConfig['sensors']:
            try:
                # Register each sensor.
                thermalNet.registerSensor(snConfig['sensors'][sensor]['loc'], snConfig['sensors'][sensor]['locDetail'], sensor)
            
            except:
                tb = traceback.format_exc()
                logger.log("Failed to register sensor %s:\n%s" %(sensor, tb))
    
    except:
        tb = traceback.format_exc()
        logger.log("Exception registering snesors:\n%s" %tb)
    
    # Create HTTP server class.
    logger.log("Init web server.")
    server = SimpleHttpServer(snConfig['listenIP'], snConfig['listenPort'])
    logger.log('Web server listening on %s:%s...' %(snConfig['listenIP'], snConfig['listenPort']))
    
    try:
        # Bring up our server.
        server.start()
    
    except KeyboardInterrupt:
        logger.log("Caught keyboard exception. Shutting down.")
        
        # Shut down.
        server.stop()
    
    except:
        tb = traceback.format_exc()
        logger.log("Exception running server:\n%tb" %tb)
        
        # Shut down.
        server.stop()
    
    # Wait for threads to exit for whatever
    server.waitForThread()
