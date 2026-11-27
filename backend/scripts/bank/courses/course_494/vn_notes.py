"""Ghi chú tiếng Việt cho file duyệt (render_review.py): tóm tắt đoạn, dịch trắc nghiệm, ghi chú tự luận.
Đợt 1 (26/11/2026): IOT, IOTM, MSG — module 1 + messaging của module 3.
Đợt 2 (27/11): SENS, RO, NI — module 2 "Sensors & Interfaces".
Đợt 3 (27/11): DA, DAT — module 4 "Data Analysis for IoT"."""

VN_CHUNK = {
    "IOT-K01": "IoT là mạng các vật thể có cảm biến, phần mềm, kết nối mạng để thu và trao đổi dữ liệu; mỗi vật cần "
    "định danh riêng (IP, mã thiết bị); vật cảm nhận môi trường, một số tác động qua cơ cấu chấp hành. Đặc "
    "điểm: kết nối, cảm nhận, định danh riêng, không đồng nhất, quy mô rất lớn, thay đổi động. Nhiều thiết "
    "bị bị giới hạn (ít bộ nhớ, xử lý yếu, chạy pin).",
    "IOT-K02": "Ứng dụng: nhà thông minh (đèn, nhiệt kế, khóa, camera điều khiển từ điện thoại), nông nghiệp (cảm "
    "biến độ ẩm đất → tưới, tiết kiệm nước), y tế (thiết bị đeo đo nhịp tim, đường huyết, báo bác sĩ từ "
    "xa), công nghiệp (đo rung, nhiệt độ máy để dự đoán hỏng — bảo trì dự đoán), thành phố (đỗ xe thông "
    "minh, đèn đường tự giảm sáng, đo chất lượng không khí).",
    "IOT-K03": "Thách thức: bảo mật (mật khẩu mặc định, ít cập nhật → bị chiếm làm botnet), riêng tư (dữ liệu cá "
    "nhân), tương thích (khác hãng, khác giao thức; chuẩn và gateway giúp), năng lượng (thiết bị pin phải "
    "tiết kiệm, ngủ phần lớn thời gian), mở rộng quy mô (hàng triệu thiết bị, dữ liệu lớn).",
    "IOTM-K01": "Thành phần: cảm biến đo, cơ cấu chấp hành tác động; node (vi điều khiển + radio); gateway nối thiết "
    "bị cục bộ với internet, chuyển đổi giao thức (Zigbee/Bluetooth → Wi-Fi/Ethernet), lọc / gộp dữ liệu; "
    "mạng; đám mây / máy chủ lưu và phân tích; ứng dụng / giao diện. Ví dụ nhà thông minh: cảm biến "
    "chuyển động → hub → đám mây → luật bật đèn.",
    "IOTM-K02": "Kiến trúc 3 lớp: lớp thu nhận (perception — cảm biến, cơ cấu chấp hành), lớp mạng (Wi-Fi, di động, "
    "Zigbee, LoRa), lớp ứng dụng (dịch vụ cho người dùng). Kiến trúc 5 lớp thêm lớp xử lý (middleware — "
    "lưu, phân tích dữ liệu lớn) giữa lớp mạng và ứng dụng, và lớp nghiệp vụ (business) trên cùng quản lý "
    "toàn hệ thống, mô hình kinh doanh, quyền riêng tư.",
    "IOTM-K03": "4 mô hình giao tiếp: thiết bị–thiết bị (trực tiếp, Bluetooth / Zigbee), thiết bị–đám mây (trực tiếp "
    "qua Wi-Fi), thiết bị–gateway (qua hub / điện thoại chuyển lên đám mây), chia sẻ dữ liệu phía sau "
    "(dịch vụ đám mây chia sẻ cho dịch vụ khác được phép). Mục tiêu thiết kế: tiêu thụ ít năng lượng, giá "
    "thấp, mở rộng, tin cậy, bảo mật và riêng tư từ thiết kế, tương thích.",
    "MSG-K01": "MQTT: giao thức nhắn tin nhẹ cho thiết bị giới hạn, mạng kém. Mô hình publish/subscribe qua broker; "
    "client publish vào topic (vd home/livingroom/temperature), broker chuyển cho client đã subscribe. "
    "Topic phân cấp bằng '/'; ký tự đại diện '+' khớp đúng 1 cấp, '#' khớp mọi cấp còn lại (phải ở cuối). "
    "Chạy trên TCP, cổng 1883, 8883 khi dùng TLS.",
    "MSG-K02": "QoS 0 = tối đa 1 lần (không xác nhận, có thể mất); QoS 1 = ít nhất 1 lần (giữ tới khi nhận PUBACK, có "
    "thể trùng); QoS 2 = đúng 1 lần (bắt tay 4 bước PUBLISH, PUBREC, PUBREL, PUBCOMP, tốn hơn). Retained "
    "message: broker giữ và gửi ngay cho người subscribe mới. Last Will: broker phát khi client rớt bất "
    "thường. Keep-alive: client gửi PINGREQ để báo còn kết nối.",
    "MSG-K03": "CoAP (RFC 7252): giao thức web cho thiết bị giới hạn, kiểu REST — tài nguyên có URI, phương thức GET "
    "/ POST / PUT / DELETE, mã phản hồi giống HTTP (2.05 Content, 4.04 Not Found). Chạy trên UDP cổng "
    "5683, header cố định 4 byte. Loại tin: CON (phải xác nhận ACK, gửi lại nếu thiếu), NON (không xác "
    "nhận), RST (không xử lý được). Observe: client đăng ký, server báo mỗi khi tài nguyên đổi.",
    "SENS-K01": "Phân loại cảm biến: theo đại lượng đo; theo nhu cầu nguồn: TỰ SINH tín hiệu (thermocouple, pin mặt "
    "trời, áp điện) / CẦN KÍCH THÍCH ngoài (thermistor, RTD, strain gauge). Nhãn active/passive dùng "
    "ngược nhau giữa các sách (NPTEL/IIT: tự sinh = active) → đoạn mô tả nhóm, không dựa vào nhãn; analog "
    "/ digital; tiếp xúc / không tiếp xúc.",
    "SENS-K02": "Case study: gia tốc kế MEMS kiểu tụ (khối thử trên lò xo dịch chuyển → điện dung đổi, tỉ lệ gia "
    "tốc); cảm biến dịch chuyển / tiệm cận (điện dung, cảm ứng — chỉ kim loại, siêu âm: khoảng cách = vận "
    "tốc âm x thời gian / 2); cảm biến nhiệt (thermistor nhạy nhưng phi tuyến, dải hẹp; RTD bạch kim gần "
    "tuyến tính, chính xác; thermocouple dải rất rộng > 1000 °C, mối nối nhỏ đáp ứng nhanh; IC 10 mV/°C).",
    "SENS-K03": "Đặc tính: range, sensitivity (độ dốc), specificity (chỉ nhạy với đại lượng cần đo), resolution, "
    "accuracy (gần giá trị thật) / precision (các lần đo lặp gần nhau), threshold, linearity, stability "
    "(drift), hysteresis (phụ thuộc chiều tăng / giảm), response time (63% / 90%).",
    "RO-K01": "Chuỗi đọc tín hiệu: front end đổi thay đổi của cảm biến thành điện áp → khuếch đại (opamp) đưa về dải "
    "ADC → ADC lấy mẫu và lượng tử hóa → vi điều khiển. Phải khuếch đại trước ADC: 50 mV vào ADC 5 V chỉ "
    "dùng ~1% dải, độ phân giải kém.",
    "RO-K02": "ADC: lấy mẫu + lượng tử hóa; tốc độ lấy mẫu > 2 lần tần số cao nhất (Nyquist), thấp hơn → aliasing; N "
    "bit → 2^N mã; LSB = Vref / 2^N (vd 8 bit, 2,048 V → 8 mV); độ phân giải theo đại lượng đo = LSB / độ "
    "nhạy.",
    "RO-K03": "Lượng tử hóa: làm tròn về mức gần nhất, sai số tối đa ½ LSB. Nhiều bit hơn → LSB nhỏ hơn nhưng tốn "
    "điện, chậm, đắt, nhiều dữ liệu. Thiết kế: chọn gain để tín hiệu lớn nhất gần nhưng không vượt full "
    "scale (vượt → bão hòa); chọn số bit theo độ phân giải cần; tốc độ lấy mẫu > 2 lần nhưng không thừa.",
    "NI-K01": "Opamp lý tưởng: điện trở vào vô hạn, điện trở ra 0, open-loop gain vô hạn, băng thông vô hạn, offset "
    "0. Opamp thật lệch khỏi các giá trị này → sai số; quan trọng khi tín hiệu nhỏ, gain lớn, cảm biến điện "
    "trở ra cao hoặc tín hiệu nhanh.",
    "NI-K02": "Điện trở vào hữu hạn → hiệu ứng tải: Rs và Rin thành cầu phân áp, opamp chỉ thấy Vs x Rin / (Rs + "
    "Rin). Rin >> Rs thì không đáng kể (1 kΩ / 1 MΩ → 99,9%). Khắc phục: buffer (voltage follower) hoặc "
    "opamp đầu vào CMOS / FET.",
    "NI-K03": "Sai số khác: input offset voltage (bị nhân với gain: 1 mV x 100 = 0,1 V); input bias current (chảy qua "
    "điện trở nguồn → điện áp sai số, lớn với cảm biến điện trở cao); open-loop gain hữu hạn → gain thực "
    "hơi thấp hơn thiết kế; băng thông (gain x băng thông ≈ hằng số); slew rate (tốc độ thay đổi tối đa của "
    "đầu ra); đầu ra không vượt điện áp nguồn → bão hòa.",
    "DA-K01": "Vì sao phân tích dữ liệu IoT: dữ liệu cảm biến rất nhiều, liên tục, đa dạng; dữ liệu thô ít giá trị "
    "cho tới khi được phân tích. Mục tiêu: giám sát, dự đoán (bảo trì dự đoán, dự báo năng lượng), phát "
    "hiện bất thường, tự động hóa. Quy luật thường chưa biết → dùng học máy.",
    "DA-K02": "Thành phần của việc học: hàm mục tiêu f chưa biết, tập dữ liệu (x, y), tập giả thuyết, thuật toán học "
    "→ giả thuyết cuối g ≈ f. Học được (theo xác suất) khi dữ liệu đại diện và đủ nhiều. Sai số trong mẫu / "
    "ngoài mẫu; overfitting. Ghi rõ đây là thuật ngữ của khung Learning From Data (khóa khác có thể gọi là "
    "'mô hình đã huấn luyện').",
    "DA-K03": "Kiểu học: có giám sát (có nhãn: hồi quy / phân loại), không giám sát (không nhãn: phân cụm), tăng "
    "cường (học từ phần thưởng). Quy trình: thu thập → làm sạch (giá trị thiếu, ngoại lai) → đặc trưng → "
    "chia train/test → huấn luyện → đánh giá. Python: NumPy, pandas, scikit-learn, matplotlib.",
    "DAT-K01": "Hồi quy tuyến tính y = w0 + w1 x (w0 hệ số chặn, w1 độ dốc); khớp bằng bình phương tối thiểu (cực "
    "tiểu MSE); vd y = 1,5 + 0,2x, x = 10 → 3,5; đánh giá bằng MSE trên tập test; ngoại suy ngoài dải dữ "
    "liệu dễ sai.",
    "DAT-K02": "Chuỗi thời gian: trend (xu hướng dài hạn), seasonality (lặp theo chu kỳ cố định), noise (dao động "
    "ngẫu nhiên). Trung bình trượt làm mượt; mô hình AR dự đoán từ các giá trị trước (thêm giá trị 24 giờ "
    "trước cho chu kỳ ngày). Không xáo trộn: train phần đầu, test phần sau.",
    "DAT-K03": "Phân cụm (không giám sát), k-means: chọn k và tâm ban đầu → gán điểm về tâm gần nhất → dời tâm về "
    "trung bình → lặp tới khi ổn định; chọn k bằng elbow; chuẩn hóa đặc trưng vì dùng khoảng cách; ứng "
    "dụng IoT: nhóm hộ theo kiểu dùng điện, điểm xa mọi tâm = bất thường.",
}


