# ruff: noqa: ISC004 — dữ liệu đề: chuỗi dài ngắt dòng trong danh sách là cố ý
"""Trắc nghiệm khóa 494 — ĐỢT 2 (27/11/2026). (đoạn số, mức, đề, [ĐÚNG, sai, sai, sai], giải thích).
Đoạn số tính trong từng kỹ năng: SENS-K01..K03, RO-K01..K03, NI-K01..K03."""

MCQ_B2 = {
    "SENS": [
        (
            1,
            "recognize",
            "Which of these sensors needs an external excitation (power) source to produce its output?",
            ["A platinum RTD", "A thermocouple", "A solar cell", "A piezoelectric crystal"],
            "An RTD's resistance can only be read by passing a current through it; the other three generate their own "
            "signal.",
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
            "An ultrasonic sensor times the echo; the sound travels there and back, so the distance is speed x time / 2.",
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
            "A temperature sensor is read by passing a small current through it and measuring the voltage. "
            "Which group does it belong to?",
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
            "An inductive proximity sensor fails to detect an object on a production line. Which object "
            "is most likely?",
            ["A plastic bottle", "A steel bolt", "An aluminium can", "A copper pipe"],
            "Inductive sensors detect metal objects through a change in inductance; plastic does not affect it.",
        ),
        (
            3,
            "understand",
            "Repeated readings of the same 25.0 degC bath give 26.1, 26.0 and 26.1 degC. How would you "
            "describe this sensor?",
            [
                "Precise but not accurate",
                "Accurate but not precise",
                "Both accurate and precise",
                "Neither accurate nor precise",
            ],
            "The readings agree closely with each other (precise) but are about 1 degC from the true value (not accurate).",
        ),
        (
            3,
            "understand",
            "A humidity sensor reads 62% when humidity rises to 60%, but 58% when humidity falls to 60%. "
            "Which characteristic does this show?",
            ["Hysteresis", "Poor specificity", "A slow response time", "A high threshold"],
            "The reading for the same input depends on the direction of change, which is hysteresis.",
        ),
        (
            3,
            "understand",
            "A gas sensor meant for carbon monoxide also changes its output when the humidity changes. "
            "Which characteristic is poor?",
            ["Specificity", "Linearity", "Resolution", "Range"],
            "Specificity (selectivity) means responding only to the intended quantity.",
        ),
        (
            3,
            "understand",
            "A sensor is placed in hot water and takes 20 s to reach 90% of its final reading. What does "
            "this figure describe?",
            ["Its response time", "Its hysteresis", "Its stability", "Its sensitivity"],
            "Response time is how long the output takes to reach (a set fraction of) its final value after a step change.",
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
            "A small signal uses only a tiny part of the ADC range; amplifying it first improves the effective resolution.",
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
            "A vibration signal contains frequencies up to 500 Hz. Which sampling rate is the lowest that "
            "still avoids aliasing?",
            ["1200 samples per second", "500 samples per second", "800 samples per second", "250 samples per second"],
            "The rate must be more than 2 x 500 Hz = 1000 samples per second; of these choices only 1200 is high enough.",
        ),
        (
            2,
            "understand",
            "A sensor has a sensitivity of 20 mV per degC and the ADC's LSB is 2 mV. What temperature "
            "change does one LSB represent?",
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
            "An ideal opamp has infinite input resistance, infinite open-loop gain, infinite bandwidth and zero offset.",
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
            "Which circuit is commonly placed between a high-resistance sensor and the rest of the readout "
            "to avoid loading?",
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
            "A sensor with Rs = 1 kOhm is connected to an amplifier with Rin = 1 MOhm. About how much of "
            "the sensor voltage does the amplifier see?",
            ["99.9%", "50%", "90%", "0.1%"],
            "Rin / (Rs + Rin) = 1000 / 1001, about 99.9%; Rin is much larger than Rs, so loading is negligible.",
        ),
        (
            2,
            "understand",
            "A sensor reading is clearly too low when the sensor is connected to the amplifier, but "
            "correct when measured with a very high-resistance meter. What is the most likely cause?",
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
            "An amplifier with a gain of 100 uses an opamp with a 1 mV input offset. What error does the "
            "offset cause at the output?",
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
            "An amplifier designed with resistors for a gain of 1000 measures a gain of 990. Which "
            "non-ideality explains this best?",
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
            "A large, fast audio-frequency signal comes out of an amplifier with sloped, triangular edges "
            "instead of its true shape. Which limit is most likely reached?",
            ["The slew rate", "The input offset voltage", "The input bias current", "The input resistance"],
            "When the output cannot change fast enough, large fast signals are distorted by the slew rate.",
        ),
        (
            3,
            "understand",
            "An amplifier's output stays stuck at the supply voltage whenever the sensor signal is "
            "large. What is happening?",
            [
                "The output is saturating because it cannot swing beyond the supply",
                "The input bias current is flowing through the feedback resistors",
                "The open-loop gain has become infinite at large input signals",
                "The input offset voltage cancels out the sensor signal completely",
            ],
            "The output cannot go beyond the supply voltages, so a too-large signal saturates.",
        ),
    ],
}
