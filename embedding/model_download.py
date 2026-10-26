import os
import argparse
from huggingface_hub import snapshot_download

def download_model(model_id: str, local_dir: str):
    """
    Tải toàn bộ artifact của model từ Hugging Face Hub về thư mục cục bộ.
    """
    print(f"🔄 Đang tải mô hình '{model_id}' từ Hugging Face Hub...")
    
    # Chỉ tải các tệp cần thiết cho việc inference của TEI (bỏ qua .bin nếu đã có .safetensors)
    ignore_patterns = ["*.msgpack", "*.h5", "*.ot", "pytorch_model.bin"] 
    
    try:
        snapshot_download(
            repo_id=model_id,
            local_dir=local_dir,
            local_dir_use_symlinks=False,
            ignore_patterns=ignore_patterns,
            token=os.getenv("HF_TOKEN") # Sử dụng nếu là model private
        )
        print(f"✅ Tải thành công! Mô hình được lưu tại: {os.path.abspath(local_dir)}")
    except Exception as e:
        print(f"❌ Đã xảy ra lỗi khi tải mô hình: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tự động tải mô hình cho Hugging Face TEI")
    parser.add_argument("--model", type=str, default="BAAI/bge-m3", help="Hugging Face Model ID (Ví dụ: BAAI/bge-m3)")
    parser.add_argument("--output", type=str, default="./data/models/", help="Thư mục lưu trữ cục bộ")
    
    args = parser.parse_args()
    
    # Tạo thư mục đầu ra nếu chưa tồn tại
    os.makedirs(args.output, exist_ok=True)
    download_model(args.model, args.output)
