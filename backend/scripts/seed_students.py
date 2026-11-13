"""Tạo hàng loạt tài khoản HỌC VIÊN mẫu (dữ liệu demo · module 01 · 13/11/2026).

Mặc định tạo 1.500 học viên (role = student), mỗi người một email riêng sinh theo họ tên:
    nguyenvanan.0001@example.com, tranthibinh.0002@example.com, ...
Domain example.com là domain dành riêng cho ví dụ (RFC 2606) → không phải hộp thư thật,
hệ thống có lỡ gửi mail cũng không tới ai.

Chạy (trong thư mục backend):
    python -m scripts.seed_students                         # 1.500 học viên, mật khẩu demo mặc định
    python -m scripts.seed_students --count 200             # số lượng khác
    python -m scripts.seed_students --csv data/students.csv # xuất danh sách email + họ tên ra CSV

Đặc điểm:
- Chạy lại nhiều lần an toàn (idempotent): email đã có thì bỏ qua, không tạo trùng.
- Cùng --count luôn sinh ra CÙNG danh sách (random có seed cố định) → cả nhóm có dữ liệu giống nhau.
- Mọi học viên dùng chung MỘT mật khẩu demo (băm bcrypt một lần rồi dùng lại → nhanh;
  băm 1.500 lần riêng mất vài phút). Đây là dữ liệu demo, không dùng cho tài khoản thật.
- Không gọi auth_service.register → không tạo 1.500 thông báo chào mừng, không gửi email.
- Kèm hồ sơ cơ bản (user_profiles): giới tính, ngày sinh, quê quán, số điện thoại. KHÔNG sinh CCCD.
"""

import argparse
import csv
import random
import sys
import unicodedata
from datetime import date, timedelta
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, create_tables
from app.core.security import hash_password, validate_password
from app.models.user import Users
from app.models.user_profile import UserProfile

DEFAULT_COUNT = 1500
DEFAULT_PASSWORD = "HocVien@123"  # đạt quy tắc mật khẩu: hoa, thường, số, ký tự đặc biệt
EMAIL_DOMAIN = "example.com"
RANDOM_SEED = 2026  # cố định → chạy lại ra đúng danh sách cũ
BATCH_SIZE = 500

FAMILY_NAMES = [
    "Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng",
    "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý", "Đinh", "Trương", "Mai", "Cao",
]
MIDDLE_NAMES = {
    "male": ["Văn", "Hữu", "Đức", "Minh", "Quốc", "Thành", "Gia", "Hoàng", "Công", "Anh"],
    "female": ["Thị", "Ngọc", "Thu", "Thanh", "Khánh", "Minh", "Phương", "Bảo", "Mỹ", "Hồng"],
}
GIVEN_NAMES = {
    "male": [
        "An", "Bình", "Cường", "Dũng", "Đạt", "Hải", "Hiếu", "Hùng", "Huy", "Khang",
        "Khoa", "Long", "Nam", "Phát", "Phúc", "Quân", "Sơn", "Tài", "Thắng", "Tuấn",
        "Trung", "Việt", "Vinh", "Khôi", "Nhân",
    ],
    "female": [
        "Anh", "Chi", "Diệp", "Giang", "Hà", "Hạnh", "Hoa", "Hương", "Lan", "Linh",
        "Mai", "My", "Ngân", "Nhung", "Oanh", "Phương", "Quỳnh", "Tâm", "Thảo", "Trang",
        "Trâm", "Uyên", "Vy", "Yến", "Hòa",
    ],
}
HOMETOWNS = [
    "Hà Nội", "TP. Hồ Chí Minh", "Đà Nẵng", "Hải Phòng", "Cần Thơ", "Huế", "Nghệ An",
    "Thanh Hóa", "Quảng Nam", "Bình Định", "Khánh Hòa", "Lâm Đồng", "Đồng Nai",
    "Bắc Ninh", "Nam Định", "Thái Bình", "An Giang", "Kiên Giang", "Quảng Ninh", "Đắk Lắk",
]
PHONE_PREFIXES = ["032", "033", "035", "070", "077", "081", "085", "090", "091", "096", "097", "098"]


def to_ascii_slug(text: str) -> str:
    """'Nguyễn Văn Đạt' → 'nguyenvandat' (bỏ dấu, bỏ khoảng trắng) để làm phần trước @ của email."""
    text = text.replace("Đ", "D").replace("đ", "d")  # NFKD không tách được chữ đ
    no_accent = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return "".join(ch for ch in no_accent.lower() if ch.isalnum())


