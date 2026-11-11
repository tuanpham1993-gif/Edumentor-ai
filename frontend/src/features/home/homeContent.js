// Nội dung trang chủ cho khách (FĐ7, 08/11/2026) — tách khỏi giao diện để dễ sửa chữ.
//
// ⚠ FEATURED_COURSES và NEWS là DỮ LIỆU MẪU: backend chưa có API khóa học / tin tức công khai.
//    Khi module khóa học (Khôi) có GET /courses → thay FEATURED_COURSES bằng dữ liệu thật.

export const HERO_POINTS = [
  { icon: 'route', text: 'Lộ trình học cá nhân hóa' },
  { icon: 'bulb', text: 'Gợi ý khóa học theo năng lực' },
  { icon: 'check', text: 'Ôn tập 20 câu để ghi nhận kỹ năng' },
];

export const STEPS = [
  {
    title: 'Tạo tài khoản và chọn mục tiêu',
    text: 'Cho EduMentor biết bạn muốn học gì và trình độ hiện tại của bạn.',
  },
  {
    title: 'Nhận lộ trình riêng',
    text: 'AI sắp xếp các khóa học theo thứ tự phù hợp với năng lực và mục tiêu của bạn.',
  },
  {
    title: 'Học, ôn tập, ghi nhận kỹ năng',
    text: 'Hoàn thành bài ôn tập 20 câu để kỹ năng được cập nhật vào hồ sơ của bạn.',
  },
];

export const FEATURES = [
  { icon: 'route', title: 'Lộ trình cá nhân hóa', text: 'Mỗi người một lộ trình, xây dựng từ mục tiêu và năng lực thực tế.' },
  { icon: 'bulb', title: 'Gợi ý khóa học thông minh', text: 'Đề xuất khóa học vừa sức, không quá dễ cũng không quá khó.' },
  { icon: 'check', title: 'Ôn tập và đánh giá', text: 'Bài ôn tập 20 câu sau mỗi khóa, chấm điểm và lưu lịch sử làm bài.' },
  { icon: 'chart', title: 'Theo dõi tiến độ', text: 'Biết mình đang ở đâu trong lộ trình và còn bao nhiêu để hoàn thành.' },
  { icon: 'badge', title: 'Hồ sơ kỹ năng', text: 'Kỹ năng đạt được tự động cập nhật vào hồ sơ cá nhân của bạn.' },
  { icon: 'bot', title: 'Trợ lý AI', text: 'Hỏi đáp và giải thích kiến thức bất cứ khi nào bạn cần.' },
];

export const SAMPLE_PATH = {
  title: 'Lập trình Web Backend',
  steps: [
    { name: 'Python cơ bản', state: 'done' },
    { name: 'Cơ sở dữ liệu SQL', state: 'current' },
    { name: 'FastAPI và REST API', state: 'todo' },
    { name: 'Triển khai ứng dụng', state: 'todo' },
  ],
};

// DỮ LIỆU MẪU — thay bằng API khóa học khi có
export const FEATURED_COURSES = [
  {
    level: 'Cơ bản',
    title: 'Lập trình Python cho người mới',
    text: 'Làm quen biến, vòng lặp, hàm và tư duy giải quyết vấn đề.',
    tone: 'ok',
  },
  {
    level: 'Trung cấp',
    title: 'Cơ sở dữ liệu với PostgreSQL',
    text: 'Thiết kế bảng, truy vấn SQL và tối ưu dữ liệu cho ứng dụng.',
    tone: 'info',
  },
  {
    level: 'Nâng cao',
    title: 'Xây dựng REST API với FastAPI',
    text: 'Tạo API, xác thực người dùng và kết nối cơ sở dữ liệu.',
    tone: 'accent',
  },
];

// DỮ LIỆU MẪU — tin nổi bật (chưa có API tin tức)
export const NEWS = [
  {
    tag: 'Cập nhật',
    date: '08/11/2026',
    title: 'Ra mắt trang hồ sơ mới với giao diện Tối / Sáng',
    text: 'Quản lý thông tin cá nhân, ảnh đại diện và mật khẩu ở cùng một nơi.',
  },
  {
    tag: 'Sắp ra mắt',
    date: '11/2026',
    title: 'Ôn tập bằng câu hỏi do AI tạo',
    text: 'Câu hỏi trắc nghiệm và tự luận được tạo theo nội dung từng khóa học.',
  },
  {
    tag: 'Mẹo học tập',
    date: '11/2026',
    title: 'Học đều 30 phút mỗi ngày hiệu quả hơn học dồn',
    text: 'Chia nhỏ lộ trình thành các mục tiêu tuần để giữ nhịp học ổn định.',
  },
];
