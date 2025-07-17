import serial
import logging
from waggle.plugin import Plugin

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)

# Open the serial port
try:
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    logging.info(f"Opened serial port: {ser.name}")
except serial.SerialException as e:
    logging.error(f"Failed to open serial port: {e}")
    exit(1)

# Read loop
try:
    while True:
        if ser.in_waiting:
            # Read a line from the serial port
            line = ser.readline().decode('utf-8', errors='replace').strip()

            # split the line into name and value
            if ':' in line:
                name, value = line.split(':', 1)
                name = name.strip()
                value = int(value.strip())
                logging.info(f"Name: {name}, Value: {value}")

                # Name the values
                if name == "Soil Moisture":
                    name = "soil_moist"
                elif name == "Soil Temperature":
                    name = "soil_temp"
                else:
                    logging.warning(f"Unknown measurement name: {name}")


                # TODO: Add your post processing logic here
                # For example, you can convert value to float if needed
                try:
                    value = float(value/100)
                except ValueError:
                    logging.error(f"Invalid value for {name}: {value}")
                    continue


                # NOTE: optionally, you can add metadata to the value
                # metadata = {}
                # metadata['unit'] = 'Celsius' if name == 'soil_temp' else 'percent'


                # Now we publish the value using the Plugin API
                with Plugin() as plugin:
                    plugin.publish(name, value) # with optional metadata change to plugin.publish(name, value, meta=metadata)
                    logging.info(f"Published {name} with value {value}")

            else:
                logging.warning(f"Malformed line: {line}")
except KeyboardInterrupt:
    logging.info("Exiting on user interrupt.")
finally:
    ser.close()
    logging.info("Serial port closed.")