VN_MCQ = {
    "IOT-TN-01": "Mỗi thiết bị IoT cần gì để được tìm thấy và gọi tới trên mạng? → Định danh riêng (IP, mã thiết bị)",
    "IOT-TN-02": "Thiết bị IoT ít bộ nhớ, xử lý yếu, chạy pin gọi là gì? → Thiết bị giới hạn (constrained)",
    "IOT-TN-03": "Thành phần nào giúp thiết bị tác động lên thế giới thực, vd mở van? → Cơ cấu chấp hành (actuator)",
    "IOT-TN-04": "Bảo trì dự đoán trong IoT công nghiệp là gì? → Dùng dữ liệu cảm biến của máy để dự đoán hỏng sớm",
    "IOT-TN-05": "Nông nghiệp thông minh: cảm biến nào báo hệ thống tưới khi cây cần nước? → Cảm biến độ ẩm đất",
    "IOT-TN-06": "Tương thích (interoperability) nghĩa là gì? → Thiết bị khác hãng làm việc được với nhau",
    "IOT-TN-07": "Vì sao nhiều thiết bị IoT dễ bị chiếm quyền? → Giữ mật khẩu mặc định và hiếm khi được cập nhật",
    "IOT-TN-08": "Bộ điều nhiệt đo nhiệt độ và bật máy sưởi khi lạnh — dùng 2 khả năng nào? → Cảm nhận và tác động",
    "IOT-TN-09": "Mạng thành phố: nghìn cảm biến nhiều hãng, có cái ngủ, thêm mới hằng tháng — thể hiện 2 đặc điểm "
    "nào? → Không đồng nhất và thay đổi động",
    "IOT-TN-10": "Bệnh viện theo dõi nhịp tim bệnh nhân tại nhà, báo bác sĩ khi nguy hiểm — lĩnh vực nào? → Theo dõi "
    "sức khỏe từ xa",
    "IOT-TN-11": "Thành phố muốn đèn đường tiết kiệm điện lúc đêm vắng — giải pháp nào? → Đèn có cảm biến chuyển "
    "động, tự giảm sáng khi không có người",
    "IOT-TN-12": "Khóa hãng A, hub hãng B không điều khiển được vì khác giao thức — thách thức nào? → Tương thích",
    "IOT-TN-13": "Vòng đeo tay ghi giờ ngủ và vị trí cả ngày, đẩy lên đám mây — vấn đề trực tiếp nhất? → Riêng tư dữ "
    "liệu cá nhân",
    "IOT-TN-14": "Vì sao cảm biến chạy pin ngủ phần lớn thời gian? → Tiết kiệm năng lượng để pin bền hơn",
    "IOTM-TN-01": "Thành phần nào nối thiết bị cục bộ với internet và chuyển đổi giao thức? → Gateway",
    "IOTM-TN-02": "Node IoT thường được xây quanh gì? → Vi điều khiển có radio",
    "IOTM-TN-03": "Việc chính của nền tảng đám mây / máy chủ? → Lưu và phân tích dữ liệu từ thiết bị",
    "IOTM-TN-04": "3 lớp của kiến trúc IoT cơ bản? → Thu nhận, mạng, ứng dụng",
    "IOTM-TN-05": "Lớp nào chứa cảm biến và cơ cấu chấp hành? → Lớp thu nhận (perception)",
    "IOTM-TN-06": "Kiến trúc 5 lớp thêm lớp nào giữa lớp mạng và lớp ứng dụng? → Lớp xử lý (processing)",
    "IOTM-TN-07": "Mô hình nào thiết bị nói chuyện trực tiếp với nhau (công tắc và bóng đèn qua Bluetooth)? → Thiết "
    "bị–thiết bị",
    "IOTM-TN-08": "Cảm biến chuyển động phát hiện người, đèn hành lang bật — đèn đóng vai trò gì? → Cơ cấu chấp hành "
    "thực hiện lệnh",
    "IOTM-TN-09": "Bóng đèn dùng Zigbee nhưng đám mây chỉ tới được qua Wi-Fi — thành phần nào giải quyết? → Hub "
    "chuyển đổi Zigbee ↔ Wi-Fi",
    "IOTM-TN-10": "Nhóm đang chọn Wi-Fi, LoRa hay di động để gửi dữ liệu lên máy chủ — đang thiết kế lớp nào? → Lớp "
    "mạng",
    "IOTM-TN-11": "Hệ thống phải lưu, phân tích hàng terabyte dữ liệu trước khi hiện lên app — lớp nào (5 lớp)? → Lớp "
    "xử lý",
    "IOTM-TN-12": "App đỗ xe thông minh chỉ chỗ trống cho tài xế thuộc lớp nào? → Lớp ứng dụng",
    "IOTM-TN-13": "Vòng đeo tay gửi dữ liệu qua Bluetooth tới điện thoại, điện thoại đẩy lên đám mây — mô hình nào? → "
    "Thiết bị–gateway",
    "IOTM-TN-14": "Công ty bộ điều nhiệt chia sẻ dữ liệu năng lượng (được phép) cho nền tảng của hãng điện — mô hình "
    "nào? → Chia sẻ dữ liệu phía sau",
    "MSG-TN-01": "MQTT dùng mô hình nhắn tin nào? → Publish/subscribe",
    "MSG-TN-02": "Máy chủ nhận tin và chuyển cho người subscribe trong MQTT gọi là gì? → Broker",
    "MSG-TN-03": "Cổng mặc định của MQTT không TLS? → 1883",
    "MSG-TN-04": "QoS nào của MQTT giao tin đúng 1 lần? → QoS 2",
    "MSG-TN-05": "Broker làm gì với retained message? → Lưu lại và gửi cho người subscribe mới của topic",
    "MSG-TN-06": "CoAP mặc định chạy trên giao thức vận chuyển nào? → UDP",
    "MSG-TN-07": "Loại tin CoAP nào bên nhận phải xác nhận? → Confirmable (CON)",
    "MSG-TN-08": "Client subscribe home/+/temperature sẽ nhận topic nào? → home/kitchen/temperature",
    "MSG-TN-09": "Subscription nào nhận mọi tin dưới home ở mọi độ sâu? → home/#",
    "MSG-TN-10": "Cảm biến gửi nhiệt độ mỗi giây, mất 1 lần không sao — QoS nào hiệu quả nhất? → QoS 0",
    "MSG-TN-11": "Khóa cửa phải nhận lệnh 'mở' đúng 1 lần dù mạng kém — QoS nào? → QoS 2",
    "MSG-TN-12": "App muốn biết khi cảm biến rớt mạng bất thường — cảm biến đặt tính năng gì khi kết nối? → Last Will "
    "and Testament",
    "MSG-TN-13": "Client gửi CoAP GET /temperature và tài nguyên tồn tại — mã phản hồi thường gặp? → 2.05 Content",
    "MSG-TN-14": "Bảng điều khiển cần được báo mỗi khi giá trị cảm biến đổi mà không gửi GET liên tục — tính năng "
    "CoAP nào? → Observe",
    "SENS-TN-01": "Cảm biến nào cần nguồn kích thích ngoài? → RTD bạch kim (không dùng nhãn active/passive).",
    "SENS-TN-02": "Ví dụ cảm biến tự sinh tín hiệu? → thermocouple.",
    "SENS-TN-03": "Gia tốc kế MEMS kiểu tụ: cái gì thay đổi khi tăng tốc? → điện dung giữa khối thử và bản cố định.",
    "SENS-TN-04": "Cảm biến siêu âm tính khoảng cách thế nào? → thời gian bay của tiếng vọng: vận tốc âm x t / 2.",
    "SENS-TN-05": "Sensitivity là gì? → thay đổi đầu ra trên một đơn vị thay đổi đầu vào.",
    "SENS-TN-06": "Đặc tính nào là độ gần với giá trị thật? → accuracy.",
    "SENS-TN-07": "Threshold là gì? → đầu vào nhỏ nhất (tính từ 0) cho đầu ra phát hiện được.",
    "SENS-TN-08": "Cảm biến nhiệt đọc bằng cách cho dòng chạy qua → nhóm nào? → cần kích thích ngoài.",
    "SENS-TN-09": "Vì sao thermocouple hợp hơn thermistor cho lò 1000 °C? → dải đo rất rộng.",
    "SENS-TN-10": "Cảm biến tiệm cận cảm ứng không phát hiện vật nào? → chai nhựa (không phải kim loại).",
    "SENS-TN-11": "Bể 25,0 °C đo lặp được 26,1 / 26,0 / 26,1 → precise nhưng không accurate.",
    "SENS-TN-12": "Độ ẩm tăng tới 60% đọc 62%, giảm tới 60% đọc 58% → hysteresis.",
    "SENS-TN-13": "Cảm biến CO đổi đầu ra khi độ ẩm đổi → specificity kém.",
    "SENS-TN-14": "Mất 20 s để đạt 90% giá trị cuối → response time.",
    "RO-TN-01": "Khối nào đưa điện áp cảm biến về dải ADC? → bộ khuếch đại dùng opamp.",
    "RO-TN-02": "Hai bước của ADC? → lấy mẫu và lượng tử hóa.",
    "RO-TN-03": "ADC 10 bit có bao nhiêu mã? → 1024.",
    "RO-TN-04": "Kích thước 1 LSB? → Vref / 2^N.",
    "RO-TN-05": "Tốc độ lấy mẫu tối thiểu cho tín hiệu tần số cao nhất f? → lớn hơn 2f.",
    "RO-TN-06": "Sai số lượng tử lớn nhất (làm tròn gần nhất)? → nửa LSB.",
    "RO-TN-07": "Điện áp vào vượt full scale thì sao? → bão hòa ở mã lớn nhất.",
    "RO-TN-08": "50 mV đưa thẳng vào ADC 5 V → chỉ dùng ~1% dải, độ phân giải kém.",
    "RO-TN-09": "ADC 8 bit, Vref 2,048 V → LSB = 8 mV.",
    "RO-TN-10": "Tín hiệu rung tới 500 Hz → tốc độ lấy mẫu thấp nhất trong các lựa chọn mà không aliasing: 1200 mẫu/s.",
    "RO-TN-11": "Độ nhạy 20 mV/°C, LSB 2 mV → 0,1 °C.",
    "RO-TN-12": "Từ 10 bit lên 12 bit cùng Vref → LSB nhỏ đi 4 lần.",
    "RO-TN-13": "Cái giá của ADC nhiều bit hơn mức cần → tốn điện, chậm, nhiều dữ liệu.",
    "RO-TN-14": "Vì sao chọn gain để tín hiệu lớn nhất ngay dưới full scale? → dùng gần hết dải mà không bão hòa.",
    "NI-TN-01": "Tính chất của opamp lý tưởng? → điện trở vào vô hạn.",
    "NI-TN-02": "Non-ideality là gì? → chỗ opamp thật khác lý tưởng, gây sai số.",
    "NI-TN-03": "Hiệu ứng tải là gì? → điện trở vào hút dòng, mất một phần điện áp cảm biến.",
    "NI-TN-04": "Mạch đặt giữa cảm biến điện trở cao và phần sau để tránh tải? → voltage follower (buffer).",
    "NI-TN-05": "Input offset voltage là gì? → điện áp DC nhỏ như cộng vào đầu vào.",
    "NI-TN-06": "Slew rate là gì? → tốc độ thay đổi tối đa của điện áp ra.",
    "NI-TN-07": "Gain-bandwidth product nghĩa là gì? → gain càng cao, tần số bắt đầu giảm gain càng thấp.",
    "NI-TN-08": "Rs 1 kΩ, Rin 1 MΩ → khoảng 99,9%.",
    "NI-TN-09": "Đọc thấp khi nối bộ khuếch đại, đúng khi đo bằng đồng hồ trở kháng cao → Rin không lớn hơn nhiều Rs.",
    "NI-TN-10": "Gain 100, offset 1 mV → sai số đầu ra 0,1 V.",
    "NI-TN-11": "Bias current quan trọng nhất với cảm biến nào? → điện trở ra rất cao.",
    "NI-TN-12": "Thiết kế gain 1000, đo được 990 → open-loop gain hữu hạn.",
    "NI-TN-13": "Tín hiệu lớn, nhanh ra cạnh dốc tam giác → slew rate.",
    "NI-TN-14": "Đầu ra kẹt ở điện áp nguồn khi tín hiệu lớn → bão hòa.",
    "DA-TN-01": "Dự đoán máy hỏng trước khi xảy ra từ dữ liệu cảm biến → bảo trì dự đoán.",
    "DA-TN-02": "Mục tiêu tìm số đọc không khớp mẫu bình thường → phát hiện bất thường.",
    "DA-TN-03": "Tập giả thuyết là gì? → họ các mô hình ứng viên thuật toán được chọn.",
    "DA-TN-04": "Sai số trên dữ liệu mới chưa thấy → sai số ngoài mẫu.",
    "DA-TN-05": "Kiểu học có đáp án đúng cho mỗi ví dụ → có giám sát.",
    "DA-TN-06": "Kiểu học thử–sai theo phần thưởng → tăng cường.",
    "DA-TN-07": "Thư viện Python xử lý bảng dữ liệu → pandas.",
    "DA-TN-08": "Vì sao dùng học máy thay luật viết tay → quy luật chưa biết / quá phức tạp.",
    "DA-TN-09": "Khớp gần hoàn hảo dữ liệu huấn luyện, sai nhiều dữ liệu mới → overfitting.",
    "DA-TN-10": "Khi nào mô hình tốt trên dữ liệu huấn luyện cũng tốt trên dữ liệu mới → dữ liệu đại diện và đủ nhiều.",
    "DA-TN-11": "Dự đoán kWh ngày mai từ dữ liệu cũ → hồi quy có giám sát.",
    "DA-TN-12": "Gán nhãn động cơ 'hỏng' / 'bình thường' → phân loại có giám sát.",
    "DA-TN-13": "Cảm biến thỉnh thoảng báo 999 °C do lỏng dây → bước làm sạch (bỏ / sửa ngoại lai).",
    "DA-TN-14": "Tính trung bình rung mỗi phút để đưa vào mô hình → bước tính đặc trưng (thay câu cũ lộ đáp án "
    "DA-TL-04).",
    "DAT-TN-01": "Trong y = w0 + w1 x, w1 là gì → độ dốc.",
    "DAT-TN-02": "Chọn trọng số hồi quy thế nào → cực tiểu MSE (bình phương tối thiểu).",
    "DAT-TN-03": "Thành phần lặp theo chu kỳ cố định → seasonality.",
    "DAT-TN-04": "Trung bình trượt làm gì → làm mượt nhiễu, dễ thấy xu hướng.",
    "DAT-TN-05": "Mô hình AR dùng gì → tổng có trọng số các giá trị trước.",
    "DAT-TN-06": "Phân cụm là kiểu học nào → không giám sát.",
    "DAT-TN-07": "k-means gán mỗi điểm vào đâu → tâm gần nhất.",
    "DAT-TN-08": "y = 1,5 + 0,2x với x = 10 → 3,5.",
    "DAT-TN-09": "y = 1,5 + 0,2x: số 1,5 nghĩa là gì → y khi x = 0, hệ số chặn (thay câu cũ lộ ý ngoại suy của "
    "DAT-TL-05).",
    "DAT-TN-10": "MSE test 4,0 và 9,0 → mô hình A tốt hơn.",
    "DAT-TN-11": "Trung bình trượt 24 giờ trên 3 tháng cho thấy gì → xu hướng chậm, chu kỳ ngày bị làm mượt (thay câu "
    "cũ lộ DAT-TL-06).",
    "DAT-TN-12": "Dữ liệu theo giờ có chu kỳ ngày → thêm giá trị 24 giờ trước.",
    "DAT-TN-13": "Điểm mới xa mọi tâm cụm → coi là bất thường cần kiểm (thay câu cũ lộ DAT-TL-04).",
    "DAT-TN-14": "Elbow chọn k nào → k mà thêm cụm không còn cải thiện nhiều.",
    "IOT-TN-15": "Đặc điểm IoT chỉ hệ thống hàng tỉ thiết bị → quy mô rất lớn.",
    "IOT-TN-16": "Ví dụ vật cảm nhận môi trường → cảm biến đo độ sáng trong phòng.",
    "IOT-TN-17": "Nhà thông minh: luật tự động hóa được việc gì → tắt đèn khi phòng không có người.",
    "IOT-TN-18": "Dịch vụ thành phố thông minh giúp tìm chỗ đỗ xe → smart parking.",
    "IOT-TN-19": "Kẻ tấn công gom nhiều thiết bị bị chiếm thành gì → botnet (nhóm loại trừ với IOT-TL-03).",
    "IOT-TN-20": "Cảm biến ngủ 1 giờ rồi vào lại mạng → thay đổi động (nhóm với IOT-TL-04).",
    "IOT-TN-21": "Cảm biến trên cột đèn đo ô nhiễm → giám sát chất lượng không khí.",
    "IOT-TN-22": "Quản lý hàng triệu thiết bị, dữ liệu lớn → khả năng mở rộng.",
    "IOT-TN-23": "Kiểm tra cửa đã khóa chưa bằng điện thoại khi đang ở cơ quan → giám sát, điều khiển từ xa.",
    "IOT-TN-24": "Rèm tự đóng khi cảm biến thấy nắng gắt: thiết bị nào tác động → động cơ kéo rèm.",
    "IOTM-TN-15": "Ngoài dịch giao thức, gateway còn làm gì với dữ liệu → lọc hoặc gộp.",
    "IOTM-TN-16": "Thành phần cho người dùng xem dữ liệu và gửi lệnh → ứng dụng / giao diện (app, dashboard).",
    "IOTM-TN-17": "Kiến trúc 5 lớp: lớp quản lý mô hình kinh doanh, quyền riêng tư → business layer (nhóm với IOTM-TL-06).",
    "IOTM-TN-18": "Tên khác của perception layer → sensing (device) layer (nhóm với IOTM-TL-02).",
    "IOTM-TN-19": "Mục tiêu thiết kế: mỗi thiết bị rẻ → chi phí thấp mỗi thiết bị.",
    "IOTM-TN-20": "Thiết bị theo dõi bệnh nhân vẫn chạy khi một đường mạng hỏng → độ tin cậy.",
    "IOTM-TN-21": "Bảo vệ dữ liệu người dùng ngay từ đầu → bảo mật và riêng tư từ khâu thiết kế.",
    "IOTM-TN-22": "Trong ví dụ nhà thông minh của khóa, sự kiện của cảm biến chuyển động qua hub tới đâu để luật bật đèn → cloud (đề ghi rõ 'ví dụ trong khóa' vì hệ thống khác có thể chạy luật trên hub / edge; nhóm với IOTM-TL-05).",
    "IOTM-TN-23": "Động cơ mở cửa sổ khi luật kích hoạt là thành phần gì → cơ cấu chấp hành (nhóm với IOTM-TL-01).",
    "IOTM-TN-24": "Trạm thời tiết gửi thẳng lên cloud qua Wi-Fi riêng → device-to-cloud (nhóm với IOTM-TL-03).",
    "MSG-TN-15": "Cổng MQTT qua TLS → 8883.",
    "MSG-TN-16": "Gói client gửi để báo vẫn còn kết nối → PINGREQ.",
    "MSG-TN-17": "Bắt tay QoS 2 có mấy bước → bốn.",
    "MSG-TN-18": "Cổng mặc định của CoAP → 5683.",
    "MSG-TN-19": "Loại tin CoAP báo không xử lý được tin nhận → Reset (RST).",
    "MSG-TN-20": "Đăng ký MQTT nào KHÔNG hợp lệ → home/#/temperature (# phải ở cuối).",
    "MSG-TN-21": "Yêu cầu /humidity không tồn tại → 4.04 Not Found.",
    "MSG-TN-22": "Vì sao QoS 2 tốn lưu lượng hơn QoS 0 → bắt tay 4 bước để giao đúng một lần.",
    "MSG-TN-23": "Topic factory/line1/motor3/temp có mấy cấp → 4.",
    "MSG-TN-24": "Đổi giá trị một tài nguyên CoAP đã có → PUT.",
    "SENS-TN-15": "Đại lượng vật lý cảm biến đo gọi là gì → measurand (đại lượng đo).",
    "SENS-TN-16": "Cảm biến số cho đầu ra dạng gì → giá trị số, vd qua bus nối tiếp.",
    "SENS-TN-17": "Nhiệt độ tăng thì điện trở thermistor NTC thế nào → giảm.",
    "SENS-TN-18": "Range của cảm biến là gì → khoảng từ giá trị nhỏ nhất tới lớn nhất đo được.",
    "SENS-TN-19": "Đầu ra thay đổi chậm theo thời gian với cùng đầu vào gọi là gì → drift (trôi).",
    "SENS-TN-20": "Nhiệt kế hồng ngoại đo trán cách 5 cm → không tiếp xúc.",
    "SENS-TN-21": "Cảm biến IC 10 mV/°C, 0 V ở 0 °C → ở 25 °C ra 250 mV.",
    "SENS-TN-22": "Lệch tối đa 0,5 °C so với đường thẳng tốt nhất → sai số phi tuyến (nhóm với SENS-TL-06).",
    "SENS-TN-23": "Cân không đổi với tải dưới 2 g → 2 g là threshold (ngưỡng).",
    "SENS-TN-24": "Cảm biến cảm ứng không thấy chai nhựa → dùng cảm biến tiệm cận kiểu tụ.",
    "RO-TN-15": "Front end làm gì với cảm biến điện trở → cấp dòng kích thích, đổi thay đổi điện trở thành điện áp.",
    "RO-TN-16": "Khối cuối xử lý mã số → vi điều khiển.",
    "RO-TN-17": "Tốc độ lấy mẫu là gì → số mẫu mỗi giây.",
    "RO-TN-18": "Lượng tử hóa biến đầu vào liên tục thành gì → bậc thang các mức rời rạc (nhóm với RO-TL-02).",
    "RO-TN-19": "Vì sao không đặt tốc độ lấy mẫu quá cao → tiết kiệm điện và dữ liệu.",
    "RO-TN-20": "ADC 16 bit có bao nhiêu mã → 65536.",
    "RO-TN-21": "Cần độ phân giải 0,5 °C, cảm biến 10 mV/°C → LSB lớn nhất chấp nhận 5 mV (nhóm với RO-TL-05).",
    "RO-TN-22": "Cảm biến đã ra 0–2 V, ADC full scale 2,048 V → thêm gain hầu như không có lợi (nhóm với RO-TL-06).",
    "RO-TN-23": "Strain gauge đổi điện trở chứ không đổi điện áp → trước hết phải đổi thay đổi điện trở thành điện áp.",
    "RO-TN-24": "Sai số lượng tử thường biểu hiện như gì → nhiễu nhỏ cộng thêm.",
    "NI-TN-15": "Opamp lý tưởng có điện trở ra bao nhiêu → 0.",
    "NI-TN-16": "Chọn opamp cho bộ khuếch đại thermocouple gain 500, kiểm gì trước khi mua → giới hạn datasheet (vd offset) so với nhu cầu (viết lại 27/11 theo góp ý: phương án sai hợp lý hơn).",
    "NI-TN-17": "Offset đầu vào thường lớn cỡ nào → micro vôn tới vài milivôn.",
    "NI-TN-18": "Đầu vào opamp kiểu nào có điện trở vào rất cao → CMOS hoặc FET (nhóm với NI-TL-05).",
    "NI-TN-19": "Khi nào sai số opamp quan trọng nhất → khi tín hiệu cảm biến rất nhỏ.",
    "NI-TN-20": "Gain 10, offset 2 mV → sai số đầu ra 20 mV (nhóm với NI-TL-01).",
    "NI-TN-21": "Tăng gain từ 10 lên 100 cùng opamp → băng thông giảm khoảng 10 lần (nhóm với NI-TL-04).",
    "NI-TN-22": "Opamp nguồn 5 V phải ra 7 V → bão hòa gần điện áp nguồn.",
    "NI-TN-23": "Rs = 2 kΩ, Rin = 2 kΩ → opamp thấy 50% (nhóm với NI-TL-05).",
    "NI-TN-24": "Slew rate 1 V/µs, đầu ra tăng 5 V cần ít nhất bao lâu → 5 µs (thay câu cũ là mặt trái của NI-TN-19; KHÔNG xếp nhóm: xếp vào ni-speed thì đề NI-TL-01+04+05 thiếu câu thông hiểu).",
}


