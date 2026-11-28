# ruff: noqa: ISC004 — dữ liệu đề: chuỗi dài ngắt dòng trong danh sách là cố ý
"""Trắc nghiệm khóa 494 — (đoạn số, mức, đề, [ĐÚNG, sai, sai, sai], giải thích).
Đáp án đúng viết ĐẦU TIÊN; build.py xoay nó vào vị trí 0..3 để đáp án rải đều. Đoạn số tính trong từng kỹ năng.
Đợt 1 (26/11/2026): IOT, IOTM, MSG — module 1 + messaging của module 3.
Đợt 2 (27/11): SENS, RO, NI — module 2 "Sensors & Interfaces".
Đợt 3 (27/11): DA, DAT — module 4 "Data Analysis for IoT".
27/11: DA-TN-14, DAT-TN-09, 11, 13 viết lại vì lộ đáp án tự luận (exclusion_group chưa được bộ ráp đề dùng)."""

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
            "Each thing needs a unique identity, such as an IP address or device ID, so that it can be found and "
            "addressed.",
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
            "Interoperability is the ability of devices from different vendors, protocols and data formats to work "
            "together.",
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
            "Many devices ship with default passwords and rarely get software updates, so attackers can take them "
            "over.",
        ),
        (
            1,
            "understand",
            "A smart thermostat measures room temperature and switches the heater on when the room gets cold. Which "
            "two IoT capabilities does it use?",
            ["Sensing and actuating", "Routing and switching", "Encryption and compression", "Storage and backup"],
            "It senses the temperature (sensor) and acts on the heater (actuator).",
        ),
        (
            1,
            "understand",
            "A smart-city network has thousands of sensors from different vendors; some sleep to save energy and new "
            "ones are added every month. Which pair of IoT characteristics does this show?",
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
            "A hospital wants to watch a patient's heart rate at home and alert the doctor if it becomes dangerous. "
            "Which IoT application area is this?",
            ["Remote health monitoring", "Precision agriculture", "Smart parking", "Predictive maintenance"],
            "Wearable devices that track heart rate and alert doctors remotely are a healthcare (remote monitoring) "
            "use.",
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
            "A company buys smart locks from vendor A and a hub from vendor B, but the hub cannot control the locks "
            "because they use different protocols. Which IoT challenge is this?",
            ["Interoperability", "Scalability", "Energy efficiency", "Latency"],
            "Devices from different vendors using different protocols that cannot work together is an "
            "interoperability problem.",
        ),
        (
            3,
            "understand",
            "A fitness band records sleep times and location all day and uploads them to the cloud. Which concern "
            "does this raise most directly?",
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
            "The five-layer architecture adds a processing layer (middleware) between the network and application "
            "layers.",
        ),
        (
            3,
            "recognize",
            "In which IoT communication model do devices talk directly to each other, for example a switch and a "
            "bulb over Bluetooth?",
            ["Device-to-device", "Device-to-cloud", "Device-to-gateway", "Back-end data sharing"],
            "In the device-to-device model, devices communicate directly with each other.",
        ),
        (
            1,
            "understand",
            "In a home automation system, a motion sensor detects a person and the hall light turns on. What is the "
            "role of the light?",
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
            "A team is choosing between Wi-Fi, LoRa and cellular to send sensor data to a server. Which layer of "
            "the three-layer architecture are they designing?",
            ["Network layer", "Perception layer", "Application layer", "Business layer"],
            "The network layer transmits data using technologies such as Wi-Fi, cellular networks, Zigbee or LoRa.",
        ),
        (
            2,
            "understand",
            "A system must store and analyse terabytes of sensor data before showing results in an app. In the "
            "five-layer architecture, which layer does this work?",
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
            "A fitness band sends data via Bluetooth to the owner's phone, and the phone uploads it to the cloud. "
            "Which communication model is this?",
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
            "A sensor sends a temperature reading every second, and losing one reading does not matter. Which QoS "
            "level is the most efficient choice?",
            ["QoS 0", "QoS 1", "QoS 2", "QoS 3"],
            "QoS 0 (at most once) has no acknowledgement overhead; an occasional lost reading is acceptable here.",
        ),
        (
            2,
            "understand",
            "A door lock must receive the 'unlock' command once and only once, even on an unreliable network. Which "
            "QoS level fits?",
            ["QoS 2", "QoS 0", "QoS 1", "QoS 3"],
            "Only QoS 2 guarantees exactly-once delivery; QoS 1 may deliver the command twice.",
        ),
        (
            2,
            "understand",
            "A monitoring app wants to know when a sensor goes offline unexpectedly. Which MQTT feature should the "
            "sensor set when it connects?",
            ["Last Will and Testament", "Retained message", "Topic wildcard", "Persistent topic"],
            "The broker publishes the Last Will message if the client disconnects unexpectedly.",
        ),
        (
            3,
            "understand",
            "A client sends a CoAP GET request for /temperature and the resource exists. Which response code is "
            "typical?",
            ["2.05 Content", "4.04 Not Found", "5.00 Internal Server Error", "2.01 Created"],
            "2.05 Content returns the resource; 4.04 means it does not exist.",
        ),
        (
            3,
            "understand",
            "A dashboard must be told every time a sensor's value changes, without sending repeated GET requests. "
            "Which CoAP feature helps?",
            ["Observe", "Reset message", "Non-confirmable message", "Port 5683"],
            "With the Observe option, the server sends notifications whenever the resource changes.",
        ),
    ],
    "SENS": [
        (
            1,
            "recognize",
            "Which of these sensors needs an external excitation (power) source to produce its output?",
            ["A platinum RTD", "A thermocouple", "A solar cell", "A piezoelectric crystal"],
            "An RTD's resistance can only be read by passing a current through it; the other three generate their "
            "own signal.",
        ),
        (
            1,
            "recognize",
            "Which of these is an example of a self-generating sensor?",
            ["A thermocouple", "A thermistor", "A platinum RTD", "A strain-sensitive resistor"],
            "A thermocouple produces its own small voltage from heat; resistive sensors need an excitation current.",
        ),
        (
            2,
            "recognize",
            "In a capacitive MEMS accelerometer, what changes when the device accelerates?",
            [
                "The capacitance between the moving mass and the fixed plates",
                "The resistance of a platinum wire wrapped around the frame",
                "The voltage produced at the junction of two different metals",
                "The time of flight of an ultrasonic echo inside the chip",
            ],
            "The proof mass moves relative to the fixed plates, which changes the capacitance between them.",
        ),
        (
            2,
            "recognize",
            "How does an ultrasonic proximity sensor work out the distance to an object?",
            [
                "From the time of flight of an echo: speed of sound x time / 2",
                "From the change in inductance caused by a nearby metal object",
                "From the change in resistance of a heated thin metal film",
                "From the voltage generated at a junction of two metals",
            ],
            "An ultrasonic sensor times the echo; the sound travels there and back, so the distance is speed x time "
            "/ 2.",
        ),
        (
            3,
            "recognize",
            "What does the sensitivity of a sensor describe?",
            [
                "The change in output per unit change in input",
                "The smallest input that gives any output from zero",
                "The span between the lowest and highest measurable value",
                "How long the output takes to settle after a change",
            ],
            "Sensitivity is the slope of the response, for example 10 mV per degC.",
        ),
        (
            3,
            "recognize",
            "Which characteristic describes how close a reading is to the true value?",
            ["Accuracy", "Precision", "Resolution", "Specificity"],
            "Accuracy is closeness to the true value; precision is closeness of repeated readings to each other.",
        ),
        (
            3,
            "recognize",
            "What is the threshold of a sensor?",
            [
                "The smallest input, starting from zero, that gives a detectable output",
                "The largest input the sensor can measure before it saturates",
                "The time the sensor needs to reach 63% of its final output",
                "The largest deviation of the output from a straight line",
            ],
            "Threshold is the minimum input from zero that produces a detectable output.",
        ),
        (
            1,
            "understand",
            "A temperature sensor is read by passing a small current through it and measuring the voltage. Which "
            "group does it belong to?",
            [
                "Externally excited, because it needs an excitation to give an output",
                "Self-generating, because it produces its own voltage from the heat",
                "Digital, because the measured voltage is later sent to an ADC",
                "Non-contact, because it does not need to touch the object",
            ],
            "A sensor that needs an excitation current to be read is an externally excited sensor.",
        ),
        (
            2,
            "understand",
            "Why is a thermocouple a better choice than an NTC thermistor for monitoring a furnace at about 1000 degC?",
            [
                "A thermocouple works over a very wide range, up to more than 1000 degC",
                "A thermocouple gives a much larger output voltage than a thermistor",
                "A thermocouple's resistance falls sharply as the temperature rises",
                "A thermocouple needs no amplifier because its signal is already large",
            ],
            "Thermocouples cover very wide ranges; thermistors are sensitive but work over a limited range.",
        ),
        (
            2,
            "understand",
            "An inductive proximity sensor fails to detect an object on a production line. Which object is most "
            "likely?",
            ["A plastic bottle", "A steel bolt", "An aluminium can", "A copper pipe"],
            "Inductive sensors detect metal objects through a change in inductance; plastic does not affect it.",
        ),
        (
            3,
            "understand",
            "Repeated readings of the same 25.0 degC bath give 26.1, 26.0 and 26.1 degC. How would you describe "
            "this sensor?",
            [
                "Precise but not accurate",
                "Accurate but not precise",
                "Both accurate and precise",
                "Neither accurate nor precise",
            ],
            "The readings agree closely with each other (precise) but are about 1 degC from the true value (not "
            "accurate).",
        ),
        (
            3,
            "understand",
            "A humidity sensor reads 62% when humidity rises to 60%, but 58% when humidity falls to 60%. Which "
            "characteristic does this show?",
            ["Hysteresis", "Poor specificity", "A slow response time", "A high threshold"],
            "The reading for the same input depends on the direction of change, which is hysteresis.",
        ),
        (
            3,
            "understand",
            "A gas sensor meant for carbon monoxide also changes its output when the humidity changes. Which "
            "characteristic is poor?",
            ["Specificity", "Linearity", "Resolution", "Range"],
            "Specificity (selectivity) means responding only to the intended quantity.",
        ),
        (
            3,
            "understand",
            "A sensor is placed in hot water and takes 20 s to reach 90% of its final reading. What does this "
            "figure describe?",
            ["Its response time", "Its hysteresis", "Its stability", "Its sensitivity"],
            "Response time is how long the output takes to reach (a set fraction of) its final value after a step "
            "change.",
        ),
    ],
    "RO": [
        (
            1,
            "recognize",
            "In a typical sensor readout chain, which block scales the sensor voltage to the ADC's input range?",
            [
                "An amplifier built with an operational amplifier",
                "The microcontroller that processes the digital codes",
                "The communication module that sends data to the cloud",
                "The reference voltage source inside the ADC chip",
            ],
            "An opamp amplifier scales the small sensor voltage to the ADC's input range.",
        ),
        (
            2,
            "recognize",
            "What are the two steps an ADC performs?",
            [
                "Sampling and quantization",
                "Amplification and filtering",
                "Excitation and calibration",
                "Modulation and demodulation",
            ],
            "An ADC samples the signal at regular instants and quantizes each sample to a digital code.",
        ),
        (
            2,
            "recognize",
            "How many output codes does a 10-bit ADC have?",
            ["1024", "10", "100", "512"],
            "An N-bit ADC has 2^N codes; 2^10 = 1024.",
        ),
        (
            2,
            "recognize",
            "What is the size of one LSB for an N-bit ADC with reference voltage Vref?",
            ["Vref / 2^N", "Vref x 2^N", "Vref / N", "2^N / Vref"],
            "The full-scale range Vref is divided into 2^N steps, so one LSB = Vref / 2^N.",
        ),
        (
            2,
            "recognize",
            "What is the minimum sampling rate needed to capture a signal whose highest frequency is f?",
            ["More than 2f", "Exactly f / 2", "At least f", "About 10 times less than f"],
            "The Nyquist criterion requires a sampling rate of more than twice the highest signal frequency.",
        ),
        (
            3,
            "recognize",
            "With rounding to the nearest level, what is the largest quantization error of an ADC?",
            ["Half an LSB", "One full LSB", "Two LSBs", "The full-scale range"],
            "Rounding to the nearest level gives an error of at most half an LSB.",
        ),
        (
            3,
            "recognize",
            "What happens when the input voltage of an ADC goes above its full-scale range?",
            [
                "The output saturates at the maximum code",
                "The ADC adds extra bits automatically",
                "The output wraps around to zero and counts again",
                "The sampling rate doubles to follow the signal",
            ],
            "Above full scale the ADC clips: every such input gives the maximum code.",
        ),
        (
            1,
            "understand",
            "A 50 mV sensor signal is fed directly into an ADC with a 5 V range. What is the main problem?",
            [
                "Only about 1% of the range is used, so few codes change and resolution is poor",
                "The ADC is damaged because the input voltage is far above its full-scale range",
                "The sampling rate becomes too low because the signal voltage is very small",
                "The ADC output saturates at the maximum code for every input value",
            ],
            "A small signal uses only a tiny part of the ADC range; amplifying it first improves the effective "
            "resolution.",
        ),
        (
            2,
            "understand",
            "An 8-bit ADC has Vref = 2.048 V. What is its LSB?",
            ["8 mV", "2 mV", "256 mV", "0.8 mV"],
            "2.048 V / 2^8 = 2.048 V / 256 = 8 mV.",
        ),
        (
            2,
            "understand",
            "A vibration signal contains frequencies up to 500 Hz. Which sampling rate is the lowest that still "
            "avoids aliasing?",
            ["1200 samples per second", "500 samples per second", "800 samples per second", "250 samples per second"],
            "The rate must be more than 2 x 500 Hz = 1000 samples per second; of these choices only 1200 is high "
            "enough.",
        ),
        (
            2,
            "understand",
            "A sensor has a sensitivity of 20 mV per degC and the ADC's LSB is 2 mV. What temperature change does one "
            "LSB represent?",
            ["0.1 degC", "10 degC", "40 degC", "0.01 degC"],
            "Resolution in the measured quantity = LSB / sensitivity = 2 mV / 20 mV per degC = 0.1 degC.",
        ),
        (
            3,
            "understand",
            "Moving from a 10-bit to a 12-bit ADC with the same Vref has which effect?",
            [
                "The LSB becomes four times smaller",
                "The LSB becomes two times larger",
                "The full-scale range becomes four times larger",
                "The sampling rate becomes four times higher",
            ],
            "Two more bits give 2^2 = 4 times as many codes over the same range, so the LSB is four times smaller.",
        ),
        (
            3,
            "understand",
            "Which is a typical cost of choosing an ADC with many more bits than the application needs?",
            [
                "More power, slower conversion and more data",
                "A larger quantization error at every sample",
                "A smaller full-scale input range for the sensor",
                "A lower sensitivity of the sensor itself",
            ],
            "More bits give finer resolution but usually cost more power, conversion time, price and data.",
        ),
        (
            3,
            "understand",
            "Why is the amplifier gain chosen so that the largest sensor signal stays just below the ADC full scale?",
            [
                "To use most of the ADC range without saturating",
                "To make the sampling rate as low as possible",
                "To remove the need for a reference voltage",
                "To make the quantization error larger than one LSB",
            ],
            "A gain close to full scale uses most ADC codes (best resolution) while avoiding clipping.",
        ),
    ],
    "NI": [
        (
            1,
            "recognize",
            "Which of these is a property of an ideal opamp?",
            ["Infinite input resistance", "Zero open-loop gain", "Zero input resistance", "A fixed 1 mV input offset"],
            "An ideal opamp has infinite input resistance, infinite open-loop gain, infinite bandwidth and zero "
            "offset.",
        ),
        (
            1,
            "recognize",
            "In readout design, what is a non-ideality?",
            [
                "A way a real opamp differs from an ideal one, adding an error to the reading",
                "A sensor that measures more than one physical quantity at the same time",
                "A digital code that the ADC cannot produce because of saturation",
                "A sampling rate that is lower than twice the signal frequency",
            ],
            "Non-idealities are the differences between a real and an ideal opamp; each adds an error.",
        ),
        (
            2,
            "recognize",
            "What is the loading effect in a sensor readout?",
            [
                "The amplifier's input resistance draws current, so part of the sensor voltage is lost",
                "The ADC rounds every sample to the nearest discrete level of its range",
                "The sensor output changes when the measured quantity changes direction",
                "The opamp output cannot go beyond the voltages of its power supply",
            ],
            "Rs and Rin form a voltage divider, so the amplifier sees only Vs x Rin / (Rs + Rin).",
        ),
        (
            2,
            "recognize",
            "Which circuit is commonly placed between a high-resistance sensor and the rest of the readout to avoid "
            "loading?",
            ["A voltage follower (buffer)", "A voltage divider", "A second sensor in series", "A larger ADC reference"],
            "A buffer has gain 1 and very high input resistance, so it draws almost no current from the sensor.",
        ),
        (
            3,
            "recognize",
            "What is the input offset voltage of an opamp?",
            [
                "A small DC voltage that acts as if it were added to the input",
                "The largest voltage the output can reach before it saturates",
                "The maximum rate at which the output voltage can change",
                "The voltage lost across the sensor's output resistance",
            ],
            "Offset makes the output non-zero when the input is zero.",
        ),
        (
            3,
            "recognize",
            "What is the slew rate of an opamp?",
            [
                "The maximum rate at which its output voltage can change",
                "The gain it has with no feedback applied",
                "The small current flowing into its input pins",
                "The range of voltages its output can reach",
            ],
            "Slew rate limits how fast the output can change; faster, large signals are distorted.",
        ),
        (
            3,
            "recognize",
            "What does the gain-bandwidth product of an opamp imply?",
            [
                "Higher gain means a lower frequency at which the gain starts to fall",
                "Higher gain means the output can swing beyond the supply voltages",
                "Higher gain means the input offset voltage becomes smaller",
                "Higher gain means the input resistance becomes much higher",
            ],
            "Gain x bandwidth is roughly constant, so raising the gain lowers the usable bandwidth.",
        ),
        (
            2,
            "understand",
            "A sensor with Rs = 1 kOhm is connected to an amplifier with Rin = 1 MOhm. About how much of the sensor "
            "voltage does the amplifier see?",
            ["99.9%", "50%", "90%", "0.1%"],
            "Rin / (Rs + Rin) = 1000 / 1001, about 99.9%; Rin is much larger than Rs, so loading is negligible.",
        ),
        (
            2,
            "understand",
            "A sensor reading is clearly too low when the sensor is connected to the amplifier, but correct when "
            "measured with a very high-resistance meter. What is the most likely cause?",
            [
                "The amplifier's input resistance is not much larger than the sensor's output resistance",
                "The ADC's number of bits is too high for the size of the sensor signal",
                "The sampling rate is more than twice the highest frequency of the signal",
                "The opamp's slew rate is too high for the slowly changing sensor signal",
            ],
            "The amplifier loads the sensor; a buffer or a higher-input-resistance opamp fixes it.",
        ),
        (
            3,
            "understand",
            "An amplifier with a gain of 100 uses an opamp with a 1 mV input offset. What error does the offset cause "
            "at the output?",
            ["0.1 V", "1 mV", "10 mV", "1 V"],
            "The offset is multiplied by the gain: 1 mV x 100 = 0.1 V.",
        ),
        (
            3,
            "understand",
            "For which sensor does the opamp's input bias current matter most?",
            [
                "One with a very high output resistance",
                "One with a very low output resistance",
                "One that already has a digital output",
                "One that is read only once a day",
            ],
            "Bias current flowing through a large source resistance creates a large error voltage.",
        ),
        (
            3,
            "understand",
            "An amplifier designed with resistors for a gain of 1000 measures a gain of 990. Which non-ideality "
            "explains this best?",
            [
                "The opamp's finite open-loop gain",
                "The opamp's high input resistance",
                "The ADC's quantization error",
                "The sensor's hysteresis",
            ],
            "Because the open-loop gain is not infinite, the closed-loop gain is slightly lower than designed.",
        ),
        (
            3,
            "understand",
            "A large, fast audio-frequency signal comes out of an amplifier with sloped, triangular edges instead of "
            "its true shape. Which limit is most likely reached?",
            ["The slew rate", "The input offset voltage", "The input bias current", "The input resistance"],
            "When the output cannot change fast enough, large fast signals are distorted by the slew rate.",
        ),
        (
            3,
            "understand",
            "An amplifier's output stays stuck at the supply voltage whenever the sensor signal is large. What is "
            "happening?",
            [
                "The output is saturating because it cannot swing beyond the supply",
                "The input bias current is flowing through the feedback resistors",
                "The open-loop gain has become infinite at large input signals",
                "The input offset voltage cancels out the sensor signal completely",
            ],
            "The output cannot go beyond the supply voltages, so a too-large signal saturates.",
        ),
    ],
    "DA": [
        (
            1,
            "recognize",
            "Predicting that a machine will fail before it actually happens, using its sensor data, is called what?",
            ["Predictive maintenance", "Anomaly logging", "Data compression", "Edge routing"],
            "Predicting failures before they happen from sensor data is predictive maintenance.",
        ),
        (
            1,
            "recognize",
            "Which goal of IoT data analysis means finding readings that do not fit the normal pattern?",
            ["Anomaly detection", "Monitoring", "Forecasting", "Automation"],
            "Anomaly detection finds readings that do not fit the normal pattern, such as a sudden spike.",
        ),
        (
            2,
            "recognize",
            "In the components of learning, what is the hypothesis set?",
            [
                "The family of candidate models the algorithm may choose from",
                "The unknown function that truly maps inputs to outputs",
                "The table of past input and output examples collected",
                "The error the final model makes on new, unseen data",
            ],
            "The hypothesis set is the family of candidate models, for example all straight lines.",
        ),
        (
            2,
            "recognize",
            "What is the error of a model on new, unseen data called?",
            ["Out-of-sample error", "In-sample error", "Quantization error", "Training error"],
            "In-sample error is on the training data; out-of-sample error is on new, unseen data.",
        ),
        (
            3,
            "recognize",
            "Which type of learning uses training examples that each come with the correct answer?",
            ["Supervised learning", "Unsupervised learning", "Reinforcement learning", "Clustering"],
            "Supervised learning uses labelled examples; unsupervised learning has no labels.",
        ),
        (
            3,
            "recognize",
            "Which type of learning lets an agent learn by trial and error from rewards?",
            ["Reinforcement learning", "Supervised learning", "Unsupervised learning", "Linear regression"],
            "Reinforcement learning learns from rewards, such as a thermostat learning from comfort feedback.",
        ),
        (
            3,
            "recognize",
            "Which Python library is mainly used to handle tables of data, such as sensor logs?",
            ["pandas", "matplotlib", "NumPy", "scikit-learn"],
            "pandas handles tables; NumPy handles arrays, scikit-learn provides models and matplotlib draws plots.",
        ),
        (
            1,
            "understand",
            "Why does IoT data analysis often use machine learning instead of hand-written rules?",
            [
                "The rules behind the data are often unknown or too complex to write by hand",
                "Machine learning models need no data at all to make their predictions",
                "Hand-written rules cannot run on any computer connected to the internet",
                "Machine learning always gives perfect predictions on every sensor",
            ],
            "Machine learning learns a model from the data when the underlying rules are unknown or too complex.",
        ),
        (
            2,
            "understand",
            "A model fits its training data almost perfectly but makes large errors on new data. What is this called?",
            ["Overfitting", "Underfitting", "Feature scaling", "Seasonality"],
            "Fitting the training data including its noise but failing on new data is overfitting.",
        ),
        (
            2,
            "understand",
            "According to the idea of feasibility of learning, when is a model that does well on its training data "
            "likely to do well on new data too?",
            [
                "When the data are representative and there are enough examples",
                "When the model is as complex as possible so it fits every point",
                "When the training data come from a single day of measurements",
                "When the test data were also used to train the same model",
            ],
            "Learning is feasible when the data represent the situations of use and there are enough examples.",
        ),
        (
            3,
            "understand",
            "Predicting tomorrow's energy use in kWh from past readings is which kind of task?",
            ["Supervised regression", "Supervised classification", "Unsupervised clustering", "Reinforcement learning"],
            "The output is a number and past answers are known, so it is supervised regression.",
        ),
        (
            3,
            "understand",
            "Labelling each motor as 'faulty' or 'normal' from its vibration features is which kind of task?",
            ["Supervised classification", "Supervised regression", "Unsupervised clustering", "Time-series smoothing"],
            "The output is a category learned from labelled examples, so it is classification.",
        ),
        (
            3,
            "understand",
            "A temperature sensor occasionally reports 999 degC because of a loose wire. Which pipeline step should "
            "deal with this?",
            [
                "Data cleaning: remove or correct the outliers",
                "Feature scaling before clustering",
                "Splitting the data into training and test sets",
                "Choosing the number of clusters k",
            ],
            "Impossible values from faulty sensors are outliers, handled in the cleaning step.",
        ),
        (
            3,
            "understand",
            "Computing the average vibration of a motor over each minute, to feed into a model, is which pipeline "
            "step?",
            [
                "Choosing or computing features",
                "Cleaning outliers from the data",
                "Collecting labels for past failures",
                "Clustering the motors into groups",
            ],
            "Turning raw readings into inputs such as a one-minute average is feature computation.",
        ),
    ],
    "DAT": [
        (
            1,
            "recognize",
            "In the linear regression model y = w0 + w1 x, what does w1 represent?",
            [
                "The slope: how much y changes when x increases by 1",
                "The value of y when x is 0",
                "The mean squared error of the fitted line",
                "The number of training examples used",
            ],
            "w1 is the slope; w0 is the intercept, the value of y when x is 0.",
        ),
        (
            1,
            "recognize",
            "How are the weights of a linear regression line chosen?",
            [
                "By minimising the mean squared error (least squares)",
                "By maximising the number of clusters",
                "By averaging the last few values of the series",
                "By sorting the data by time before fitting",
            ],
            "Least squares chooses the weights that minimise the mean squared error.",
        ),
        (
            2,
            "recognize",
            "Which component of a time series is a pattern that repeats with a fixed period, such as a daily cycle?",
            ["Seasonality", "Trend", "Noise", "Intercept"],
            "Seasonality repeats with a fixed period; the trend is a long-term increase or decrease.",
        ),
        (
            2,
            "recognize",
            "What does a moving average do to a time series?",
            [
                "It smooths out noise so the trend is easier to see",
                "It removes the time order of the readings",
                "It groups the readings into k clusters",
                "It turns the readings into labels",
            ],
            "A moving average averages the last few values, which smooths noise.",
        ),
        (
            2,
            "recognize",
            "What does an autoregressive (AR) model use to predict the next value?",
            [
                "A weighted sum of previous values of the series",
                "The distance to the nearest cluster centre",
                "Only the value of a different, unrelated sensor",
                "A random value drawn from the training data",
            ],
            "An AR model predicts the next value from previous values.",
        ),
        (
            3,
            "recognize",
            "Clustering is which type of learning?",
            ["Unsupervised", "Supervised", "Reinforcement", "Regression"],
            "Clustering groups unlabelled data, so it is unsupervised.",
        ),
        (
            3,
            "recognize",
            "In k-means, what is each point assigned to in every iteration?",
            ["Its nearest centroid", "The largest cluster", "A random cluster", "The cluster with the oldest data"],
            "Each point is assigned to its nearest centroid, then the centroids move to the mean of their points.",
        ),
        (
            1,
            "understand",
            "A line fitted as y = 1.5 + 0.2 x is used with x = 10. What is the prediction?",
            ["3.5", "2.0", "1.7", "15.2"],
            "1.5 + 0.2 x 10 = 3.5.",
        ),
        (
            1,
            "understand",
            "For the fitted line y = 1.5 + 0.2 x, what does the number 1.5 mean?",
            [
                "The predicted y when x is 0",
                "The change in y when x increases by 1",
                "The mean squared error of the line",
                "The largest x used in training",
            ],
            "1.5 is the intercept w0, the value of y when x is 0.",
        ),
        (
            1,
            "understand",
            "Model A has a test MSE of 4.0 and model B has a test MSE of 9.0. Which predicts better?",
            ["Model A", "Model B", "They are equally good", "It cannot be compared with MSE"],
            "A smaller MSE means the predictions are closer to the actual values.",
        ),
        (
            2,
            "understand",
            "A 24-hour moving average is drawn over three months of hourly temperatures. What does it mainly show?",
            [
                "The slow long-term movement, with the daily cycle smoothed out",
                "Every individual daily peak more sharply than the raw data",
                "Only the random noise left after removing the trend",
                "The temperature forecast for the next three months",
            ],
            "Averaging a full day smooths the daily cycle and the noise, leaving the slow long-term movement.",
        ),
        (
            2,
            "understand",
            "To capture a daily cycle in hourly temperature data, which extra input helps an AR model?",
            [
                "The value from 24 hours earlier",
                "The value from 24 days earlier",
                "The value of a random other hour",
                "The total number of readings",
            ],
            "In hourly data the daily cycle repeats every 24 values, so the value 24 hours earlier helps.",
        ),
        (
            3,
            "understand",
            "After clustering households by energy use, one new reading is far from every centroid. How can it be "
            "treated?",
            [
                "As a possible anomaly worth checking",
                "As the centre of a new largest cluster",
                "As proof that k must be reduced to one",
                "As a reading that belongs to every cluster",
            ],
            "A point far from all centroids does not fit any normal group, so it can be flagged as an anomaly.",
        ),
        (
            3,
            "understand",
            "In the elbow method, which k is usually chosen?",
            [
                "The k after which more clusters stop giving a large improvement",
                "The largest k that was tried",
                "The k that gives exactly one point per cluster",
                "The k equal to the number of features",
            ],
            "The elbow is where adding clusters stops reducing the total distance much.",
        ),
    ],
}


