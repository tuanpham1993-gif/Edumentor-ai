# ruff: noqa: ISC004 — dữ liệu đề: chuỗi dài ngắt dòng trong danh sách là cố ý
"""Tự luận khóa 494 (đợt 1: IOT, IOTM, MSG · đợt 2: SENS, RO, NI · đợt 3: DA, DAT).
Mỗi ý: (câu mô tả, điểm, main_keywords, sub_keywords).

Câu mô tả theo MỨC TỐI THIỂU, hai mẫu cố định (Tuấn duyệt 26/11, khớp quy tắc 8 và 12 của prompt chấm):
  "<ý> (any one of: a, b, c)."       nêu MỘT chi tiết là đạt; danh sách KHÔNG dùng "and"
  "<chủ thể> (both needed: a; b)."   phải đủ; KHÔNG có câu tóm tắt ở đầu (Gemini coi nó là ý chính)
Từ khóa chính = phần giải thích / cách xử lý; tên khái niệm làm chủ thể (sub) khi cần gắn đúng đối tượng.

PROBES: bài thử bộ chấm từ khóa — (nhãn, bài, điều kiện ">=7" / "<=3" / "c"); "c" = GIỚI HẠN ĐÃ BIẾT của bộ
        chấm từ khóa, chỉ in ra (đảo vai trò trong cùng một vế câu — chờ (c); câu ngắn toàn từ của đề bị luật chép
        đề L7 bỏ dù đúng).
GEMINI_PROBES: (bản A, bản B) cho probe_gemini.py — A: mỗi ý đúng 1 chi tiết, ý "both" chỉ 1 phần
        (mong Gemini none); B: chi tiết khác, ý "both" đủ 2 phần.
"""

