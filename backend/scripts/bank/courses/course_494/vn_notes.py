"""Ghi chú tiếng Việt cho file duyệt (render_review.py): tóm tắt đoạn, dịch trắc nghiệm, ghi chú tự luận."""

VN_CHUNK = {
    "IOT-K01": "IoT là mạng các vật thể có cảm biến, phần mềm, kết nối mạng để thu và trao đổi dữ liệu; mỗi vật cần định danh "
    "riêng (IP, mã thiết bị); vật cảm nhận môi trường, một số tác động qua cơ cấu chấp hành. Đặc điểm: kết nối, "
    "cảm nhận, định danh riêng, không đồng nhất, quy mô rất lớn, thay đổi động. Nhiều thiết bị bị giới hạn "
    "(ít bộ nhớ, xử lý yếu, chạy pin).",
    "IOT-K02": "Ứng dụng: nhà thông minh (đèn, nhiệt kế, khóa, camera điều khiển từ điện thoại), nông nghiệp (cảm biến độ "
    "ẩm đất → tưới, tiết kiệm nước), y tế (thiết bị đeo đo nhịp tim, đường huyết, báo bác sĩ từ xa), công "
    "nghiệp (đo rung, nhiệt độ máy để dự đoán hỏng — bảo trì dự đoán), thành phố (đỗ xe thông minh, đèn "
    "đường tự giảm sáng, đo chất lượng không khí).",
    "IOT-K03": "Thách thức: bảo mật (mật khẩu mặc định, ít cập nhật → bị chiếm làm botnet), riêng tư (dữ liệu cá nhân), "
    "tương thích (khác hãng, khác giao thức; chuẩn và gateway giúp), năng lượng (thiết bị pin phải tiết kiệm, "
    "ngủ phần lớn thời gian), mở rộng quy mô (hàng triệu thiết bị, dữ liệu lớn).",
    "IOTM-K01": "Thành phần: cảm biến đo, cơ cấu chấp hành tác động; node (vi điều khiển + radio); gateway nối thiết bị cục "
    "bộ với internet, chuyển đổi giao thức (Zigbee/Bluetooth → Wi-Fi/Ethernet), lọc / gộp dữ liệu; mạng; "
    "đám mây / máy chủ lưu và phân tích; ứng dụng / giao diện. Ví dụ nhà thông minh: cảm biến chuyển động → "
    "hub → đám mây → luật bật đèn.",
    "IOTM-K02": "Kiến trúc 3 lớp: lớp thu nhận (perception — cảm biến, cơ cấu chấp hành), lớp mạng (Wi-Fi, di động, Zigbee, "
    "LoRa), lớp ứng dụng (dịch vụ cho người dùng). Kiến trúc 5 lớp thêm lớp xử lý (middleware — lưu, phân "
    "tích dữ liệu lớn) giữa lớp mạng và ứng dụng, và lớp nghiệp vụ (business) trên cùng quản lý toàn hệ "
    "thống, mô hình kinh doanh, quyền riêng tư.",
    "IOTM-K03": "4 mô hình giao tiếp: thiết bị–thiết bị (trực tiếp, Bluetooth / Zigbee), thiết bị–đám mây (trực tiếp qua "
    "Wi-Fi), thiết bị–gateway (qua hub / điện thoại chuyển lên đám mây), chia sẻ dữ liệu phía sau (dịch vụ "
    "đám mây chia sẻ cho dịch vụ khác được phép). Mục tiêu thiết kế: tiêu thụ ít năng lượng, giá thấp, mở "
    "rộng, tin cậy, bảo mật và riêng tư từ thiết kế, tương thích.",
    "MSG-K01": "MQTT: giao thức nhắn tin nhẹ cho thiết bị giới hạn, mạng kém. Mô hình publish/subscribe qua broker; client "
    "publish vào topic (vd home/livingroom/temperature), broker chuyển cho client đã subscribe. Topic phân cấp "
    "bằng '/'; ký tự đại diện '+' khớp đúng 1 cấp, '#' khớp mọi cấp còn lại (phải ở cuối). Chạy trên TCP, "
    "cổng 1883, 8883 khi dùng TLS.",
    "MSG-K02": "QoS 0 = tối đa 1 lần (không xác nhận, có thể mất); QoS 1 = ít nhất 1 lần (giữ tới khi nhận PUBACK, có thể "
    "trùng); QoS 2 = đúng 1 lần (bắt tay 4 bước PUBLISH, PUBREC, PUBREL, PUBCOMP, tốn hơn). Retained message: "
    "broker giữ và gửi ngay cho người subscribe mới. Last Will: broker phát khi client rớt bất thường. "
    "Keep-alive: client gửi PINGREQ để báo còn kết nối.",
    "MSG-K03": "CoAP (RFC 7252): giao thức web cho thiết bị giới hạn, kiểu REST — tài nguyên có URI, phương thức GET / POST "
    "/ PUT / DELETE, mã phản hồi giống HTTP (2.05 Content, 4.04 Not Found). Chạy trên UDP cổng 5683, header "
    "cố định 4 byte. Loại tin: CON (phải xác nhận ACK, gửi lại nếu thiếu), NON (không xác nhận), RST (không "
    "xử lý được). Observe: client đăng ký, server báo mỗi khi tài nguyên đổi.",
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
    "IOT-TN-09": "Mạng thành phố: nghìn cảm biến nhiều hãng, có cái ngủ, thêm mới hằng tháng — thể hiện 2 đặc điểm nào? → Không đồng nhất và thay đổi động",
    "IOT-TN-10": "Bệnh viện theo dõi nhịp tim bệnh nhân tại nhà, báo bác sĩ khi nguy hiểm — lĩnh vực nào? → Theo dõi sức khỏe từ xa",
    "IOT-TN-11": "Thành phố muốn đèn đường tiết kiệm điện lúc đêm vắng — giải pháp nào? → Đèn có cảm biến chuyển động, tự giảm sáng khi không có người",
    "IOT-TN-12": "Khóa hãng A, hub hãng B không điều khiển được vì khác giao thức — thách thức nào? → Tương thích",
    "IOT-TN-13": "Vòng đeo tay ghi giờ ngủ và vị trí cả ngày, đẩy lên đám mây — vấn đề trực tiếp nhất? → Riêng tư dữ liệu cá nhân",
    "IOT-TN-14": "Vì sao cảm biến chạy pin ngủ phần lớn thời gian? → Tiết kiệm năng lượng để pin bền hơn",
    "IOTM-TN-01": "Thành phần nào nối thiết bị cục bộ với internet và chuyển đổi giao thức? → Gateway",
    "IOTM-TN-02": "Node IoT thường được xây quanh gì? → Vi điều khiển có radio",
    "IOTM-TN-03": "Việc chính của nền tảng đám mây / máy chủ? → Lưu và phân tích dữ liệu từ thiết bị",
    "IOTM-TN-04": "3 lớp của kiến trúc IoT cơ bản? → Thu nhận, mạng, ứng dụng",
    "IOTM-TN-05": "Lớp nào chứa cảm biến và cơ cấu chấp hành? → Lớp thu nhận (perception)",
    "IOTM-TN-06": "Kiến trúc 5 lớp thêm lớp nào giữa lớp mạng và lớp ứng dụng? → Lớp xử lý (processing)",
    "IOTM-TN-07": "Mô hình nào thiết bị nói chuyện trực tiếp với nhau (công tắc và bóng đèn qua Bluetooth)? → Thiết bị–thiết bị",
    "IOTM-TN-08": "Cảm biến chuyển động phát hiện người, đèn hành lang bật — đèn đóng vai trò gì? → Cơ cấu chấp hành thực hiện lệnh",
    "IOTM-TN-09": "Bóng đèn dùng Zigbee nhưng đám mây chỉ tới được qua Wi-Fi — thành phần nào giải quyết? → Hub chuyển đổi Zigbee ↔ Wi-Fi",
    "IOTM-TN-10": "Nhóm đang chọn Wi-Fi, LoRa hay di động để gửi dữ liệu lên máy chủ — đang thiết kế lớp nào? → Lớp mạng",
    "IOTM-TN-11": "Hệ thống phải lưu, phân tích hàng terabyte dữ liệu trước khi hiện lên app — lớp nào (5 lớp)? → Lớp xử lý",
    "IOTM-TN-12": "App đỗ xe thông minh chỉ chỗ trống cho tài xế thuộc lớp nào? → Lớp ứng dụng",
    "IOTM-TN-13": "Vòng đeo tay gửi dữ liệu qua Bluetooth tới điện thoại, điện thoại đẩy lên đám mây — mô hình nào? → Thiết bị–gateway",
    "IOTM-TN-14": "Công ty bộ điều nhiệt chia sẻ dữ liệu năng lượng (được phép) cho nền tảng của hãng điện — mô hình nào? → Chia sẻ dữ liệu phía sau",
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
    "MSG-TN-12": "App muốn biết khi cảm biến rớt mạng bất thường — cảm biến đặt tính năng gì khi kết nối? → Last Will and Testament",
    "MSG-TN-13": "Client gửi CoAP GET /temperature và tài nguyên tồn tại — mã phản hồi thường gặp? → 2.05 Content",
    "MSG-TN-14": "Bảng điều khiển cần được báo mỗi khi giá trị cảm biến đổi mà không gửi GET liên tục — tính năng CoAP nào? → Observe",
}

