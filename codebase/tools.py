"""Công cụ của bài toán — NHÓM VIẾT. Điền ở guide bước 2.2 (thiết kế) và 3.2 (code).

Mỗi công cụ là một hàm Python có @tool. Docstring ghi đúng 4 ý như sơ đồ ở spec.md §4:
    tên · input · output · có tác động ra ngoài không (gửi tin, sửa dữ liệu, chấm điểm…)
Khung tự ghi mỗi lần gọi công cụ vào trace (tên, input, output rút gọn, thời gian, lỗi).

Số công cụ, kiểu công cụ do thiết kế của nhóm quyết định — có bài chỉ cần một công cụ tra cứu.
Công cụ có tác động ra ngoài: KHÔNG tự làm. Trả về bản nháp chờ người duyệt (guide bước 2.2, "chỗ người duyệt").
Dữ liệu công cụ đọc (bài mẫu, thông báo mẫu, lịch…): để trong data/ và mô tả ở data/DATA_CARD.md.
"""
from tracing import tool, TOOLS  # noqa: F401  (TOOLS: danh sách công cụ đã đăng ký, dùng khi viết vòng lặp agent)
from shopee_reviews import fetch_product_reviews


@tool
def search_example(query: str) -> list:
    """(ví dụ — thay bằng công cụ của nhóm) Tra dữ liệu mẫu theo câu hỏi.
    Input: câu hỏi (str). Output: danh sách đoạn {"code", "text"}. Không tác động ra ngoài."""
    return [{"code": "VD-1", "text": "(ví dụ) đoạn dữ liệu giả — thay bằng dữ liệu thật của bài toán"}]


@tool
def crawl_shopee_reviews(url: str, max_reviews: int = 100) -> dict:
    """Lấy review công khai của một listing Shopee Việt Nam.
    Input: link shopee.vn và số review tối đa. Output: thông tin sản phẩm,
    review đã ẩn danh và metadata độ phủ. Chỉ đọc qua dịch vụ bên thứ ba; không sửa dữ liệu shop."""
    return fetch_product_reviews(url, max_reviews=max_reviews)
