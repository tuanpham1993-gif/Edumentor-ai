## 3. Tạo và kích hoạt môi trường ảo (Virtual Environment)

Thực hiện các lệnh sau tại thư mục gốc của dự án (*project root*: 'Edumentor-ai\').

### Windows PowerShell

**Bước 1: Tạo môi trường ảo**

```powershell
python -m venv .venv
```

Lệnh này tạo môi trường ảo Python trong thư mục `.venv` nhằm tách biệt các thư viện của dự án với những dự án Python khác trên máy tính.

**Bước 2: Kích hoạt môi trường ảo**

```powershell
.\.venv\Scripts\Activate.ps1
```

Sau khi kích hoạt thành công, bạn thường sẽ thấy `(.venv)` xuất hiện ở đầu dòng lệnh trong terminal.

**Bước 3: Cài đặt các thư viện cần thiết**

```powershell
python -m pip install -r backend\requirements.txt
```

Lệnh này cài đặt các thư viện được liệt kê trong file `\backend\requirements.txt` của dự án.

## 4. Cấu hình biến môi trường (Environment Variables) + docker postgres

1. Chuyển `\Edumentor-ai\.env.example` sang `\Edumentor-ai\.env` tại thư mục gốc của dự án, cùng cấp với file `docker-compose.yaml`.
2. đối với file docker-compose.yaml. Tại `\Edumentor-ai\` chạy lệnh: "docker docker-compose up --build -d"

3. setting pgadmin4 cấu hình:
    - General/name: edumentor
    - Connection/hostname: 127.0.0.1
    - Port: 5433
    - Username: edumentor
    - Password: edumentor123
    