ESSAY = {
    "IOT": [
        (
            1,
            "easy",
            "Explain what the Internet of Things is and what an object needs in order to become part of it.",
            [
                (
                    "Things exchange data over a network (any one of: collect data, send data, share data, exchange data).",
                    4,
                    [
                        "exchange data",
                        "collect data",
                        "share data",
                        "send data",
                        "transmit data",
                        "exchange information",
                        "share information",
                        "send and receive",
                        "communicate",
                    ],
                    [],
                ),
                (
                    "What an object needs (both needed: sensors; network connectivity).",
                    3,
                    [
                        "sensor",
                        "connectivity",
                        "internet connection",
                        "network connection",
                        "connect to the internet",
                        "connected to the internet",
                    ],
                    [],
                ),
                (
                    "Each thing has a unique identity",
                    3,
                    ["unique identity", "unique id", "unique identifier", "unique address", "ip address", "device id"],
                    [],
                ),
            ],
            "The Internet of Things is a network of physical things that collect and exchange data over the "
            "internet. An object needs sensors, software and network connectivity. It also needs a unique identity, "
            "such as an IP address.",
        ),
        (
            2,
            "easy",
            "Describe how IoT is used in healthcare and in industry, and give the benefit of each.",
            [
                (
                    "Healthcare use of IoT (any one of: wearables track heart rate or blood glucose, doctors are alerted "
                    "remotely).",
                    4,
                    [
                        "wearable",
                        "heart rate",
                        "blood glucose",
                        "blood sugar",
                        "smartwatch",
                        "fitness tracker",
                        "vital sign",
                        "alert",
                        "remote",
                        "remotely",
                        "doctor",
                    ],
                    [],
                ),
                (
                    "Industry: sensors on machines measure vibration or temperature",
                    3,
                    ["vibration", "machine", "equipment", "factory", "temperature"],
                    ["machine", "factory", "industry", "equipment"],
                ),
                (
                    "Industry benefit (any one of: failures predicted before they happen, fewer breakdowns, less "
                    "downtime).",
                    3,
                    [
                        "predict failure",
                        "predictive maintenance",
                        "before they happen",
                        "before it happen",
                        "before fail",
                        "before failing",
                        "before break",
                        "fewer failures",
                        "fewer breakdowns",
                        "less downtime",
                        "repaired early",
                        "repair early",
                    ],
                    [],
                ),
            ],
            "In healthcare, wearable devices track a patient's heart rate or blood glucose and alert doctors "
            "remotely when something is wrong. In industry, sensors on machines measure vibration and temperature, "
            "so the company can predict failures before they happen and repair the machine in time.",
        ),
        (
            3,
            "easy",
            "Explain why security and privacy are serious problems for IoT devices used in homes.",
            [
                (
                    "Devices are easy to break into (any one of: default passwords, weak passwords, rarely updated).",
                    4,
                    [
                        "default password",
                        "factory password",
                        "same password",
                        "weak password",
                        "rarely updated",
                        "rarely get update",
                        "not updated",
                        "never updated",
                        "no update",
                        "without update",
                        "outdated",
                    ],
                    [],
                ),
                (
                    "Attackers can take the devices over (any one of: hijack, control the device, use it in a botnet).",
                    3,
                    ["botnet", "hijack", "hacker", "attacker", "attack"],
                    [],
                ),
                (
                    "Sensors collect personal data about people (any one of: habits, health, daily life).",
                    3,
                    ["personal data", "personal information", "habit", "health", "private", "daily life"],
                    [],
                ),
            ],
            "Many home IoT devices ship with default passwords and rarely get software updates, so attackers can "
            "take them over and use them in a botnet. Privacy is also at risk, because cameras, sensors and "
            "wearables collect personal data about people's habits and health.",
        ),
        (
            1,
            "easy",
            "IoT devices and systems are often described as constrained, heterogeneous and dynamic. Explain what "
            "each of these three characteristics means.",
            [
                (
                    "Constrained: devices have limited resources (any one of: little memory, low processing power, battery "
                    "power).",
                    4,
                    [
                        "little memory",
                        "limited memory",
                        "low memory",
                        "small memory",
                        "low processing power",
                        "limited processing",
                        "weak processor",
                        "battery",
                    ],
                    [],
                ),
                (
                    "Heterogeneous: devices differ from each other (any one of: many vendors, different hardware, "
                    "different protocols).",
                    3,
                    [
                        "many vendors",
                        "different vendors",
                        "different manufacturers",
                        "different hardware",
                        "different protocols",
                        "different types of devices",
                        "different kinds of devices",
                        "many kinds",
                    ],
                    [],
                ),
                (
                    "Dynamic: the set of devices keeps changing (any one of: devices join, leave, move, go offline).",
                    3,
                    ["join", "leave", "move", "go offline", "disconnect", "come and go"],
                    [],
                ),
            ],
            "Constrained means that many devices have little memory and low processing power and run on batteries. "
            "Heterogeneous means that the devices come from many vendors with different hardware and protocols. "
            "Dynamic means that devices join, leave or move all the time, so the system keeps changing.",
        ),
        (
            2,
            "advanced",
            "A farm wants to use less water for irrigation. Describe an IoT solution: which device measures the "
            "field, which device acts on the water supply, and what rule the system follows.",
            [
                (
                    "Soil moisture sensors measure the field",
                    3,
                    ["soil moisture", "moisture sensor", "humidity sensor"],
                    [],
                ),
                (
                    "An actuator such as a valve or pump controls the water",
                    3,
                    ["valve", "pump", "actuator", "sprinkler"],
                    [],
                ),
                (
                    "Rule: water only when the soil is dry or below a threshold",
                    2,
                    ["dry", "threshold", "only when needed", "only when necessary"],
                    [],
                ),
                (
                    "Benefit: less water is used",
                    2,
                    [
                        "save water",
                        "less water",
                        "reduce water",
                        "water use",
                        "waste water",
                        "wasting water",
                        "water consumption",
                    ],
                    [],
                ),
            ],
            "Soil moisture sensors are placed in the fields to measure how wet the soil is. A valve on the water "
            "pipe is the actuator that the system opens or closes. The rule is to open the valve only when the soil "
            "is dry, so the farm saves water.",
        ),
        (
            3,
            "advanced",
            "A city plans to install 100,000 IoT sensors from several vendors, most of them running on batteries. "
            "For each of these three challenges — security, interoperability and energy — suggest one concrete way "
            "to handle it. Also explain why energy matters so much for this project.",
            [
                (
                    "Security: one concrete protection (any one of: unique or strong passwords, regular updates, "
                    "encryption).",
                    3,
                    [
                        "unique password",
                        "strong password",
                        "change default password",
                        "change the default password",
                        "software update",
                        "security update",
                        "firmware update",
                        "regular update",
                        "update regularly",
                        "patch",
                        "encryption",
                        "encrypt",
                    ],
                    [],
                ),
                (
                    "Interoperability: require open standards or use gateways that translate protocols",
                    2,
                    ["standard", "gateway", "translate", "common protocol", "same protocol"],
                    [],
                ),
                (
                    "Energy: one way to save power (any one of: low-power hardware or radios, sleep most of the time, "
                    "energy harvesting).",
                    3,
                    ["low-power", "low power", "sleep", "energy harvesting", "solar"],
                    [],
                ),
                (
                    "Why energy matters: batteries are hard to service at this scale (any one of: replacing or recharging "
                    "100,000 batteries is slow, costly, impractical).",
                    2,
                    ["replace", "recharge", "battery life", "change the batteries", "costly", "expensive"],
                    [],
                ),
            ],
            "For security, every sensor should get a unique password and regular security updates. For "
            "interoperability, the city should require open standards or use gateways that translate between "
            "protocols. For energy, the sensors should use low-power radios and sleep most of the time, waking up "
            "only to send data. Energy matters so much because replacing 100,000 batteries would be slow and "
            "expensive.",
        ),
    ],
    "IOTM": [
        (
            1,
            "easy",
            "Explain what sensors, actuators and a gateway each do in an IoT system.",
            [
                (
                    "Sensors measure physical quantities",
                    3,
                    ["measure", "detect", "sense", "collect data", "read"],
                    ["sensor"],
                ),
                (
                    "Actuators change the physical world",
                    3,
                    ["change", "act", "switch", "turn", "move", "control", "open"],
                    ["actuator"],
                ),
                (
                    "A gateway links local devices to the internet (any one of: connects them to the internet, translates "
                    "protocols, forwards their data).",
                    4,
                    ["connect", "translate", "forward", "bridge", "link"],
                    ["gateway", "hub"],
                ),
            ],
            "Sensors measure the physical world, for example temperature. Actuators change it, for example by "
            "switching a relay. A gateway connects the local devices to the internet and translates between "
            "protocols such as Zigbee and Wi-Fi.",
        ),
        (
            2,
            "easy",
            "In the three-layer IoT architecture, which layer is at the bottom and which is at the top? Describe "
            "what the bottom layer does.",
            [
                (
                    "The lowest layer is the perception layer",
                    3,
                    ["perception layer", "sensing layer", "device layer"],
                    ["lowest", "bottom", "first"],
                ),
                (
                    "The top layer is the application layer",
                    3,
                    ["application layer"],
                    ["top", "highest", "last", "upper"],
                ),
                (
                    "The bottom layer collects data from the physical world (any one of: with sensors, with actuators, "
                    "senses the environment).",
                    4,
                    ["collect data", "gather data", "sensor", "physical world"],
                    [],
                ),
            ],
            "The lowest layer is the perception layer. It uses sensors and actuators to collect data from the "
            "physical world. The top layer is the application layer, which delivers services to users.",
        ),
        (
            3,
            "easy",
            "Explain the difference between the device-to-cloud and the device-to-gateway communication models.",
            [
                (
                    "Device-to-cloud: the device connects directly to a cloud service",
                    5,
                    ["directly", "straight", "own internet connection", "wi-fi", "wifi"],
                    ["device-to-cloud", "device to cloud"],
                ),
                (
                    "Device-to-gateway (both needed: a local gateway such as a hub or phone; it forwards the data onward "
                    "to the cloud).",
                    5,
                    ["hub", "smartphone", "phone", "gateway", "forward", "pass", "relay"],
                    ["device-to-gateway", "device to gateway"],
                ),
            ],
            "In the device-to-cloud model, the device connects directly to a cloud service over the internet, for "
            "example through Wi-Fi. In the device-to-gateway model, the device connects to a local hub or "
            "smartphone, which forwards the data to the cloud.",
        ),
        (
            3,
            "easy",
            "Explain why low power consumption and scalability are important design goals for IoT systems.",
            [
                (
                    "Low power: many devices run on batteries for a long time",
                    5,
                    ["battery", "years", "long time", "recharge", "replace"],
                    [],
                ),
                (
                    "Scalability: a system may grow very large (any one of: millions of devices, large volumes of data).",
                    5,
                    [
                        "million",
                        "billion",
                        "thousand",
                        "many devices",
                        "large number",
                        "large volume",
                        "more devices",
                        "grow",
                    ],
                    [],
                ),
            ],
            "Low power consumption matters because many devices run on batteries that must last for years. "
            "Scalability matters because a system may grow to millions of devices that produce large volumes of "
            "data.",
        ),
        (
            1,
            "advanced",
            "Design a home automation system that turns on the hall light when someone enters at night. Describe "
            "the components and map them to the three architecture layers.",
            [
                (
                    "A motion sensor detects the person",
                    2,
                    ["motion sensor", "pir", "presence sensor", "motion detector"],
                    [],
                ),
                (
                    "A smart bulb or relay is the actuator",
                    2,
                    ["smart bulb", "relay", "actuator", "smart switch", "smart light"],
                    [],
                ),
                (
                    "The network layer carries the data (any one of: via the hub, via the gateway, over Zigbee or Wi-Fi).",
                    2,
                    ["network layer"],
                    ["hub", "gateway", "zigbee", "wi-fi", "wifi", "data"],
                ),
                (
                    "Perception layer mapping (both needed: the motion sensor; the smart bulb or relay).",
                    2,
                    ["perception layer", "sensing layer", "device layer"],
                    ["sensor", "bulb", "relay", "actuator", "device"],
                ),
                (
                    "The rule runs in the application layer",
                    2,
                    ["application layer"],
                    ["rule", "app", "automation", "logic"],
                ),
            ],
            "A motion sensor detects a person, and a smart bulb is the actuator that switches the light. The sensor "
            "and the bulb belong to the perception layer. They talk to a hub over Zigbee, and the network layer "
            "carries the data to the cloud. The rule that turns on the light at night runs in the application "
            "layer.",
        ),
        (
            2,
            "advanced",
            "Describe the five-layer IoT architecture layer by layer, and explain what the two extra layers add "
            "compared with the three-layer model.",
            [
                (
                    "Perception layer: sensors collect data",
                    2,
                    ["collect", "sense", "sensor", "gather"],
                    ["perception", "sensing layer"],
                ),
                ("Network layer: transmits the data", 2, ["transmit", "send", "carry", "transfer"], ["network layer"]),
                (
                    "Processing layer: handles large amounts of data (any one of: stores, analyses, processes).",
                    2,
                    ["store", "analyse", "analyze", "analyses", "database", "big data", "large amount"],
                    ["processing layer", "middleware"],
                ),
                ("Application layer: delivers services to users", 2, ["service", "user", "app"], ["application layer"]),
                (
                    "Business layer: manages the whole system (any one of: overall management, business models, privacy).",
                    2,
                    ["manage", "business model", "privacy", "profit", "whole system"],
                    ["business layer"],
                ),
            ],
            "The perception layer has sensors and actuators that collect data. The network layer transmits the "
            "data. The processing layer, or middleware, stores and analyses large amounts of data. The application "
            "layer delivers services to users. The business layer manages the whole system, including business "
            "models and privacy.",
        ),
    ],
    "MSG": [
        (
            1,
            "easy",
            "Explain how messages travel from one client to another in MQTT.",
            [
                ("Messages go through a central broker", 4, ["broker", "central server"], []),
                ("A client publishes a message to a topic", 3, ["publish", "topic"], []),
                (
                    "The broker forwards the message to the subscribers",
                    3,
                    ["forward", "deliver", "pass", "route"],
                    ["broker"],
                ),
            ],
            "In MQTT, clients do not send messages directly to each other. A client publishes a message to a topic "
            "on a central broker, and the broker forwards it to every client that has subscribed to that topic.",
        ),
        (
            2,
            "easy",
            "Compare MQTT QoS 0 and QoS 1.",
            [
                (
                    "QoS 0 (both needed: delivered at most once or without acknowledgement; the message may be lost).",
                    5,
                    [
                        "at most once",
                        "no acknowledgement",
                        "no acknowledgment",
                        "without acknowledgement",
                        "without acknowledgment",
                        "no ack",
                        "without ack",
                        "not acknowledged",
                        "lost",
                        "fire and forget",
                    ],
                    ["qos 0", "qos0", "level 0"],
                ),
                (
                    "QoS 1 (both needed: delivered at least once or acknowledged with PUBACK; the message may be "
                    "duplicated).",
                    5,
                    [
                        "at least once",
                        "puback",
                        "acknowledgement",
                        "acknowledgment",
                        "acknowledged",
                        "ack",
                        "duplicate",
                        "more than once",
                        "resend",
                        "retransmit",
                    ],
                    ["qos 1", "qos1", "level 1"],
                ),
            ],
            "QoS 0 means at most once: the message is sent without acknowledgement, so it may be lost. QoS 1 means "
            "at least once: the sender keeps the message until it gets a PUBACK, so it arrives but may be "
            "duplicated.",
        ),
        (
            3,
            "easy",
            "Why does CoAP define both Confirmable and Non-confirmable messages?",
            [
                ("CoAP runs over unreliable UDP", 4, ["udp", "unreliable", "lose packets"], []),
                (
                    "Confirmable messages (both needed: acknowledged with an ACK; retransmitted if no ACK arrives).",
                    3,
                    [
                        "ack",
                        "acknowledge",
                        "acknowledgement",
                        "acknowledgment",
                        "retransmit",
                        "resend",
                        "sent again",
                        "repeat",
                    ],
                    ["confirmable", "con"],
                ),
                (
                    "Non-confirmable messages are not acknowledged, which saves resources (any one of: energy, bandwidth, "
                    "fewer messages).",
                    3,
                    [
                        "save energy",
                        "bandwidth",
                        "overhead",
                        "faster",
                        "less traffic",
                        "fewer messages",
                        "lost",
                        "not important",
                    ],
                    ["non-confirmable", "non"],
                ),
            ],
            "CoAP runs over UDP, which is unreliable. Confirmable messages must be acknowledged with an ACK and are "
            "retransmitted if no ACK arrives. Non-confirmable messages are not acknowledged, which saves energy and "
            "bandwidth for data that can be lost.",
        ),
        (
            3,
            "easy",
            "Give two ways in which CoAP is similar to HTTP and one way in which it is different.",
            [
                (
                    "Both follow the REST style: resources identified by URIs",
                    3,
                    ["rest", "restful", "uri", "url", "resource"],
                    [],
                ),
                (
                    "Like HTTP, CoAP uses requests with methods or codes (any one of: methods such as GET or POST, similar "
                    "response codes).",
                    3,
                    ["method", "response code", "status code", "post", "delete"],
                    [],
                ),
                (
                    "CoAP differs in transport or size (any one of: runs over UDP instead of TCP, small 4-byte header).",
                    4,
                    ["udp", "small header", "4-byte", "compact header"],
                    ["coap"],
                ),
            ],
            "Like HTTP, CoAP follows the REST style and identifies resources with URIs. It also uses methods such as "
            "GET and POST and response codes similar to HTTP. Unlike HTTP, CoAP runs over UDP instead of TCP.",
        ),
        (
            1,
            "advanced",
            "Design the MQTT messaging for a smart greenhouse with a temperature sensor and a fan in each of three "
            "rooms. Give example topics, a subscription that lets one dashboard read all rooms, and the delivery "
            "guarantee you would use for sensor data and for fan commands.",
            [
                ("All messages go through one broker", 2, ["broker"], []),
                (
                    "Each room has its own topic level (any one of: greenhouse/<room>/temperature, one topic per room).",
                    2,
                    ["greenhouse /", "/ temperature", "/ temp", "/ fan", "per room"],
                    [],
                ),
                (
                    "The dashboard subscribes with the single-level wildcard (any one of: +, plus sign, matches one "
                    "level).",
                    2,
                    ["+", "plus sign", "wildcard", "one level", "single level"],
                    [],
                ),
                (
                    "Sensor data: QoS 0 (at most once)",
                    2,
                    ["qos 0", "qos0", "at most once"],
                    ["sensor", "temperature", "reading"],
                ),
                (
                    "Fan commands: QoS 1 or QoS 2",
                    2,
                    ["qos 1", "qos 2", "qos1", "qos2", "at least once", "exactly once"],
                    ["fan", "command"],
                ),
            ],
            "All devices connect to one broker. Each room publishes to its own topic, for example "
            "greenhouse/room1/temperature, and each fan subscribes to a command topic such as greenhouse/room1/fan. "
            "The dashboard subscribes to greenhouse/+/temperature, where the plus sign matches one level, so it gets "
            "all rooms. Sensor readings use QoS 0, because a lost reading is replaced a second later. Fan commands "
            "use QoS 1, so a command is not lost.",
        ),
        (
            3,
            "advanced",
            "A battery-powered sensor network must choose between MQTT and CoAP. Compare the two protocols and "
            "recommend one for a device that only answers occasional requests from a server.",
            [
                ("MQTT runs over TCP", 2, ["tcp"], ["mqtt"]),
                ("MQTT needs a broker", 2, ["broker"], ["mqtt"]),
                (
                    "CoAP is light on the network (any one of: runs over UDP, small 4-byte header).",
                    2,
                    ["udp", "small header", "4-byte", "compact header"],
                    ["coap"],
                ),
                ("CoAP follows the REST style", 2, ["rest", "restful", "resource", "uri"], ["coap"]),
                ("Recommends CoAP", 2, ["recommend", "prefer", "choose", "pick"], ["coap"]),
            ],
            "MQTT runs over TCP and needs a broker, and devices keep a connection open. CoAP runs over UDP with a "
            "small 4-byte header, which saves energy. CoAP follows the REST style, where a server reads a resource "
            "with GET. For a device that only answers occasional requests, I recommend CoAP, because it needs no "
            "broker and no open TCP connection.",
        ),
    ],
    "SENS": [
        (
            1,
            "easy",
            "Sensors can be grouped by whether they need an external power source. Explain the difference between "
            "the two groups and give one example of each.",
            [
                (
                    "One group needs an excitation to give an output (any one of: external excitation, a power supply, a "
                    "current must be passed through it). The label active or passive is not required.",
                    4,
                    ["excitation", "excite", "current", "power supply", "powered", "battery"],
                    [],
                ),
                (
                    "The other group generates its own signal (any one of: self-generating, produces its own voltage, no "
                    "external power needed). The label active or passive is not required.",
                    3,
                    [
                        "generate",
                        "generates",
                        "produce",
                        "produces",
                        "make",
                        "makes",
                        "self-generating",
                        "without external",
                        "no external",
                    ],
                    [],
                ),
                (
                    "Examples (both needed: an excited sensor such as a thermistor, RTD or strain gauge; a "
                    "self-generating sensor such as a thermocouple, solar cell or piezoelectric sensor).",
                    3,
                    ["thermistor", "rtd", "strain gauge", "thermocouple", "solar cell", "piezoelectric", "piezo"],
                    [],
                ),
            ],
            "One group needs an external excitation to give an output; for example, a thermistor can only be read "
            "by passing a current through it. The other group is self-generating: it generates its own signal from "
            "the energy it measures; for example, a thermocouple produces its own small voltage from heat.",
        ),
        (
            3,
            "easy",
            "Explain the difference between the accuracy and the precision of a sensor.",
            [
                (
                    "Accuracy is closeness to the true value (any one of: close to the true value, close to the actual "
                    "value, small error from the real value).",
                    5,
                    ["true value", "actual value", "real value", "correct value", "reference value"],
                    ["accuracy", "accurate"],
                ),
                (
                    "Precision is closeness of repeated readings to each other (any one of: repeatability, consistent "
                    "readings, small spread).",
                    5,
                    [
                        "repeated",
                        "repeatability",
                        "repeat",
                        "close together",
                        "agree",
                        "consistent",
                        "spread",
                        "same result",
                    ],
                    ["precision", "precise"],
                ),
            ],
            "Accuracy is how close a reading is to the true value of the quantity. Precision is how close repeated "
            "readings of the same input are to each other, so a sensor can be precise but not accurate.",
        ),
        (
            3,
            "easy",
            "What is hysteresis in a sensor, and why can it be a problem for the readings?",
            [
                (
                    "The output for the same input depends on the direction of change (any one of: increasing versus "
                    "decreasing input, rising versus falling, depends on the previous value).",
                    5,
                    ["direction", "increasing", "decreasing", "rising", "falling", "previous"],
                    [],
                ),
                (
                    "Problem: the same input can give different readings (any one of: two possible readings, an error of "
                    "up to the hysteresis width, the reading is not unique).",
                    5,
                    [
                        "different reading",
                        "different readings",
                        "different output",
                        "different value",
                        "two reading",
                        "two readings",
                        "two value",
                        "not unique",
                        "uncertain",
                        "error",
                    ],
                    [],
                ),
            ],
            "Hysteresis means that the output for the same input depends on whether the input was increasing or "
            "decreasing. It is a problem because the same true value can give different readings, which adds an "
            "error.",
        ),
        (
            2,
            "easy",
            "Explain how a capacitive MEMS accelerometer turns acceleration into an electrical signal.",
            [
                (
                    "A proof mass on springs moves when the device accelerates (any one of: the mass moves, the mass "
                    "shifts, the springs bend).",
                    4,
                    ["move", "shift", "displace", "deflect", "bend"],
                    ["mass", "spring"],
                ),
                (
                    "The movement changes the capacitance of the plates (any one of: capacitance changes, one capacitance "
                    "rises while the other falls).",
                    3,
                    [
                        "capacitance change",
                        "change the capacitance",
                        "changes capacitance",
                        "change in capacitance",
                        "capacitance vary",
                        "capacitance increase",
                        "capacitance decrease",
                        "capacitance rise",
                        "capacitance rises",
                        "capacitance fall",
                        "capacitance falls",
                    ],
                    [],
                ),
                (
                    "The readout measures this change to obtain the acceleration (any one of: the change is proportional "
                    "to the acceleration, the circuit converts it to a voltage).",
                    3,
                    ["proportional", "convert", "measure", "calculate", "indicate"],
                    ["acceleration", "readout", "circuit"],
                ),
            ],
            "A capacitive MEMS accelerometer has a tiny proof mass held by springs. When the device accelerates, "
            "the mass moves relative to the frame, and this changes the capacitance between the mass and the fixed "
            "plates. The readout circuit measures the change, which is proportional to the acceleration.",
        ),
        (
            2,
            "advanced",
            "A cold-storage room must be kept between -30 degC and +10 degC with small temperature changes "
            "detected, and a furnace must be monitored up to 1000 degC where temperature can jump quickly. Which "
            "type of temperature sensor would you choose for each place? Justify each choice by range or response "
            "time.",
            [
                (
                    "Cold room: a thermistor or RTD (any one of: thermistor, RTD, platinum RTD, IC temperature sensor).",
                    2,
                    ["thermistor", "rtd", "ic temperature sensor", "platinum"],
                    ["cold", "storage", "room"],
                ),
                (
                    "Reason for the cold room (any one of: narrow range is enough, high sensitivity, accurate, stable).",
                    2,
                    [
                        "narrow range",
                        "small range",
                        "limited range",
                        "sensitive",
                        "sensitivity",
                        "accurate",
                        "accuracy",
                        "stable",
                    ],
                    [],
                ),
                ("Furnace: a thermocouple.", 2, ["thermocouple"], ["furnace", "1000"]),
                (
                    "Reason for the furnace by range (any one of: very wide range, works above 1000 degC, survives high "
                    "temperature).",
                    2,
                    ["wide range", "wide", "high temperature", "extreme temperature", "1000"],
                    [],
                ),
                (
                    "Reason by response time (any one of: a small junction responds quickly, fast response, follows "
                    "sudden jumps).",
                    2,
                    ["quickly", "fast", "small junction", "respond", "response time"],
                    [],
                ),
            ],
            "For the cold room I would choose a thermistor, because the range is narrow and a thermistor is very "
            "sensitive, so small changes are detected. For the furnace I would choose a thermocouple, because it "
            "works over a very wide range up to more than 1000 degC, and a thermocouple with a small junction "
            "responds quickly to sudden jumps.",
        ),
        (
            3,
            "advanced",
            "A greenhouse controller switches a fan on at 70 %RH. Two humidity sensors are offered. Sensor Alpha: "
            "accuracy +/-2 %RH, hysteresis 1 %RH, non-linearity 0.5 %RH. Sensor Beta: accuracy +/-5 %RH, hysteresis "
            "4 %RH, non-linearity 3 %RH. Which sensor would you choose, and what would each of Beta's three figures "
            "mean for when the fan switches?",
            [
                (
                    "Chooses Alpha.",
                    2,
                    ["alpha", "choose alpha", "pick alpha"],
                    ["choose", "pick", "prefer", "select", "recommend", "better", "best"],
                ),
                (
                    "Beta's accuracy: the fan may switch anywhere from about 65 to 75 %RH (any one of: up to 5 %RH from "
                    "the true humidity, switches too early or too late).",
                    3,
                    ["65", "75", "early", "late", "wrong humidity", "true humidity"],
                    ["beta", "accuracy"],
                ),
                (
                    "Beta's hysteresis: the switching point depends on whether humidity is rising or falling (any one of: "
                    "different point when rising than falling, up to 4 %RH apart).",
                    3,
                    ["rising", "falling", "increasing", "decreasing", "direction"],
                    [],
                ),
                (
                    "Beta's non-linearity: the error is different at different humidity levels (any one of: error changes "
                    "across the range, readings do not follow a straight line).",
                    2,
                    [
                        "straight line",
                        "not follow a straight line",
                        "non-linear",
                        "nonlinear",
                        "different level",
                        "across the range",
                        "changes across",
                        "not proportional",
                        "different humidity",
                    ],
                    [],
                ),
            ],
            "I would choose Alpha. With Beta, the accuracy of +/-5 %RH means the fan could switch anywhere from "
            "about 65 to 75 %RH. Its hysteresis of 4 %RH means the switching point is different when humidity is "
            "rising than when it is falling. Its non-linearity means the error changes across the range, so the "
            "readings do not follow a straight line.",
        ),
    ],
    "RO": [
        (
            1,
            "easy",
            "Why does a sensor readout chain usually amplify the sensor signal before the ADC?",
            [
                (
                    "Sensor signals are often small (any one of: millivolts, microvolts, a weak signal).",
                    3,
                    ["small", "millivolt", "microvolt", "mv", "weak", "tiny", "low voltage"],
                    [],
                ),
                (
                    "Without amplification only a small part of the ADC range is used (any one of: few codes change, poor "
                    "resolution, most of the range is unused).",
                    4,
                    [
                        "poor resolution",
                        "low resolution",
                        "small part",
                        "small fraction",
                        "1 %",
                        "unused",
                        "wasted",
                        "only a few codes",
                        "only a few adc codes",
                    ],
                    [],
                ),
                (
                    "Amplifying scales the signal to the ADC's full range (any one of: use the full scale, match the ADC "
                    "input range).",
                    3,
                    [
                        "full range",
                        "full scale",
                        "full-scale",
                        "whole range",
                        "entire range",
                        "match the range",
                        "input range",
                    ],
                    [],
                ),
            ],
            "Sensor signals are often small, only millivolts or microvolts. Fed directly into an ADC, such a signal "
            "uses only a small part of the range, so few codes change and the resolution is poor. Amplifying first "
            "scales the signal to the ADC's full range.",
        ),
        (
            3,
            "easy",
            "What is quantization in an ADC, and how large can the quantization error be?",
            [
                (
                    "Quantization maps each sample to one of a limited number of levels (any one of: nearest level, "
                    "rounding, discrete steps).",
                    5,
                    ["nearest level", "nearest", "round", "discrete", "staircase", "step"],
                    [],
                ),
                (
                    "The error is at most half an LSB (any one of: half an LSB, LSB / 2, 0.5 LSB).",
                    5,
                    ["half", "lsb / 2", "0.5 lsb"],
                    [],
                ),
            ],
            "Quantization maps each sampled value to the nearest of the ADC's discrete levels, so the input becomes a "
            "staircase. With rounding to the nearest level, the quantization error is at most half an LSB.",
        ),
        (
            2,
            "easy",
            "How fast must an ADC sample a signal, and what goes wrong if it samples too slowly?",
            [
                (
                    "Sample faster than twice the highest signal frequency (any one of: more than twice, more than 2f, "
                    "double the highest frequency).",
                    5,
                    ["twice", "two times", "2 times", "double", "2f", "2 f", "2 x"],
                    [],
                ),
                (
                    "Too slow causes aliasing (any one of: the signal appears at a wrong lower frequency, fast changes are "
                    "missed, the signal is distorted).",
                    5,
                    ["aliasing", "alias", "wrong frequency", "lower frequency", "missed", "miss", "distort"],
                    [],
                ),
            ],
            "The ADC must sample at more than twice the highest frequency in the signal. If it samples too slowly, "
            "fast changes are missed and the signal appears at a wrong, lower frequency, which is called aliasing.",
        ),
        (
            3,
            "easy",
            "What do you gain and what do you lose when you choose an ADC with more bits?",
            [
                (
                    "Gain: a smaller LSB (any one of: finer resolution, more levels, smaller steps).",
                    5,
                    [
                        "smaller lsb",
                        "finer",
                        "fine",
                        "fine resolution",
                        "higher resolution",
                        "better resolution",
                        "smaller step",
                        "more level",
                        "more code",
                        "lsb become smaller",
                        "lsb is smaller",
                    ],
                    [],
                ),
                (
                    "Loss (any one of: more power, slower conversion, higher cost, more data).",
                    5,
                    ["power", "slower", "slow", "cost", "expensive", "more data", "memory"],
                    [],
                ),
            ],
            "More bits give a smaller LSB, so the resolution is finer. The cost is that the ADC usually uses more "
            "power, converts more slowly, is more expensive and produces more data.",
        ),
        (
            2,
            "advanced",
            "A temperature sensor outputs 10 mV per degC. It is read by a 12-bit ADC with a full-scale reference of "
            "4.096 V. Calculate the LSB size and the smallest temperature change the system can resolve, showing your "
            "method.",
            [
                (
                    "Method for the LSB (any one of: Vref / 2^N, 4.096 / 4096, divide 4.096 V by 2^12).",
                    2,
                    ["4096", "2 ** 12", "vref / 2", "4.096 divided", "4.096 v divided"],
                    [],
                ),
                ("Result: LSB = 1 mV.", 3, ["1 mv", "1mv", "0.001 v", "1 millivolt", "0.001"], []),
                (
                    "Method for the temperature resolution (any one of: LSB / sensitivity, 1 mV / 10 mV per degC).",
                    2,
                    ["sensitivity", "/ 10", "divide"],
                    [],
                ),
                (
                    "Result: 0.1 degC.",
                    3,
                    ["0.1"],
                    ["degc", "degree", "celsius", "deg", "resolution", "temperature", "resolve"],
                ),
            ],
            "The LSB is Vref / 2^N = 4.096 V / 4096 = 1 mV. The temperature resolution is the LSB divided by the "
            "sensitivity: 1 mV / 10 mV per degC = 0.1 degC.",
        ),
        (
            3,
            "advanced",
            "A pressure sensor gives 0 to 100 mV. The ADC input range is 0 to 4.096 V. Choose an amplifier gain that "
            "uses the ADC range well without saturating it, and explain your choice.",
            [
                (
                    "Method (any one of: gain = ADC range / largest sensor signal, 4.096 / 0.1, 4096 mV / 100 mV).",
                    2,
                    [
                        "4.096 / 0.1",
                        "4096 / 100",
                        "4096 mv / 100 mv",
                        "4.096 v / 0.1 v",
                        "range divided",
                        "divided by the largest",
                        "divide",
                    ],
                    [],
                ),
                ("Result: a gain of about 40, no more than 40.96.", 3, ["40", "40.96"], []),
                (
                    "Reason: it uses most of the ADC range (any one of: best resolution, most codes used, close to full "
                    "scale).",
                    2,
                    ["most of the range", "full range", "full scale", "whole range", "resolution", "most code"],
                    [],
                ),
                (
                    "A higher gain would saturate the ADC (any one of: clipping, exceeds 4.096 V, output stuck at the "
                    "maximum code).",
                    3,
                    ["saturate", "saturation", "clip", "exceed", "maximum code"],
                    [],
                ),
            ],
            "The gain is the ADC range divided by the largest sensor signal: 4.096 V / 0.1 V = 40.96, so I choose a "
            "gain of 40. This uses most of the ADC range, which gives the best resolution. A higher gain such as 41 "
            "would give 4.1 V, which exceeds 4.096 V and would saturate the ADC.",
        ),
    ],
    "NI": [
        (
            3,
            "easy",
            "What is the input offset voltage of an opamp, and why does it matter more when the amplifier gain is "
            "large?",
            [
                (
                    "Offset is a small DC voltage that acts as if added to the input (any one of: output not zero for a "
                    "zero input, a small error voltage at the input).",
                    5,
                    [
                        "small dc",
                        "small voltage",
                        "not zero",
                        "non-zero",
                        "zero input",
                        "error voltage",
                        "added to the input",
                    ],
                    [],
                ),
                (
                    "The gain multiplies the offset (any one of: amplified by the gain, a large output error).",
                    5,
                    ["multiplied", "multiply", "amplified", "times the gain", "gain times", "x 100"],
                    [],
                ),
            ],
            "The input offset voltage is a small DC voltage that acts as if it were added to the input, so the output "
            "is not zero when the input is zero. The amplifier multiplies the offset by its gain, so with a large "
            "gain it becomes a large output error.",
        ),
        (
            3,
            "easy",
            "What is the input bias current of an opamp, and why is it a problem for sensors with a high output "
            "resistance?",
            [
                (
                    "A small current flows into the opamp's input pins (any one of: current into the inputs, the opamp "
                    "draws a small current).",
                    5,
                    ["small current", "tiny current", "current flow", "draws", "draw", "leak"],
                    [],
                ),
                (
                    "It flows through the source resistance, creating an error voltage (any one of: voltage drop across the "
                    "sensor resistance, larger error for high resistance).",
                    5,
                    ["voltage drop", "error voltage", "extra voltage", "ir drop"],
                    [],
                ),
            ],
            "The input bias current is a small current that flows into the opamp's input pins. It flows through the "
            "sensor's source resistance and creates an error voltage, which is large when the resistance is high.",
        ),
        (
            3,
            "easy",
            "Why is the real gain of an opamp amplifier slightly different from the gain set by its resistors?",
            [
                (
                    "The open-loop gain of a real opamp is not infinite (any one of: finite open-loop gain, limited "
                    "open-loop gain).",
                    5,
                    ["not infinite", "finite", "limited open-loop", "open-loop gain is limited"],
                    [],
                ),
                (
                    "So the closed-loop gain is slightly lower than designed (any one of: lower, smaller, a small gain "
                    "error).",
                    5,
                    ["lower", "smaller", "less", "gain error"],
                    [],
                ),
            ],
            "A real opamp's open-loop gain is finite, not infinite. Because of this, the closed-loop gain of the "
            "amplifier is slightly lower than the value set by its resistors.",
        ),
        (
            3,
            "easy",
            "Why can an opamp fail to amplify a fast-changing sensor signal correctly? Name the two limits involved "
            "and what each does.",
            [
                (
                    "Limited bandwidth: the gain falls at high frequencies (any one of: gain-bandwidth product, higher gain "
                    "means lower bandwidth, high frequencies are attenuated).",
                    5,
                    ["gain fall", "gain drop", "gain is reduced", "attenuat", "lower bandwidth", "high frequenc"],
                    ["bandwidth"],
                ),
                (
                    "Slew rate: the output can change only at a maximum rate (any one of: cannot change fast enough, large "
                    "fast signals are distorted).",
                    5,
                    ["maximum rate", "max rate", "fast enough", "rate of change", "distort"],
                    ["slew"],
                ),
            ],
            "The first limit is the bandwidth: because the gain-bandwidth product is constant, the gain falls at high "
            "frequencies. The second is the slew rate: the output can change only at a maximum rate, so large, fast "
            "signals are distorted.",
        ),
        (
            2,
            "advanced",
            "A sensor behaves like a voltage source with an output resistance of 10 kOhm. It is connected to an "
            "amplifier with an input resistance of 90 kOhm. What fraction of the sensor voltage does the amplifier "
            "see? Explain why, and suggest how to fix the problem.",
            [
                (
                    "Method: the two resistances form a voltage divider (any one of: Rin / (Rs + Rin), 90 / (10 + 90), 90 "
                    "kOhm / 100 kOhm).",
                    2,
                    ["voltage divider", "divider", "90 / 100", "90 / ( 10 + 90 )", "rin / ( rs + rin )"],
                    [],
                ),
                ("Result: 90%.", 3, ["90 %", "90 percent", "0.9"], []),
                (
                    "Why: current flows through the sensor's output resistance (any one of: voltage drop across Rs, loading "
                    "effect, Rin is not much larger than Rs).",
                    2,
                    ["voltage drop", "drop across", "loading", "not much larger", "comparable", "current flow"],
                    [],
                ),
                (
                    "Fix (any one of: a buffer or voltage follower, a much higher input resistance, an opamp with CMOS or "
                    "FET inputs).",
                    3,
                    ["buffer", "voltage follower", "higher input resistance", "much larger input", "cmos", "fet"],
                    [],
                ),
            ],
            "The output resistance and the input resistance form a voltage divider, so the amplifier sees Rin / (Rs + "
            "Rin) = 90 / (10 + 90) = 90% of the sensor voltage. Current flows through the sensor's output resistance "
            "and 10% of the voltage is lost across it, because Rin is not much larger than Rs. To fix it, put a "
            "buffer (voltage follower) with a very high input resistance between the sensor and the amplifier.",
        ),
        (
            3,
            "advanced",
            "A gas sensor has a very high output resistance of about 10 MOhm, its signal changes slowly over minutes, "
            "and it is read by an opamp amplifier. Which opamp property matters MOST here, and which matters LEAST? "
            "Explain both.",
            [
                (
                    "Most important (any one of: very high input resistance, very low input bias current, CMOS or FET "
                    "inputs).",
                    3,
                    ["input resistance", "bias current", "input impedance", "cmos", "fet"],
                    [],
                ),
                (
                    "Reason: with a 10 MOhm source, current into the opamp causes a large error (any one of: loading loses "
                    "voltage, bias current makes a large voltage drop).",
                    3,
                    ["voltage drop", "error voltage", "loading", "large error", "lose", "10 mohm", "high resistance"],
                    [],
                ),
                (
                    "Least important: bandwidth or slew rate.",
                    2,
                    ["bandwidth", "slew"],
                    ["least", "not important", "does not matter", "matters less"],
                ),
                (
                    "Reason: the signal changes slowly (any one of: slow signal, low frequency, changes over minutes).",
                    2,
                    ["slow", "low frequency", "minutes"],
                    [],
                ),
            ],
            "The input resistance, or equivalently a very low input bias current, matters most. With a 10 MOhm "
            "source, any current the opamp draws makes a large voltage drop across the sensor resistance and a large "
            "error. The bandwidth and slew rate matter least, because the signal changes slowly over minutes, so it "
            "is a very low frequency signal.",
        ),
    ],
    "DA": [
        (
            1,
            "easy",
            "Explain why raw IoT sensor readings need to be analysed, and what predictive maintenance and anomaly "
            "detection each achieve.",
            [
                (
                    "Raw readings are of little use until analysed (any one of: huge amounts of data, must be turned into "
                    "information, needed for decisions).",
                    3,
                    [
                        "large amount",
                        "huge amount",
                        "too much data",
                        "little use",
                        "information",
                        "decision",
                        "insight",
                    ],
                    [],
                ),
                (
                    "Predictive maintenance predicts failures before they happen (any one of: repair in time, avoid "
                    "breakdowns).",
                    4,
                    [
                        "before it happen",
                        "before they happen",
                        "before fail",
                        "before failing",
                        "predict failure",
                        "predicts failure",
                        "in time",
                        "avoid breakdown",
                    ],
                    [],
                ),
                (
                    "Anomaly detection finds readings that do not fit the normal pattern (any one of: unusual readings, a "
                    "sudden spike, a sign of a fault or attack).",
                    3,
                    ["unusual", "normal pattern", "abnormal", "spike", "do not fit", "does not fit", "fault", "attack"],
                    [],
                ),
            ],
            "Raw sensor readings arrive in huge amounts and are of little use until they are analysed and turned into "
            "information and decisions. Predictive maintenance predicts machine failures before they happen, so "
            "repairs can be made in time. Anomaly detection finds readings that do not fit the normal pattern, such "
            "as a sudden spike that may mean a fault or an attack.",
        ),
        (
            2,
            "easy",
            "Describe the components of learning from data: what is unknown, what we have, and what the learning "
            "algorithm produces.",
            [
                (
                    "An unknown target function maps inputs to outputs (any one of: target function, true function f, the "
                    "real relationship we cannot see).",
                    3,
                    [
                        "target function",
                        "true function",
                        "unknown function",
                        "real relationship",
                        "maps input",
                        "map input",
                        "not see",
                        "not known",
                        "not know",
                    ],
                    [],
                ),
                (
                    "We have a data set of past examples (any one of: data set, examples of input with output, training "
                    "data).",
                    3,
                    ["data set", "dataset", "example", "examples", "past data", "training data", "sample", "samples"],
                    [],
                ),
                (
                    "The algorithm picks a final hypothesis from a hypothesis set (any one of: chooses the best candidate "
                    "model, the final model approximates the target function).",
                    4,
                    [
                        "hypothesis set",
                        "final hypothesis",
                        "candidate model",
                        "approximate",
                        "close to the target",
                        "best fit",
                        "fits the data best",
                    ],
                    [],
                ),
            ],
            "There is an unknown target function f that maps inputs to outputs. What we have is a data set of past "
            "examples of inputs with their outputs. The learning algorithm searches a hypothesis set of candidate "
            "models and picks the final hypothesis g that fits the data best, so that it approximates f.",
        ),
        (
            3,
            "easy",
            "How do supervised, unsupervised and reinforcement learning differ in the kind of feedback the learner "
            "gets?",
            [
                (
                    "Supervised: every example has the correct answer (any one of: labels, labelled data, known outputs).",
                    4,
                    ["label", "labels", "labelled", "labeled", "correct answer", "known answer", "known output"],
                    ["supervised"],
                ),
                (
                    "Unsupervised: no labels, finds structure by itself (any one of: no labels, groups similar data, finds "
                    "patterns).",
                    3,
                    [
                        "no label",
                        "no labels",
                        "without label",
                        "without labels",
                        "unlabelled",
                        "unlabeled",
                        "structure",
                        "group",
                        "pattern",
                    ],
                    ["unsupervised"],
                ),
                (
                    "Reinforcement: learns from rewards (any one of: reward, learning by trial, feedback on actions).",
                    3,
                    ["reward", "rewards", "trial and error", "feedback"],
                    ["reinforcement"],
                ),
            ],
            "In supervised learning every training example comes with the correct answer, a label. In unsupervised "
            "learning there are no labels, so the algorithm finds structure, such as groups, by itself. In "
            "reinforcement learning the agent learns by trial and error from rewards.",
        ),
        (
            3,
            "easy",
            "Why is the data split into a training set and a test set before building a model?",
            [
                (
                    "The test set checks performance on data the model has not seen (any one of: unseen data, new data, how "
                    "it will work in practice).",
                    5,
                    ["unseen", "new data", "not seen", "never seen", "has not seen", "in practice", "real use"],
                    [],
                ),
                (
                    "So the test set must be kept separate from training (any one of: kept aside, never used to fit the "
                    "model, held out).",
                    5,
                    [
                        "kept aside",
                        "keep aside",
                        "held-out",
                        "not used for training",
                        "never used",
                        "not used to train",
                    ],
                    [],
                ),
            ],
            "The training set is used to fit the model, and the test set checks how well the model works on data it "
            "has not seen, which is how it will be used in practice. For that, the test set must be kept aside and "
            "never used for training.",
        ),
        (
            3,
            "advanced",
            "A factory wants to predict motor failures from vibration sensors. Describe the data-driven pipeline from "
            "raw data to an action: how the data is prepared, which type of learning fits and why, and what the "
            "system does with a prediction.",
            [
                (
                    "Collect past data with labels (any one of: record which motors failed, labelled history).",
                    2,
                    ["label", "labels", "labelled", "labeled", "history", "past failure", "record"],
                    [],
                ),
                (
                    "Clean the data (any one of: handle missing values, remove outliers from faulty sensors).",
                    2,
                    ["missing", "outlier", "outliers", "clean", "faulty reading"],
                    [],
                ),
                (
                    "Compute features (any one of: average vibration, RMS, peak value over a time window).",
                    2,
                    ["feature", "features", "average", "rms", "mean", "peak"],
                    [],
                ),
                (
                    "Type of learning (both needed: supervised classification or a classifier; because the past failures "
                    "are labelled).",
                    2,
                    ["supervised", "classification", "classifier", "classify"],
                    [],
                ),
                (
                    "Action (any one of: raise an alert, schedule maintenance before failure, notify a technician).",
                    2,
                    ["alert", "schedule", "maintenance", "repair", "warn", "notify"],
                    [],
                ),
            ],
            "First collect past vibration data and record which motors failed, so the data are labelled. Clean the "
            "data by handling missing values and removing outliers from faulty sensors. Compute features such as the "
            "average and peak vibration over each minute. Because the past failures are labelled, supervised "
            "classification fits. When the model predicts a failure, the system raises an alert and schedules "
            "maintenance before the motor breaks.",
        ),
        (
            2,
            "advanced",
            "A model that predicts a greenhouse's humidity was trained only on summer data. It works well in summer "
            "but makes large errors in winter. Using the idea of feasibility of learning, explain why, and suggest "
            "how to fix it.",
            [
                (
                    "The training data are not representative of winter (any one of: only summer conditions, the model "
                    "never saw winter).",
                    3,
                    [
                        "not representative",
                        "representative",
                        "only summer",
                        "never saw",
                        "never seen",
                        "different conditions",
                        "does not cover",
                        "not cover",
                    ],
                    [],
                ),
                (
                    "Low error on training data does not guarantee low error on new data (any one of: in-sample vs "
                    "out-of-sample error, generalisation fails).",
                    2,
                    [
                        "in-sample",
                        "out-of-sample",
                        "training error",
                        "generalis",
                        "generaliz",
                        "generalize",
                        "generalise",
                        "not generalize",
                        "not generalise",
                    ],
                    [],
                ),
                (
                    "Fix: collect data from all seasons, then retrain (any one of: whole year of data, add winter data, "
                    "retrain).",
                    3,
                    [
                        "all season",
                        "all seasons",
                        "every season",
                        "whole year",
                        "add winter",
                        "include winter",
                        "collect winter",
                        "retrain",
                        "more data",
                    ],
                    [],
                ),
                (
                    "Check the model on winter test data before using it (any one of: test on winter, validate on new "
                    "conditions).",
                    2,
                    ["test on winter", "winter test", "winter data", "winter reading", "winter readings", "winter"],
                    ["test", "evaluate", "validate", "check"],
                ),
            ],
            "Learning is only feasible when the training data are representative of the situations where the model is "
            "used; this model only saw summer conditions, so winter is not represented. Its low in-sample error does "
            "not guarantee a low out-of-sample error. To fix it, collect data from all seasons and retrain, then "
            "check the model on winter test data before using it.",
        ),
    ],
    "DAT": [
        (
            1,
            "easy",
            "What does linear regression find, and how is the line fitted to the data?",
            [
                (
                    "It finds a straight line relating the input to the output (any one of: a slope with an intercept, y = "
                    "w0 + w1 x, a linear relationship).",
                    5,
                    ["straight line", "line", "slope", "intercept", "w0", "w1"],
                    [],
                ),
                (
                    "The line is fitted by least squares (any one of: minimise the mean squared error, minimise squared "
                    "differences, MSE).",
                    5,
                    [
                        "least squares",
                        "squared error",
                        "squared difference",
                        "mse",
                        "minimise",
                        "minimize",
                        "minimises",
                        "minimizes",
                    ],
                    [],
                ),
            ],
            "Linear regression finds a straight line y = w0 + w1 x that describes how the output changes with the "
            "input. The line is fitted by least squares, choosing the weights that minimise the mean squared error "
            "between the predicted and actual values.",
        ),
        (
            2,
            "easy",
            "Explain the three components that a time series is often described by.",
            [
                (
                    "Trend: a long-term rise or fall (any one of: long-term increase, long-term decrease, overall "
                    "direction).",
                    4,
                    ["long-term", "long term", "increase", "decrease", "overall direction", "rise", "fall"],
                    ["trend"],
                ),
                (
                    "Seasonality: a pattern that repeats with a fixed period (any one of: daily cycle, weekly cycle, "
                    "repeating pattern).",
                    3,
                    ["repeat", "repeats", "repeating", "cycle", "period", "daily", "weekly"],
                    ["seasonality", "seasonal"],
                ),
                (
                    "Noise: the random variation that is left (any one of: random, irregular, unpredictable).",
                    3,
                    ["random", "irregular", "unpredictable", "remaining", "leftover"],
                    ["noise"],
                ),
            ],
            "The trend is the long-term increase or decrease. Seasonality is a pattern that repeats with a fixed "
            "period, such as a daily cycle. Noise is the random variation that is left over.",
        ),
        (
            3,
            "easy",
            "Describe how the k-means algorithm groups data points once k starting centroids are chosen.",
            [
                (
                    "Assign every point to its nearest centroid (any one of: nearest, closest).",
                    4,
                    ["nearest", "closest", "close", "shortest distance"],
                    [],
                ),
                (
                    "Move each centroid to the mean of its points (any one of: mean, average, update the centroid).",
                    3,
                    ["mean", "average", "update", "move"],
                    ["centroid", "centre", "center"],
                ),
                (
                    "Repeat until the assignments stop changing (any one of: repeat, converge, stable).",
                    3,
                    ["repeat", "converge", "no longer change", "stop changing", "stable", "iterate"],
                    [],
                ),
            ],
            "Each point is assigned to its nearest centroid. Then each centroid is moved to the mean of the points "
            "assigned to it. These two steps are repeated until the assignments no longer change.",
        ),
        (
            3,
            "easy",
            "Why should features usually be scaled before running k-means clustering?",
            [
                (
                    "k-means groups points by distance (any one of: distance, how far apart points are).",
                    5,
                    ["distance", "distances", "far apart"],
                    [],
                ),
                (
                    "Unscaled, the feature with the larger range dominates (any one of: dominate, outweigh, gets more "
                    "weight).",
                    5,
                    [
                        "dominate",
                        "dominates",
                        "outweigh",
                        "more weight",
                        "larger range",
                        "large range",
                        "bigger values",
                        "larger values",
                    ],
                    [],
                ),
            ],
            "k-means groups points by their distance to the centroids. If the features are not scaled, the feature "
            "with the larger numeric range dominates the distances and the other features hardly matter.",
        ),
        (
            1,
            "advanced",
            "A building's daily energy use was modelled from outdoor temperatures between 10 and 35 degC as E = 2 + "
            "0.5 T, with E in kWh and T in degC. Predict the energy use at 30 degC, showing your method; explain "
            "what the number 0.5 means; and say whether you would trust a prediction for 60 degC.",
            [
                (
                    "Method: substitute T = 30 into the line (any one of: 2 + 0.5 x 30, 0.5 times 30 plus 2).",
                    2,
                    ["0.5 x 30", "0.5 * 30", "0.5 × 30", "0.5 times 30", "2 + 15", "substitute", "plug", "put 30"],
                    [],
                ),
                ("Result: 17 kWh.", 3, ["17"], ["kwh", "energy", "predict", "prediction", "use"]),
                (
                    "0.5 is the slope (any one of: energy rises 0.5 kWh per degree, per 1 degC increase).",
                    2,
                    ["per degree", "per degc", "one degree", "1 degc", "0.5 kwh", "slope"],
                    [],
                ),
                (
                    "60 degC is extrapolation, not to be trusted (any one of: outside the 10 to 35 range, beyond the data, "
                    "the line may not stay linear).",
                    3,
                    [
                        "extrapolation",
                        "extrapolate",
                        "outside",
                        "beyond",
                        "not trust",
                        "not reliable",
                        "not stay linear",
                    ],
                    [],
                ),
            ],
            "Substituting T = 30 gives E = 2 + 0.5 x 30 = 17 kWh. The number 0.5 is the slope: the energy use rises "
            "by 0.5 kWh per degree. I would not trust a prediction for 60 degC, because it is outside the 10 to 35 "
            "degC range of the data; that is extrapolation, and the relationship may not stay linear.",
        ),
        (
            2,
            "advanced",
            "You must forecast the next hour's temperature in a greenhouse from hourly readings collected over three "
            "months, and the temperature has a clear daily cycle. How would you split the data for training and "
            "testing, which inputs would your model use, and why?",
            [
                (
                    "Split in time order: train on the earlier part, test on the later part.",
                    3,
                    [
                        "earlier",
                        "later",
                        "first",
                        "last",
                        "older",
                        "oldest",
                        "most recent",
                        "newest",
                        "first part",
                        "last part",
                        "time order",
                        "chronological",
                        "chronologically",
                    ],
                    [],
                ),
                (
                    "Why (any one of: do not shuffle, the future must not leak into training, never test on the past using "
                    "the future).",
                    2,
                    ["not shuffle", "no shuffling", "without shuffling", "future", "leak"],
                    [],
                ),
                (
                    "Inputs: previous hours' values (any one of: last few readings, autoregressive, lagged values).",
                    2,
                    ["previous", "past value", "past values", "autoregressive", "lag", "lagged"],
                    [],
                ),
                (
                    "Daily cycle: also the value from 24 hours earlier (any one of: 24-hour lag, same hour yesterday).",
                    3,
                    ["24", "same hour yesterday", "yesterday"],
                    [],
                ),
            ],
            "I would split the data in time order: train on the first two and a half months and test on the later "
            "part, and not shuffle, so the future never leaks into training. The model would be autoregressive, "
            "using the previous few hours' values, plus the value from 24 hours earlier to capture the daily "
            "cycle.",
        ),
    ],
}


