#!/usr/bin/env python3
import serial, sys, json, logging
import paho.mqtt.client as mqtt

CONFIG_FILE='config.json'
try:
    with open(CONFIG_FILE) as config_file:
        config = json.load(config_file)
except:
    print("Config file not present or invalid JSON!")
    sys.exit(1)

header_retained = b'#R'
header_unretained = b'#U'

ser = serial.Serial()
ser.baudrate = config['baudrate']
ser.port = config['port']
ser.timeout = 5

logging.basicConfig(level=logging.DEBUG if config['debug'] else logging.WARNING, format="%(levelname)s: %(message)s")
log = logging.getLogger("")

try:
    ser.open()
except:
    log.error("Failed to open serial port {}!".format(config['port']))

    import serial.tools.list_ports
    ports = serial.tools.list_ports.comports()
    print("Available serial ports:".format(port))
    for port, desc, hwid in sorted(ports):
        print("{}: {}".format(port, desc))
    sys.exit(1)

def onConnect(client, userdata, flags, rc):
    log.info("Connected to MQTT server")

def onDisconnect(client, userdata, rc):
    log.info("Disconnected from MQTT server")

def onLog(client, userdata, level, buf):
    if (level == mqtt.MQTT_LOG_INFO or level == mqtt.MQTT_LOG_NOTICE):
        log.info(buf)
    elif (level == mqtt.MQTT_LOG_WARNING or level == mqtt.MQTT_LOG_ERR):
        log.warning(buf)

def post_mqtt(topic, message, retain = False):
    (rc, mid) = mqttc.publish(topic, message, qos=0, retain=retain)
    if (rc != mqtt.MQTT_ERR_SUCCESS):
        log.warning("MQTT Publish unsuccessful!")

mqttc = mqtt.Client()

mqttc.on_connect = onConnect
mqttc.on_disconnect = onDisconnect
mqttc.on_log = onLog

try:
    mqttc.connect(config['mqtt_server'], config['mqtt_port'], 60)
except Exception as e:
    log.error("Can't connect to the MQTT broker! {}".format(e))
    if ser.is_open:
        ser.close()
    sys.exit(1)

mqttc.loop_start()

while True:
    try:
        line = ser.readline().rstrip()
        if line is not b'':
            log.debug(line.decode("utf-8"))
        if line.startswith(header_retained) or line.startswith(header_unretained):
            topic = line[2:]
            try:
                (topic, message) = topic.split(b' ', 1)
            except ValueError:
                message = b''
            log.info("Posting {} to topic {}".format(
                message.decode("utf-8"), topic.decode("utf-8")))
            post_mqtt(topic.decode('utf8'), message, line.startswith(header_retained))
    except KeyboardInterrupt:
        print('\n')
        mqttc.disconnect()
        if ser.is_open:
            ser.close()
        sys.exit(0)
    except Exception as e:
        log.error("{}".format(e))
        if ser.is_open:
            ser.close()
        sys.exit(1)
        
