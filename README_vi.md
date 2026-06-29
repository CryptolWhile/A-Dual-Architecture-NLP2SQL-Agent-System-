# A Dual-Architecture NLP2SQL Agent System

![UI Query GPT Agent](figures/UI%20Query%20GPT%20Agent.png)

Một hệ thống AI kiến trúc kép cho phép bạn trò chuyện với dữ liệu CSV của mình bằng Ngôn ngữ tự nhiên để tạo ra các truy vấn SQL và biểu đồ. Kho lưu trữ này chủ động phát triển và so sánh song song hai phương pháp kiến trúc khác biệt.

## Tính năng

- **Tải lên bất kỳ file CSV nào (Hệ thống Baseline)**: Ứng dụng tự động suy luận cấu trúc dữ liệu và đọc siêu dữ liệu (metadata).
- **Ngôn ngữ tự nhiên sang SQL**: Chuyển đổi các câu hỏi chat của bạn thành các câu truy vấn DuckDB được tối ưu hóa.
- **Tự động trực quan hóa dữ liệu (Hệ thống Baseline)**: Tự động viết mã Python để tạo và hiển thị biểu đồ trực tiếp bằng Matplotlib/Plotly.
- **Triển khai kiến trúc kép**: 
  - **Hệ thống Baseline**: Một pipeline 3-agent với **Lớp ngữ nghĩa (Semantic Layer)** để tiền phân tích truy vấn dựa trên tập luật (Semantic -> Analyzer -> SQL -> Chart).
  - **Hệ thống Query GPT**: Một pipeline 6 bước nâng cao lấy cảm hứng từ Query GPT của Uber (Enhance -> Intent -> Table -> Prune -> GenAI -> Execute) kết hợp với Cơ chế định tuyến Workspace (Workspace Routing).
- **Đánh giá Benchmark**: Một bộ đánh giá chuyên dụng kiểm tra cả hai hệ thống trên 257 câu hỏi truy vấn phức tạp.

## Kiến trúc hệ thống

### 1. Hệ thống Baseline (Pipeline 3-Agent + Lớp ngữ nghĩa)

```text
[Người dùng Chat]
      |
      v
+--------------+
|  Streamlit   |-------+
|     UI       |       | (Tải lên CSV)
+--------------+       |
      |                v
      |         +--------------+
      |         | Trích xuất   |
      |         | Metadata CSV |
      |         +--------------+
      |                |
      v                v
+-----------------------------+
|    Lớp ngữ nghĩa (Semantic) | <-- (Dựa trên luật, Không dùng LLM)
|  +------------------------+ |
|  | - Nhận diện Ý định     | |
|  | - Khớp tên Cột         | |
|  | - Nhận diện Tính toán  | |
|  | - Nhận diện Thời gian  | |
|  | - Nhận diện Đầu ra     | |
|  +------------------------+ |
+-----------------------------+
      |
      | (SemanticResult: intent, columns, ops, ...)
      v
+--------------+ <-- (Schema + SemanticResult + User Query)
|   Analyzer   |
|    Agent     |
+--------------+
      |
      | (Tạo Kế hoạch trích xuất dữ liệu)
      v
+--------------+
|     SQL      | --> [DuckDB Thực thi SQL]
|    Agent     | <-- [Trả về tập dữ liệu con]
+--------------+
      |
      | (Chuyển dữ liệu & kiểm tra có cần vẽ biểu đồ không)
      v
+--------------+
|    Chart     | --> [Tạo biểu đồ Plotly/Matplotlib]
|    Agent     | --> [Lưu vào output/]
+--------------+
      |
      v
[Streamlit UI Hiển thị Dữ liệu/Biểu đồ]
```

1. **Lớp ngữ nghĩa (semantic/)**: Một module tiền xử lý dựa trên tập luật (không gọi LLM) phân tích câu hỏi của người dùng trước khi chuyển cho các agent LLM. Module này trích xuất siêu dữ liệu có cấu trúc để giảm khối lượng công việc của LLM và cải thiện độ chính xác:
   - **Nhận diện Ý định (Intent Detection)**: Phân loại ý định truy vấn (tổng hợp, lọc, so sánh, xếp hạng, xu hướng, phân phối) sử dụng khớp từ khóa.
   - **Khớp tên Cột (Column Matching)**: Khớp mờ các từ trong truy vấn với tên cột CSV bằng 4 chiến lược: chính xác, chuẩn hóa (bỏ dấu), dựa trên từ đồng nghĩa (Việt <-> Anh), và khớp mờ (SequenceMatcher).
   - **Nhận diện Tính toán (Aggregation Detection)**: Xác định các phép toán SQL (SUM, AVG, COUNT, MAX, MIN) từ từ khóa tiếng Việt/Anh.
   - **Nhận diện Thời gian (Time Period Detection)**: Trích xuất độ phân giải thời gian (ngày/tháng/quý/năm) và các bộ lọc thời gian cụ thể.
   - **Nhận diện Đầu ra (Output Type Detection)**: Xác định định dạng đầu ra mong muốn (biểu đồ, bảng, giá trị đơn).
   - **Nhận diện GROUP BY / Sort**: Xác định các gợi ý gom nhóm và sắp xếp.
