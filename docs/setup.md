# Setup



# Build docker


# Download embedding model


# Changing model
Khi bạn tiến hành đổi mô hình (Embedding hoặc Reranker) chạy trên Docker Image cực kỳ tối ưu của Hugging Face **Text Embeddings Inference (TEI)**, có **5 lưu ý kỹ thuật cốt lõi** bạn bắt buộc phải kiểm tra để tránh làm sập hệ thống hoặc trả về kết quả sai lệch ngữ nghĩa.

Dưới đây là checklist chi tiết giúp bạn kiểm soát việc đổi mô hình an toàn tuyệt đối:

---

### 1. Sự tương thích về định dạng tệp (Model Weights Compatibility)
TEI được viết bằng ngôn ngữ Rust để tối ưu hóa hiệu năng tối đa. Nó **không tự động tải và chạy mọi mô hình** giống như thư viện `transformers` của Python.
*   **Trọng số `.safetensors`:** TEI yêu cầu mô hình phải có tệp trọng số ở định dạng mã hóa an toàn `.safetensors`. Nếu bạn đổi sang một mô hình chỉ có file trọng số kiểu cũ là `pytorch_model.bin`, TEI sẽ báo lỗi và không thể khởi động.
*   **Với Image ONNX (`:cpu-1.8.1`):** Image này **bắt buộc** thư mục model cục bộ của bạn phải chứa tệp mô hình đã được xuất sang định dạng ONNX (thường là `model.onnx` hoặc `model_quantized.onnx`). Bạn không thể mount một thư mục chứa tệp PyTorch/Safetensors thông thường vào image ONNX này.

### 2. Thiết lập Pooling Layer (Mean vs CLS vs Last-Token)
Mỗi mô hình được huấn luyện để tổng hợp vector theo các phương pháp "pooling" khác nhau. Đây là lỗi phổ biến nhất khiến hệ thống chạy thành công nhưng **kết quả tìm kiếm (RAG) bị sai lệch hoàn toàn về ngữ nghĩa**.
*   **Mean Pooling (Phổ biến nhất):** Tính trung bình cộng của toàn bộ các token (ví dụ: `BGE-M3`, `Qwen3-Embedding-0.6B`).
*   **CLS Pooling:** Lấy vector của token đặc biệt `[CLS]` ở đầu câu (thường có ở các mô hình BERT đời cũ).
*   **Last-Token Pooling:** Thường dùng cho các mô hình embedding phát triển từ mô hình ngôn ngữ lớn Decoder-only (như `Qwen3-Embedding-8B` hoặc các dòng Llama-based).
*   **Cách xử lý:** Mặc định TEI sẽ cố gắng đọc cấu hình pooling từ tệp `1_Pooling/config.json` của mô hình. Tuy nhiên, để an toàn tuyệt đối, bạn nên thiết lập ghi đè (override) tường minh thông qua tham số khởi động:
    ```bash
    --pooling mean   # Hoặc --pooling cls, --pooling last-token tùy mô hình
    ```

### 3. Giới hạn số lượng Token tối đa (Context Window / Max Tokens)
Khi đổi mô hình, độ dài văn bản đầu vào tối đa mà mô hình đó hỗ trợ sẽ thay đổi.
*   Nếu bạn đổi từ mô hình hỗ trợ ngữ cảnh ngắn (như `bge-small-en-v1.5` - 512 tokens) sang mô hình hỗ trợ ngữ cảnh siêu dài (như `Qwen3-Embedding-0.6B` - 32,768 tokens) hoặc ngược lại:
    *   Bạn bắt buộc phải điều chỉnh tham số `--max-batch-tokens` và cấu hình bộ nhớ của mình.
    *   Nếu gửi một chunk tài liệu vượt quá giới hạn mô hình mà không cấu hình tự động cắt bớt (`--auto-truncate`), TEI sẽ trả về lỗi HTTP 400 hoặc 500 cho API Client của bạn.

### 4. Kích thước Vector đầu ra (Dimension Size) & Độ đo khoảng cách
Sự thay đổi về kích thước chiều của vector (Dimension size) sẽ **làm hỏng Vector Database hiện tại của bạn**.
*   **Ví dụ:** Mô hình cũ của bạn sinh ra vector có độ dài `768` (như `bge-small`), nhưng mô hình mới lại sinh ra vector độ dài `1,024` (như `BGE-M3` hay `Qwen3-Embedding`).
*   **Hậu quả:** Vector DB (như FAISS hay LanceDB của bạn) sẽ báo lỗi không khớp chiều (Dimension Mismatch) khi bạn ghi đè dữ liệu mới hoặc truy vấn.
*   **Khắc phục:** Khi đổi mô hình có chiều vector khác, bạn **bắt buộc phải xóa/khởi tạo lại (Re-index) toàn bộ index trong Vector Database**. Đồng thời, hãy kiểm tra xem mô hình mới yêu cầu đo khoảng cách bằng **Cosine Similarity** hay **Dot Product (Inner Product)**.

### 5. Cấu hình phần cứng (CPU Instruction Sets & RAM)
Khi bạn chạy trên môi trường CPU:
*   Các mô hình embedding mới lớn hơn (ví dụ từ `300M` lên `600M` hoặc `1.5B` tham số) sẽ tiêu tốn bộ nhớ RAM hơn và làm tăng độ trễ (latency).
*   Hãy điều chỉnh lại hai tham số tối ưu hóa luồng xử lý của TEI trong tệp cấu hình Compose để tránh làm treo CPU:
    *   `--max-client-batch-size`: Đặt thấp xuống (ví dụ: `16` hoặc `32`) nếu đổi sang mô hình nặng hơn để tránh nghẽn hàng đợi.
    *   `--tokenization-workers`: Giới hạn số luồng CPU dùng để parse text (mặc định TEI sẽ chiếm dụng toàn bộ nhân CPU hiện có).

---

### 📝 Tóm tắt Checklist thao tác khi đổi mô hình trong Docker Compose:

1.  [ ] Tải đúng phiên bản mô hình (ưu tiên định dạng `.safetensors`).
2.  [ ] Kiểm tra xem thư mục model có tệp `1_Pooling/config.json` chưa, nếu chưa thì phải đặt cờ `--pooling` thủ công.
3.  [ ] Cập nhật biến môi trường `MODEL_ID` trong `docker-compose.yml` chỉ chính xác đến thư mục chứa model mới.
4.  [ ] Điều chỉnh lại `--max-batch-tokens` phù hợp với Context Limit của mô hình mới.
5.  [ ] **Xóa chỉ mục cũ và chạy lại pipeline Indexing của SpecRAG** để đảm bảo đồng bộ hóa kích thước vector mới.

# Convert Model to ONNX (cpu run)

python convert_to_onnx.py --model Qwen/Qwen3-Embedding-0.6B --output ./models/qwen3-onnx

python convert_to_onnx.py --model Qwen/Qwen3-Embedding-0.6B --output ./models/qwen3-onnx-int8 --quantize



# Run docker