def generate_students(count: int) -> list[dict]:
    """Sinh `count` học viên giả. Số thứ tự trong email đảm bảo email không bao giờ trùng."""
    rng = random.Random(RANDOM_SEED)
    width = max(4, len(str(count)))  # 0001..1500; nếu > 9999 thì tự dài thêm
    students = []
    for i in range(1, count + 1):
        gender = rng.choice(("male", "female"))
        full_name = " ".join(
            (rng.choice(FAMILY_NAMES), rng.choice(MIDDLE_NAMES[gender]), rng.choice(GIVEN_NAMES[gender]))
        )
        students.append(
            {
                "full_name": full_name,
                "email": f"{to_ascii_slug(full_name)}.{i:0{width}d}@{EMAIL_DOMAIN}",
                "gender": gender,
                # Tuổi 18–30 tính tới 2026
                "date_of_birth": date(1996, 1, 1) + timedelta(days=rng.randrange(0, 12 * 365)),
                "hometown": rng.choice(HOMETOWNS),
                "phone": rng.choice(PHONE_PREFIXES) + f"{rng.randrange(0, 10**7):07d}",
            }
        )
    return students


def seed_students(db: Session, students: list[dict], password: str) -> tuple[int, int]:
    """Thêm học viên chưa có vào DB. Trả về (số tạo mới, số bỏ qua vì email đã tồn tại)."""
    validate_password(password)  # mật khẩu demo cũng phải đúng quy tắc, nếu không sẽ không đăng nhập được
    hashed = hash_password(password)  # băm MỘT lần, dùng chung

    emails = [s["email"] for s in students]
    existing: set[str] = set()
    for start in range(0, len(emails), BATCH_SIZE):  # IN (...) theo lô, tránh câu SQL quá dài
        chunk = emails[start : start + BATCH_SIZE]
        existing.update(db.scalars(select(Users.email).where(Users.email.in_(chunk))))

    created = 0
    for s in students:
        if s["email"] in existing:
            continue
        user = Users(email=s["email"], full_name=s["full_name"], hashed_password=hashed, role="student")
        user.profile = UserProfile(
            gender=s["gender"], date_of_birth=s["date_of_birth"], hometown=s["hometown"], phone=s["phone"]
        )
        db.add(user)
        created += 1
        if created % BATCH_SIZE == 0:
            db.flush()
    db.commit()
    return created, len(existing)


def write_csv(path: Path, students: list[dict]) -> None:
    """Xuất danh sách email + họ tên (KHÔNG có mật khẩu) để tiện đăng nhập thử / import."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:  # utf-8-sig: Excel đọc đúng tiếng Việt
        writer = csv.writer(f)
        writer.writerow(["stt", "email", "full_name", "gender", "date_of_birth", "hometown", "phone"])
        for i, s in enumerate(students, start=1):
            writer.writerow(
                [i, s["email"], s["full_name"], s["gender"], s["date_of_birth"].isoformat(), s["hometown"], s["phone"]]
            )


def main() -> int:
    parser = argparse.ArgumentParser(description="Tạo học viên mẫu cho EduMentor AI")
    parser.add_argument("--count", type=int, default=DEFAULT_COUNT, help="Số học viên (mặc định 1500)")
    parser.add_argument("--password", default=DEFAULT_PASSWORD, help="Mật khẩu demo chung")
    parser.add_argument("--csv", type=Path, help="Đường dẫn file CSV xuất danh sách email")
    parser.add_argument("--csv-only", action="store_true", help="Chỉ xuất CSV, không ghi vào DB")
    args = parser.parse_args()

    if args.count < 1:
        print("--count phải >= 1")
        return 1

    students = generate_students(args.count)

    if args.csv:
        write_csv(args.csv, students)
        print(f"Đã xuất {len(students)} email ra {args.csv}")
    if args.csv_only:
        return 0

    create_tables()  # phòng khi chạy trước lần đầu khởi động server
    db = SessionLocal()
    try:
        created, skipped = seed_students(db, students, args.password)
    except ValueError as error:  # mật khẩu không đạt quy tắc
        print(f"Mật khẩu không hợp lệ: {error}")
        return 1
    finally:
        db.close()

    print(f"Đã tạo {created} học viên mới, bỏ qua {skipped} email đã có.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
