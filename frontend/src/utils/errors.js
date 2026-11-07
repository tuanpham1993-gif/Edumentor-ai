// Đổi lỗi từ backend FastAPI thành dữ liệu dễ hiển thị (module 01 · Tuấn · FĐ1, 07/11/2026).
//
// Backend trả lỗi 2 dạng:
//   - 400 / 401 / 403 / 404 / 409 / 413 / 415: {"detail": "Email đã được sử dụng."}
//   - 422 (Pydantic):  {"detail": [{"loc": ["body", "password"], "msg": "Value error, Mật khẩu ..."}]}
//
// parseApiError(error) → { status, message, fieldErrors }
//   status      : mã HTTP (0 nếu không tới được máy chủ)
//   message     : câu tổng quát để hiện trên hộp .alert, vd "Lỗi 401: Email hoặc mật khẩu không đúng."
//   fieldErrors : lỗi theo từng ô (422), vd { password: "Mật khẩu phải có ít nhất 1 chữ hoa." }

const NETWORK_MESSAGE = 'Không kết nối được máy chủ. Vui lòng thử lại.';

function cleanMessage(msg) {
  return String(msg ?? '').replace(/^Value error, /, '');
}

export function parseApiError(error) {
  const response = error?.response;
  if (!response) {
    return { status: 0, message: NETWORK_MESSAGE, fieldErrors: {} };
  }

  const { status, data } = response;
  const detail = data?.detail;

  if (Array.isArray(detail)) {
    const fieldErrors = {};
    for (const item of detail) {
      const loc = item.loc ?? [];
      // ["body", "password"] → "password"; lỗi cả form (model_validator) → loc = ["body"]
      const field = loc.length > 1 ? loc[loc.length - 1] : '_form';
      if (!fieldErrors[field]) fieldErrors[field] = cleanMessage(item.msg);
    }
    const first = Object.values(fieldErrors)[0] ?? 'Dữ liệu chưa hợp lệ.';
    return { status, message: `Lỗi ${status}: ${first}`, fieldErrors };
  }

  const text = typeof detail === 'string' ? detail : 'Có lỗi xảy ra. Vui lòng thử lại.';
  return { status, message: `Lỗi ${status}: ${text}`, fieldErrors: {} };
}
