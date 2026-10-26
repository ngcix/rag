import os
import argparse
from optimum.onnxruntime import ORTModelForFeatureExtraction
from transformers import AutoTokenizer

def convert_model_to_onnx(model_id: str, output_dir: str, quantize_int8: bool = False):
    """
    Tải và chuyển đổi mô hình Embedding sang định dạng ONNX.
    """
    print(f"🔄 Đang tải mô hình '{model_id}' và khởi tạo quá trình convert sang ONNX...")
    
    # 1. Tải và lưu Tokenizer
    print("📥 Đang tải Tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    tokenizer.save_pretrained(output_dir)
    
    # 2. Tải và chuyển đổi Mô hình sang ONNX
    print("⚡ Đang convert model sang ONNX (với cấu hình Feature Extraction)...")
    # Sử dụng export=True để Optimum tự động build đồ thị ONNX từ weights gốc
    model = ORTModelForFeatureExtraction.from_pretrained(
        model_id, 
        export=True,
        provider="CPUExecutionProvider" # Hoặc "CUDAExecutionProvider" nếu chạy GPU
    )
    
    # Lưu mô hình ONNX tiêu chuẩn (FP32)
    model.save_pretrained(output_dir)
    print(f"✅ Đã lưu mô hình ONNX chuẩn tại: {output_dir}")
    
    # 3. Lượng tử hóa sang INT8 nếu được yêu cầu (Rất khuyến khích cho CPU)
    if quantize_int8:
        print("⚙️ Đang thực hiện lượng tử hóa (Quantization) sang INT8 để tối ưu hóa CPU...")
        from optimum.onnxruntime.configuration import AutoQuantizationConfig
        from optimum.onnxruntime import ORTQuantizer
        
        # Cấu hình lượng tử hóa động (Dynamic Quantization) tối ưu cho CPU
        qconfig = AutoQuantizationConfig.avx512_vnni(is_static=False, per_channel=False)
        quantizer = ORTQuantizer.from_pretrained(model_dir=output_dir)
        
        # Thực hiện lượng tử hóa file 'model.onnx' thành 'model_quantized.onnx'
        quantizer.quantize(
            save_dir=output_dir,
            quantization_config=qconfig,
        )
        # Ghi đè file chính để TEI sử dụng bản INT8 làm mặc định
        if os.path.exists(os.path.join(output_dir, "model_quantized.onnx")):
            os.replace(
                os.path.join(output_dir, "model_quantized.onnx"),
                os.path.join(output_dir, "model.onnx")
            )
            print("✅ Đã lượng tử hóa thành công và cấu hình mô hình mặc định thành INT8!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Hugging Face Embedding Model to ONNX")
    parser.add_argument("--model", type=str, default="./data/models/Qwen3-Embedding-0.6B", help="Hugging Face Model ID")
    parser.add_argument("--output", type=str, default="./data/models/qwen3-onnx", help="Thư mục đầu ra")
    parser.add_argument("--quantize", action="store_true", help="Kích hoạt lượng tử hóa INT8 (Tối ưu cho CPU)")
    
    args = parser.parse_args()
    
    os.makedirs(args.output, exist_ok=True)
    convert_model_to_onnx(args.model, args.output, quantize_int8=args.quantize)
