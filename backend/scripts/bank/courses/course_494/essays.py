# ruff: noqa: ISC004 — dữ liệu đề: chuỗi dài ngắt dòng trong danh sách là cố ý
"""Tự luận khóa 494 — mỗi ý: (câu mô tả, điểm, main_keywords, sub_keywords).

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
            "The Internet of Things is a network of physical things that collect and exchange data over the internet. "
            "An object needs sensors, software and network connectivity. It also needs a unique identity, such as an IP "
            "address.",
        ),
        (
            2,
            "easy",
            "Describe how IoT is used in healthcare and in industry, and give the benefit of each.",
            [
                (
                    "Healthcare use of IoT (any one of: wearables track heart rate or blood glucose, doctors are alerted remotely).",
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
                    "Industry benefit (any one of: failures predicted before they happen, fewer breakdowns, less downtime).",
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
            "In healthcare, wearable devices track a patient's heart rate or blood glucose and alert doctors remotely when "
            "something is wrong. In industry, sensors on machines measure vibration and temperature, so the company can "
            "predict failures before they happen and repair the machine in time.",
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
            "Many home IoT devices ship with default passwords and rarely get software updates, so attackers can take "
            "them over and use them in a botnet. Privacy is also at risk, because cameras, sensors and wearables collect "
            "personal data about people's habits and health.",
        ),
        (
            1,
            "easy",
            "IoT devices and systems are often described as constrained, heterogeneous and dynamic. Explain "
            "what each of these three characteristics means.",
            [
                (
                    "Constrained: devices have limited resources (any one of: little memory, low processing power, battery power).",
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
                    "Heterogeneous: devices differ from each other (any one of: many vendors, different hardware, different protocols).",
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
            "Heterogeneous means that the devices come from many vendors with different hardware and protocols. Dynamic "
            "means that devices join, leave or move all the time, so the system keeps changing.",
        ),
        (
            2,
            "advanced",
            "A farm wants to use less water for irrigation. Describe an IoT solution: which device measures "
            "the field, which device acts on the water supply, and what rule the system follows.",
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
            "Soil moisture sensors are placed in the fields to measure how wet the soil is. A valve on the water pipe is "
            "the actuator that the system opens or closes. The rule is to open the valve only when the soil is dry, so the "
            "farm saves water.",
        ),
        (
            3,
            "advanced",
            "A city plans to install 100,000 IoT sensors from several vendors, most of them running on "
            "batteries. For each of these three challenges — security, interoperability and energy — suggest one "
            "concrete way to handle it. Also explain why energy matters so much for this project.",
            [
                (
                    "Security: one concrete protection (any one of: unique or strong passwords, regular updates, encryption).",
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
                    "Energy: one way to save power (any one of: low-power hardware or radios, sleep most of the time, energy harvesting).",
                    3,
                    ["low-power", "low power", "sleep", "energy harvesting", "solar"],
                    [],
                ),
                (
                    "Why energy matters: batteries are hard to service at this scale (any one of: replacing or recharging 100,000 batteries is slow, costly, impractical).",
                    2,
                    ["replace", "recharge", "battery life", "change the batteries", "costly", "expensive"],
                    [],
                ),
            ],
            "For security, every sensor should get a unique password and regular security updates. For interoperability, "
            "the city should require open standards or use gateways that translate between protocols. For energy, the "
            "sensors should use low-power radios and sleep most of the time, waking up only to send data. Energy matters so much because replacing 100,000 "
            "batteries would be slow and expensive.",
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
                    "A gateway links local devices to the internet (any one of: connects them to the internet, translates protocols, forwards their data).",
                    4,
                    ["connect", "translate", "forward", "bridge", "link"],
                    ["gateway", "hub"],
                ),
            ],
            "Sensors measure the physical world, for example temperature. Actuators change it, for example by switching a "
            "relay. A gateway connects the local devices to the internet and translates between protocols such as "
            "Zigbee and Wi-Fi.",
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
                    "The bottom layer collects data from the physical world (any one of: with sensors, with actuators, senses the environment).",
                    4,
                    ["collect data", "gather data", "sensor", "physical world"],
                    [],
                ),
            ],
            "The lowest layer is the perception layer. It uses sensors and actuators to collect data from the physical "
            "world. The top layer is the application layer, which delivers services to users.",
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
                    "Device-to-gateway (both needed: a local gateway such as a hub or phone; it forwards the data onward to the cloud).",
                    5,
                    ["hub", "smartphone", "phone", "gateway", "forward", "pass", "relay"],
                    ["device-to-gateway", "device to gateway"],
                ),
            ],
            "In the device-to-cloud model, the device connects directly to a cloud service over the internet, for example "
            "through Wi-Fi. In the device-to-gateway model, the device connects to a local hub or smartphone, which "
            "forwards the data to the cloud.",
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
            "Low power consumption matters because many devices run on batteries that must last for years. Scalability "
            "matters because a system may grow to millions of devices that produce large volumes of data.",
        ),
        (
            1,
            "advanced",
            "Design a home automation system that turns on the hall light when someone enters at night. "
            "Describe the components and map them to the three architecture layers.",
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
            "A motion sensor detects a person, and a smart bulb is the actuator that switches the light. The sensor and "
            "the bulb belong to the perception layer. They talk to a hub over Zigbee, and the network layer carries the "
            "data to the cloud. The rule that turns on the light at night runs in the application layer.",
        ),
        (
            2,
            "advanced",
            "Describe the five-layer IoT architecture layer by layer, and explain what the two extra layers "
            "add compared with the three-layer model.",
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
            "The perception layer has sensors and actuators that collect data. The network layer transmits the data. The "
            "processing layer, or middleware, stores and analyses large amounts of data. The application layer delivers "
            "services to users. The business layer manages the whole system, including business models and privacy.",
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
            "In MQTT, clients do not send messages directly to each other. A client publishes a message to a topic on a "
            "central broker, and the broker forwards it to every client that has subscribed to that topic.",
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
                    "QoS 1 (both needed: delivered at least once or acknowledged with PUBACK; the message may be duplicated).",
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
            "QoS 0 means at most once: the message is sent without acknowledgement, so it may be lost. QoS 1 means at "
            "least once: the sender keeps the message until it gets a PUBACK, so it arrives but may be duplicated.",
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
                    "Non-confirmable messages are not acknowledged, which saves resources (any one of: energy, bandwidth, fewer messages).",
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
                    "Like HTTP, CoAP uses requests with methods or codes (any one of: methods such as GET or POST, similar response codes).",
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
            "Like HTTP, CoAP follows the REST style and identifies resources with URIs. It also uses methods such as GET "
            "and POST and response codes similar to HTTP. Unlike HTTP, CoAP runs over UDP instead of TCP.",
        ),
        (
            1,
            "advanced",
            "Design the MQTT messaging for a smart greenhouse with a temperature sensor and a fan in each of "
            "three rooms. Give example topics, a subscription that lets one dashboard read all rooms, and the delivery "
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
                    "The dashboard subscribes with the single-level wildcard (any one of: +, plus sign, matches one level).",
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
            "All devices connect to one broker. Each room publishes to its own topic, for example greenhouse/room1/"
            "temperature, and each fan subscribes to a command topic such as greenhouse/room1/fan. The dashboard "
            "subscribes to greenhouse/+/temperature, where the plus sign matches one level, so it gets all rooms. Sensor "
            "readings use QoS 0, because a lost reading is replaced a second later. Fan commands use QoS 1, so a command "
            "is not lost.",
        ),
        (
            3,
            "advanced",
            "A battery-powered sensor network must choose between MQTT and CoAP. Compare the two protocols "
            "and recommend one for a device that only answers occasional requests from a server.",
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
            "MQTT runs over TCP and needs a broker, and devices keep a connection open. CoAP runs over UDP with a small "
            "4-byte header, which saves energy. CoAP follows the REST style, where a server reads a resource with GET. For "
            "a device that only answers occasional requests, I recommend CoAP, because it needs no broker and no open TCP "
            "connection.",
        ),
    ],
}

PROBES = {
    "IOT-TL-01": [
        (
            "đúng, chữ khác",
            "IoT is a network of devices that send and receive information over the internet. Each "
            "device needs an internet connection, a sensor and a unique ID.",
            ">=7",
        ),
        ("chỉ tên", "IoT is things. They need sensors, connectivity and identity.", "<=4"),
    ],
    "IOT-TL-02": [
        (
            "lợi ích y tế, không nêu thiết bị",
            "In healthcare, IoT alerts doctors remotely when a patient is in danger. "
            "In factories, equipment temperature is watched so failures are predicted before they happen.",
            ">=7",
        ),
        (
            "nhiệt độ cơ thể ở phần y tế",
            "In healthcare, a smartwatch measures body temperature and alerts the "
            "doctor remotely. Industry is also important.",
            "<=4",
        ),
        (
            "đúng, chữ khác",
            "In healthcare, a smartwatch monitors the heart rate and warns the doctor remotely. In "
            "industry, vibration sensors on machines show when a machine will fail, so it is repaired early.",
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
            "Devices are often not updated and keep factory passwords, so hackers can control them. "
            "Smart cameras also record private moments of daily life.",
            ">=7",
        ),
        ("chỉ tên", "Security and privacy are problems for home devices.", "<=2"),
    ],
    "IOT-TL-04": [
        (
            "đúng, chữ khác",
            "Constrained devices have limited memory and a weak processor. Heterogeneous means "
            "different manufacturers use different protocols. Dynamic means devices go offline and come back.",
            ">=7",
        ),
        ("chỉ tên", "IoT devices are constrained, heterogeneous and dynamic.", "<=2"),
    ],
    "IOT-TL-05": [
        (
            "đúng, chữ khác",
            "A moisture sensor in the soil measures the field. A pump is switched on by the system "
            "only when the moisture drops below a threshold, which reduces water use.",
            ">=7",
        ),
        ("không có quy tắc", "The farm uses sensors and a computer to watch the crops every day.", "<=3"),
    ],
    "IOT-TL-06": [
        (
            "chỉ tên (lỗi Tuấn nêu)",
            "The three challenges are security, interoperability and energy. These are the "
            "main problems for the city project.",
            "<=2",
        ),
        (
            "đúng, chữ khác",
            "Security: force a strong password and push firmware updates. Interoperability: buy only "
            "devices that follow a common standard. Energy: put the radios to sleep between readings, since changing "
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
            "Actuators measure the temperature. Sensors switch the motor on. The "
            "gateway links devices to the internet.",
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
            "The bottom layer is the perception layer, which gathers data with sensors. The highest "
            "layer is the application layer.",
            ">=7",
        ),
    ],
    "IOTM-TL-03": [
        (
            "đúng, chữ khác (lỗi Tuấn nêu)",
            "In device-to-cloud the device sends data straight to the cloud. In "
            "device-to-gateway the device sends data to a gateway that passes it on.",
            ">=7",
        ),
        (
            "đảo hai mô hình",
            "In device-to-cloud the device sends data to a hub; in device-to-gateway the device "
            "connects directly to the cloud.",
            "<=2",
        ),
    ],
    "IOTM-TL-04": [
        (
            "đúng, chữ khác",
            "Devices are powered by batteries that should not be replaced often. A city may have "
            "thousands of devices, and the system must grow with them.",
            ">=7",
        ),
        ("chỉ tên", "Low power consumption and scalability are both important goals.", "<=2"),
    ],
    "IOTM-TL-05": [
        (
            "xếp sai lớp, có dấu phẩy",
            "A motion sensor detects people, a relay switches the light, and a hub connects "
            "them. The rule belongs to the perception layer, and the sensor is in the application layer.",
            "<=6",
        ),
        (
            "xếp sai lớp, cùng một vế (lỗi Tuấn nêu)",
            "A smart bulb relay switches the light and a motion sensor detects "
            "people. A hub is the gateway. The motion sensor belongs to the application layer and the rule runs in the "
            "perception layer.",
            "c",
        ),
    ],
    "IOTM-TL-06": [
        (
            "chỉ tên (lỗi Tuấn nêu)",
            "The five layers are perception layer, network layer, processing layer, "
            "application layer and business layer.",
            "<=2",
        ),
        ("chỉ 'analyses' ở lớp xử lý", "The processing layer analyses large amounts of data.", ">=2"),
        (
            "đúng, chữ khác",
            "The perception layer uses sensors to sense the world. The network layer sends the data. "
            "The processing layer keeps a database and analyzes it. The application layer gives services to users. The "
            "business layer manages profit and privacy.",
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
            "QoS 0 delivers at most once and the message can be lost. QoS 1 delivers at "
            "least once using an acknowledgment, so copies can arrive.",
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
            "CoAP works over UDP, which is unreliable. A confirmable message needs an acknowledgment "
            "and is sent again if none comes. Non-confirmable messages have less overhead.",
            ">=7",
        ),
    ],
    "MSG-TL-04": [
        (
            "đúng, chữ khác (lỗi Tuấn nêu)",
            "Both are REST protocols that use URL addresses for resources. Both use GET "
            "and POST methods and response codes. CoAP uses UDP.",
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
            "All devices use one broker. Topics are greenhouse/kitchen/temp and "
            "greenhouse/hall/temp. The + wildcard matches a single level. Sensor data uses QoS 0, fans use QoS 1.",
            ">=7",
        ),
        (
            "đảo QoS, có dấu phẩy",
            "One broker is used with topics like greenhouse/room1/temperature and "
            "greenhouse/+/temperature for the dashboard. Fan commands use QoS 0, sensor readings use QoS 1.",
            "<=6",
        ),
        (
            "đảo QoS, cùng một vế (lỗi Tuấn nêu)",
            "One broker. Topics greenhouse/room1/temperature. Dashboard uses "
            "greenhouse/+/temperature, the plus sign matches one level. Sensor data uses QoS 1 and fan commands use "
            "QoS 0.",
            "c",
        ),
    ],
    "MSG-TL-06": [
        (
            "câu đề xuất ngắn toàn từ của đề — luật chép đề (L7) bỏ câu, ý 5 mất điểm",
            "MQTT runs over TCP. MQTT needs a broker. CoAP runs over UDP. CoAP follows the REST style. I recommend CoAP.",
            "c",
        ),
        (
            "đủ 5 ý, câu đề xuất tự nhiên",
            "MQTT runs over TCP. MQTT needs a broker. CoAP runs over UDP. CoAP follows the REST style. For this sensor I "
            "recommend CoAP because it is lighter.",
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
            "MQTT runs over TCP and needs a broker. CoAP runs over UDP and follows the "
            "REST style. MQTT is better than CoAP for this device.",
            "<=8",
        ),
        (
            "đảo TCP/UDP, cùng một vế",
            "MQTT runs over UDP and CoAP runs over TCP with a broker. CoAP follows the REST style. I recommend CoAP.",
            "c",
        ),
    ],
}

GEMINI_PROBES = {
    "IOT-TL-01": (
        "IoT is a network of physical things that send data over the internet. An object needs sensors. Each thing "
        "has a unique ID.",
        "IoT connects everyday objects so they can share data with other systems. An object needs sensors and an "
        "internet connection. Each one has its own IP address.",
    ),
    "IOT-TL-02": (
        "In healthcare, wearables track a patient's heart rate. In industry, sensors measure the vibration of "
        "machines. This predicts failures before they happen.",
        "In healthcare, doctors are alerted remotely when a patient is in danger. In factories, sensors watch the "
        "temperature of equipment, so the company has less downtime.",
    ),
    "IOT-TL-03": (
        "Home devices often keep their default passwords. Attackers can hijack them. Smart cameras collect personal "
        "data about people's daily life.",
        "Many home devices are rarely updated. Hackers can then use them in a botnet. Wearables record health "
        "information, which is private.",
    ),
    "IOT-TL-04": (
        "Constrained means the devices have little memory. Heterogeneous means they come from many vendors. Dynamic "
        "means devices join the network at any time.",
        "Constrained devices run on batteries. Heterogeneous devices use different protocols. Dynamic means devices "
        "go offline and come back.",
    ),
    "IOT-TL-05": (
        "Soil moisture sensors measure the field. A valve controls the water supply. The rule is to water only when "
        "the soil is dry. This saves water.",
        "A moisture sensor is placed in the soil. A pump is the actuator that waters the field. It switches on only "
        "when the moisture is below a threshold, which reduces water use.",
    ),
    "IOT-TL-06": (
        "For security, give each sensor a unique password. For interoperability, require an open standard. For "
        "energy, let the sensors sleep most of the time. Energy matters because replacing 100,000 batteries is "
        "costly.",
        "For security, encrypt the data. For interoperability, use gateways that translate protocols. For energy, "
        "use low-power radios. Energy matters because recharging so many batteries is slow.",
    ),
    "IOTM-TL-01": (
        "Sensors measure temperature. Actuators switch a motor on. A gateway connects local devices to the internet.",
        "A sensor detects motion. An actuator opens a valve. A gateway translates protocols such as Zigbee to Wi-Fi.",
    ),
    "IOTM-TL-02": (
        "The lowest layer is the perception layer. The top layer is the application layer. The bottom layer "
        "collects data with sensors.",
        "The perception layer is at the bottom. The application layer is at the top. The bottom layer senses the "
        "physical world.",
    ),
    "IOTM-TL-03": (
        "In device-to-cloud, the device connects directly to the cloud. In device-to-gateway, the device sends data "
        "to a hub.",
        "In the device-to-cloud model the device uses its own Wi-Fi to reach the cloud. In the device-to-gateway "
        "model a smartphone forwards the data.",
    ),
    "IOTM-TL-04": (
        "Low power matters because devices run on batteries. Scalability matters because a system may have "
        "millions of devices.",
        "Low power consumption matters because batteries must last for years. Scalability matters because the "
        "system must handle large volumes of data.",
    ),
    "IOTM-TL-05": (
        "A motion sensor detects a person. A smart bulb is the actuator. The network layer carries the data via the "
        "hub. The motion sensor belongs to the perception layer. The rule runs in the application layer.",
        "A PIR motion sensor detects people. A relay switches the light. The network layer carries the data over "
        "Zigbee. The sensor and the bulb belong to the perception layer. The app logic runs in the application "
        "layer.",
    ),
    "IOTM-TL-06": (
        "The perception layer collects data with sensors. The network layer transmits the data. The processing "
        "layer stores large amounts of data. The application layer delivers services to users. The business layer "
        "manages the whole system.",
        "The perception layer senses the world. The network layer sends the data. The processing layer analyses big "
        "data. The application layer offers an app to the user. The business layer handles privacy.",
    ),
    "MSG-TL-01": (
        "Messages go through a central broker. A client publishes a message to a topic. The broker forwards it to "
        "the subscribers.",
        "All messages pass through a broker. A sender publishes to a topic. The broker delivers the message to "
        "every subscriber.",
    ),
    "MSG-TL-02": (
        "QoS 0 delivers a message at most once. QoS 1 delivers a message at least once.",
        "QoS 0 delivers at most once, so the message may be lost. QoS 1 delivers at least once, so the message may "
        "be duplicated.",
    ),
    "MSG-TL-03": (
        "CoAP runs over UDP, which is unreliable. Confirmable messages are acknowledged with an ACK. Non-confirmable "
        "messages are not acknowledged, which saves energy.",
        "CoAP uses UDP, so packets can be lost. A confirmable message is acknowledged, and it is retransmitted if no "
        "ACK arrives. Non-confirmable messages save bandwidth.",
    ),
    "MSG-TL-04": (
        "Like HTTP, CoAP follows the REST style. Like HTTP, CoAP uses methods such as GET. Unlike HTTP, CoAP runs "
        "over UDP.",
        "Like HTTP, CoAP identifies resources with URIs. Like HTTP, CoAP returns similar response codes. Unlike "
        "HTTP, CoAP has a small 4-byte header.",
    ),
    "MSG-TL-05": (
        "All devices use one broker. Each room has its own topic, such as greenhouse/room1/temperature. The "
        "dashboard subscribes with the + wildcard. Sensor readings use QoS 0. Fan commands use QoS 1.",
        "Everything goes through one broker. There is one topic per room, for example greenhouse/kitchen/temp. The "
        "dashboard uses greenhouse/+/temp, where the plus sign matches one level. Sensor data uses QoS 0. Fan "
        "commands use QoS 2.",
    ),
    "MSG-TL-06": (
        "MQTT runs over TCP. MQTT needs a broker. CoAP runs over UDP. CoAP follows the REST style. For this sensor I "
        "recommend CoAP because it is lighter.",
        "MQTT uses a TCP connection. MQTT clients talk through a broker. CoAP has a small 4-byte header. CoAP reads "
        "resources with GET. I would choose CoAP for this device.",
    ),
}
