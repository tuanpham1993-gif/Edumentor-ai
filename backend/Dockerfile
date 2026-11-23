
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    HF_HOME=/cache/huggingface \
    NLTK_DATA=/usr/local/share/nltk_data

WORKDIR /app/backend

COPY requirements.txt ./requirements.txt

# Cài PyTorch bản CPU-only trước
RUN pip install --no-cache-dir \
    --index-url https://download.pytorch.org/whl/cpu \
    torch

# Cài các thư viện còn lại
RUN pip install --no-cache-dir -r requirements.txt

# Tải dữ liệu NLTK
RUN python -m nltk.downloader \
    -d /usr/local/share/nltk_data \
    punkt_tab \
    stopwords \
    wordnet \
    averaged_perceptron_tagger_eng

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