2. **Analyzer Agent**: Phân tích ý định của người dùng sử dụng cả schema của CSV và SemanticResult từ Lớp ngữ nghĩa. Các gợi ý có cấu trúc cho phép LLM xác thực và tinh chỉnh thay vì phân tích lại từ đầu.
3. **SQL Agent**: Dịch các chỉ dẫn thành câu truy vấn SQL tối ưu và thực thi an toàn bằng engine DuckDB. Sử dụng dấu nháy kép cho các định danh để hỗ trợ tên bảng/cột có ký tự đặc biệt.
4. **Chart Agent (Tùy chọn)**: Kích hoạt nếu có yêu cầu trực quan hóa, agent này viết và thực thi mã Python (matplotlib/plotly) để vẽ biểu đồ bên trong Streamlit.

### 2. Hệ thống Query GPT (Lấy cảm hứng từ Uber)

Một kiến trúc mới điều khiển bởi schema được tối ưu hóa cho tập hợp lớn các file CSV (hơn 68 file) và giảm thiểu việc tràn context-window thông qua cơ chế Định tuyến Workspace thông minh.

```text
       [Câu hỏi Chat của người dùng]
              |
              v
   +----------------------+    +-------------------------+
   | 1. Prompt Enhancer   |    | 0. Metadata Scanner     |
   | (Mở rộng Truy vấn)   |    | (Tạo schema &           |
   +----------------------+    |  workspaces.json)       |
              |                +-------------+-----------+
              v                              |
   +----------------------+                  |
   | 2. Intent Agent      |                  |
   | (Định tuyến Workspace|                  |
   +----------------------+                  v
              |                +-------------------------+
              v                | Người dùng Chọn/Sửa CSV |
   +-----------------------------------------+-----------+
   | 3. Table Agent (Tìm CSV tốt nhất trong  |
   |    Workspace đã khớp)                   |
   +-----------------------------------------+
              |
              v (Schema CSV đã khớp + Truy vấn đã mở rộng)
   +--------------------------------------------------+
   | 4. Column Pruner (Loại bỏ các cột không liên quan|
   +--------------------------------------------------+
              |
              v (Schema đã cắt tỉa + Truy vấn đã mở rộng)
   +--------------------------------------------------+    +-----------------------+
   | 5. GenAI SQL Gateway (Sinh SQL DuckDB)           |<---| SQL Samples RAG       |
   +--------------------------------------------------+    +----------+------------+
              |                                                       ^
              |                                            +----------+------------+
              |                                            | Ingest Data           |
              |                                            | (Vector hóa mẫu SQL)  |
              |                                            +-----------------------+
              v (SQL có thể thực thi)
   +--------------------------------------------------+
   | 6. SQL Executor (Chạy DuckDB & Format Markdown)  |
   +--------------------------------------------------+
              |
              v
      [Streamlit UI Hiển thị Dữ liệu Markdown]
```

1. **Metadata Scanner (schema_builder.py & build_workspaces.py)**: Quét trước thư mục data-code/InfiAgent/da-dev-tables/, xây dựng một schema_registry.json tổng, và nhóm hơn 68 file vào các workspace theo chủ đề (Tài chính, Y tế, Thể thao, Giao thông, Chung) thông qua workspaces.json.
2. **Prompt Enhancer**: Đón các câu hỏi ngắn hoặc mơ hồ và sử dụng LLM để mở rộng chúng thành các câu hỏi chi tiết, rõ ràng nhằm cải thiện độ chính xác ở các bước sau.
3. **Intent Agent**: Phân loại chủ đề ngữ nghĩa của đầu vào đã mở rộng và định tuyến câu hỏi đến ID Workspace chính xác.
4. **Table Agent**: Sử dụng Workspace và Câu hỏi để xác định file CSV duy nhất có liên quan nhất từ nhóm dữ liệu cụ thể đó. (Bao gồm UI để người dùng chọn thủ công hoặc sửa đổi file CSV đã chọn).
5. **Column Pruner Agent**: CHỈ chọn các cột tuyệt đối cần thiết để trả lời câu hỏi, loại bỏ phần còn lại để tiết kiệm đáng kể token LLM và ngăn chặn hiện tượng ảo giác (hallucination).
6. **GenAI SQL Gateway**: Một pipeline chuyên dụng kết hợp schema đã cắt tỉa, các mẫu SQL truy xuất được (thông qua RAG), và câu hỏi của người dùng để sinh ra SQL DuckDB Few-Shot có độ chính xác cao.
7. **SQL Executor**: Một wrapper chạy trong môi trường sandbox thực thi câu hỏi trên DuckDB và truyền kết quả về cho người dùng.
8. **SQL Sample RAG (sql_samples/)**: Sử dụng Agno và ChromaDB để tìm các ví dụ SQL liên quan tương tự với câu hỏi của người dùng, giúp tăng cường độ chính xác khi sinh SQL.

