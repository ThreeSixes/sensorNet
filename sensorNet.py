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
from pprint import pprint

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
            if None != re.search('^/v1/thermal(/)?(.+)?$', self.path):
                
                # Set newData to None by default.
                newData = None
                
                # Get match chunks.
                chunks = re.match('^/v1/thermal(/)?(.+)?$', self.path)
                
                # If we have a URL sans slash...
                if (chunks.groups()[0] == None) and (chunks.groups()[1] == None):
                    # Set our HTTP status stuff.
                    httpStatus = 200
                    sendData = json.dumps(thermalNet.getReadings()) + "\n"
                    
                elif (chunks.groups()[0] == "/") and (chunks.groups()[1] == None):
                    # Set our HTTP status stuff.
                    httpStatus = 200
                    sendData = json.dumps(thermalNet.getReadings()) + "\n"
                
                elif (chunks.groups()[0] == "/") and (chunks.groups()[1] != None):
                    # Grab the target sensor
                    targetSensor = chunks.groups()[1]
                    
                    try:
                        # Get the new data from the end of the URL.
                        newData = {targetSensor: thermalNet.getReadings()[targetSensor]}
                    
                    except KeyError:
                        # Set HTTP 404.
                        httpStatus = 404
                        sendData = None
                    
                    except Exception as e:
                        # Pass other exceptions back up.
                        raise e
                    
                    # If we got some new data...
                    if (newData != None) and (newData != {}):
                        # Set our HTTP status stuff.
                        httpStatus = 200
                        sendData = json.dumps(newData) + "\n"
                    
                    else:
                        # Set HTTP 404.
                        httpStatus = 404
                        sendData = None
                
                else:
                    # 404, no data.
                    httpStatus = 404
                    sendData = None
            
            # If we request the proper thing send it.
            elif None != re.search('^/v1/sensors(/)?(.+)?$', self.path):
                
                # Get match chunks.
                chunks = re.match('^/v1/sensors(/)?(.+)?$', self.path)
                
                # If we have a URL sans slash...
                if (chunks.groups()[0] == None) and (chunks.groups()[1] == None):
                    # Set our HTTP status stuff.
                    httpStatus = 200
                    sendData = json.dumps(thermalNet.getSensorMeta()) + "\n"
                    
                elif (chunks.groups()[0] == "/") and (chunks.groups()[1] == None):
                    # Set our HTTP status stuff.
                    httpStatus = 200
                    sendData = json.dumps(thermalNet.getSensorMeta()) + "\n"
                
                elif (chunks.groups()[0] == "/") and (chunks.groups()[1] != None):
                    
                    # Get the new data from the end of the URL.
                    newData = thermalNet.getSensorMeta(chunks.groups()[1])
                    
                    # If we got some new data...
                    if (newData != None) and (newData != {}):
                        # Set our HTTP status stuff.
                        httpStatus = 200
                        sendData = json.dumps(newData) + "\n"
                    
                    else:
                        # Set HTTP 404.
                        httpStatus = 404
                        sendData = None
                
                else:
                    # 404, no data.
                    httpStatus = 404
                    sendData = None
            
            else:
                # 404, no data.
                httpStatus = 404
                sendData = None
        
        except KeyboardInterrupt:
            # Pass it up.
            raise KeyboardInterrupt
        
        except:
            # HTTP 500.
            httpStatus = 500
            sendData = None
            
            tb = traceback.format_exc()
            logger.log("Caught exception in do_get():\n%s" %tb)
        
        try:
            # Send the HTTP respnose code.
            self.send_response(httpStatus)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # If we have data.
            if sendData != None:
                # Send the data.
                self.wfile.write(sendData)
        
        except:
            tb = traceback.format_exc()
            logger.log("Caught exception trying to send HTTP response:\n%s" %tb)
        
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
                thermalNet.registerSensor(sensor, snConfig['sensors'][sensor]['loc'], snConfig['sensors'][sensor]['locDetail'], snConfig['sensors'][sensor]['sensorMeta'])
            
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
