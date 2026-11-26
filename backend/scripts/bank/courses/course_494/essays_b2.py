# ruff: noqa: ISC004 — dữ liệu đề: chuỗi dài ngắt dòng trong danh sách là cố ý
"""Tự luận khóa 494 — ĐỢT 2 (27/11/2026). Cùng quy ước với essays.py (đợt 1): mỗi ý (câu mô tả, điểm, main, sub);
câu mô tả theo hai mẫu "(any one of: …)" / "(both needed: …)"; câu tính toán tách ý CÁCH LÀM và ý KẾT QUẢ."""

ESSAY_B2 = {
    "SENS": [
        (
            1,
            "easy",
            "Sensors can be grouped by whether they need an external power source. Explain the difference between "
            "the two groups and give one example of each.",
            [
                (
                    "One group needs an excitation to give an output (any one of: external excitation, a power "
                    "supply, a current must be passed through it). The label active or passive is not required.",
                    4,
                    ["excitation", "excite", "current", "power supply", "powered", "battery"],
                    [],
                ),
                (
                    "The other group generates its own signal (any one of: self-generating, produces its own voltage, "
                    "no external power needed). The label active or passive is not required.",
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
            "One group needs an external excitation to give an output; for example, a thermistor can only be read by "
            "passing a current through it. The other group is self-generating: it generates its own signal from the "
            "energy it measures; for example, a thermocouple produces its own small voltage from heat.",
        ),
        (
            3,
            "easy",
            "Explain the difference between the accuracy and the precision of a sensor.",
            [
                (
                    "Accuracy is closeness to the true value (any one of: close to the true value, close to the actual value, "
                    "small error from the real value).",
                    5,
                    ["true value", "actual value", "real value", "correct value", "reference value"],
                    ["accuracy", "accurate"],
                ),
                (
                    "Precision is closeness of repeated readings to each other (any one of: repeatability, consistent readings, "
                    "small spread).",
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
            "Accuracy is how close a reading is to the true value of the quantity. Precision is how close repeated readings "
            "of the same input are to each other, so a sensor can be precise but not accurate.",
        ),
        (
            3,
            "easy",
            "What is hysteresis in a sensor, and why can it be a problem for the readings?",
            [
                (
                    "The output for the same input depends on the direction of change (any one of: increasing versus decreasing "
                    "input, rising versus falling, depends on the previous value).",
                    5,
                    ["direction", "increasing", "decreasing", "rising", "falling", "previous"],
                    [],
                ),
                (
                    "Problem: the same input can give different readings (any one of: two possible readings, an error of up to "
                    "the hysteresis width, the reading is not unique).",
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
            "decreasing. It is a problem because the same true value can give different readings, which adds an error.",
        ),
        (
            2,
            "easy",
            "Explain how a capacitive MEMS accelerometer turns acceleration into an electrical signal.",
            [
                (
                    "A proof mass on springs moves when the device accelerates (any one of: the mass moves, the mass shifts, the "
                    "springs bend).",
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
                    "The readout measures this change to obtain the acceleration (any one of: the change is proportional to "
                    "the acceleration, the circuit converts it to a voltage).",
                    3,
                    ["proportional", "convert", "measure", "calculate", "indicate"],
                    ["acceleration", "readout", "circuit"],
                ),
            ],
            "A capacitive MEMS accelerometer has a tiny proof mass held by springs. When the device accelerates, the mass "
            "moves relative to the frame, and this changes the capacitance between the mass and the fixed plates. The "
            "readout circuit measures the change, which is proportional to the acceleration.",
        ),
        (
            2,
            "advanced",
            "A cold-storage room must be kept between -30 degC and +10 degC with small temperature "
            "changes detected, and a furnace must be monitored up to 1000 degC where temperature can jump quickly. Which "
            "type of temperature sensor would you choose for each place? Justify each choice by range or response time.",
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
                    "Reason by response time (any one of: a small junction responds quickly, fast response, follows sudden "
                    "jumps).",
                    2,
                    ["quickly", "fast", "small junction", "respond", "response time"],
                    [],
                ),
            ],
            "For the cold room I would choose a thermistor, because the range is narrow and a thermistor is very "
            "sensitive, so small changes are detected. For the furnace I would choose a thermocouple, because it works "
            "over a very wide range up to more than 1000 degC, and a thermocouple with a small junction responds quickly "
            "to sudden jumps.",
        ),
        (
            3,
            "advanced",
            "A greenhouse controller switches a fan on at 70 %RH. Two humidity sensors are offered. Sensor "
            "Alpha: accuracy +/-2 %RH, hysteresis 1 %RH, non-linearity 0.5 %RH. Sensor Beta: accuracy +/-5 %RH, "
            "hysteresis 4 %RH, non-linearity 3 %RH. Which sensor would you choose, and what would each of Beta's three "
            "figures mean for when the fan switches?",
            [
                (
                    "Chooses Alpha.",
                    2,
                    ["alpha", "choose alpha", "pick alpha"],
                    ["choose", "pick", "prefer", "select", "recommend", "better", "best"],
                ),
                (
                    "Beta's accuracy: the fan may switch anywhere from about 65 to 75 %RH (any one of: up to 5 %RH from the "
                    "true humidity, switches too early or too late).",
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
            "I would choose Alpha. With Beta, the accuracy of +/-5 %RH means the fan could switch anywhere from about 65 "
            "to 75 %RH. Its hysteresis of 4 %RH means the switching point is different when humidity is rising than when "
            "it is falling. Its non-linearity means the error changes across the range, so the readings do not follow a "
            "straight line.",
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
                    "Amplifying scales the signal to the ADC's full range (any one of: use the full scale, match the ADC input "
                    "range).",
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
            "Sensor signals are often small, only millivolts or microvolts. Fed directly into an ADC, such a signal uses "
            "only a small part of the range, so few codes change and the resolution is poor. Amplifying first scales the "
            "signal to the ADC's full range.",
        ),
        (
            3,
            "easy",
            "What is quantization in an ADC, and how large can the quantization error be?",
            [
                (
                    "Quantization maps each sample to one of a limited number of levels (any one of: nearest level, rounding, "
                    "discrete steps).",
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
                    "Sample faster than twice the highest signal frequency (any one of: more than twice, more than 2f, double "
                    "the highest frequency).",
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
            "The ADC must sample at more than twice the highest frequency in the signal. If it samples too slowly, fast "
            "changes are missed and the signal appears at a wrong, lower frequency, which is called aliasing.",
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
            "More bits give a smaller LSB, so the resolution is finer. The cost is that the ADC usually uses more power, "
            "converts more slowly, is more expensive and produces more data.",
        ),
        (
            2,
            "advanced",
            "A temperature sensor outputs 10 mV per degC. It is read by a 12-bit ADC with a full-scale "
            "reference of 4.096 V. Calculate the LSB size and the smallest temperature change the system can resolve, "
            "showing your method.",
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
            "A pressure sensor gives 0 to 100 mV. The ADC input range is 0 to 4.096 V. Choose an amplifier "
            "gain that uses the ADC range well without saturating it, and explain your choice.",
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
                    "A higher gain would saturate the ADC (any one of: clipping, exceeds 4.096 V, output stuck at the maximum "
                    "code).",
                    3,
                    ["saturate", "saturation", "clip", "exceed", "maximum code"],
                    [],
                ),
            ],
            "The gain is the ADC range divided by the largest sensor signal: 4.096 V / 0.1 V = 40.96, so I choose a gain "
            "of 40. This uses most of the ADC range, which gives the best resolution. A higher gain such as 41 would give "
            "4.1 V, which exceeds 4.096 V and would saturate the ADC.",
        ),
    ],
    "NI": [
        (
            3,
            "easy",
            "What is the input offset voltage of an opamp, and why does it matter more when the amplifier gain "
            "is large?",
            [
                (
                    "Offset is a small DC voltage that acts as if added to the input (any one of: output not zero for a zero "
                    "input, a small error voltage at the input).",
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
            "The input offset voltage is a small DC voltage that acts as if it were added to the input, so the output is "
            "not zero when the input is zero. The amplifier multiplies the offset by its gain, so with a large gain it "
            "becomes a large output error.",
        ),
        (
            3,
            "easy",
            "What is the input bias current of an opamp, and why is it a problem for sensors with a high output "
            "resistance?",
            [
                (
                    "A small current flows into the opamp's input pins (any one of: current into the inputs, the opamp draws a "
                    "small current).",
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
                    "The open-loop gain of a real opamp is not infinite (any one of: finite open-loop gain, limited open-loop "
                    "gain).",
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
            "Why can an opamp fail to amplify a fast-changing sensor signal correctly? Name the two limits "
            "involved and what each does.",
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
            "A sensor behaves like a voltage source with an output resistance of 10 kOhm. It is connected "
            "to an amplifier with an input resistance of 90 kOhm. What fraction of the sensor voltage does the amplifier "
            "see? Explain why, and suggest how to fix the problem.",
            [
                (
                    "Method: the two resistances form a voltage divider (any one of: Rin / (Rs + Rin), 90 / (10 + 90), "
                    "90 kOhm / 100 kOhm).",
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
                    "Fix (any one of: a buffer or voltage follower, a much higher input resistance, an opamp with CMOS or FET "
                    "inputs).",
                    3,
                    ["buffer", "voltage follower", "higher input resistance", "much larger input", "cmos", "fet"],
                    [],
                ),
            ],
            "The output resistance and the input resistance form a voltage divider, so the amplifier sees Rin / (Rs + "
            "Rin) = 90 / (10 + 90) = 90% of the sensor voltage. Current flows through the sensor's output resistance and "
            "10% of the voltage is lost across it, because Rin is not much larger than Rs. To fix it, put a buffer "
            "(voltage follower) with a very high input resistance between the sensor and the amplifier.",
        ),
        (
            3,
            "advanced",
            "A gas sensor has a very high output resistance of about 10 MOhm, its signal changes slowly over "
            "minutes, and it is read by an opamp amplifier. Which opamp property matters MOST here, and which "
            "matters LEAST? Explain both.",
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
            "The input resistance, or equivalently a very low input bias current, matters most. With a 10 MOhm source, "
            "any current the opamp draws makes a large voltage drop across the sensor resistance and a large error. The "
            "bandwidth and slew rate matter least, because the signal changes slowly over minutes, so it is a very low "
            "frequency signal.",
        ),
    ],
}

PROBES_B2 = {
    "SENS-TL-01": [
        (
            "đúng, chữ khác",
            "Some sensors must be powered by an external source, like an RTD that needs a current. Others make their "
            "own voltage, like a thermocouple.",
            ">=7",
        ),
        (
            "quy ước IIT/NPTEL (active = tự sinh)",
            "An active sensor generates its own voltage, like a thermocouple. A passive sensor needs an excitation "
            "current, like an RTD.",
            ">=7",
        ),
        (
            "quy ước Fraden (active = cần kích thích)",
            "An active sensor needs an excitation current, like an RTD. A passive sensor generates its own voltage, "
            "like a thermocouple.",
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
            "Accuracy means the reading is near the actual value. Precision means repeated readings "
            "are consistent with each other.",
            ">=7",
        ),
        (
            "đảo",
            "Accuracy means repeated readings are consistent with each other. Precision means the reading is near "
            "the actual value.",
            "<=2",
        ),
        ("chỉ tên", "Accuracy and precision are two important sensor characteristics.", "<=2"),
    ],
    "SENS-TL-03": [
        (
            "đúng, chữ khác",
            "With hysteresis the reading depends on whether the input is rising or falling, so one "
            "value can produce two readings.",
            ">=7",
        ),
        ("chỉ tên", "Hysteresis is a sensor characteristic listed in datasheets.", "<=2"),
    ],
    "SENS-TL-04": [
        (
            "đúng, chữ khác",
            "Inside, a small mass on springs shifts when the phone accelerates. This changes the "
            "capacitance between the plates, and the circuit converts that change into an acceleration value.",
            ">=7",
        ),
        ("chỉ tên", "A MEMS accelerometer uses a proof mass, springs and capacitance.", "<=3"),
    ],
    "SENS-TL-05": [
        (
            "đúng, chữ khác",
            "In the cold room an RTD is best because it is accurate over this small range. The furnace "
            "needs a thermocouple since it handles a very wide range up to 1000 degC and responds fast.",
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
            "Pick Alpha. Beta could turn the fan on too early or too late because of its 5 % accuracy. "
            "Its hysteresis makes the point differ when humidity is rising or falling. Its non-linearity means the error "
            "is different at different humidity levels.",
            ">=7",
        ),
        ("chọn Beta, chỉ nhắc số", "Beta is better. Its figures are 5, 4 and 3.", "<=2"),
        (
            "câu chọn ngắn toàn từ của đề — luật chép đề (L7) bỏ câu, ý 1 mất điểm",
            "I choose Alpha. Beta could turn "
            "the fan on too early or too late. Its point differs when humidity is rising or falling. Its error is "
            "different at different humidity levels.",
            "c",
        ),
    ],
    "RO-TL-01": [
        (
            "đúng, chữ khác",
            "Sensors give tiny millivolt signals. Without gain they use a small part of the ADC, so "
            "resolution is poor. The amplifier stretches the signal to the full scale of the ADC.",
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
        ("viết dấu phẩy thập phân", "LSB = 4.096 / 4096 = 1 mV. Then 1 mV / 10 mV per degC = 0,1 degC.", "c"),
    ],
    "RO-TL-06": [
        (
            "đúng, chữ khác",
            "Divide 4.096 V by 0.1 V to get 40.96, so a gain of 40 uses most of the range. A bigger "
            "gain would clip at the maximum code.",
            ">=7",
        ),
        (
            "gain 41 (vượt 4,096 V)",
            "Divide 4096 mV by 100 mV and round up: a gain of 41 uses the full scale and gives "
            "the best resolution. Too much gain would saturate the ADC.",
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
            "Offset is a small DC voltage, so the output is non-zero with a zero input. A big gain "
            "multiplies it into a big error.",
            ">=7",
        ),
        ("chỉ tên", "Input offset voltage is an opamp non-ideality.", "<=2"),
    ],
    "NI-TL-02": [
        (
            "đúng, chữ khác",
            "A small current flows into the opamp's inputs. Through a large sensor resistance it makes "
            "a voltage drop that adds an error.",
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
            "Bandwidth: the gain drops at high frequencies. Slew rate: the output cannot change fast "
            "enough, so big fast signals distort.",
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
            "It is a voltage divider: 90 / (10 + 90) = 0.9 of the voltage. Current flowing through the "
            "10 kOhm causes a voltage drop. Fix it with a voltage follower.",
            ">=7",
        ),
        ("sai kết quả", "It is a voltage divider: 10 / 90 = 11 percent. Fix it with a buffer.", "<=6"),
    ],
    "NI-TL-06": [
        (
            "đúng, chữ khác",
            "A very low bias current matters most, because current through the 10 MOhm sensor gives a "
            "large error voltage. Bandwidth is least important because the gas signal is slow.",
            ">=7",
        ),
        ("đảo nhiều/ít", "Bandwidth matters most. The input resistance does not matter.", "<=3"),
    ],
}

GEMINI_PROBES_B2 = {
    "SENS-TL-01": (
        "One group needs an external excitation. The other group generates its own signal. A thermistor needs "
        "excitation.",
        "In IIT terms, an active sensor makes its own voltage, like a thermocouple, while a passive sensor needs a "
        "current through it, like an RTD.",
    ),
    "SENS-TL-02": (
        "Accuracy is closeness to the true value. Precision is repeatability.",
        "An accurate sensor has a small error from the real value. A precise sensor gives consistent readings with a "
        "small spread.",
    ),
    "SENS-TL-03": (
        "The reading depends on whether the input is increasing or decreasing. So the same input can give different "
        "readings.",
        "The output depends on the previous value. This makes the reading uncertain by up to the hysteresis width.",
    ),
    "SENS-TL-04": (
        "The proof mass moves when the device accelerates. The capacitance changes. The readout measures this to get "
        "the acceleration.",
        "Springs holding the mass bend under acceleration. One capacitance rises while the other falls. The circuit "
        "converts the change to a voltage.",
    ),
    "SENS-TL-05": (
        "Cold room: thermistor, because it is very sensitive. Furnace: thermocouple, because it has a very wide "
        "range. It also responds quickly.",
        "Cold room: RTD, because the narrow range is enough and it is accurate. Furnace: thermocouple, which works "
        "above 1000 degC. A small junction gives a fast response.",
    ),
    "SENS-TL-06": (
        "I choose Alpha because it is more accurate. Beta's accuracy means the fan could switch up to 5 %RH from the true humidity. Its hysteresis "
        "means a different switching point when rising than when falling. Its non-linearity means the error changes "
        "across the range.",
        "Alpha is better. With Beta the fan may switch too early or too late. The point depends on whether humidity "
        "is rising or falling. The readings do not follow a straight line.",
    ),
    "RO-TL-01": (
        "Sensor signals are only millivolts. So only a few ADC codes change. The amplifier scales it to the full "
        "scale.",
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
        "4096 mV / 100 mV is about 41, so I would use 40 to stay below the limit. This gives the best resolution. A "
        "gain of 41 would clip at 4.1 V.",
    ),
    "NI-TL-01": (
        "Offset is a small DC voltage added to the input. The gain multiplies it.",
        "With a zero input the output is not zero. A large gain amplifies this into a large output error.",
    ),
    "NI-TL-02": (
        "A small current flows into the input pins. Through the source resistance it creates an error voltage.",
        "The opamp draws a small current. It makes a voltage drop across the sensor resistance, larger for high "
        "resistance.",
    ),
    "NI-TL-03": (
        "The open-loop gain is finite. So the closed-loop gain is slightly lower.",
        "The opamp's open-loop gain is limited, not infinite. This gives a small gain error: the gain is less than "
        "designed.",
    ),
    "NI-TL-04": (
        "Bandwidth: the gain falls at high frequencies. Slew rate: the output can change only at a maximum rate.",
        "The gain-bandwidth product means a higher gain gives a lower bandwidth. The slew rate means large fast "
        "signals are distorted.",
    ),
    "NI-TL-05": (
        "It is a voltage divider. The amplifier sees 90%. Current flows through the output resistance. Use a buffer.",
        "Rin / (Rs + Rin) = 90 / 100. That is 0.9 of the voltage, lost by loading. Use an opamp with CMOS inputs.",
    ),
    "NI-TL-06": (
        "Most important: very high input resistance. With 10 MOhm, current into the opamp causes a large error. "
        "Least important: bandwidth. The signal is slow.",
        "Most important: very low bias current. It would make a large voltage drop across the sensor. The slew rate "
        "matters least, because it is a low frequency signal.",
    ),
}
