# ruff: noqa: ISC004 — dữ liệu đề: chuỗi dài ngắt dòng trong danh sách là cố ý
"""Đoạn tri thức khóa 494 — (mã kỹ năng, tiêu đề, nội dung). Mã đoạn: <KỸ NĂNG>-K01, K02… theo thứ tự.
Đợt 1 (26/11/2026): IOT, IOTM, MSG — module 1 + messaging của module 3.
Đợt 2 (27/11): SENS, RO, NI — module 2 "Sensors & Interfaces".
Đợt 3 (27/11): DA, DAT — module 4 "Data Analysis for IoT".
Mỗi đoạn bám tên video trong đề cương công khai của khóa (IIT Bombay, Coursera)."""

CHUNKS = [
    (
        "IOT",
        "What the Internet of Things is",
        "The Internet of Things (IoT) is a network of physical objects, called things, that have sensors, software and "
        "network connectivity so they can collect data and exchange it with other devices and systems over the internet. "
        "Each thing needs a unique identity, such as an IP address or a device ID, so that it can be found and "
        "addressed. Things sense their environment, for example temperature, motion or light, and some can also act on "
        "it through actuators such as motors, valves or switches. Key characteristics of IoT are connectivity, sensing, "
        "unique identity, heterogeneity (devices from many vendors with different hardware and protocols), very large "
        "scale (billions of devices) and dynamic change, because devices join, leave, move or sleep to save energy. Many "
        "IoT devices are constrained: they have little memory, low processing power and run on batteries.",
    ),
    (
        "IOT",
        "Applications of IoT",
        "IoT is used in many sectors. In smart homes, connected lights, thermostats, door locks and cameras can be "
        "monitored and controlled from a phone, and rules can automate them, such as turning off lights when nobody is "
        "in a room. In agriculture, soil moisture sensors tell an irrigation system when to water crops, which saves "
        "water. In healthcare, wearable devices track heart rate or blood glucose and can alert doctors remotely. In "
        "industry, sensors on machines measure vibration and temperature to predict failures before they happen, which "
        "is called predictive maintenance. In smart cities, IoT supports smart parking, street lights that dim when "
        "roads are empty, and air quality monitoring.",
    ),
    (
        "IOT",
        "Challenges of IoT",
        "IoT also brings challenges. Security is a major one: many devices ship with default passwords and rarely get "
        "software updates, so attackers can take them over, for example to build a botnet. Privacy is another, because "
        "sensors in homes and wearables collect personal data about people's habits and health. Interoperability is hard "
        "because devices from different vendors use different protocols and data formats, so they cannot always work "
        "together; standards and gateways help. Energy is limited for battery-powered devices, so they must use "
        "low-power hardware and radios and sleep most of the time. Scalability matters because a system may have to "
        "manage millions of devices and handle large volumes of data.",
    ),
    (
        "IOTM",
        "Components of an IoT system",
        "A typical IoT system has several components. Sensors measure physical quantities such as temperature, humidity "
        "or motion, and actuators change the physical world, for example by switching a relay or turning a motor. The "
        "sensors and actuators are attached to an IoT node (device), usually built around a microcontroller with a "
        "radio. A gateway connects local devices to the internet and can translate between protocols, for example from "
        "Zigbee or Bluetooth to Wi-Fi or Ethernet, and can filter or aggregate data. The network carries the data, and a "
        "cloud or server platform stores and analyses it. Finally, an application or user interface, such as a mobile "
        "app or dashboard, lets people see the data and send commands. In home automation, a motion sensor in a room "
        "sends an event through a hub (gateway) to the cloud, and a rule turns on the light.",
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
        "connects directly to a cloud service over the internet, for example through Wi-Fi. In the device-to-gateway "
        "model, devices connect to a local gateway, such as a smartphone or hub, which forwards data to the cloud. In "
        "the back-end data-sharing model, data collected in one cloud service is shared with other authorised services "
        "so they can combine and analyse it. Design goals for IoT systems include low power consumption, low cost per "
        "device, scalability, reliability, security and privacy by design, and interoperability between devices from "
        "different vendors.",
    ),
    (
        "MSG",
        "MQTT basics",
        "MQTT (Message Queuing Telemetry Transport) is a lightweight messaging protocol designed for constrained devices "
        "and unreliable networks. It uses a publish/subscribe model: clients do not send messages directly to each other "
        "but to a central server called a broker. A client that sends data publishes a message to a topic, a text string "
        "such as home/livingroom/temperature, and the broker forwards the message to every client that has subscribed to "
        "that topic. Topics are hierarchical, with levels separated by slashes. Subscribers can use wildcards: the plus "
        "sign (+) matches exactly one level, so home/+/temperature matches home/kitchen/temperature, and the hash sign "
        "(#) matches all remaining levels and must be the last character, so home/# matches every topic under home. MQTT "
        "runs over TCP; the default port is 1883, and 8883 is used for MQTT over TLS.",
    ),
    (
        "MSG",
        "MQTT quality of service and session features",
        "MQTT offers three Quality of Service (QoS) levels for delivering a message. QoS 0 means at most once: the "
        "message is sent once without acknowledgement, so it may be lost. QoS 1 means at least once: the sender keeps "
        "the message until it receives a PUBACK, so the message arrives but may be duplicated. QoS 2 means exactly once: "
        "a four-step handshake (PUBLISH, PUBREC, PUBREL, PUBCOMP) makes sure the message arrives once, at the cost of "
        "more overhead. A retained message is stored by the broker for its topic and sent immediately to new "
        "subscribers, so they get the last known value. The Last Will and Testament is a message the client registers "
        "when it connects; the broker publishes it if the client disconnects unexpectedly. The keep-alive interval tells "
        "the broker how long the client may stay silent; the client sends PINGREQ packets to show it is still "
        "connected.",
    ),
    (
        "MSG",
        "CoAP",
        "CoAP (Constrained Application Protocol) is a web transfer protocol for constrained devices and networks, "
        "standardised by the IETF in RFC 7252. Like HTTP it follows the REST style: resources are identified by URIs and "
        "accessed with the methods GET, POST, PUT and DELETE, and responses use codes similar to HTTP, such as 2.05 "
        "Content or 4.04 Not Found. Unlike HTTP, CoAP runs over UDP, by default on port 5683, and uses a compact 4-byte "
        "fixed header to save bandwidth and energy. Because UDP is unreliable, CoAP has its own message types: "
        "Confirmable (CON) messages must be acknowledged with an Acknowledgement (ACK) and are retransmitted if no ACK "
        "arrives; Non-confirmable (NON) messages are not acknowledged; a Reset (RST) message indicates that a received "
        "message could not be processed. With the Observe option, a client can register interest in a resource and the "
        "server sends notifications whenever it changes.",
    ),
    (
        "SENS",
        "Classification of sensors",
        "A sensor detects a physical quantity, called the measurand, and converts it into a signal that a circuit can "
        "use, usually an electrical voltage, current, resistance or capacitance. Sensors are classified in several ways. "
        "By measurand: temperature, pressure, acceleration, displacement, proximity, light or humidity sensors. By the "
        "need for an external power source: a self-generating sensor produces its own electrical signal from the energy "
        "it measures, for example a thermocouple, which generates a small voltage from heat, a solar cell or a "
        "piezoelectric sensor; an externally excited sensor needs an excitation or power source to produce its output, "
        "for example a thermistor, an RTD or a strain gauge, whose resistance can only be read by passing a current "
        "through it. The labels active and passive are used for these two groups in opposite ways: many Indian "
        "engineering texts (NPTEL / IIT) call self-generating sensors active and excited sensors passive, while some "
        "other books use the reverse, so it is clearer to describe the group than to rely on the label. By output: an "
        "analog sensor gives a continuous signal, while a digital sensor already gives a digital value, for example over "
        "a serial bus. Sensors can also be contact (touching the object) or non-contact (for example infrared or "
        "ultrasonic).",
    ),
    (
        "SENS",
        "Case studies: accelerometer, proximity and temperature sensors",
        "A capacitive MEMS accelerometer contains a tiny proof mass held by springs. When the device accelerates, the "
        "mass moves relative to the frame, and because the mass forms a movable plate between fixed plates, the "
        "capacitance between the plates changes; often one capacitance increases while the other decreases. The readout "
        "measures this change, which is proportional to the acceleration. Accelerometers are used in phones, wearables "
        "and vibration monitoring. Displacement and proximity sensors detect position or the presence of a nearby "
        "object: capacitive sensors detect a change in capacitance, inductive sensors detect metal objects through a "
        "change in inductance, and ultrasonic sensors measure the time of flight of an echo, so distance = speed of "
        "sound x time / 2. Temperature sensors include the thermistor, whose resistance changes strongly with "
        "temperature (an NTC thermistor's resistance falls as temperature rises), giving high sensitivity but a "
        "non-linear response over a limited range; the RTD, usually platinum, whose resistance rises almost linearly and "
        "which is accurate and stable; the thermocouple, two different metals joined at a junction that produce a small "
        "voltage of tens of microvolts per degree, which works over a very wide range up to more than 1000 degC and, "
        "with a small junction, responds quickly; and IC temperature sensors that give a linear output such as 10 mV per "
        "degC.",
    ),
    (
        "SENS",
        "Sensor characteristics",
        "Sensor characteristics describe and compare sensors. Range is the span between the smallest and largest value "
        "the sensor can measure. Sensitivity is the change in output per unit change in input, the slope of the "
        "response, for example 10 mV per degC. Specificity (selectivity) means the sensor responds only to the intended "
        "quantity and not to others, such as a gas sensor that also reacts to humidity. Resolution is the smallest "
        "change in input that produces a detectable change in output. Accuracy is how close a reading is to the true "
        "value, while precision is how close repeated readings of the same input are to each other; a sensor can be "
        "precise but not accurate. Threshold is the smallest input, starting from zero, that produces a detectable "
        "output. Linearity describes how closely the output follows a straight line against the input; the largest "
        "deviation from that line is the non-linearity error. Stability is the ability to give the same output for the "
        "same input over time; slow change is called drift. Hysteresis means the output for the same input depends on "
        "whether the input was increasing or decreasing. Response time is how long the sensor takes to reach its final "
        "output, often to 63% or 90% of it, after a sudden change in input.",
    ),
    (
        "RO",
        "The sensor readout chain",
        "Sensor readout is the electronics that turns a sensor's output into numbers a microcontroller can use. Many "
        "sensor signals are small analog signals, millivolts or even microvolts as from a thermocouple, or a change in "
        "resistance or capacitance. A typical readout chain has a front end that turns the sensor change into a voltage "
        "(for example by passing an excitation current through a resistive sensor), an amplifier, usually built with an "
        "operational amplifier (opamp), that scales the voltage to the input range of the analog-to-digital converter "
        "(ADC), the ADC itself, which samples and quantizes the voltage into a digital code, and finally the "
        "microcontroller that processes the codes. Amplification before the ADC matters: if a 50 mV signal is fed to an "
        "ADC with a 5 V range, it uses only about 1% of the range, so only a few output codes change and the effective "
        "resolution is poor.",
    ),
    (
        "RO",
        "Analog-to-digital conversion",
        "An ADC converts an analog voltage into a digital code in two steps: sampling and quantization. Sampling takes "
        "the value of the signal at regular instants; the sampling rate is the number of samples per second. To capture "
        "a signal correctly, the sampling rate must be more than twice the highest frequency in the signal (the Nyquist "
        "criterion); if it is lower, fast changes are missed and the signal appears at a wrong, lower frequency, which "
        "is called aliasing. An N-bit ADC has 2^N possible output codes spread over its full-scale input range, set by "
        "the reference voltage Vref. The size of one step, the least significant bit (LSB), is Vref / 2^N. For example, "
        "an 8-bit ADC with Vref = 2.048 V has 256 codes and an LSB of 8 mV. The ADC's resolution in the measured "
        "quantity is the LSB divided by the sensor's sensitivity.",
    ),
    (
        "RO",
        "Quantization and readout design choices",
        "Quantization maps each sampled value to the nearest of the ADC's discrete levels, so a continuous input becomes "
        "a staircase. The difference between the true value and the quantized value is the quantization error; with "
        "rounding to the nearest level it is at most half an LSB, and it behaves like a small added noise. Using more "
        "bits makes the LSB smaller and the resolution finer, but the ADC usually costs more, uses more power, converts "
        "more slowly and produces more data. Readout design involves a few choices: choose the amplifier gain so that "
        "the largest sensor signal comes close to, but does not exceed, the ADC full-scale range, because a signal above "
        "full scale saturates (clips) at the maximum code; choose the number of bits so that the LSB, expressed in the "
        "measured quantity, is smaller than the resolution the application needs; and choose a sampling rate comfortably "
        "above twice the signal's highest frequency, but not much higher than needed, to save power and data.",
    ),
    (
        "NI",
        "Readout non-idealities: ideal and real opamps",
        "Readout circuits are designed as if the opamp were ideal: infinite input resistance, so it draws no current "
        "from the sensor; zero output resistance; infinite open-loop gain; infinite bandwidth; and zero offset, so a "
        "zero input gives a zero output. Real opamps only approximate these properties. Each difference, called a "
        "non-ideality, adds an error to the reading. The error is usually small, but it becomes important when the "
        "sensor signal is tiny, when the gain is large, when the sensor has a high output resistance or when the signal "
        "changes quickly. Designers therefore check the opamp's datasheet limits against the needs of the sensor and the "
        "application.",
    ),
    (
        "NI",
        "Opamp input resistance and loading",
        "A sensor can be modelled as a voltage source Vs with an output (source) resistance Rs. When it is connected to "
        "an amplifier with input resistance Rin, current flows through Rs and part of the voltage is lost across it: Rs "
        "and Rin form a voltage divider, so the amplifier sees only Vs x Rin / (Rs + Rin). This is the loading effect. "
        "If Rin is much larger than Rs, the loss is negligible; for example Rs = 1 kOhm and Rin = 1 MOhm keep 99.9% of "
        "the voltage. If Rin is comparable to Rs, the reading is noticeably too low. The fix is to make the input "
        "resistance much larger than the source resistance, typically by placing a buffer (a voltage follower, an opamp "
        "with gain 1 and very high input resistance) between the sensor and the rest of the circuit, or by choosing an "
        "opamp with a very high input resistance, such as one with CMOS or FET inputs.",
    ),
    (
        "NI",
        "Other opamp non-idealities",
        "Input offset voltage is a small DC voltage, typically microvolts to a few millivolts, that acts as if it were "
        "added to the input: the output is not exactly zero when the input is zero. The amplifier multiplies the offset "
        "by its gain, so a 1 mV offset with a gain of 100 gives a 0.1 V error at the output. Input bias current is the "
        "small current that flows into the opamp's input pins; flowing through the sensor's source resistance, it "
        "creates an extra error voltage, which is significant for high-resistance sensors. Because the open-loop gain is "
        "finite, the closed-loop gain of an amplifier is slightly lower than the value set by its resistors. The "
        "bandwidth is limited: the gain-bandwidth product is roughly constant, so the higher the gain, the lower the "
        "frequency at which the gain starts to fall. The slew rate is the maximum rate at which the output voltage can "
        "change; faster, large signals are distorted. Finally, the output cannot swing beyond the supply voltages, so a "
        "too-large signal saturates.",
    ),
    (
        "DA",
        "Why data analysis for IoT",
        "IoT systems produce very large amounts of data: many sensors report readings continuously, often every few "
        "seconds, and the data comes in many forms, such as temperatures, vibrations, images and logs. Raw readings are "
        "of little use until they are analysed. Data analysis turns them into information and decisions. Typical goals "
        "are monitoring (showing the current state of a system on a dashboard), prediction (for example predicting a "
        "machine failure before it happens, called predictive maintenance, or forecasting energy demand), anomaly "
        "detection (finding readings that do not fit the normal pattern, such as a sudden temperature spike that may "
        "mean a fault or an attack) and automation (letting the system act by itself, such as switching irrigation on "
        "when the soil is predicted to be dry). Because the rules behind the data are often unknown or too complex to "
        "write by hand, IoT data analysis often uses machine learning, which learns a model from the data itself.",
    ),
    (
        "DA",
        "Components and feasibility of learning",
        "Learning from data can be described with a few components. There is an unknown target function f that maps an "
        "input x (for example the vibration readings of a motor) to an output y (for example whether the motor will fail "
        "soon). We do not know f, but we have a data set of examples (x, y) collected in the past. A learning algorithm "
        "searches a hypothesis set, the family of candidate models it is allowed to choose from (for example all "
        "straight lines), and picks the final hypothesis g that fits the data best, hoping that g is close to f. "
        "Learning is feasible, in a probabilistic sense, when the data are representative of the situations where the "
        "model will be used and there are enough examples: then a model that does well on the training data is likely to "
        "do well on new data too. The error on the training data is the in-sample error; the error on new, unseen data "
        "is the out-of-sample error. These terms (target function, hypothesis set, final hypothesis, in-sample and "
        "out-of-sample error) come from the widely used Learning From Data framework; other courses may simply call the "
        "final hypothesis the trained model. A model that is too complex can fit the training data almost perfectly, "
        "including its noise, yet perform badly on new data; this is called overfitting.",
    ),
    (
        "DA",
        "Types of learning and data-driven techniques",
        "There are three main types of learning. In supervised learning, every training example has the correct answer "
        "(a label): if the output is a number it is regression, for example predicting tomorrow's energy use, and if it "
        "is a category it is classification, for example faulty or normal. In unsupervised learning, the data has no "
        "labels and the algorithm looks for structure by itself, for example clustering similar devices. In "
        "reinforcement learning, an agent learns by trial and error from rewards, for example a thermostat that learns a "
        "schedule from comfort feedback. A data-driven project follows a pipeline: collect the data; clean it by "
        "handling missing values and removing or correcting outliers caused by faulty sensors; choose or compute "
        "features, such as the average vibration over a minute; split the data into a training set to fit the model and "
        "a test set, kept aside, to check how well it works on unseen data; train the model; and evaluate it. In Python, "
        "NumPy handles arrays of numbers, pandas handles tables of data such as sensor logs, scikit-learn provides "
        "models such as linear regression and k-means, and matplotlib draws plots.",
    ),
    (
        "DAT",
        "Linear regression",
        "Linear regression models the relationship between an input x and a numeric output y with a straight line, y = "
        "w0 + w1 x, where w0 is the intercept (the value of y when x is 0) and w1 is the slope (how much y changes when "
        "x increases by 1). The line is fitted by least squares: the weights are chosen to minimise the mean squared "
        "error (MSE), the average of the squared differences between the predicted and the actual values. For example, "
        "if the fitted line is y = 1.5 + 0.2 x, an input of x = 10 gives a prediction of 1.5 + 0.2 x 10 = 3.5. The model "
        "is evaluated on test data, for example with the MSE: a smaller MSE means better predictions. A fitted line "
        "should only be trusted within the range of inputs it was trained on; predicting far outside that range is "
        "extrapolation and can be badly wrong, because the relationship may not stay linear.",
    ),
    (
        "DAT",
        "Time-series data and models",
        "A time series is a sequence of measurements taken in time order, usually at regular intervals, such as a "
        "temperature reading every hour. A time series is often described by three components: the trend, a long-term "
        "increase or decrease; seasonality, a pattern that repeats with a fixed period, such as a daily or weekly cycle; "
        "and noise, the random variation that is left. A moving average, the mean of the last few values, smooths out "
        "noise so the trend is easier to see. An autoregressive (AR) model predicts the next value as a weighted sum of "
        "previous values; to capture a daily cycle in hourly data, it can also use the value from 24 hours earlier. "
        "Because the order of the data matters, a time series must not be shuffled before splitting: the model is "
        "trained on the earlier part and tested on the later part, so that it is never tested on the past using "
        "knowledge of the future.",
    ),
    (
        "DAT",
        "Clustering",
        "Clustering is an unsupervised technique that groups data points so that points in the same group (cluster) are "
        "similar and points in different groups are different. The most common algorithm is k-means. First choose the "
        "number of clusters k and pick k starting centres (centroids). Then repeat two steps: assign every point to its "
        "nearest centroid, and move each centroid to the mean of the points assigned to it. Stop when the assignments no "
        "longer change. The value of k is often chosen with the elbow method: plot the total distance of points to their "
        "centroids for several values of k and pick the k where adding more clusters stops giving a large improvement. "
        "Because k-means uses distances, features with large numeric ranges would dominate, so the features are usually "
        "scaled (standardised) first. In IoT, clustering can group households by their energy-use profiles or sensors by "
        "their behaviour, and a reading that is far from every centroid can be flagged as an anomaly.",
    ),
]