VN_ESSAY = {
    "IOT-TL-01": "IoT là gì, một vật cần gì để tham gia IoT. (giữ nguyên đề, thêm từ đồng nghĩa)",
    "IOT-TL-02": "**ĐỀ MỚI** — IoT dùng trong y tế và công nghiệp thế nào, lợi ích mỗi bên. (cũ: tự chọn 2 lĩnh vực nhưng barem ép nhà thông minh; bỏ nông nghiệp vì trùng ý với IOT-TL-05)",
    "IOT-TL-03": "**ĐỀ MỚI** — Vì sao bảo mật và quyền riêng tư là vấn đề lớn với thiết bị IoT trong nhà. (cũ có hỏi cách xử lý → trùng ý với IOT-TL-06; nay chỉ hỏi vì sao)",
    "IOT-TL-04": "**CÂU MỚI** — Giải thích 3 đặc điểm: thiết bị hạn chế tài nguyên, không đồng nhất, thay đổi liên tục. (thay câu năng lượng cũ vì trùng ý với IOT-TL-06)",
    "IOT-TL-05": "**ĐỀ MỚI** — Trang trại muốn tiết kiệm nước tưới: thiết bị đo gì, thiết bị nào tác động lên nguồn nước, hệ thống theo quy tắc nào. (bỏ LoRa / gateway / cloud / dashboard — không có trong tài liệu kỹ năng này)",
    "IOT-TL-06": "**ĐỀ MỚI** — Thành phố lắp 100.000 cảm biến nhiều hãng, chủ yếu chạy pin: đề xuất 1 cách xử lý cho mỗi thách thức security, interoperability, energy; giải thích vì sao energy quan trọng với dự án này. (cách 1 Tuấn chốt; thêm ý 4 vì câu nâng cao cần 4–5 ý)",
    "IOTM-TL-01": "**ĐỀ MỚI** — Cảm biến, cơ cấu chấp hành, gateway mỗi cái làm gì. (bỏ cloud để đủ khung 3 ý của câu dễ)",
    "IOTM-TL-02": '**ĐỀ MỚI** — Kiến trúc 3 lớp: lớp nào dưới cùng, lớp nào trên cùng; lớp dưới cùng làm gì. (đủ khung 3 ý; ý tên lớp có chủ thể "lowest/top" nên viết đảo không được điểm)',
    "IOTM-TL-03": "Khác nhau giữa device-to-cloud và device-to-gateway. (giữ đề, gắn chủ thể tên mô hình, thêm đồng nghĩa)",
    "IOTM-TL-04": '**ĐỀ MỚI** — Vì sao tiêu thụ ít năng lượng và khả năng mở rộng là mục tiêu thiết kế quan trọng. (cũ cho tự chọn 3 mục tiêu nhưng ép "low power")',
    "IOTM-TL-05": "Thiết kế hệ bật đèn hành lang ban đêm, gán thành phần vào 3 lớp. (giữ đề, gắn chủ thể cho ý gán lớp; ý 3 nay chấm lớp mạng — hub / Zigbee + network layer)",
    "IOTM-TL-06": "Mô tả 5 lớp và 2 lớp thêm vào bổ sung gì. (giữ đề; từ khóa chính là việc lớp đó làm, tên lớp là chủ thể)",
    "MSG-TL-01": "Tin nhắn MQTT đi từ client này sang client khác thế nào. (giữ đề; ý 3 cần broker chuyển tiếp)",
    "MSG-TL-02": 'So sánh QoS 0 và QoS 1. (giữ đề; gắn chủ thể QoS 0 / QoS 1, nhận "at most once", "acknowledgment")',
    "MSG-TL-03": "Vì sao CoAP có cả Confirmable và Non-confirmable. (giữ đề; gắn chủ thể CON / NON)",
    "MSG-TL-04": "2 điểm CoAP giống HTTP, 1 điểm khác. (giữ đề; nhận REST, URL; ý 3 nhận thêm header nhỏ 4 byte)",
    "MSG-TL-05": 'Thiết kế MQTT cho nhà kính 3 phòng. (bỏ "with reasons" vì barem không chấm lý do; nhận mọi tên phòng)',
    "MSG-TL-06": 'MQTT hay CoAP cho mạng cảm biến chạy pin. (giữ đề; gắn chủ thể MQTT / CoAP; nhận "recommend using CoAP")',
}
