# Sửa cách ghi nhận số đo — 25/10/2026

Firmware protocol 3 tách độ hợp lệ heap khỏi kết quả dò stack. Mẫu có heap
hợp lệ nhưng stack chưa xác định được web ghi partial; stack để trống, không
quy về 0. Lý do stack được ghi: unavailable / measured / untouched / saturated.
Các nhóm so sánh web tách theo phiên bản giao thức để không ghép v2 và v3.
Parser v1/v2 vẫn tương thích; không phục hồi mẫu v2 invalid vì không có lý do.

Đã qua 35 kiểm thử Python, kiểm tra cú pháp JavaScript và build firmware.
Chưa nạp firmware, chưa restart server và chưa xác nhận mẫu protocol 3 trên bo.
Chỉ tạo bộ ảnh/số liệu mới sau khi dùng cùng firmware v3 cho cả hai chế độ.
Minh chứng và log cũ không thuộc bản mã nguồn phân phối.

Để áp dụng: thoát Serial Monitor đang giữ cổng, nạp build-perf với sdkconfig.perf,
khởi động lại Flask. Thu thử trước một lô nhỏ ở cả hai chế độ, xem stack_status.
Nếu AES tắt chủ yếu untouched, kết quả là dưới ngưỡng quan sát của bộ dò, không
phải RAM bằng 0. Có thể báo cáo heap; chưa kết luận chênh stack hoặc tổng RAM.
Phép đo stack hiện tại vẫn cần hiệu chuẩn riêng trước kết luận RAM của AES.

Kế hoạch năng lượng giữ nguyên MQTT→ACK, cửa sổ và INA219:
- Chốt trước số cặp, ví dụ 5 cặp x 100 chu kỳ/đợt; đảo thứ tự giữa các cặp.
- Cùng firmware, nguồn, tải, vị trí Wi-Fi; không tải file, build hay thực hiện
  công việc nặng khác trên máy chủ trong phiên đo. Không đo thêm chỉ để có CI
  không chứa 0. Không loại đợt hợp lệ chỉ vì năng lượng cao hoặc chênh âm.
- Giữ tiêu chí chất lượng hiện có và ghi các đợt lỗi; thống kê chênh ghép cặp.
- Báo cáo N cặp, mean/SD/CI, năng lượng, thời lượng và công suất cùng nhau.
- Nếu CI vẫn chứa 0, kết luận chưa phân biệt được hai chế độ với thiết lập này.
  Đó là kết quả hợp lệ, không phải lỗi cần sửa cho ra chênh lệch dương.
