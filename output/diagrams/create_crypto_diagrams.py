"""Monochrome report figures for the implemented AES-enabled control payload.
Sources: main/web_server.py:encrypt_payload; main/crypto_app.c:process_control_payload;
main/mqtt_app.c:receive_message, dispatch_payload. No change to firmware/runtime.
"""
from diagram_primitives import Figure, BLACK, WHITE, OUT, PDF, A4, canvas, renderPDF
from reportlab.graphics.shapes import Rect, Polygon

class FlowFigure(Figure):
    def terminal(self,x,y,w,h,s):
        self.d.add(Rect(x,self.h-y-h,w,h,rx=h/2,ry=h/2,
                        fillColor=WHITE,strokeColor=BLACK,strokeWidth=1))
        self.text(x+w/2,y+h/2+4,s,11.5)
    def diamond(self,x,y,w,h,rows,size=11.5):
        self.d.add(Polygon([x+w/2,self.h-y,x+w,self.h-y-h/2,
                           x+w/2,self.h-y-h,x,self.h-y-h/2],
                          fillColor=WHITE,strokeColor=BLACK,strokeWidth=1))
        start=y+h/2-(len(rows)-1)*8+size*.34
        self.lines(x+w/2,start,rows,size,16)

# Figure 3: byte offsets refer to the decoded binary packet, not the HEX text.
a=Figure(560,643)
a.text(280,22,'Payload điều khiển: device/esp32/control (AES bật)',11)
a.text(16,51,'Vị trí byte (tính từ 0)',10,anchor='start')
xs=[16,136,296,376,544]
for x,s in zip(xs,['0','12','28','36','36 + N']):
    a.text(x,75,s,10,anchor='end' if x==544 else 'start')
for x,w,rows in [(16,120,['Nonce','12 byte']),
                 (136,160,['Tag xác thực','16 byte']),
                 (296,80,['Timestamp','(AAD)','8 byte']),
                 (376,168,['Ciphertext','N byte'])]:
    a.box(x,86,w,77,rows,11,18)
# Brackets group the fixed-size header and the variable-length ciphertext.
a.line(16,174,16,182); a.line(16,182,376,182); a.line(376,174,376,182)
a.text(196,201,'Phần cố định: 36 byte',11)
a.line(385,174,385,182); a.line(385,182,544,182); a.line(544,174,544,182)
a.text(464.5,201,'N = số byte bản rõ',10)
a.arrow([(280,211),(280,242)])
a.box(44,242,472,76,['Chuỗi HEX gửi qua MQTT','HEX(Nonce | Tag | Timestamp | Ciphertext)',
                        'Độ dài: 2 × (36 + N) ký tự HEX'],12,20)
# Field meaning is kept close to the packet diagram, with no separate title/caption.
a.box(16,347,252,74,['NONCE','Sinh ngẫu nhiên cho mỗi gói','Không lặp lại với cùng khóa'],11,18)
a.box(292,347,252,74,['TAG XÁC THỰC','Kiểm tra tính toàn vẹn của','Ciphertext và AAD'],11,18)
a.box(16,439,252,74,['TIMESTAMP / AAD','Unix timestamp; uint64 little-endian','Được xác thực, không mã hóa'],11,18)
a.box(292,439,252,74,['CIPHERTEXT','Bản mã của ON/OFF và command_id','Có cùng độ dài với bản rõ'],11,18)
a.line(16,536,544,536,lw=.7)
a.text(280,557,'id16: mã lệnh gồm 16 ký tự HEX',10.5)
a.text(280,578,'ON:<id16>  →  55 byte / 110 ký tự HEX',11)
a.text(280,599,'OFF:<id16>  →  56 byte / 112 ký tự HEX',11)
a.text(280,629,'Khóa AES-128 (16 byte) được cấu hình ở hai phía, không gửi kèm gói.',10.3)
a.save('03_cau_truc_goi_tin_aes_gcm')