## Đánh giá Benchmark

Một bộ benchmark nghiêm ngặt (benchmark/) đánh giá cả hai hệ thống với tập dữ liệu gồm 257 câu hỏi dạng bảng phức tạp.

- **Hiệu suất Hệ thống Baseline**: 90 / 257 câu đúng (Độ chính xác: 35.02%)
- **Hiệu suất Hệ thống Query GPT**: 85 / 257 câu đúng (Độ chính xác: 33.07%)

*Lưu ý: Kiến trúc Query GPT hiện tại đang bỏ qua bước Table Agent trong quá trình đánh giá tự động (được hardcode chọn đúng bảng). Sự khác biệt về độ chính xác làm nổi bật các cơ hội tối ưu hóa trong các bước Cắt tỉa cột (Column Pruning) và Sinh SQL (GenAI SQL Generation).*

## Cài đặt

1. **Yêu cầu trước**: Đảm bảo bạn đã cài đặt Python. Chúng tôi khuyên dùng [uv](https://github.com/astral-sh/uv) để quản lý môi trường của bạn.

2. **Khởi tạo môi trường python và cài đặt thư viện**:
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install -r requirements.txt
   ```

3. **Cấu hình biến môi trường**:
   Sao chép file môi trường mẫu và thêm OpenAI API Key của bạn:
   ```bash
   cp .env.example .env
   ```
   Sau đó, mở file `.env` và thiết lập khóa của bạn:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Hướng dẫn sử dụng

Kho lưu trữ này chứa các bash script có thể thực thi cho cả hai hệ thống riêng biệt. Các tài nguyên dữ liệu (data-code/) được chia sẻ nhiều giữa hai hệ thống.

### Chạy Hệ thống Baseline
1. Khởi động ứng dụng Streamlit:
   ```bash
   ./run_baseline.sh
   ```
2. Tải lên một file CSV thông qua thanh bên trái (sidebar).
3. Chat với dữ liệu của bạn!

### Chạy Hệ thống Query GPT
Trước khi khởi động kiến trúc query GPT, bạn **bắt buộc** phải xây dựng metadata schema registry và phân bổ workspace ít nhất một lần:
```bash
python query_gpt_system/metadata/schema_builder.py
python query_gpt_system/metadata/build_workspaces.py
```
Quá trình này sẽ quét sâu tất cả các file CSV lớn trong data-code/InfiAgent/da-dev-tables/ và cấu trúc định dạng của chúng cho Table Agent.

Tiếp theo, bạn cần nạp các mẫu SQL vào cơ sở dữ liệu vector cho hệ thống RAG:
```bash
python query_gpt_system/sql_samples/ingest_samples.py
```

Sau khi registry được nạp thành công và dữ liệu mẫu đã được lưu trữ:
```bash
./run_query_gpt.sh
```

### Chạy Benchmark đánh giá
Để chạy các bài kiểm tra tự động và tạo file `results.json`:
```bash
python benchmark/run_eval_baseline.py
python benchmark/run_eval_query_gpt.py
```

### Ví dụ về Prompt
- "Tuổi trung bình của hành khách trong từng hạng vé là bao nhiêu?"
- "Tìm 10 quốc gia có điểm hạnh phúc cao nhất và vẽ biểu đồ cho chúng."
- "Mối tương quan giữa số lượng phòng và giá nhà là gì?"

## Xây dựng bằng
- [Agno](https://agno.com/) - Framework đa tác nhân (Multi-agent)
- [Streamlit](https://streamlit.io/) - Giao diện Web tương tác
- [DuckDB](https://duckdb.org/) - Cơ sở dữ liệu SQL phân tích in-memory
- [OpenAI](https://openai.com/) - Sử dụng mô hình ngôn ngữ gpt-4o-mini
- [ChromaDB](https://www.trychroma.com/) - Cơ sở dữ liệu AI mã nguồn mở