VN_ESSAY = {
    "IOT-TL-01": "IoT là gì, một vật cần gì để tham gia IoT. (giữ nguyên đề, thêm từ đồng nghĩa)",
    "IOT-TL-02": "**ĐỀ MỚI** — IoT dùng trong y tế và công nghiệp thế nào, lợi ích mỗi bên. (cũ: tự chọn 2 lĩnh vực "
    "nhưng barem ép nhà thông minh; bỏ nông nghiệp vì trùng ý với IOT-TL-05)",
    "IOT-TL-03": "**ĐỀ MỚI** — Vì sao bảo mật và quyền riêng tư là vấn đề lớn với thiết bị IoT trong nhà. (cũ có hỏi "
    "cách xử lý → trùng ý với IOT-TL-06; nay chỉ hỏi vì sao)",
    "IOT-TL-04": "**CÂU MỚI** — Giải thích 3 đặc điểm: thiết bị hạn chế tài nguyên, không đồng nhất, thay đổi liên "
    "tục. (thay câu năng lượng cũ vì trùng ý với IOT-TL-06)",
    "IOT-TL-05": "**ĐỀ MỚI** — Trang trại muốn tiết kiệm nước tưới: thiết bị đo gì, thiết bị nào tác động lên nguồn "
    "nước, hệ thống theo quy tắc nào. (bỏ LoRa / gateway / cloud / dashboard — không có trong tài liệu "
    "kỹ năng này)",
    "IOT-TL-06": "**ĐỀ MỚI** — Thành phố lắp 100.000 cảm biến nhiều hãng, chủ yếu chạy pin: đề xuất 1 cách xử lý cho "
    "mỗi thách thức security, interoperability, energy; giải thích vì sao energy quan trọng với dự án "
    "này. (cách 1 Tuấn chốt; thêm ý 4 vì câu nâng cao cần 4–5 ý)",
    "IOTM-TL-01": "**ĐỀ MỚI** — Cảm biến, cơ cấu chấp hành, gateway mỗi cái làm gì. (bỏ cloud để đủ khung 3 ý của câu "
    "dễ)",
    "IOTM-TL-02": "**ĐỀ MỚI** — Kiến trúc 3 lớp: lớp nào dưới cùng, lớp nào trên cùng; lớp dưới cùng làm gì. (đủ "
    'khung 3 ý; ý tên lớp có chủ thể "lowest/top" nên viết đảo không được điểm)',
    "IOTM-TL-03": "Khác nhau giữa device-to-cloud và device-to-gateway. (giữ đề, gắn chủ thể tên mô hình, thêm đồng "
    "nghĩa)",
    "IOTM-TL-04": "**ĐỀ MỚI** — Vì sao tiêu thụ ít năng lượng và khả năng mở rộng là mục tiêu thiết kế quan trọng. "
    '(cũ cho tự chọn 3 mục tiêu nhưng ép "low power")',
    "IOTM-TL-05": "Thiết kế hệ bật đèn hành lang ban đêm, gán thành phần vào 3 lớp. (giữ đề, gắn chủ thể cho ý gán "
    "lớp; ý 3 nay chấm lớp mạng — hub / Zigbee + network layer)",
    "IOTM-TL-06": "Mô tả 5 lớp và 2 lớp thêm vào bổ sung gì. (giữ đề; từ khóa chính là việc lớp đó làm, tên lớp là "
    "chủ thể)",
    "MSG-TL-01": "Tin nhắn MQTT đi từ client này sang client khác thế nào. (giữ đề; ý 3 cần broker chuyển tiếp)",
    "MSG-TL-02": 'So sánh QoS 0 và QoS 1. (giữ đề; gắn chủ thể QoS 0 / QoS 1, nhận "at most once", "acknowledgment")',
    "MSG-TL-03": "Vì sao CoAP có cả Confirmable và Non-confirmable. (giữ đề; gắn chủ thể CON / NON)",
    "MSG-TL-04": "2 điểm CoAP giống HTTP, 1 điểm khác. (giữ đề; nhận REST, URL; ý 3 nhận thêm header nhỏ 4 byte)",
    "MSG-TL-05": 'Thiết kế MQTT cho nhà kính 3 phòng. (bỏ "with reasons" vì barem không chấm lý do; nhận mọi tên '
    "phòng)",
    "MSG-TL-06": 'MQTT hay CoAP cho mạng cảm biến chạy pin. (giữ đề; gắn chủ thể MQTT / CoAP; nhận "recommend using '
    'CoAP")',
    "SENS-TL-01": "Hai nhóm cảm biến theo nhu cầu nguồn ngoài (tự sinh / cần kích thích), mỗi nhóm một ví dụ. KHÔNG "
    "bắt nhãn active/passive — bài thử viết theo quy ước IIT hay Fraden đều đạt. Giới hạn (c): từ khóa "
    "không gắn được ví dụ với nhóm (bài đảo ví dụ vẫn lọt từ khóa; Gemini chấm theo nghĩa).",
    "SENS-TL-02": "Phân biệt accuracy / precision. Gắn chủ thể để chặn bài viết đảo.",
    "SENS-TL-03": "Hysteresis là gì, vì sao gây vấn đề cho số đọc.",
    "SENS-TL-04": "Gia tốc kế MEMS kiểu tụ đổi gia tốc thành tín hiệu điện thế nào: khối thử dịch chuyển → điện dung "
    "đổi → mạch đọc đo thay đổi.",
    "SENS-TL-05": "(Nâng cao) Chọn cảm biến nhiệt cho kho lạnh -30…+10 °C và lò 1000 °C, lý do theo dải đo / thời "
    "gian đáp ứng.",
    "SENS-TL-06": "(Nâng cao) Đọc bảng đặc tính hai cảm biến độ ẩm (Alpha / Beta), chọn một; giải thích accuracy, "
    "hysteresis, non-linearity của Beta ảnh hưởng thế nào tới điểm bật quạt 70 %RH. Hỏi HỆ QUẢ trong "
    "tình huống, không hỏi lại định nghĩa (tránh trùng SENS-TL-02, 03).",
    "RO-TL-01": "Vì sao phải khuếch đại trước ADC.",
    "RO-TL-02": "Lượng tử hóa là gì, sai số tối đa bao nhiêu (½ LSB).",
    "RO-TL-03": "Tốc độ lấy mẫu tối thiểu (> 2 lần tần số cao nhất) và hậu quả nếu chậm (aliasing). Barem không cho "
    "điểm chỉ vì gọi tên 'Nyquist'.",
    "RO-TL-04": "ADC nhiều bit hơn: được gì (LSB nhỏ hơn), mất gì (điện, tốc độ, giá, dữ liệu).",
    "RO-TL-05": "(Nâng cao, tính toán) 10 mV/°C, ADC 12 bit, Vref 4,096 V → LSB = 1 mV, độ phân giải 0,1 °C. Tách ý "
    "cách làm / ý kết quả.",
    "RO-TL-06": "(Nâng cao, thiết kế) Cảm biến 0–100 mV, ADC 0–4,096 V → gain ≈ 40 (≤ 40,96). Bài thử 'gain 41' phải "
    "trượt ý kết quả.",
    "NI-TL-01": "Input offset voltage là gì, vì sao quan trọng hơn khi gain lớn.",
    "NI-TL-02": "Input bias current là gì, vì sao là vấn đề với cảm biến điện trở ra cao.",
    "NI-TL-03": "Vì sao gain thực hơi khác gain đặt bằng điện trở (open-loop gain hữu hạn).",
    "NI-TL-04": "Vì sao opamp có thể khuếch đại sai tín hiệu thay đổi nhanh: băng thông và slew rate (chủ thể gắn với "
    "từng giới hạn).",
    "NI-TL-05": "(Nâng cao, tính toán) Rs 10 kΩ, Rin 90 kΩ → 90%; vì sao; cách khắc phục (buffer).",
    "NI-TL-06": "(Nâng cao, tình huống) Cảm biến khí 10 MΩ, tín hiệu chậm, đọc qua bộ khuếch đại opamp: tính chất nào "
    "quan trọng NHẤT (điện trở vào / bias current) và ÍT NHẤT (băng thông / slew rate). Đã bỏ 'gain 1000' "
    "(Tuấn 27/11) để offset không thành đáp án đúng thứ hai và không trùng NI-TL-01.",
    "DA-TL-01": "Vì sao dữ liệu cảm biến thô cần phân tích; bảo trì dự đoán và phát hiện bất thường mỗi cái đạt được "
    "gì (đề ghi rõ hai mục tiêu, không cho chọn tự do).",
    "DA-TL-02": "Các thành phần của việc học: cái chưa biết (hàm mục tiêu), cái đang có (dữ liệu), thuật toán tạo ra "
    "gì (giả thuyết cuối từ tập giả thuyết).",
    "DA-TL-03": "Ba kiểu học khác nhau ở loại phản hồi (nhãn / không nhãn / phần thưởng). Có chủ thể để chặn bài viết "
    "đảo supervised / unsupervised.",
    "DA-TL-04": "Vì sao chia train / test: kiểm tra trên dữ liệu chưa thấy; tập test phải để riêng. KHÔNG hỏi "
    "overfitting (nằm ở DA-TL-06).",
    "DA-TL-05": "(Nâng cao) Quy trình bảo trì dự đoán từ dữ liệu rung: gán nhãn, làm sạch, đặc trưng, chọn kiểu học "
    "(có giám sát, phân loại), hành động. Không có ý 'đánh giá' (tránh trùng DA-TL-04).",
    "DA-TL-06": "(Nâng cao) Mô hình học dữ liệu mùa hè sai vào mùa đông: dữ liệu không đại diện, sai số trong mẫu "
    "thấp không bảo đảm ngoài mẫu, cách khắc phục, kiểm trên dữ liệu mùa đông.",
    "DAT-TL-01": "Hồi quy tuyến tính tìm gì (đường thẳng, độ dốc, hệ số chặn) và khớp thế nào (bình phương tối thiểu).",
    "DAT-TL-02": "Ba thành phần chuỗi thời gian kèm giải thích; chủ thể gắn từng thành phần (bài đảo không được điểm).",
    "DAT-TL-03": "Các bước k-means sau khi chọn k tâm: gán về tâm gần nhất, dời tâm về trung bình, lặp tới khi ổn "
    "định.",
    "DAT-TL-04": "Vì sao chuẩn hóa đặc trưng trước k-means: dùng khoảng cách, đặc trưng dải lớn lấn át.",
    "DAT-TL-05": "(Nâng cao, tính toán) E = 2 + 0,5T, dải dữ liệu 10–35 °C: dự đoán ở 30 °C = 17 kWh (ý cách làm / ý "
    "kết quả tách riêng), ý nghĩa 0,5, không tin dự đoán 60 °C (ngoại suy). Bài thử thay sai 60 → 32 "
    "trượt ý kết quả.",
    "DAT-TL-06": "(Nâng cao, thiết kế) Dự báo nhiệt độ giờ tới: chia theo thời gian không xáo trộn, đầu vào là các "
    "giờ trước và giá trị 24 giờ trước.",
}
