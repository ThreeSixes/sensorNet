# Generic device metadata for a DS18B20...
ds18b20Meta = {
    'sensor': 'DS18B20',
    'cap': 'temp',
    'accuracy': '0.5',
    'unit': 'C',
    'min': -55,
    'max': 125,
    'interface': '1Wire'
}

# Configuration
config = {
    'debug': True, # To debug or not to debug?
    'listenIP': '0.0.0.0', # Listen address. Default is 0.0.0.0
    'listenPort': 8092, # Listen port. Default is 8092
    'logMode': 'stdout', # Log mode. Can be stdout, syslog, or none.
    'sensorMode': 'worker', # Sensor mode specifies where we get sensor data from. Valid modes are 'dummy' and 'worker'. This is mostly for development and testing on devices that don't have 1-Wire sensors connected. 
    'sensors': {
        #'1-Wire sensor ID': {'loc': '<General location>', 'locDetail': '<location detail>', 'sensorMeta': ds18b20Meta}
        # Example DS18B20 with address 28-000006de8409: '28-000006de8409': {'loc': 'outside', 'locDetail': 'west face', 'sensorMeta': ds18b20Meta}
    }
}