PROBES = {
    "IOT-TL-01": [
        (
            "đúng, chữ khác",
            "IoT is a network of devices that send and receive information over the internet. Each device "
            "needs an internet connection, a sensor and a unique ID.",
            ">=7",
        ),
        ("chỉ tên", "IoT is things. They need sensors, connectivity and identity.", "<=4"),
    ],
    "IOT-TL-02": [
        (
            "lợi ích y tế, không nêu thiết bị",
            "In healthcare, IoT alerts doctors remotely when a patient is in danger. In factories, equipment "
            "temperature is watched so failures are predicted before they happen.",
            ">=7",
        ),
        (
            "nhiệt độ cơ thể ở phần y tế",
            "In healthcare, a smartwatch measures body temperature and alerts the doctor remotely. Industry is "
            "also important.",
            "<=4",
        ),
        (
            "đúng, chữ khác",
            "In healthcare, a smartwatch monitors the heart rate and warns the doctor remotely. In industry, "
            "vibration sensors on machines show when a machine will fail, so it is repaired early.",
            ">=7",
        ),
        (
            "chỉ tên lĩnh vực",
            "IoT is used in healthcare and in industry. Both sectors get many benefits from it.",
            "<=2",
        ),
    ],
    "IOT-TL-03": [
        (
            "đúng, chữ khác",
            "Devices are often not updated and keep factory passwords, so hackers can control them. Smart "
            "cameras also record private moments of daily life.",
            ">=7",
        ),
        ("chỉ tên", "Security and privacy are problems for home devices.", "<=2"),
    ],
    "IOT-TL-04": [
        (
            "đúng, chữ khác",
            "Constrained devices have limited memory and a weak processor. Heterogeneous means different "
            "manufacturers use different protocols. Dynamic means devices go offline and come back.",
            ">=7",
        ),
        ("chỉ tên", "IoT devices are constrained, heterogeneous and dynamic.", "<=2"),
    ],
    "IOT-TL-05": [
        (
            "đúng, chữ khác",
            "A moisture sensor in the soil measures the field. A pump is switched on by the system only when "
            "the moisture drops below a threshold, which reduces water use.",
            ">=7",
        ),
        ("không có quy tắc", "The farm uses sensors and a computer to watch the crops every day.", "<=3"),
    ],
    "IOT-TL-06": [
        (
            "chỉ tên (lỗi Tuấn nêu)",
            "The three challenges are security, interoperability and energy. These are the main problems for "
            "the city project.",
            "<=2",
        ),
        (
            "đúng, chữ khác",
            "Security: force a strong password and push firmware updates. Interoperability: buy only devices "
            "that follow a common standard. Energy: put the radios to sleep between readings, since changing "
            "the batteries of so many sensors is expensive.",
            ">=7",
        ),
    ],
    "IOTM-TL-01": [
        ("chỉ tên (lỗi Tuấn nêu)", "The main components of an IoT system are sensors, actuators and a gateway.", "<=2"),
        (
            "đúng, chữ khác",
            "A sensor detects motion. An actuator turns a motor. The hub links the home devices to the internet.",
            ">=7",
        ),
        (
            "đảo sensor/actuator, câu riêng",
            "Actuators measure the temperature. Sensors switch the motor on. The gateway links devices to the "
            "internet.",
            "<=4",
        ),
    ],
    "IOTM-TL-02": [
        (
            "đảo lớp (lỗi Tuấn nêu)",
            "The lowest layer is the application layer. The top layer is the perception layer.",
            "<=2",
        ),
        (
            "đúng, chữ khác",
            "The bottom layer is the perception layer, which gathers data with sensors. The highest layer is "
            "the application layer.",
            ">=7",
        ),
    ],
    "IOTM-TL-03": [
        (
            "đúng, chữ khác (lỗi Tuấn nêu)",
            "In device-to-cloud the device sends data straight to the cloud. In device-to-gateway the device "
            "sends data to a gateway that passes it on.",
            ">=7",
        ),
        (
            "đảo hai mô hình",
            "In device-to-cloud the device sends data to a hub; in device-to-gateway the device connects "
            "directly to the cloud.",
            "<=2",
        ),
    ],
    "IOTM-TL-04": [
        (
            "đúng, chữ khác",
            "Devices are powered by batteries that should not be replaced often. A city may have thousands of "
            "devices, and the system must grow with them.",
            ">=7",
        ),
        ("chỉ tên", "Low power consumption and scalability are both important goals.", "<=2"),
    ],
    "IOTM-TL-05": [
        (
            "xếp sai lớp, có dấu phẩy",
            "A motion sensor detects people, a relay switches the light, and a hub connects them. The rule "
            "belongs to the perception layer, and the sensor is in the application layer.",
            "<=6",
        ),
        (
            "xếp sai lớp, cùng một vế (lỗi Tuấn nêu)",
            "A smart bulb relay switches the light and a motion sensor detects people. A hub is the gateway. "
            "The motion sensor belongs to the application layer and the rule runs in the perception layer.",
            "c",
        ),
    ],
    "IOTM-TL-06": [
        (
            "chỉ tên (lỗi Tuấn nêu)",
            "The five layers are perception layer, network layer, processing layer, application layer and "
            "business layer.",
            "<=2",
        ),
        ("chỉ 'analyses' ở lớp xử lý", "The processing layer analyses large amounts of data.", ">=2"),
        (
            "đúng, chữ khác",
            "The perception layer uses sensors to sense the world. The network layer sends the data. The "
            "processing layer keeps a database and analyzes it. The application layer gives services to "
            "users. The business layer manages profit and privacy.",
            ">=7",
        ),
    ],
    "MSG-TL-01": [
        (
            "without (lỗi Tuấn nêu)",
            "Clients send messages directly to each other without a broker, using a topic that others subscribed to.",
            "<=4",
        ),
        (
            "đúng, chữ khác",
            "A client publishes a message to a topic, and the broker delivers it to all subscribers of that topic.",
            ">=7",
        ),
    ],
    "MSG-TL-02": [
        (
            "đảo QoS (lỗi Tuấn nêu)",
            "QoS 1 is sent with no acknowledgement and may be lost. QoS 0 waits for a PUBACK and may be duplicated.",
            "<=2",
        ),
        (
            "đúng, chữ khác (lỗi Tuấn nêu)",
            "QoS 0 delivers at most once and the message can be lost. QoS 1 delivers at least once using an "
            "acknowledgment, so copies can arrive.",
            ">=7",
        ),
    ],
    "MSG-TL-03": [
        (
            "đảo CON/NON",
            "CoAP uses UDP which can lose packets. Non-confirmable messages are acknowledged and resent; "
            "confirmable messages are not acknowledged, which saves energy.",
            "<=4",
        ),
        (
            "đúng, chữ khác",
            "CoAP works over UDP, which is unreliable. A confirmable message needs an acknowledgment and is "
            "sent again if none comes. Non-confirmable messages have less overhead.",
            ">=7",
        ),
    ],
    "MSG-TL-04": [
        (
            "đúng, chữ khác (lỗi Tuấn nêu)",
            "Both are REST protocols that use URL addresses for resources. Both use GET and POST methods and "
            "response codes. CoAP uses UDP.",
            ">=7",
        ),
        ("chỉ nói khác", "CoAP is for small devices and HTTP is for websites.", "<=2"),
        (
            "khác ở header",
            "Both follow REST with URIs and both use methods like POST. CoAP has a small 4-byte header.",
            ">=7",
        ),
    ],
    "MSG-TL-05": [
        (
            "đúng, tên phòng khác (lỗi Tuấn nêu)",
            "All devices use one broker. Topics are greenhouse/kitchen/temp and greenhouse/hall/temp. The + "
            "wildcard matches a single level. Sensor data uses QoS 0, fans use QoS 1.",
            ">=7",
        ),
        (
            "đảo QoS, có dấu phẩy",
            "One broker is used with topics like greenhouse/room1/temperature and greenhouse/+/temperature for "
            "the dashboard. Fan commands use QoS 0, sensor readings use QoS 1.",
            "<=6",
        ),
        (
            "đảo QoS, cùng một vế (lỗi Tuấn nêu)",
            "One broker. Topics greenhouse/room1/temperature. Dashboard uses greenhouse/+/temperature, the "
            "plus sign matches one level. Sensor data uses QoS 1 and fan commands use QoS 0.",
            "c",
        ),
    ],
    "MSG-TL-06": [
        (
            "câu đề xuất ngắn toàn từ của đề — luật chép đề (L7) bỏ câu, ý 5 mất điểm",
            "MQTT runs over TCP. MQTT needs a broker. CoAP runs over UDP. CoAP follows the REST style. I "
            "recommend CoAP.",
            "c",
        ),
        (
            "đủ 5 ý, câu đề xuất tự nhiên",
            "MQTT runs over TCP. MQTT needs a broker. CoAP runs over UDP. CoAP follows the REST style. For "
            "this sensor I recommend CoAP because it is lighter.",
            ">=10",
        ),
        (
            "đúng, chữ khác (lỗi Tuấn nêu)",
            "MQTT uses TCP and a broker. CoAP uses UDP and is resource based. I recommend using CoAP for this device.",
            ">=7",
        ),
        (
            "without (lỗi Tuấn nêu)",
            "MQTT works without a broker over TCP. CoAP uses UDP. I would recommend CoAP.",
            "<=6",
        ),
        (
            "khen MQTT, không đề xuất CoAP",
            "MQTT runs over TCP and needs a broker. CoAP runs over UDP and follows the REST style. MQTT is "
            "better than CoAP for this device.",
            "<=8",
        ),
        (
            "đảo TCP/UDP, cùng một vế",
            "MQTT runs over UDP and CoAP runs over TCP with a broker. CoAP follows the REST style. I recommend CoAP.",
            "c",
        ),
    ],
    "SENS-TL-01": [
        (
            "đúng, chữ khác",
            "Some sensors must be powered by an external source, like an RTD that needs a current. Others "
            "make their own voltage, like a thermocouple.",
            ">=7",
        ),
        (
            "quy ước IIT/NPTEL (active = tự sinh)",
            "An active sensor generates its own voltage, like a thermocouple. A passive sensor needs an "
            "excitation current, like an RTD.",
            ">=7",
        ),
        (
            "quy ước Fraden (active = cần kích thích)",
            "An active sensor needs an excitation current, like an RTD. A passive sensor generates its own "
            "voltage, like a thermocouple.",
            ">=7",
        ),
        (
            "đảo ví dụ giữa hai nhóm — từ khóa không gắn được ví dụ với nhóm",
            "A thermocouple needs an excitation current. A thermistor generates its own voltage.",
            "c",
        ),
        ("chỉ tên", "Sensors are active or passive, for example thermistors and thermocouples.", "<=3"),
    ],
    "SENS-TL-02": [
        (
            "đúng, chữ khác",
            "Accuracy means the reading is near the actual value. Precision means repeated readings are "
            "consistent with each other.",
            ">=7",
        ),
        (
            "đảo",
            "Accuracy means repeated readings are consistent with each other. Precision means the reading is "
            "near the actual value.",
            "<=2",
        ),
        ("chỉ tên", "Accuracy and precision are two important sensor characteristics.", "<=2"),
    ],
    "SENS-TL-03": [
        (
            "đúng, chữ khác",
            "With hysteresis the reading depends on whether the input is rising or falling, so one value can "
            "produce two readings.",
            ">=7",
        ),
        ("chỉ tên", "Hysteresis is a sensor characteristic listed in datasheets.", "<=2"),
    ],
    "SENS-TL-04": [
        (
            "đúng, chữ khác",
            "Inside, a small mass on springs shifts when the phone accelerates. This changes the capacitance "
            "between the plates, and the circuit converts that change into an acceleration value.",
            ">=7",
        ),
        ("chỉ tên", "A MEMS accelerometer uses a proof mass, springs and capacitance.", "<=3"),
    ],
    "SENS-TL-05": [
        (
            "đúng, chữ khác",
            "In the cold room an RTD is best because it is accurate over this small range. The furnace needs "
            "a thermocouple since it handles a very wide range up to 1000 degC and responds fast.",
            ">=7",
        ),
        (
            "đảo hai nơi, câu riêng",
            "For the furnace I would use a thermistor. For the cold room I would use a thermocouple.",
            "<=4",
        ),
    ],
    "SENS-TL-06": [
        (
            "đúng, chữ khác",
            "Pick Alpha. Beta could turn the fan on too early or too late because of its 5 % accuracy. Its "
            "hysteresis makes the point differ when humidity is rising or falling. Its non-linearity means "
            "the error is different at different humidity levels.",
            ">=7",
        ),
        ("chọn Beta, chỉ nhắc số", "Beta is better. Its figures are 5, 4 and 3.", "<=2"),
        (
            "câu chọn ngắn toàn từ của đề — luật chép đề (L7) bỏ câu, ý 1 mất điểm",
            "I choose Alpha. Beta could turn the fan on too early or too late. Its point differs when "
            "humidity is rising or falling. Its error is different at different humidity levels.",
            "c",
        ),
    ],
    "RO-TL-01": [
        (
            "đúng, chữ khác",
            "Sensors give tiny millivolt signals. Without gain they use a small part of the ADC, so resolution "
            "is poor. The amplifier stretches the signal to the full scale of the ADC.",
            ">=7",
        ),
        ("chỉ tên", "There is an amplifier and an ADC in the readout chain.", "<=2"),
    ],
    "RO-TL-02": [
        (
            "đúng, chữ khác",
            "Quantization rounds every sample to a discrete step. The error is at most half of one LSB.",
            ">=7",
        ),
        (
            "sai độ lớn sai số",
            "Quantization rounds every sample to a discrete step. The error can be two whole LSBs.",
            "<=5",
        ),
    ],
    "RO-TL-03": [
        ("đúng, chữ khác", "Sample at more than double the highest frequency. Otherwise you get aliasing.", ">=7"),
        ("chỉ tên", "This is about the Nyquist rate of the ADC.", "<=2"),
    ],
    "RO-TL-04": [
        ("đúng, chữ khác", "More bits mean finer resolution, but the converter is slower and more expensive.", ">=7"),
        ("chỉ nêu được", "More bits mean finer resolution.", "<=5"),
    ],
    "RO-TL-05": [
        (
            "đúng, chữ khác",
            "LSB = 4.096 / 2^12 = 0.001 V. Dividing by the sensitivity: 1 mV / 10 mV per degC gives 0.1 degC.",
            ">=7",
        ),
        ("đúng cách, sai số", "LSB = 4.096 / 4096 = 10 mV. Then 10 mV / 10 mV per degC = 1 degC.", "<=5"),
        (
            "viết °C (ký hiệu bị bỏ khi tiền xử lý)",
            "The LSB is 4.096 / 4096 = 1 mV. With 10 mV per degree, the smallest temperature change is 0.1 °C.",
            ">=7",
        ),
        (
            "0.1 xuất hiện ở chỗ khác, kết quả sai",
            "The LSB is 4.096 / 4096 = 0.1 V. Dividing by the sensitivity, the resolution is 10 degC.",
            "<=5",
        ),
        (
            "viết dấu phẩy thập phân (chuẩn hóa 27/11)",
            "LSB = 4.096 / 4096 = 1 mV. Then 1 mV / 10 mV per degC = 0,1 degC.",
            ">=7",
        ),
    ],
    "RO-TL-06": [
        (
            "đúng, chữ khác",
            "Divide 4.096 V by 0.1 V to get 40.96, so a gain of 40 uses most of the range. A bigger gain would "
            "clip at the maximum code.",
            ">=7",
        ),
        (
            "gain 41 (vượt 4,096 V)",
            "Divide 4096 mV by 100 mV and round up: a gain of 41 uses the full scale and gives the best "
            "resolution. Too much gain would saturate the ADC.",
            "<=7",
        ),
        (
            "gain 41 nhưng có ghi 40.96",
            "4.096 / 0.1 = 40.96, so I round to a gain of 41, which uses the full scale. A higher gain would saturate.",
            "c",
        ),
    ],
    "NI-TL-01": [
        (
            "đúng, chữ khác",
            "Offset is a small DC voltage, so the output is non-zero with a zero input. A big gain multiplies "
            "it into a big error.",
            ">=7",
        ),
        ("chỉ tên", "Input offset voltage is an opamp non-ideality.", "<=2"),
    ],
    "NI-TL-02": [
        (
            "đúng, chữ khác",
            "A small current flows into the opamp's inputs. Through a large sensor resistance it makes a "
            "voltage drop that adds an error.",
            ">=7",
        ),
        ("chỉ tên", "Bias current is listed in the opamp datasheet.", "<=2"),
    ],
    "NI-TL-03": [
        (
            "đúng, chữ khác",
            "The open-loop gain is finite, so the real gain is slightly less than the designed value.",
            ">=7",
        ),
        ("chỉ tên", "It is because of the open-loop gain.", "<=2"),
    ],
    "NI-TL-04": [
        (
            "đúng, chữ khác",
            "Bandwidth: the gain drops at high frequencies. Slew rate: the output cannot change fast enough, so "
            "big fast signals distort.",
            ">=7",
        ),
        ("chỉ tên (lỗi đã gặp ở đợt 1)", "The two limits are bandwidth and slew rate.", "<=2"),
        (
            "đảo vai trò, câu riêng",
            "Slew rate: the gain drops at high frequencies. Bandwidth: the output cannot change fast enough.",
            "<=2",
        ),
    ],
    "NI-TL-05": [
        (
            "đúng, chữ khác",
            "It is a voltage divider: 90 / (10 + 90) = 0.9 of the voltage. Current flowing through the 10 kOhm "
            "causes a voltage drop. Fix it with a voltage follower.",
            ">=7",
        ),
        ("sai kết quả", "It is a voltage divider: 10 / 90 = 11 percent. Fix it with a buffer.", "<=6"),
    ],
    "NI-TL-06": [
        (
            "đúng, chữ khác",
            "A very low bias current matters most, because current through the 10 MOhm sensor gives a large "
            "error voltage. Bandwidth is least important because the gas signal is slow.",
            ">=7",
        ),
        ("đảo nhiều/ít", "Bandwidth matters most. The input resistance does not matter.", "<=3"),
    ],
    "DA-TL-01": [
        (
            "đúng, chữ khác",
            "Sensors produce too much data to read by hand, so it must become information. Predictive "
            "maintenance fixes machines before they fail. Anomaly detection spots unusual readings such as a "
            "spike.",
            ">=7",
        ),
        ("chỉ tên", "IoT data analysis includes predictive maintenance and anomaly detection.", "<=3"),
    ],
    "DA-TL-02": [
        (
            "đúng, chữ khác",
            "The true function from input to output is unknown. We have a dataset of past examples. The "
            "algorithm chooses the candidate model that fits the data best from its hypothesis set.",
            ">=7",
        ),
        (
            "chỉ nhắc lại đề",
            "Learning has something unknown, something we have, and something the algorithm produces.",
            "<=2",
        ),
    ],
    "DA-TL-03": [
        (
            "đúng, chữ khác",
            "Supervised learning gets labelled examples. Unsupervised learning gets no labels and finds groups "
            "by itself. Reinforcement learning gets rewards for its actions.",
            ">=7",
        ),
        (
            "đảo supervised/unsupervised",
            "Supervised learning gets no labels and finds groups. Unsupervised learning gets labelled examples. "
            "Reinforcement learning gets rewards.",
            "<=4",
        ),
        ("chỉ tên", "The three types are supervised, unsupervised and reinforcement learning.", "<=2"),
    ],
    "DA-TL-04": [
        (
            "đúng, chữ khác",
            "The test data checks how the model does on new data. It is held out and never used to train.",
            ">=7",
        ),
        ("chỉ tên", "We split the data into a training set and a test set.", "<=2"),
        (
            "chép đề (có 'separate')",
            "We separate the data into a training set and a test set before building a model.",
            "<=2",
        ),
    ],
    "DA-TL-05": [
        (
            "đúng, chữ khác",
            "Record which motors broke so the history is labelled. Remove outliers and fill missing values. Use "
            "the RMS vibration as a feature. Train a classifier, a supervised model. Send an alert to the "
            "technician when a failure is predicted.",
            ">=7",
        ),
        ("thiếu quy trình", "Use machine learning on the vibration data to predict failures.", "<=2"),
    ],
    "DA-TL-06": [
        (
            "đúng, chữ khác",
            "The summer data does not cover winter conditions, so it is not representative. Low training error "
            "does not mean the model generalizes. Retrain with a whole year of data and validate it on winter "
            "readings.",
            ">=7",
        ),
        ("chỉ nhắc lại đề", "The model was trained on summer data and is wrong in winter.", "<=2"),
        (
            "ý 4 viết 'test it with winter data' (Tuấn nêu)",
            "It only saw summer, so it is not representative and does not generalize. Retrain with all seasons. "
            "Then test it with winter data.",
            ">=7",
        ),
    ],
    "DAT-TL-01": [
        (
            "đúng, chữ khác",
            "It finds the slope and intercept of a line through the data. The weights minimize the squared "
            "differences between predictions and real values.",
            ">=7",
        ),
        ("chỉ nhắc lại đề", "Linear regression finds a regression for the data.", "<=2"),
    ],
    "DAT-TL-02": [
        (
            "đúng, chữ khác",
            "The trend is the overall direction over a long time. Seasonality is a cycle that repeats, like "
            "every day. Noise is the irregular part that is left over.",
            ">=7",
        ),
        ("chỉ tên", "The three components are trend, seasonality and noise.", "<=2"),
        (
            "đảo trend/seasonality, câu riêng",
            "The trend is a cycle that repeats every day. Seasonality is the long-term rise. Noise is random.",
            "<=4",
        ),
    ],
    "DAT-TL-03": [
        (
            "đúng, chữ khác",
            "Every point joins the closest centroid. Each centroid then moves to the average of its points. "
            "This is repeated until nothing changes and it converges.",
            ">=7",
        ),
        ("chỉ nhắc lại đề", "k-means groups the data points into k groups.", "<=2"),
    ],
    "DAT-TL-04": [
        (
            "đúng, chữ khác",
            "Clustering uses the distance between points. A feature with bigger values would outweigh the others.",
            ">=7",
        ),
        ("chỉ nhắc lại đề", "Features should be scaled before clustering.", "<=2"),
    ],
    "DAT-TL-05": [
        (
            "đúng, chữ khác",
            "Put 30 into the formula: 2 + 0.5 x 30 = 17 kWh of energy. The slope 0.5 means 0.5 kWh more per "
            "degree. 60 degC is beyond the data, so I would not trust it.",
            ">=7",
        ),
        (
            "thay sai số",
            "Using 60 instead: 2 + 0.5 x 60 = 32 kWh of energy. The slope is 0.5. I would trust 60 degC.",
            "<=5",
        ),
        (
            "viết 17.0 kWh, 2 + 15",
            "Substitute T = 30: E = 2 + 15 = 17.0 kWh. 0.5 is the slope. 60 degC is outside the range, so it "
            "is extrapolation.",
            ">=7",
        ),
    ],
    "DAT-TL-06": [
        (
            "đúng, chữ khác",
            "Use the first months for training and the last weeks for testing, without shuffling, so no future "
            "data leaks. Use lagged values of the past hours and the same hour yesterday.",
            ">=7",
        ),
        (
            "xáo trộn ngẫu nhiên",
            "Shuffle the readings randomly and split them 80/20. Use the humidity as the input.",
            "<=3",
        ),
    ],
}


