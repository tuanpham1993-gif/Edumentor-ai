# ruff: noqa: ISC004 — dữ liệu đề: chuỗi dài ngắt dòng trong danh sách là cố ý
"""Đoạn tri thức khóa 494 — ĐỢT 2 (27/11/2026): Module 2 "Sensors & Interfaces" của khóa (IIT Bombay).
Bám đề cương công khai của module (tên video): Classification of Sensors · Case Study: Accelerometer / Capacitive
Accelerometer · Case Study: Displacement/Proximity · Case Study: Temperature Sensors · Sensitivity, Specificity, and
Range · Precision, Accuracy and Resolution · Threshold and Linearity/non-Linearity · Stability, Hysteresis and Response
time · Sensor Readout · ADC · Quantization · Design Choices · Readout Non-Idealities · Opamp Input Resistance · Other Opamp
Non-Idealities. Nội dung từng đoạn là kiến thức chuẩn của chủ đề đó, mức nhập môn (không công thức nhiễu nâng cao)."""

CHUNKS_B2 = [
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
        "other books use the reverse, so it is clearer to describe the group than to rely on the label. By output: an analog sensor gives a "
        "continuous signal, while a digital sensor already gives a digital value, for example over a serial bus. "
        "Sensors can also be contact (touching the object) or non-contact (for example infrared or ultrasonic).",
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
        "non-linear response over a limited range; the RTD, usually platinum, whose resistance rises almost linearly "
        "and which is accurate and stable; the thermocouple, two different metals joined at a junction that produce a "
        "small voltage of tens of microvolts per degree, which works over a very wide range up to more than 1000 degC "
        "and, with a small junction, responds quickly; and IC temperature sensors that give a linear output such as "
        "10 mV per degC.",
    ),
    (
        "SENS",
        "Sensor characteristics",
        "Sensor characteristics describe and compare sensors. Range is the span between the smallest and largest value "
        "the sensor can measure. Sensitivity is the change in output per unit change in input, the slope of the "
        "response, for example 10 mV per degC. Specificity (selectivity) means the sensor responds only to the "
        "intended quantity and not to others, such as a gas sensor that also reacts to humidity. Resolution is the "
        "smallest change in input that produces a detectable change in output. Accuracy is how close a reading is to "
        "the true value, while precision is how close repeated readings of the same input are to each other; a sensor "
        "can be precise but not accurate. Threshold is the smallest input, starting from zero, that produces a "
        "detectable output. Linearity describes how closely the output follows a straight line against the input; the "
        "largest deviation from that line is the non-linearity error. Stability is the ability to give the same output "
        "for the same input over time; slow change is called drift. Hysteresis means the output for the same input "
        "depends on whether the input was increasing or decreasing. Response time is how long the sensor takes to "
        "reach its final output, often to 63% or 90% of it, after a sudden change in input.",
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
        "the largest sensor signal comes close to, but does not exceed, the ADC full-scale range, because a signal "
        "above full scale saturates (clips) at the maximum code; choose the number of bits so that the LSB, expressed in "
        "the measured quantity, is smaller than the resolution the application needs; and choose a sampling rate "
        "comfortably above twice the signal's highest frequency, but not much higher than needed, to save power and "
        "data.",
    ),
    (
        "NI",
        "Readout non-idealities: ideal and real opamps",
        "Readout circuits are designed as if the opamp were ideal: infinite input resistance, so it draws no current "
        "from the sensor; zero output resistance; infinite open-loop gain; infinite bandwidth; and zero offset, so a "
        "zero input gives a zero output. Real opamps only approximate these properties. Each difference, called a "
        "non-ideality, adds an error to the reading. The error is usually small, but it becomes important when the "
        "sensor signal is tiny, when the gain is large, when the sensor has a high output resistance or when the signal "
        "changes quickly. Designers therefore check the opamp's datasheet limits against the needs of the sensor and "
        "the application.",
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
        "creates an extra error voltage, which is significant for high-resistance sensors. Because the open-loop gain "
        "is finite, the closed-loop gain of an amplifier is slightly lower than the value set by its resistors. The "
        "bandwidth is limited: the gain-bandwidth product is roughly constant, so the higher the gain, the lower the "
        "frequency at which the gain starts to fall. The slew rate is the maximum rate at which the output voltage can "
        "change; faster, large signals are distorted. Finally, the output cannot swing beyond the supply voltages, so a "
        "too-large signal saturates.",
    ),
]
