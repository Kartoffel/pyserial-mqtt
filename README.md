# pyserial-mqtt
Simple script to read lines from a serial port and relay them to MQTT.

To install the required pip modules, run

    sudo -H python3 -m pip install -r requirements.txt

Next, copy `config.json.template` to `config.json` and modify the settings for your serial port and MQTT broker.

### Usage
The script expects serial lines in the following format:

    #R[topic] [payload]

or

    #U[topic] [payload]

To publish retained and unretained messages respectively.

Note that the topic may not contain spaces as these are used to separate topic and payload, but the payload can be anything. Empty payloads work as well.


### Systemd service
A systemd unit file is provided for your convenience. Make sure to edit the user and working directory before installing.