# Figure 4: two process columns; rejection branches share one vertical path.
b=FlowFigure(600,853)
b.text(129,23,'PHÍA MÃ HÓA / PYTHON',12.5,True)
b.text(472,23,'PHÍA GIẢI MÃ / ESP32',12.5,True)
b.terminal(59,42,140,34,'Bắt đầu')
b.terminal(376,42,192,34,'Nhận payload MQTT')
# Sender: common AES-128-GCM control path with tracked command IDs.
enc=[(105,70,['Chuẩn bị bản rõ P','ON:<id16> hoặc OFF:<id16>','Khóa K: 16 byte']),
     (212,70,['Sinh Nonce ngẫu nhiên','12 byte','Không lặp Nonce với cùng K']),
     (319,70,['Tạo Timestamp / AAD','Unix timestamp: 8 byte','Số nguyên little-endian']),
     (426,70,['Mã hóa AES-128-GCM','Đầu vào: K, Nonce, P, AAD','Đầu ra: Ciphertext và Tag']),
     (533,70,['Ghép gói nhị phân','Nonce | Tag | Timestamp | CT']),
     (640,70,['Chuyển sang chuỗi HEX','Gửi MQTT qua TLS','retain=false'])]
last=76
for y,h,rows in enc:
    b.arrow([(129,last),(129,y)])
    b.box(16,y,226,h,rows,11.7,19)
    last=y+h
b.arrow([(129,last),(129,789)])
b.terminal(59,789,140,34,'Kết thúc')
# Receiver: format/size, authenticated decryption, time policy, command syntax.
b.arrow([(472,76),(472,100)])
b.diamond(374,100,196,62,['HEX / độ dài','hợp lệ?'])
b.arrow([(472,162),(472,190)])
b.text(484,180,'Có',10,anchor='start')
b.box(362,190,220,60,['Giải mã HEX, tách các trường','Nonce, Tag, Timestamp (AAD),','Ciphertext'],11.4,17)
b.arrow([(472,250),(472,272)])
b.box(362,272,220,54,['Giải mã AES-128-GCM','và xác thực Tag bằng khóa K'],11.5,19)
b.arrow([(472,326),(472,346)])
b.diamond(374,346,196,54,['Tag hợp lệ?'])
b.arrow([(472,400),(472,428)])
b.text(484,418,'Có',10,anchor='start')
b.box(362,428,220,57,['Đọc timestamp đã xác thực','Khởi tạo giờ nếu chưa hợp lệ'],11.2,19)
b.arrow([(472,485),(472,507)])
b.diamond(374,507,196,70,['Thời gian hợp lệ?','Cửa sổ ±10 giây'],11.1)
b.arrow([(472,577),(472,608)])
b.text(484,596,'Có',10,anchor='start')
b.diamond(374,608,196,62,['Cú pháp lệnh','hợp lệ?'])
b.arrow([(472,670),(472,701)])
b.text(484,690,'Có',10,anchor='start')
b.box(362,701,220,60,['Chấp nhận bản rõ','Đưa lệnh vào hàng đợi','Xóa bộ đệm bản rõ'],11.5,17)
b.arrow([(472,761),(472,789)])
b.terminal(402,789,140,34,'Kết thúc')
# Reject incoming malformed, unauthenticated, stale or invalid control messages.
for y in [131,373,542,639]:
    b.arrow([(374,y),(315,y)])
    b.text(344.5,y-8,'Không',10)
b.line(315,131,315,765,lw=1.15)
b.arrow([(315,765),(301,765),(301,789)])
b.box(252,789,98,45,['Từ chối gói','Không thực thi'],10.3,16)
b.save('04_luu_do_ma_hoa_giai_ma_aes_gcm')

c=canvas.Canvas(str(PDF/'so_do_aes_gcm_A4.pdf'),pagesize=A4)
c.setTitle('Cấu trúc gói tin và lưu đồ AES-GCM')
c.setAuthor('ESP32 AES-GCM Security')
for fig in [a,b]:
    scale=min(475/fig.w,744/fig.h)
    x=(A4[0]-fig.w*scale)/2
    y=A4[1]-38-fig.h*scale
    c.saveState(); c.translate(x,y); c.scale(scale,scale)
    renderPDF.draw(fig.d,c,0,0); c.restoreState(); c.showPage()
c.save()
print('Created packet and cryptography diagrams, SVGs and two-page A4 PDF.')