# Bổ sung lên mục tiêu D25 (SKILL_TARGET: 12 nhận biết + 12 thông hiểu / kỹ năng) — Tuấn duyệt hướng B 27/11.
# Mã nối tiếp TN-15… ; build xoay vị trí đáp án của MCQ_EXTRA SAU mọi câu cũ → câu cũ giữ nguyên từng byte.
MCQ_EXTRA = {
    "IOT": [
        (
            1,
            "recognize",
            "Which key characteristic of IoT refers to systems with billions of connected devices?",
            ["Very large scale", "Unique identity", "Heterogeneity", "Connectivity"],
            "Very large scale means IoT systems can contain billions of devices.",
        ),
        (
            1,
            "recognize",
            "Which of these is an example of a thing sensing its environment?",
            [
                "A sensor measuring the light level in a room",
                "A cloud server storing last month's readings",
                "A phone app showing a chart of temperatures",
                "A router forwarding packets to the internet",
            ],
            "Things sense their environment, for example temperature, motion or light.",
        ),
        (
            2,
            "recognize",
            "In a smart home, which task can a rule automate?",
            [
                "Turning off the lights when nobody is in a room",
                "Choosing the vendor of each new device",
                "Writing the firmware for the door lock",
                "Replacing the batteries of every sensor",
            ],
            "Rules automate devices, such as turning off lights when nobody is in a room.",
        ),
        (
            2,
            "recognize",
            "Which smart-city service helps drivers find free spaces?",
            ["Smart parking", "Air quality monitoring", "Predictive maintenance", "Remote health monitoring"],
            "Smart parking shows drivers where free spaces are.",
        ),
        (
            3,
            "recognize",
            "What can attackers build from many hijacked IoT devices?",
            ["A botnet", "A gateway", "A dashboard", "A sensor network"],
            "Attackers can take devices over and combine them into a botnet.",
        ),
        (
            1,
            "understand",
            "A sensor sleeps for an hour to save energy and then rejoins the network. Which IoT "
            "characteristic does this illustrate?",
            ["Dynamic change", "Unique identity", "Very large scale", "Sensing"],
            "Devices joining, leaving, moving or sleeping is dynamic change.",
        ),
        (
            2,
            "understand",
            "A city mounts sensors on lampposts to measure pollution levels. Which IoT application is this?",
            ["Air quality monitoring", "Smart parking", "Predictive maintenance", "Home automation"],
            "Measuring pollution in a city is air quality monitoring.",
        ),
        (
            3,
            "understand",
            "A platform must manage millions of devices and handle large volumes of data. Which IoT "
            "challenge is this mainly about?",
            ["Scalability", "Privacy", "Interoperability", "Sensing"],
            "Scalability is about managing very many devices and large volumes of data.",
        ),
        (
            2,
            "understand",
            "From work, a homeowner checks on a phone whether the front door is locked. Which smart-home "
            "capability is this?",
            [
                "Monitoring and controlling devices remotely from a phone",
                "Predicting failures of the door motor",
                "Translating between two radio protocols",
                "Measuring the vibration of the door",
            ],
            "Smart-home devices such as door locks can be monitored and controlled from a phone.",
        ),
        (
            1,
            "understand",
            "A smart blind closes automatically when a light sensor detects strong sun. Which device "
            "acts on the physical world?",
            ["The motor that moves the blind", "The light sensor", "The phone app", "The Wi-Fi router"],
            "Actuators such as motors act on the physical world; the light sensor only senses.",
        ),
    ],
    "IOTM": [
        (
            1,
            "recognize",
            "Besides translating between protocols, what else can an IoT gateway do with the data?",
            [
                "Filter or aggregate it",
                "Generate it from scratch",
                "Encrypt the sensors' firmware",
                "Replace the cloud platform",
            ],
            "A gateway can translate between protocols and filter or aggregate data.",
        ),
        (
            1,
            "recognize",
            "Which component of an IoT system lets people see the data and send commands?",
            [
                "The application or user interface, such as a mobile app",
                "The microcontroller inside each node",
                "The radio that sends readings to the gateway",
                "The actuator that switches a relay",
            ],
            "An application or user interface such as a mobile app or dashboard lets people see data and send commands.",
        ),
        (
            2,
            "recognize",
            "In the five-layer architecture, which layer manages business models and user privacy?",
            ["Business layer", "Processing layer", "Network layer", "Perception layer"],
            "The business layer on top manages the whole system, including business models and user privacy.",
        ),
        (
            2,
            "recognize",
            "What is another name for the perception layer?",
            ["The sensing (device) layer", "The middleware layer", "The business layer", "The transport layer"],
            "The perception layer is also called the sensing or device layer.",
        ),
        (
            3,
            "recognize",
            "Which IoT design goal means each device should be cheap to produce?",
            ["Low cost per device", "Scalability", "Reliability", "Interoperability"],
            "Low cost per device is one of the design goals of IoT systems.",
        ),
        (
            3,
            "understand",
            "A patient-monitoring device must keep working even if one network link fails. Which design goal is this?",
            ["Reliability", "Low cost per device", "Low power consumption", "Back-end data sharing"],
            "Reliability means the system keeps working correctly even when parts fail.",
        ),
        (
            3,
            "understand",
            "A company builds protection of users' data into a product from the start instead of adding "
            "it later. Which design goal is this?",
            ["Security and privacy by design", "Scalability", "Low cost per device", "Interoperability"],
            "Security and privacy by design build protection in from the start.",
        ),
        (
            1,
            "understand",
            "In the home automation example described in this course, a motion sensor's event passes through the "
            "hub to which place, where a rule turns on the light?",
            ["The cloud", "The motion sensor itself", "The light bulb's battery", "The Wi-Fi router"],
            "In the example, the motion sensor sends an event through a hub (gateway) to the cloud, and a rule there "
            "turns on the light. Other systems may run such rules on the hub or at the edge.",
        ),
        (
            1,
            "understand",
            "When a rule fires, a motor opens a window. Which IoT component is the motor?",
            ["An actuator", "A sensor", "A gateway", "A cloud platform"],
            "Actuators change the physical world, for example by turning a motor.",
        ),
        (
            3,
            "understand",
            "A weather station uploads its readings straight to a cloud service over its own Wi-Fi. "
            "Which communication model is this?",
            ["Device-to-cloud", "Device-to-device", "Device-to-gateway", "Back-end data sharing"],
            "Connecting directly to a cloud service over the internet is the device-to-cloud model.",
        ),
    ],
    "MSG": [
        (
            1,
            "recognize",
            "Which port is used for MQTT over TLS?",
            ["8883", "1883", "5683", "8080"],
            "MQTT uses port 1883 by default and 8883 over TLS.",
        ),
        (
            2,
            "recognize",
            "Which packet does an MQTT client send to show the broker it is still connected?",
            ["PINGREQ", "PUBACK", "PUBREC", "SUBSCRIBE"],
            "During the keep-alive interval the client sends PINGREQ packets.",
        ),
        (
            2,
            "recognize",
            "How many steps does the MQTT QoS 2 handshake use?",
            ["Four", "One", "Two", "Three"],
            "QoS 2 uses PUBLISH, PUBREC, PUBREL and PUBCOMP.",
        ),
        (
            3,
            "recognize",
            "What is CoAP's default port?",
            ["5683", "1883", "8883", "443"],
            "CoAP runs over UDP, by default on port 5683.",
        ),
        (
            3,
            "recognize",
            "Which CoAP message type indicates that a received message could not be processed?",
            ["Reset (RST)", "Acknowledgement (ACK)", "Confirmable (CON)", "Non-confirmable (NON)"],
            "A Reset (RST) message indicates that a received message could not be processed.",
        ),
        (
            1,
            "understand",
            "Which MQTT subscription is NOT valid?",
            ["home/#/temperature", "home/#", "home/+/temperature", "home/kitchen/temperature"],
            "The hash sign must be the last character of a topic filter.",
        ),
        (
            3,
            "understand",
            "A CoAP client requests /humidity, but the server has no such resource. Which response code is typical?",
            ["4.04 Not Found", "2.05 Content", "2.01 Created", "5.00 Internal Server Error"],
            "CoAP response codes are similar to HTTP: 4.04 Not Found for a missing resource.",
        ),
        (
            2,
            "understand",
            "Why does QoS 2 create more network traffic than QoS 0?",
            [
                "It uses a four-step handshake to deliver exactly once",
                "It sends every message to every topic",
                "It needs a separate TLS connection for each topic",
                "It repeats each message until a GET arrives",
            ],
            "QoS 2 delivers exactly once through a four-step handshake, at the cost of more overhead.",
        ),
        (
            1,
            "understand",
            "How many levels does the MQTT topic factory/line1/motor3/temp have?",
            ["4", "1", "3", "5"],
            "Topic levels are separated by slashes: factory, line1, motor3 and temp.",
        ),
        (
            3,
            "understand",
            "A CoAP client wants to change the value of an existing resource on a server. Which method fits best?",
            ["PUT", "GET", "DELETE", "Observe"],
            "Like HTTP, CoAP uses PUT to update a resource; GET reads it and DELETE removes it.",
        ),
    ],
    "SENS": [
        (
            1,
            "recognize",
            "What is the physical quantity that a sensor measures called?",
            ["The measurand", "The threshold", "The excitation", "The resolution"],
            "A sensor detects a physical quantity, called the measurand, and converts it into a signal.",
        ),
        (
            1,
            "recognize",
            "What kind of output does a digital sensor give?",
            [
                "A digital value, for example over a serial bus",
                "A continuous voltage that an ADC must sample",
                "A change in resistance that needs a current",
                "A small voltage generated from heat",
            ],
            "An analog sensor gives a continuous signal; a digital sensor already gives a digital value.",
        ),
        (
            2,
            "recognize",
            "What happens to the resistance of an NTC thermistor as the temperature rises?",
            ["It falls", "It rises", "It stays constant", "It becomes zero"],
            "An NTC thermistor's resistance falls as the temperature rises.",
        ),
        (
            3,
            "recognize",
            "What is the range of a sensor?",
            [
                "The span between the smallest and largest value it can measure",
                "The smallest change in input that it can detect",
                "The change in output per unit change in input",
                "The time it needs to reach its final output",
            ],
            "Range is the span between the smallest and largest measurable value.",
        ),
        (
            3,
            "recognize",
            "What is a slow change in a sensor's output for the same input over time called?",
            ["Drift", "Hysteresis", "Threshold", "Specificity"],
            "Stability is giving the same output over time; a slow change is called drift.",
        ),
        (
            1,
            "understand",
            "An infrared thermometer measures a person's forehead from 5 cm away. How is it classified?",
            ["Non-contact", "Contact", "Self-generating", "Digital only"],
            "It measures without touching the object, so it is a non-contact sensor.",
        ),
        (
            2,
            "understand",
            "An IC temperature sensor outputs 10 mV per degC and 0 V at 0 degC. What is its output at 25 degC?",
            ["250 mV", "25 mV", "2.5 V", "10 mV"],
            "The output is linear: 25 degC x 10 mV per degC = 250 mV.",
        ),
        (
            3,
            "understand",
            "A datasheet says the output deviates at most 0.5 degC from the best straight line. What "
            "does this figure describe?",
            ["The non-linearity error", "The response time", "The hysteresis", "The threshold"],
            "The largest deviation from the straight line is the non-linearity error.",
        ),
        (
            3,
            "understand",
            "A scale shows no change for loads below 2 g but responds to heavier loads. Which "
            "characteristic is the 2 g?",
            ["The threshold", "The range", "The drift", "The sensitivity"],
            "Threshold is the smallest input, starting from zero, that produces a detectable output.",
        ),
        (
            2,
            "understand",
            "An inductive sensor cannot detect plastic bottles on a conveyor. Which proximity sensor "
            "type could detect them?",
            ["A capacitive proximity sensor", "A second inductive sensor", "A thermocouple", "An NTC thermistor"],
            "Inductive sensors detect only metal; capacitive sensors detect a change in capacitance from other objects.",
        ),
    ],
    "RO": [
        (
            1,
            "recognize",
            "For a resistive sensor, what does the front end of a readout chain usually do?",
            [
                "Passes an excitation current and turns the resistance change into a voltage",
                "Converts the digital codes back into an analog voltage",
                "Stores the readings in the cloud for later analysis",
                "Rounds every sample to the nearest ADC level",
            ],
            "The front end turns the sensor change into a voltage, for example by passing an excitation current.",
        ),
        (
            1,
            "recognize",
            "Which block of a readout chain finally processes the digital codes?",
            ["The microcontroller", "The front end", "The opamp amplifier", "The sensor itself"],
            "The microcontroller processes the codes produced by the ADC.",
        ),
        (
            2,
            "recognize",
            "What is the sampling rate of an ADC?",
            [
                "The number of samples taken per second",
                "The number of bits in each code",
                "The size of one quantization step",
                "The largest voltage it can convert",
            ],
            "The sampling rate is the number of samples per second.",
        ),
        (
            3,
            "recognize",
            "What does quantization turn a continuous input into?",
            [
                "A staircase of discrete levels",
                "A smooth analog curve",
                "A higher sampling rate",
                "A larger reference voltage",
            ],
            "Quantization maps each value to the nearest discrete level, so the input becomes a staircase.",
        ),
        (
            3,
            "recognize",
            "Why is the sampling rate usually not set much higher than needed?",
            [
                "To save power and data",
                "To make the LSB larger",
                "To increase the quantization error",
                "To avoid using an amplifier",
            ],
            "A sampling rate far above what is needed wastes power and produces more data.",
        ),
        (
            2,
            "understand",
            "How many output codes does a 16-bit ADC have?",
            ["65536", "16", "256", "4096"],
            "An N-bit ADC has 2^N codes; 2^16 = 65536.",
        ),
        (
            3,
            "understand",
            "An application needs 0.5 degC resolution from a 10 mV per degC sensor. What is the largest "
            "acceptable LSB?",
            ["5 mV", "0.5 mV", "50 mV", "20 mV"],
            "The LSB in degC must be at most 0.5 degC: 0.5 degC x 10 mV per degC = 5 mV.",
        ),
        (
            3,
            "understand",
            "A sensor already gives 0 to 2 V and the ADC's full scale is 2.048 V. Is extra gain useful?",
            [
                "Hardly; the signal already uses most of the ADC range",
                "Yes; a gain of about 40 is needed",
                "Yes; the ADC cannot read signals above 1 V",
                "No; the ADC needs a signal of at least 5 V",
            ],
            "The signal already comes close to full scale, so more gain would risk saturation without much benefit.",
        ),
        (
            1,
            "understand",
            "A strain gauge changes its resistance, not its voltage. What must the readout do first?",
            [
                "Turn the resistance change into a voltage, for example with an excitation current",
                "Send the resistance value directly to the microcontroller",
                "Lower the sampling rate below the signal frequency",
                "Remove the ADC and use a digital sensor instead",
            ],
            "The front end must turn the resistance change into a voltage before amplification and conversion.",
        ),
        (
            3,
            "understand",
            "How does quantization error usually behave in a measurement?",
            [
                "Like a small added noise",
                "Like a slowly growing drift",
                "Like a sudden saturation",
                "Like a change of sampling rate",
            ],
            "With rounding to the nearest level, quantization error behaves like a small added noise.",
        ),
    ],
    "NI": [
        (
            1,
            "recognize",
            "What output resistance does an ideal opamp have?",
            ["Zero", "Infinite", "Equal to the sensor's resistance", "1 kOhm"],
            "An ideal opamp has zero output resistance and infinite input resistance.",
        ),
        (
            1,
            "recognize",
            "A designer is choosing an opamp for a thermocouple amplifier with a gain of 500. What should be checked "
            "before buying it?",
            [
                "Its datasheet limits, such as offset, against the needs of the sensor and application",
                "Only its supply voltage, because all opamps behave alike at any gain",
                "Only its price, because non-idealities never matter in sensor readout",
                "Only its output current, because the input side does not affect accuracy",
            ],
            "Designers check the opamp's datasheet limits against the sensor and application; with a gain of 500 and "
            "microvolt signals, offset and other non-idealities matter.",
        ),
        (
            3,
            "recognize",
            "What is a typical size of an opamp's input offset voltage?",
            ["Microvolts to a few millivolts", "Several volts", "Exactly zero", "Hundreds of volts"],
            "Input offset voltage is typically microvolts to a few millivolts.",
        ),
        (
            2,
            "recognize",
            "Which kind of opamp inputs gives a very high input resistance?",
            [
                "CMOS or FET inputs",
                "Inputs with a 1 kOhm resistor",
                "Inputs connected to ground",
                "Inputs with a large offset",
            ],
            "Opamps with CMOS or FET inputs have a very high input resistance.",
        ),
        (
            1,
            "recognize",
            "In which situation do opamp non-idealities matter most?",
            [
                "When the sensor signal is tiny",
                "When the signal is large and slow",
                "When the gain is exactly 1 and the source resistance is low",
                "When no ADC is used",
            ],
            "Errors matter most with tiny signals, large gain, high source resistance or fast signals.",
        ),
        (
            3,
            "understand",
            "An amplifier with a gain of 10 uses an opamp with a 2 mV input offset. What output error "
            "does the offset cause?",
            ["20 mV", "2 mV", "0.2 mV", "200 mV"],
            "The offset is multiplied by the gain: 2 mV x 10 = 20 mV.",
        ),
        (
            3,
            "understand",
            "Raising an amplifier's gain from 10 to 100 with the same opamp changes its bandwidth how?",
            [
                "It becomes about ten times lower",
                "It becomes about ten times higher",
                "It stays exactly the same",
                "It becomes zero",
            ],
            "The gain-bandwidth product is roughly constant, so ten times more gain gives about ten times less bandwidth.",
        ),
        (
            3,
            "understand",
            "An opamp on a 5 V supply is asked to output 7 V. What happens?",
            [
                "The output saturates near the supply voltage",
                "The output reaches 7 V but slowly",
                "The opamp adds an offset of 2 V",
                "The input resistance becomes zero",
            ],
            "The output cannot swing beyond the supply voltages, so it saturates.",
        ),
        (
            2,
            "understand",
            "A sensor with Rs = 2 kOhm feeds an amplifier with Rin = 2 kOhm. What fraction of the "
            "sensor voltage does the amplifier see?",
            ["50%", "100%", "25%", "99%"],
            "Rin / (Rs + Rin) = 2 / (2 + 2) = 50%.",
        ),
        (
            1,
            "understand",
            "An opamp has a slew rate of 1 V per microsecond. What is the shortest time its output needs to rise by 5 V?",
            ["5 microseconds", "1 microsecond", "0.2 microseconds", "50 microseconds"],
            "The output can change at most 1 V per microsecond, so a 5 V step needs at least 5 microseconds.",
        ),
    ],
    "DA": [
        (
            1,
            "recognize",
            "Which goal of IoT data analysis means showing the current state of a system on a dashboard?",
            ["Monitoring", "Anomaly detection", "Automation", "Prediction"],
            "Monitoring shows the current state of a system, for example on a dashboard.",
        ),
        (
            1,
            "recognize",
            "Forecasting a building's energy demand for next week is an example of which analysis goal?",
            ["Prediction", "Monitoring", "Automation", "Anomaly detection"],
            "Forecasting what will happen, such as energy demand, is prediction.",
        ),
        (
            3,
            "recognize",
            "Which Python library provides ready-made models such as linear regression and k-means?",
            ["scikit-learn", "pandas", "NumPy", "matplotlib"],
            "scikit-learn provides models; pandas handles tables, NumPy arrays and matplotlib plots.",
        ),
        (
            2,
            "recognize",
            "In the components of learning, what is the target function f?",
            [
                "The unknown mapping from inputs to outputs",
                "The model that the algorithm finally selects",
                "The set of past examples used for training",
                "The error measured on new, unseen data",
            ],
            "f is the unknown function that maps inputs to outputs; the data set holds past examples of it.",
        ),
        (
            3,
            "recognize",
            "What is the part of the data that is used to fit the model called?",
            ["Training set", "Test set", "Hypothesis set", "Target set"],
            "The training set fits the model; the test set is kept aside.",
        ),
        (
            1,
            "understand",
            "A system switches irrigation on by itself when it predicts that the soil will be dry. Which analysis goal is the switching?",
            ["Automation", "Monitoring", "Anomaly detection", "Data cleaning"],
            "Letting the system act by itself is automation.",
        ),
        (
            3,
            "understand",
            "Which order of steps is right for a data-driven project?",
            [
                "Collect, clean, build features, split, train, evaluate",
                "Collect, build features, clean, split, train, evaluate",
                "Collect, clean, split, evaluate, build features, train",
                "Collect, clean, build features, train, split, evaluate",
            ],
            "Data are collected and cleaned, turned into features, split, used for training and then evaluated.",
        ),
        (
            3,
            "understand",
            "A team tries many model settings and keeps the one with the lowest error on the test set. "
            "What is wrong with this?",
            [
                "The test set helped choose the model, so it is no longer unseen",
                "Test error can only be computed after the features are removed",
                "The test set must always be larger than the training set",
                "A lower test error always means the model is overfitting",
            ],
            "The test set is kept aside to check unseen data; a model picked by its test error has already used it.",
        ),
        (
            3,
            "understand",
            "A utility has smart-meter data without any labels and wants to find groups of similar households. Which type of learning fits?",
            ["Unsupervised learning", "Supervised learning", "Reinforcement learning", "Regression"],
            "There are no labels and the algorithm must find structure itself, so it is unsupervised.",
        ),
        (
            1,
            "understand",
            "A factory streams vibration readings every second, together with camera images and machine logs. What does this mainly illustrate?",
            [
                "IoT data are large in volume and come in many forms",
                "IoT data are useful before any analysis is done",
                "IoT systems can only analyse numeric readings",
                "IoT sensors usually report just once a day",
            ],
            "Sensors report continuously and the data come in many forms, which is why analysis is needed.",
        ),
    ],
    "DAT": [
        (
            2,
            "recognize",
            "What is a time series?",
            [
                "Measurements taken in time order",
                "Measurements sorted by their size",
                "Groups of similar measurements",
                "Measurements with the time removed",
            ],
            "A time series is a sequence of measurements in time order, usually at regular intervals.",
        ),
        (
            3,
            "recognize",
            "What does clustering aim for?",
            [
                "Similar points share a group and different points are separated",
                "Each point receives a numeric prediction from a fitted line",
                "The next value is forecast from the values that came before",
                "Every group contains the same number of points as the others",
            ],
            "Clustering groups points so that points in a cluster are similar and clusters differ.",
        ),
        (
            3,
            "recognize",
            "What is usually done to features before k-means is run?",
            [
                "They are scaled (standardised)",
                "They are sorted by time",
                "They are turned into class labels",
                "They are replaced by their cluster number",
            ],
            "k-means uses distances, so features are usually scaled first.",
        ),
        (
            1,
            "recognize",
            "Predicting far outside the range of inputs used for training is called what?",
            ["Extrapolation", "Interpolation", "Standardisation", "Overfitting"],
            "Extrapolation can be badly wrong because the relationship may not stay linear.",
        ),
        (
            3,
            "recognize",
            "In k-means, what must be chosen before the algorithm can start?",
            [
                "The number of clusters k",
                "The final group of every point",
                "A label for every data point",
                "The slope of a fitted line",
            ],
            "First choose k and k starting centres; the groups are found by the algorithm.",
        ),
        (
            1,
            "understand",
            "For the fitted line y = 10 - 2 x, what happens to the prediction when x increases by 1?",
            ["It decreases by 2", "It increases by 10", "It decreases by 10", "It increases by 2"],
            "The slope is -2, so y falls by 2 for each increase of 1 in x.",
        ),
        (
            1,
            "understand",
            "A line predicts 5 and 8, while the actual values are 4 and 10. What is the mean squared error?",
            ["2.5", "1.5", "5.0", "3.0"],
            "The errors are 1 and −2; their squares are 1 and 4, and the mean is 2.5.",
        ),
        (
            2,
            "understand",
            "A model for hourly electricity load is trained on January to March and tested on April. Why is this a sound split?",
            [
                "The model is tested on a later period that it has not seen",
                "April always has less noise than the three earlier months",
                "Testing on April shuffles the readings in a random order",
                "The test period must be longer than the training period",
            ],
            "A time series is split in time order, so training never uses knowledge of the future.",
        ),
        (
            2,
            "understand",
            "Over five years, a building's average energy use climbs slowly, apart from its daily ups and downs. Which time-series component is the slow climb?",
            ["Trend", "Seasonality", "Noise", "Intercept"],
            "A long-term increase or decrease is the trend.",
        ),
        (
            3,
            "understand",
            "In k-means, a cluster holds the points (2, 2), (4, 2) and (6, 5). Where does its centroid move?",
            ["(4, 3)", "(4, 2)", "(6, 5)", "(12, 9)"],
            "The centroid moves to the mean of its points: x = 12 / 3 = 4 and y = 9 / 3 = 3.",
        ),
    ],
}
