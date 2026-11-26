# ruff: noqa: ISC004 — dữ liệu đề: chuỗi dài ngắt dòng trong danh sách là cố ý
"""Trắc nghiệm khóa 494 — (đoạn số, mức, đề, [ĐÚNG, sai, sai, sai], giải thích).
Đáp án đúng viết ĐẦU TIÊN; build.py xoay nó vào vị trí 0..3 để đáp án rải đều."""

MCQ = {
    "IOT": [
        (
            1,
            "recognize",
            "What does each IoT device need so that it can be found and addressed on a network?",
            [
                "A unique identity such as an IP address or device ID",
                "A large colour touch screen for local user input",
                "A permanent wired connection to the electricity grid",
                "A full desktop operating system such as Windows",
            ],
            "Each thing needs a unique identity, such as an IP address or device ID, so that it can be found and addressed.",
        ),
        (
            1,
            "recognize",
            "Which term describes IoT devices that have little memory, low processing power and run on batteries?",
            ["Constrained devices", "Mainframe devices", "Virtual devices", "Redundant devices"],
            "Devices with little memory, low processing power and battery power are called constrained devices.",
        ),
        (
            1,
            "recognize",
            "Which component lets an IoT device act on the physical world, for example by opening a valve?",
            ["An actuator", "A sensor", "A gateway", "A broker"],
            "Actuators such as motors, valves or switches act on the physical world; sensors only measure it.",
        ),
        (
            2,
            "recognize",
            "What is predictive maintenance in industrial IoT?",
            [
                "Using machine sensor data to predict failures early",
                "Replacing every machine on a fixed yearly schedule",
                "Repairing machines only after they have broken down",
                "Buying spare machines in case one of them fails",
            ],
            "Sensors measure vibration and temperature so failures can be predicted before they happen.",
        ),
        (
            2,
            "recognize",
            "In smart agriculture, which sensor tells an irrigation system when crops need water?",
            ["Soil moisture sensor", "Accelerometer", "Smoke detector", "Proximity sensor"],
            "Soil moisture sensors tell the irrigation system when to water crops, which saves water.",
        ),
        (
            3,
            "recognize",
            "What does interoperability mean for IoT devices?",
            [
                "Devices from different vendors can work together",
                "Devices can run for years on a single battery",
                "Devices can encrypt every message that they send",
                "Devices can be installed without any network",
            ],
            "Interoperability is the ability of devices from different vendors, protocols and data formats to work together.",
        ),
        (
            3,
            "recognize",
            "Why are many IoT devices easy for attackers to take over?",
            [
                "They often keep default passwords and rarely get updates",
                "They always use the newest and strongest encryption",
                "They are never connected to the public internet at all",
                "They are protected by a powerful firewall in the cloud",
            ],
            "Many devices ship with default passwords and rarely get software updates, so attackers can take them over.",
        ),
        (
            1,
            "understand",
            "A smart thermostat measures room temperature and switches the heater on when the room gets cold. "
            "Which two IoT capabilities does it use?",
            ["Sensing and actuating", "Routing and switching", "Encryption and compression", "Storage and backup"],
            "It senses the temperature (sensor) and acts on the heater (actuator).",
        ),
        (
            1,
            "understand",
            "A smart-city network has thousands of sensors from different vendors; some sleep to save energy "
            "and new ones are added every month. Which pair of IoT characteristics does this show?",
            [
                "Heterogeneity and dynamic change",
                "Low latency and high bandwidth",
                "Central control and fixed topology",
                "Wired power and identical hardware",
            ],
            "Devices from many vendors show heterogeneity; devices that sleep, join and leave show dynamic change.",
        ),
        (
            2,
            "understand",
            "A hospital wants to watch a patient's heart rate at home and alert the doctor if it becomes "
            "dangerous. Which IoT application area is this?",
            ["Remote health monitoring", "Precision agriculture", "Smart parking", "Predictive maintenance"],
            "Wearable devices that track heart rate and alert doctors remotely are a healthcare (remote monitoring) use.",
        ),
        (
            2,
            "understand",
            "A city wants its street lights to use less energy late at night when roads are empty. Which IoT "
            "solution fits best?",
            [
                "Lights with motion sensors that dim when nobody is near",
                "Replacing all street lights with brighter bulbs",
                "Switching every street light off for the whole night",
                "Asking residents to report broken lights by email",
            ],
            "Smart street lights dim when roads are empty, saving energy without leaving roads dark.",
        ),
        (
            3,
            "understand",
            "A company buys smart locks from vendor A and a hub from vendor B, but the hub cannot control the "
            "locks because they use different protocols. Which IoT challenge is this?",
            ["Interoperability", "Scalability", "Energy efficiency", "Latency"],
            "Devices from different vendors using different protocols that cannot work together is an interoperability problem.",
        ),
        (
            3,
            "understand",
            "A fitness band records sleep times and location all day and uploads them to the cloud. Which "
            "concern does this raise most directly?",
            ["Privacy of personal data", "Battery chemistry", "Radio interference", "Screen resolution"],
            "Wearables collect personal data about people's habits and health, which is a privacy concern.",
        ),
        (
            3,
            "understand",
            "Why do battery-powered IoT sensors usually sleep most of the time and wake up only to send data?",
            [
                "To save energy so the battery lasts longer",
                "To get more processing power from the CPU",
                "To make the radio signal travel much further",
                "To store more readings in their small memory",
            ],
            "Energy is limited for battery-powered devices, so they sleep most of the time to save it.",
        ),
    ],
    "IOTM": [
        (
            1,
            "recognize",
            "Which IoT component connects local devices to the internet and can translate between protocols?",
            ["Gateway", "Sensor", "Actuator", "Dashboard"],
            "A gateway connects local devices to the internet and can translate, for example, from Zigbee to Wi-Fi.",
        ),
        (
            1,
            "recognize",
            "What is an IoT node usually built around?",
            [
                "A microcontroller with a radio",
                "A large database server",
                "A desktop graphics card",
                "A fibre-optic switch",
            ],
            "An IoT node is usually built around a microcontroller with a radio.",
        ),
        (
            1,
            "recognize",
            "In an IoT system, what is the main job of the cloud or server platform?",
            [
                "To store and analyse data from the devices",
                "To measure the room temperature directly",
                "To physically switch the lights on and off",
                "To supply power to battery-powered devices",
            ],
            "The cloud or server platform stores and analyses the data; sensors measure and actuators act.",
        ),
        (
            2,
            "recognize",
            "What are the three layers of the basic IoT architecture?",
            [
                "Perception, network and application",
                "Physical, data link and transport",
                "Client, server and database",
                "Input, storage and output",
            ],
            "The basic three-layer IoT architecture has a perception layer, a network layer and an application layer.",
        ),
        (
            2,
            "recognize",
            "Which layer of the three-layer IoT architecture contains the sensors and actuators?",
            ["Perception layer", "Application layer", "Network layer", "Business layer"],
            "The perception (sensing) layer contains the sensors and actuators.",
        ),
        (
            2,
            "recognize",
            "Which layer does the five-layer IoT architecture add between the network and application layers?",
            ["Processing layer", "Presentation layer", "Physical layer", "Session layer"],
            "The five-layer architecture adds a processing layer (middleware) between the network and application layers.",
        ),
        (
            3,
            "recognize",
            "In which IoT communication model do devices talk directly to each other, for example a switch and "
            "a bulb over Bluetooth?",
            ["Device-to-device", "Device-to-cloud", "Device-to-gateway", "Back-end data sharing"],
            "In the device-to-device model, devices communicate directly with each other.",
        ),
        (
            1,
            "understand",
            "In a home automation system, a motion sensor detects a person and the hall light turns on. What "
            "is the role of the light?",
            [
                "An actuator that acts on a command",
                "A sensor that measures motion",
                "A gateway that links two networks",
                "A broker that routes the messages",
            ],
            "The light changes the physical world when it receives a command, so it is an actuator.",
        ),
        (
            1,
            "understand",
            "Smart bulbs in a house use Zigbee, but the cloud service can only be reached over Wi-Fi. Which "
            "component solves this?",
            [
                "A hub that translates between Zigbee and Wi-Fi",
                "A second Zigbee bulb next to the Wi-Fi router",
                "A larger battery inside every one of the bulbs",
                "A mobile app that shows the status of the bulbs",
            ],
            "A gateway (hub) connects local devices to the internet and translates between protocols.",
        ),
        (
            2,
            "understand",
            "A team is choosing between Wi-Fi, LoRa and cellular to send sensor data to a server. Which layer "
            "of the three-layer architecture are they designing?",
            ["Network layer", "Perception layer", "Application layer", "Business layer"],
            "The network layer transmits data using technologies such as Wi-Fi, cellular networks, Zigbee or LoRa.",
        ),
        (
            2,
            "understand",
            "A system must store and analyse terabytes of sensor data before showing results in an app. In "
            "the five-layer architecture, which layer does this work?",
            ["Processing layer", "Perception layer", "Business layer", "Network layer"],
            "The processing layer (middleware) stores, analyses and processes large amounts of data.",
        ),
        (
            2,
            "understand",
            "A smart parking app shows drivers where the free parking spaces are. Which layer of the IoT "
            "architecture does the app belong to?",
            ["Application layer", "Perception layer", "Network layer", "Processing layer"],
            "The application layer delivers services, such as a smart parking app, to users.",
        ),
        (
            3,
            "understand",
            "A fitness band sends data via Bluetooth to the owner's phone, and the phone uploads it to the "
            "cloud. Which communication model is this?",
            ["Device-to-gateway", "Device-to-device", "Device-to-cloud", "Back-end data sharing"],
            "The phone acts as a local gateway that forwards the band's data to the cloud.",
        ),
        (
            3,
            "understand",
            "A thermostat company shares its users' energy data, with their permission, with the electricity "
            "provider's platform. Which communication model is this?",
            ["Back-end data sharing", "Device-to-device", "Device-to-gateway", "Device-to-cloud"],
            "Data collected in one cloud service is shared with another authorised service: back-end data sharing.",
        ),
    ],
    "MSG": [
        (
            1,
            "recognize",
            "Which messaging model does MQTT use?",
            ["Publish/subscribe", "Request/response", "Peer-to-peer streaming", "Remote procedure call"],
            "MQTT uses a publish/subscribe model with a central broker.",
        ),
        (
            1,
            "recognize",
            "In MQTT, what is the server that receives messages and forwards them to subscribers called?",
            ["Broker", "Router", "Gateway", "Proxy"],
            "Clients send messages to a central server called a broker, which forwards them to subscribers.",
        ),
        (
            1,
            "recognize",
            "What is the default port for MQTT without TLS?",
            ["1883", "80", "443", "5683"],
            "MQTT uses port 1883 by default and 8883 over TLS; 5683 is the CoAP port.",
        ),
        (
            2,
            "recognize",
            "Which MQTT QoS level delivers a message exactly once?",
            ["QoS 2", "QoS 0", "QoS 1", "QoS 3"],
            "QoS 2 uses a four-step handshake to deliver a message exactly once; there is no QoS 3.",
        ),
        (
            2,
            "recognize",
            "What does the broker do with a retained message?",
            [
                "Stores it and sends it to new subscribers of the topic",
                "Deletes it after the first subscriber reads it",
                "Sends it back only to the client that published it",
                "Hides it until the publisher connects again",
            ],
            "A retained message is stored for its topic and sent immediately to new subscribers.",
        ),
        (
            3,
            "recognize",
            "Which transport protocol does CoAP use by default?",
            ["UDP", "TCP", "HTTP", "SCTP"],
            "Unlike HTTP, CoAP runs over UDP, by default on port 5683.",
        ),
        (
            3,
            "recognize",
            "Which CoAP message type must be acknowledged by the receiver?",
            ["Confirmable (CON)", "Non-confirmable (NON)", "Reset (RST)", "Notification (NTF)"],
            "Confirmable messages must be acknowledged with an ACK and are retransmitted if no ACK arrives.",
        ),
        (
            1,
            "understand",
            "A client subscribes to the topic home/+/temperature. Which published topic will it receive?",
            [
                "home/kitchen/temperature",
                "home/kitchen/humidity",
                "home/floor1/kitchen/temperature",
                "office/kitchen/temperature",
            ],
            "The plus sign matches exactly one level, so only home/<one level>/temperature matches.",
        ),
        (
            1,
            "understand",
            "Which subscription receives every message published under home, at any depth?",
            ["home/#", "home/+", "home/*", "#/home"],
            "The hash sign matches all remaining levels and must be the last character.",
        ),
        (
            2,
            "understand",
            "A sensor sends a temperature reading every second, and losing one reading does not matter. "
            "Which QoS level is the most efficient choice?",
            ["QoS 0", "QoS 1", "QoS 2", "QoS 3"],
            "QoS 0 (at most once) has no acknowledgement overhead; an occasional lost reading is acceptable here.",
        ),
        (
            2,
            "understand",
            "A door lock must receive the 'unlock' command once and only once, even on an unreliable "
            "network. Which QoS level fits?",
            ["QoS 2", "QoS 0", "QoS 1", "QoS 3"],
            "Only QoS 2 guarantees exactly-once delivery; QoS 1 may deliver the command twice.",
        ),
        (
            2,
            "understand",
            "A monitoring app wants to know when a sensor goes offline unexpectedly. Which MQTT feature "
            "should the sensor set when it connects?",
            ["Last Will and Testament", "Retained message", "Topic wildcard", "Persistent topic"],
            "The broker publishes the Last Will message if the client disconnects unexpectedly.",
        ),
        (
            3,
            "understand",
            "A client sends a CoAP GET request for /temperature and the resource exists. Which response "
            "code is typical?",
            ["2.05 Content", "4.04 Not Found", "5.00 Internal Server Error", "2.01 Created"],
            "2.05 Content returns the resource; 4.04 means it does not exist.",
        ),
        (
            3,
            "understand",
            "A dashboard must be told every time a sensor's value changes, without sending repeated GET "
            "requests. Which CoAP feature helps?",
            ["Observe", "Reset message", "Non-confirmable message", "Port 5683"],
            "With the Observe option, the server sends notifications whenever the resource changes.",
        ),
    ],
}
