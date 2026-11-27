"""Khóa 494 — Introduction to Internet of Things. Đợt 1 (26/11/2026): IoT, Model and Components, Messaging Protocols.
Đợt 2 (27/11/2026): Sensors, Sensor Readout, Readout Non-Idealities (module 2 "Sensors & Interfaces" của khóa).
Đợt 3 (27/11/2026): Data analysis for IoT, Data Analysis Techniques (module 4 "Data Analysis for IoT").
Soạn: Claude · duyệt: Tuấn. Dựng: python -m scripts.bank.build 494"""

from scripts.bank.courses.course_494.chunks import CHUNKS
from scripts.bank.courses.course_494.essays import ESSAY, GEMINI_PROBES, PROBES
from scripts.bank.courses.course_494.mcq import MCQ, MCQ_EXTRA
from scripts.bank.courses.course_494.vn_notes import VN_CHUNK, VN_ESSAY, VN_MCQ

COURSE_ID = 494
COURSE_TITLE = "Introduction to Internet of Things"
SKILLS = {"IOT": 1109, "IOTM": 1112, "MSG": 1108, "SENS": 1106, "RO": 1110, "NI": 1113, "DA": 1111, "DAT": 1107}
SKILL_NAMES = {
    "IOT": "Internet of Things (IoT)",
    "IOTM": "Model and Components of IoT",
    "MSG": "Messaging Protocols",
    "SENS": "Sensors",
    "RO": "Sensor Readout",
    "NI": "Readout Non-Idealities",
    "DA": "Data analysis for IoT",
    "DAT": "Data Analysis Techniques",
}
# 7.5b (27/11): câu cùng nhóm không vào cùng một đề. Trắc nghiệm minh họa cùng cách làm với câu tự luận tính toán.
# Cặp lộ đáp án trắc nghiệm ↔ tự luận đợt 1 (lượt bổ sung 1, 27/11); đợt 2 bổ sung ở lượt 2.
EXCLUSION = {
    # IOT
    "IOT-TN-01": "iot-identity", "IOT-TL-01": "iot-identity",
    "IOT-TN-02": "iot-characteristics", "IOT-TN-09": "iot-characteristics", "IOT-TN-20": "iot-characteristics",
    "IOT-TL-04": "iot-characteristics",
    "IOT-TN-04": "iot-health-industry", "IOT-TN-10": "iot-health-industry", "IOT-TL-02": "iot-health-industry",
    "IOT-TN-03": "iot-irrigation", "IOT-TN-05": "iot-irrigation", "IOT-TL-05": "iot-irrigation",
    "IOT-TN-07": "iot-security", "IOT-TN-13": "iot-security", "IOT-TN-19": "iot-security", "IOT-TL-03": "iot-security",
    "IOT-TN-14": "iot-energy", "IOT-TL-06": "iot-energy",
    # IOTM
    "IOTM-TN-01": "iotm-roles", "IOTM-TN-09": "iotm-roles", "IOTM-TN-23": "iotm-roles", "IOTM-TL-01": "iotm-roles",
    "IOTM-TN-04": "iotm-layers3", "IOTM-TN-05": "iotm-layers3", "IOTM-TN-18": "iotm-layers3",
    "IOTM-TL-02": "iotm-layers3",
    "IOTM-TN-06": "iotm-layers5", "IOTM-TN-11": "iotm-layers5", "IOTM-TN-17": "iotm-layers5",
    "IOTM-TL-06": "iotm-layers5",
    "IOTM-TN-13": "iotm-models", "IOTM-TN-24": "iotm-models", "IOTM-TL-03": "iotm-models",
    "IOTM-TN-08": "iotm-home", "IOTM-TN-22": "iotm-home", "IOTM-TL-05": "iotm-home",
    # MSG — MSG-TL-02 và MSG-TL-05 chung nhóm (cùng ý QoS) → không cùng đề
    "MSG-TN-01": "msg-broker", "MSG-TN-02": "msg-broker", "MSG-TL-01": "msg-broker",
    "MSG-TN-08": "msg-qos-topics", "MSG-TN-10": "msg-qos-topics", "MSG-TN-11": "msg-qos-topics",
    "MSG-TL-02": "msg-qos-topics", "MSG-TL-05": "msg-qos-topics",
    "MSG-TN-06": "msg-coap-con", "MSG-TN-07": "msg-coap-con", "MSG-TL-03": "msg-coap-con",
    # DAT
    "DAT-TN-08": "dat-linreg-substitute", "DAT-TL-05": "dat-linreg-substitute",
}  # fmt: skip
NOTE = (
    "English bank (drafted by Claude, reviewed by Tuấn). Batch 1 (26/11/2026): IoT, Model and Components of IoT, "
    "Messaging Protocols. Batch 2 (27/11/2026): Sensors, Sensor Readout, Readout Non-Idealities (course module 2 "
    "'Sensors & Interfaces'). Each skill: 20 questions (14 MCQ = 7 recognize + 7 understand, 6 essays = 4 easy + 2 "
    "advanced) + 3 knowledge chunks. Batch 3 (27/11/2026): Data analysis for IoT, Data Analysis Techniques (course module "
    "4). Content: well-established "
    "IoT basics, MQTT (OASIS standard), CoAP (RFC 7252), introductory sensors and readout electronics. Load "
    "with: python -m app.core.seed_data.seed_review --file data/review/course_494_en.json"
)

__all__ = [
    "CHUNKS",
    "COURSE_ID",
    "COURSE_TITLE",
    "ESSAY",
    "EXCLUSION",
    "GEMINI_PROBES",
    "MCQ",
    "MCQ_EXTRA",
    "NOTE",
    "PROBES",
    "SKILLS",
    "SKILL_NAMES",
    "VN_CHUNK",
    "VN_ESSAY",
    "VN_MCQ",
]
