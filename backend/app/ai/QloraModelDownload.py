
import os
from pathlib import Path

from dotenv import load_dotenv
from huggingface_hub import HfApi, hf_hub_download


# ==========================================
# 1. Resolve paths
# ==========================================

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parents[2]

ENV_FILE = PROJECT_ROOT / ".env"
DOWNLOAD_DIR = CURRENT_DIR / "models"

DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ==========================================
# 2. Load Hugging Face token
# ==========================================

load_dotenv(ENV_FILE)

HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    raise ValueError(f"HF_TOKEN not found: {ENV_FILE}")


# ==========================================
# 3. Repository configuration
# ==========================================

REPO_ID = "RWain/edumentor-qwen3-skill-extraction_2-F16-GGUF"

api = HfApi(token=HF_TOKEN)


# ==========================================
# 4. Find GGUF file
# ==========================================

print("Checking Hugging Face repository...")

files = api.list_repo_files(
    repo_id=REPO_ID,
    repo_type="model"
)

gguf_files = [
    filename for filename in files
    if filename.lower().endswith(".gguf")
]

if not gguf_files:
    raise FileNotFoundError("No GGUF files found in repository.")

if len(gguf_files) > 1:
    raise RuntimeError(
        f"Multiple GGUF files found: {gguf_files}. "
        "Please select one explicitly."
    )

FILENAME = gguf_files[0]

print("Found GGUF:", FILENAME)


# ==========================================
# 5. Download
# ==========================================

print("\nStarting download...")

file_path = hf_hub_download(
    repo_id=REPO_ID,
    filename=FILENAME,
    repo_type="model",
    token=HF_TOKEN,
    local_dir=DOWNLOAD_DIR
)


# ==========================================
# 6. Verify
# ==========================================

file_path = Path(file_path)

if not file_path.exists():
    raise FileNotFoundError("Download verification failed.")

file_size_gb = file_path.stat().st_size / (1024 ** 3)

print("\nDownload completed!")
print("File:", file_path)
print(f"Size: {file_size_gb:.2f} GB")
