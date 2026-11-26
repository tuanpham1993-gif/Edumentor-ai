# ruff: noqa: ISC004 — dữ liệu đề: chuỗi dài ngắt dòng trong danh sách là cố ý
"""Đoạn tri thức khóa 494 — (mã kỹ năng, tiêu đề, nội dung). Mã đoạn: <KỸ NĂNG>-K01, K02… theo thứ tự."""

CHUNKS = [
    (
        "IOT",
        "What the Internet of Things is",
        "The Internet of Things (IoT) is a network of physical objects, called things, that have sensors, software and "
        "network connectivity so they can collect data and exchange it with other devices and systems over the internet. "
        "Each thing needs a unique identity, such as an IP address or a device ID, so that it can be found and addressed. "
        "Things sense their environment, for example temperature, motion or light, and some can also act on it through "
        "actuators such as motors, valves or switches. Key characteristics of IoT are connectivity, sensing, unique "
        "identity, heterogeneity (devices from many vendors with different hardware and protocols), very large scale "
        "(billions of devices) and dynamic change, because devices join, leave, move or sleep to save energy. Many IoT "
        "devices are constrained: they have little memory, low processing power and run on batteries.",
    ),
    (
        "IOT",
        "Applications of IoT",
        "IoT is used in many sectors. In smart homes, connected lights, thermostats, door locks and cameras can be "
        "monitored and controlled from a phone, and rules can automate them, such as turning off lights when nobody is in "
        "a room. In agriculture, soil moisture sensors tell an irrigation system when to water crops, which saves water. "
        "In healthcare, wearable devices track heart rate or blood glucose and can alert doctors remotely. In industry, "
        "sensors on machines measure vibration and temperature to predict failures before they happen, which is called "
        "predictive maintenance. In smart cities, IoT supports smart parking, street lights that dim when roads are empty, "
        "and air quality monitoring.",
    ),
    (
        "IOT",
        "Challenges of IoT",
        "IoT also brings challenges. Security is a major one: many devices ship with default passwords and rarely get "
        "software updates, so attackers can take them over, for example to build a botnet. Privacy is another, because "
        "sensors in homes and wearables collect personal data about people's habits and health. Interoperability is hard "
        "because devices from different vendors use different protocols and data formats, so they cannot always work "
        "together; standards and gateways help. Energy is limited for battery-powered devices, so they must use low-power "
        "hardware and radios and sleep most of the time. Scalability matters because a system may have to manage millions "
        "of devices and handle large volumes of data.",
    ),
    (
        "IOTM",
        "Components of an IoT system",
        "A typical IoT system has several components. Sensors measure physical quantities such as temperature, humidity or "
        "motion, and actuators change the physical world, for example by switching a relay or turning a motor. The sensors "
        "and actuators are attached to an IoT node (device), usually built around a microcontroller with a radio. A gateway "
        "connects local devices to the internet and can translate between protocols, for example from Zigbee or Bluetooth "
        "to Wi-Fi or Ethernet, and can filter or aggregate data. The network carries the data, and a cloud or server "
        "platform stores and analyses it. Finally, an application or user interface, such as a mobile app or dashboard, "
        "lets people see the data and send commands. In home automation, a motion sensor in a room sends an event through "
        "a hub (gateway) to the cloud, and a rule turns on the light.",
    ),
    (
        "IOTM",
        "Layered IoT architectures",
        "IoT architectures are often described in layers. The basic three-layer architecture has a perception layer, a "
        "network layer and an application layer. The perception layer (also called the sensing or device layer) contains "
        "sensors and actuators that collect data from the physical world. The network layer transmits that data to other "
        "devices and servers using technologies such as Wi-Fi, cellular networks, Zigbee or LoRa. The application layer "
        "delivers services to users, such as a smart home app or a smart city service. A five-layer architecture adds a "
        "processing layer (middleware) between the network and application layers to store, analyse and process large "
        "amounts of data, and a business layer on top that manages the whole system, including business models and user "
        "privacy.",
    ),
    (
        "IOTM",
        "Communication models and design goals",
        "IoT devices communicate in four common models. In the device-to-device model, devices talk directly to each "
        "other, for example a light switch and a bulb using Bluetooth or Zigbee. In the device-to-cloud model, a device "
        "connects directly to a cloud service over the internet, for example through Wi-Fi. In the device-to-gateway model, "
        "devices connect to a local gateway, such as a smartphone or hub, which forwards data to the cloud. In the back-end "
        "data-sharing model, data collected in one cloud service is shared with other authorised services so they can "
        "combine and analyse it. Design goals for IoT systems include low power consumption, low cost per device, "
        "scalability, reliability, security and privacy by design, and interoperability between devices from different "
        "vendors.",
    ),
    (
        "MSG",
        "MQTT basics",
        "MQTT (Message Queuing Telemetry Transport) is a lightweight messaging protocol designed for constrained devices "
        "and unreliable networks. It uses a publish/subscribe model: clients do not send messages directly to each other "
        "but to a central server called a broker. A client that sends data publishes a message to a topic, a text string "
        "such as home/livingroom/temperature, and the broker forwards the message to every client that has subscribed to "
        "that topic. Topics are hierarchical, with levels separated by slashes. Subscribers can use wildcards: the plus "
        "sign (+) matches exactly one level, so home/+/temperature matches home/kitchen/temperature, and the hash sign (#) "
        "matches all remaining levels and must be the last character, so home/# matches every topic under home. MQTT runs "
        "over TCP; the default port is 1883, and 8883 is used for MQTT over TLS.",
    ),
    (
        "MSG",
        "MQTT quality of service and session features",
        "MQTT offers three Quality of Service (QoS) levels for delivering a message. QoS 0 means at most once: the message "
        "is sent once without acknowledgement, so it may be lost. QoS 1 means at least once: the sender keeps the message "
        "until it receives a PUBACK, so the message arrives but may be duplicated. QoS 2 means exactly once: a four-step "
        "handshake (PUBLISH, PUBREC, PUBREL, PUBCOMP) makes sure the message arrives once, at the cost of more overhead. A "
        "retained message is stored by the broker for its topic and sent immediately to new subscribers, so they get the "
        "last known value. The Last Will and Testament is a message the client registers when it connects; the broker "
        "publishes it if the client disconnects unexpectedly. The keep-alive interval tells the broker how long the client "
        "may stay silent; the client sends PINGREQ packets to show it is still connected.",
    ),
    (
        "MSG",
        "CoAP",
        "CoAP (Constrained Application Protocol) is a web transfer protocol for constrained devices and networks, "
        "standardised by the IETF in RFC 7252. Like HTTP it follows the REST style: resources are identified by URIs and "
        "accessed with the methods GET, POST, PUT and DELETE, and responses use codes similar to HTTP, such as 2.05 Content "
        "or 4.04 Not Found. Unlike HTTP, CoAP runs over UDP, by default on port 5683, and uses a compact 4-byte fixed header "
        "to save bandwidth and energy. Because UDP is unreliable, CoAP has its own message types: Confirmable (CON) "
        "messages must be acknowledged with an Acknowledgement (ACK) and are retransmitted if no ACK arrives; "
        "Non-confirmable (NON) messages are not acknowledged; a Reset (RST) message indicates that a received message "
        "could not be processed. With the Observe option, a client can register interest in a resource and the server "
        "sends notifications whenever it changes.",
    ),
]