GEMINI_PROBES = {
    "IOT-TL-01": (
        "IoT is a network of physical things that send data over the internet. An object needs sensors. "
        "Each thing has a unique ID.",
        "IoT connects everyday objects so they can share data with other systems. An object needs sensors "
        "and an internet connection. Each one has its own IP address.",
    ),
    "IOT-TL-02": (
        "In healthcare, wearables track a patient's heart rate. In industry, sensors measure the vibration "
        "of machines. This predicts failures before they happen.",
        "In healthcare, doctors are alerted remotely when a patient is in danger. In factories, sensors "
        "watch the temperature of equipment, so the company has less downtime.",
    ),
    "IOT-TL-03": (
        "Home devices often keep their default passwords. Attackers can hijack them. Smart cameras collect "
        "personal data about people's daily life.",
        "Many home devices are rarely updated. Hackers can then use them in a botnet. Wearables record "
        "health information, which is private.",
    ),
    "IOT-TL-04": (
        "Constrained means the devices have little memory. Heterogeneous means they come from many vendors. "
        "Dynamic means devices join the network at any time.",
        "Constrained devices run on batteries. Heterogeneous devices use different protocols. Dynamic means "
        "devices go offline and come back.",
    ),
    "IOT-TL-05": (
        "Soil moisture sensors measure the field. A valve controls the water supply. The rule is to water "
        "only when the soil is dry. This saves water.",
        "A moisture sensor is placed in the soil. A pump is the actuator that waters the field. It switches "
        "on only when the moisture is below a threshold, which reduces water use.",
    ),
    "IOT-TL-06": (
        "For security, give each sensor a unique password. For interoperability, require an open standard. "
        "For energy, let the sensors sleep most of the time. Energy matters because replacing 100,000 "
        "batteries is costly.",
        "For security, encrypt the data. For interoperability, use gateways that translate protocols. For "
        "energy, use low-power radios. Energy matters because recharging so many batteries is slow.",
    ),
    "IOTM-TL-01": (
        "Sensors measure temperature. Actuators switch a motor on. A gateway connects local devices to the internet.",
        "A sensor detects motion. An actuator opens a valve. A gateway translates protocols such as Zigbee to Wi-Fi.",
    ),
    "IOTM-TL-02": (
        "The lowest layer is the perception layer. The top layer is the application layer. The bottom "
        "layer collects data with sensors.",
        "The perception layer is at the bottom. The application layer is at the top. The bottom layer "
        "senses the physical world.",
    ),
    "IOTM-TL-03": (
        "In device-to-cloud, the device connects directly to the cloud. In device-to-gateway, the device "
        "sends data to a hub.",
        "In the device-to-cloud model the device uses its own Wi-Fi to reach the cloud. In the "
        "device-to-gateway model a smartphone forwards the data.",
    ),
    "IOTM-TL-04": (
        "Low power matters because devices run on batteries. Scalability matters because a system may have "
        "millions of devices.",
        "Low power consumption matters because batteries must last for years. Scalability matters because "
        "the system must handle large volumes of data.",
    ),
    "IOTM-TL-05": (
        "A motion sensor detects a person. A smart bulb is the actuator. The network layer carries the "
        "data via the hub. The motion sensor belongs to the perception layer. The rule runs in the "
        "application layer.",
        "A PIR motion sensor detects people. A relay switches the light. The network layer carries the "
        "data over Zigbee. The sensor and the bulb belong to the perception layer. The app logic runs in "
        "the application layer.",
    ),
    "IOTM-TL-06": (
        "The perception layer collects data with sensors. The network layer transmits the data. The "
        "processing layer stores large amounts of data. The application layer delivers services to users. "
        "The business layer manages the whole system.",
        "The perception layer senses the world. The network layer sends the data. The processing layer "
        "analyses big data. The application layer offers an app to the user. The business layer handles "
        "privacy.",
    ),
    "MSG-TL-01": (
        "Messages go through a central broker. A client publishes a message to a topic. The broker forwards "
        "it to the subscribers.",
        "All messages pass through a broker. A sender publishes to a topic. The broker delivers the message "
        "to every subscriber.",
    ),
    "MSG-TL-02": (
        "QoS 0 delivers a message at most once. QoS 1 delivers a message at least once.",
        "QoS 0 delivers at most once, so the message may be lost. QoS 1 delivers at least once, so the "
        "message may be duplicated.",
    ),
    "MSG-TL-03": (
        "CoAP runs over UDP, which is unreliable. Confirmable messages are acknowledged with an ACK. "
        "Non-confirmable messages are not acknowledged, which saves energy.",
        "CoAP uses UDP, so packets can be lost. A confirmable message is acknowledged, and it is "
        "retransmitted if no ACK arrives. Non-confirmable messages save bandwidth.",
    ),
    "MSG-TL-04": (
        "Like HTTP, CoAP follows the REST style. Like HTTP, CoAP uses methods such as GET. Unlike HTTP, "
        "CoAP runs over UDP.",
        "Like HTTP, CoAP identifies resources with URIs. Like HTTP, CoAP returns similar response codes. "
        "Unlike HTTP, CoAP has a small 4-byte header.",
    ),
    "MSG-TL-05": (
        "All devices use one broker. Each room has its own topic, such as greenhouse/room1/temperature. The "
        "dashboard subscribes with the + wildcard. Sensor readings use QoS 0. Fan commands use QoS 1.",
        "Everything goes through one broker. There is one topic per room, for example "
        "greenhouse/kitchen/temp. The dashboard uses greenhouse/+/temp, where the plus sign matches one "
        "level. Sensor data uses QoS 0. Fan commands use QoS 2.",
    ),
    "MSG-TL-06": (
        "MQTT runs over TCP. MQTT needs a broker. CoAP runs over UDP. CoAP follows the REST style. For this "
        "sensor I recommend CoAP because it is lighter.",
        "MQTT uses a TCP connection. MQTT clients talk through a broker. CoAP has a small 4-byte header. "
        "CoAP reads resources with GET. I would choose CoAP for this device.",
    ),
    "SENS-TL-01": (
        "One group needs an external excitation. The other group generates its own signal. A thermistor "
        "needs excitation.",
        "In IIT terms, an active sensor makes its own voltage, like a thermocouple, while a passive sensor "
        "needs a current through it, like an RTD.",
    ),
    "SENS-TL-02": (
        "Accuracy is closeness to the true value. Precision is repeatability.",
        "An accurate sensor has a small error from the real value. A precise sensor gives consistent "
        "readings with a small spread.",
    ),
    "SENS-TL-03": (
        "The reading depends on whether the input is increasing or decreasing. So the same input can give "
        "different readings.",
        "The output depends on the previous value. This makes the reading uncertain by up to the hysteresis width.",
    ),
    "SENS-TL-04": (
        "The proof mass moves when the device accelerates. The capacitance changes. The readout measures "
        "this to get the acceleration.",
        "Springs holding the mass bend under acceleration. One capacitance rises while the other falls. "
        "The circuit converts the change to a voltage.",
    ),
    "SENS-TL-05": (
        "Cold room: thermistor, because it is very sensitive. Furnace: thermocouple, because it has a very "
        "wide range. It also responds quickly.",
        "Cold room: RTD, because the narrow range is enough and it is accurate. Furnace: thermocouple, "
        "which works above 1000 degC. A small junction gives a fast response.",
    ),
    "SENS-TL-06": (
        "I choose Alpha because it is more accurate. Beta's accuracy means the fan could switch up to 5 "
        "%RH from the true humidity. Its hysteresis means a different switching point when rising than "
        "when falling. Its non-linearity means the error changes across the range.",
        "Alpha is better. With Beta the fan may switch too early or too late. The point depends on whether "
        "humidity is rising or falling. The readings do not follow a straight line.",
    ),
    "RO-TL-01": (
        "Sensor signals are only millivolts. So only a few ADC codes change. The amplifier scales it to the "
        "full scale.",
        "The sensor signal is weak. Most of the ADC range would be unused. Amplifying matches the ADC input range.",
    ),
    "RO-TL-02": (
        "Quantization rounds each sample to the nearest level. The error is at most half an LSB.",
        "The input becomes discrete steps. The maximum error is LSB / 2.",
    ),
    "RO-TL-03": (
        "Sample at more than twice the highest frequency. Otherwise aliasing happens.",
        "Sample faster than 2f. If too slow, fast changes are missed and the signal appears at a lower frequency.",
    ),
    "RO-TL-04": (
        "More bits give a smaller LSB. But the ADC uses more power.",
        "More bits give finer resolution. But conversion is slower.",
    ),
    "RO-TL-05": (
        "LSB = Vref / 2^N = 4.096 / 4096 = 1 mV. Resolution = LSB / sensitivity = 1 mV / 10 mV per degC = 0.1 degC.",
        "4.096 V divided by 2^12 gives 0.001 V. Dividing 1 mV by 10 mV per degC gives 0.1 degC.",
    ),
    "RO-TL-06": (
        "Gain = 4.096 / 0.1 = 40.96, so a gain of 40. It uses most of the range. A higher gain would saturate.",
        "4096 mV / 100 mV is about 41, so I would use 40 to stay below the limit. This gives the best "
        "resolution. A gain of 41 would clip at 4.1 V.",
    ),
    "NI-TL-01": (
        "Offset is a small DC voltage added to the input. The gain multiplies it.",
        "With a zero input the output is not zero. A large gain amplifies this into a large output error.",
    ),
    "NI-TL-02": (
        "A small current flows into the input pins. Through the source resistance it creates an error voltage.",
        "The opamp draws a small current. It makes a voltage drop across the sensor resistance, larger for "
        "high resistance.",
    ),
    "NI-TL-03": (
        "The open-loop gain is finite. So the closed-loop gain is slightly lower.",
        "The opamp's open-loop gain is limited, not infinite. This gives a small gain error: the gain is "
        "less than designed.",
    ),
    "NI-TL-04": (
        "Bandwidth: the gain falls at high frequencies. Slew rate: the output can change only at a maximum rate.",
        "The gain-bandwidth product means a higher gain gives a lower bandwidth. The slew rate means large "
        "fast signals are distorted.",
    ),
    "NI-TL-05": (
        "It is a voltage divider. The amplifier sees 90%. Current flows through the output resistance. Use a buffer.",
        "Rin / (Rs + Rin) = 90 / 100. That is 0.9 of the voltage, lost by loading. Use an opamp with CMOS inputs.",
    ),
    "NI-TL-06": (
        "Most important: very high input resistance. With 10 MOhm, current into the opamp causes a large "
        "error. Least important: bandwidth. The signal is slow.",
        "Most important: very low bias current. It would make a large voltage drop across the sensor. The "
        "slew rate matters least, because it is a low frequency signal.",
    ),
    "DA-TL-01": (
        "Raw readings are of little use until analysed. Predictive maintenance predicts failures before they "
        "happen. Anomaly detection finds unusual readings.",
        "Sensors send huge amounts of data that must be turned into decisions. Predictive maintenance lets "
        "repairs happen in time. Anomaly detection finds a sudden spike that may mean an attack.",
    ),
    "DA-TL-02": (
        "The target function is unknown. We have a data set of examples. The algorithm picks a final "
        "hypothesis from the hypothesis set.",
        "We cannot see the true function from inputs to outputs. We have training data. The algorithm "
        "chooses the candidate model that approximates the target.",
    ),
    "DA-TL-03": (
        "Supervised learning has labels. Unsupervised learning has no labels. Reinforcement learning learns "
        "from rewards.",
        "In supervised learning the correct answers are known. Unsupervised learning finds patterns by "
        "itself. Reinforcement learning learns by trial and error.",
    ),
    "DA-TL-04": (
        "The test set shows how the model works on unseen data. It is kept aside during training.",
        "We want to know how the model performs in practice on new data. So the test data is held out and "
        "never used to fit the model.",
    ),
    "DA-TL-05": (
        "Collect labelled history. Clean the data by removing outliers. Compute the average vibration as a "
        "feature. Use supervised learning. Raise an alert.",
        "Record past failures. Handle missing values. Use the peak vibration as a feature. Train a "
        "classifier because the failures are labelled. Schedule maintenance before the motor breaks.",
    ),
    "DA-TL-06": (
        "The summer data is not representative of winter. Low in-sample error does not guarantee low "
        "out-of-sample error. Collect data from all seasons and retrain. Validate on winter data.",
        "The model never saw winter conditions. It does not generalize. Add a whole year of data and "
        "retrain, then test on winter before using it.",
    ),
    "DAT-TL-01": (
        "Linear regression finds a straight line. It is fitted by least squares.",
        "It finds the slope and intercept relating input to output. The weights minimise the mean squared error.",
    ),
    "DAT-TL-02": (
        "Trend: a long-term increase. Seasonality: a repeating daily cycle. Noise: random variation.",
        "Trend is the overall direction. Seasonality is a pattern with a fixed period, like weekly. Noise "
        "is the irregular part left over.",
    ),
    "DAT-TL-03": (
        "Assign every point to its nearest centroid. Move each centroid to the mean of its points. Repeat "
        "until stable.",
        "Each point goes to the closest centre. Each centre is updated to the average of its points. "
        "Iterate until the assignments no longer change.",
    ),
    "DAT-TL-04": (
        "k-means uses distances between points. The feature with the larger range would dominate.",
        "Points are grouped by how far apart they are. Without scaling, a feature with larger values gets more weight.",
    ),
    "DAT-TL-05": (
        "E = 2 + 0.5 x 30 = 17 kWh. 0.5 is the slope, 0.5 kWh per degree. 60 degC is extrapolation, so I "
        "would not trust it.",
        "Substitute T = 30 to predict 17 kWh of energy use. Each 1 degC adds 0.5 kWh. 60 degC is outside "
        "the 10 to 35 range, so the line may not stay linear.",
    ),
    "DAT-TL-06": (
        "Train on the earlier part and test on the later part. Do not shuffle, so the future does not leak. "
        "Use the previous hours as inputs. Also use the value 24 hours earlier.",
        "Split chronologically. Never test on the past using the future. Use lagged values of the last few "
        "hours. Add the same hour yesterday to capture the daily cycle.",
    ),
}
