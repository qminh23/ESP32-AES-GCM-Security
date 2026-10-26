"""ESP32 control-command flow, separated into MQTT processing and hardware task.
Based on receive_message, process_control_payload, apply_control_text, post_item,
and control_task. Other topics (mode and energy) are outside this figure.
"""
from diagram_primitives import Figure, BLACK, WHITE
from reportlab.graphics.shapes import Rect, Polygon, Circle

class Flow(Figure):
    def terminal(self,x,y,w,h,s):
        self.d.add(Rect(x,self.h-y-h,w,h,rx=h/2,ry=h/2,fillColor=WHITE,strokeColor=BLACK,strokeWidth=1))
        self.text(x+w/2,y+h/2+4,s,12)
    def diamond(self,x,y,w,h,rows,size=12):
        self.d.add(Polygon([x+w/2,self.h-y,x+w,self.h-y-h/2,x+w/2,self.h-y-h,x,self.h-y-h/2],fillColor=WHITE,strokeColor=BLACK,strokeWidth=1))
        self.lines(x+w/2,y+h/2-(len(rows)-1)*9+size*.34,rows,size,18)
    def connector(self,x,y,s):
        self.d.add(Circle(x,self.h-y,15,fillColor=WHITE,strokeColor=BLACK,strokeWidth=1))
        self.text(x,y+4,s,12,True)

f=Flow(640,900)
f.text(170,23,'TIẾP NHẬN VÀ KIỂM TRA',13,True)
f.text(470,23,'THỰC THI VÀ PHẢN HỒI',13,True)
f.terminal(78,48,184,40,'Nhận lệnh MQTT')
f.arrow([(170,88),(170,116)])
f.box(60,116,220,70,['Topic: device/esp32/control','Kiểm tra retain và kích thước','Ghép đủ các mảnh payload'],11.7,19)
f.arrow([(170,186),(170,212)])
f.diamond(72,212,196,66,['Bản tin hợp lệ?','retain=false; 1..256 ký tự'],10.8)
f.arrow([(170,278),(170,312)])
f.text(183,300,'Có',10.5,anchor='start')
f.diamond(72,312,196,64,['AES đang bật?'])
f.arrow([(170,376),(170,416)])
f.text(183,400,'Có',10.5,anchor='start')
f.box(60,416,220,68,['Giải mã HEX / AES-GCM','Xác thực Tag','Kiểm tra timestamp ±10 s'],12,19)
f.arrow([(170,484),(170,526)])
f.diamond(72,526,196,64,['Kiểm tra đạt?'])
f.arrow([(170,590),(170,628)])
f.text(183,610,'Có',10.5,anchor='start')
# AES OFF joins the plaintext parser directly.
f.arrow([(268,344),(310,344),(310,616),(170,616)])
f.text(290,334,'Không',10.2)
f.text(305,604,'Bản rõ',10.5,anchor='end')
f.box(60,628,220,54,['Đọc lệnh ON/OFF','và command_id (nếu có)'],12,19)
f.arrow([(170,682),(170,720)])
f.diamond(72,720,196,64,['Cú pháp hợp lệ?'])
f.arrow([(170,784),(170,835)])
f.text(183,809,'Có',10.5,anchor='start')
f.connector(170,850,'A')
# Invalid packets are discarded and never enter the hardware queue.
for y in [245,558,752]:
    f.arrow([(72,y),(20,y)])
    f.text(46,y-8,'Không',10.2)
f.arrow([(20,245),(20,798),(69,798),(69,815)])
f.box(10,815,118,64,['Từ chối gói','Không thực thi','Ghi log / báo lỗi'],10.8,17)
# FreeRTOS queue -> GPIO -> application ACK.
f.connector(470,63,'A')
f.arrow([(470,78),(470,116)])
f.box(360,116,220,60,['Đưa lệnh vào hàng đợi','FreeRTOS (16 phần tử)'],12,19)
f.arrow([(470,176),(470,212)])
f.diamond(372,212,196,66,['Đưa vào hàng đợi','thành công?'])
f.arrow([(470,278),(470,312)])
f.text(483,300,'Có',10.5,anchor='start')
f.box(360,312,220,72,['Task phần cứng lấy lệnh','ON: GPIO18 = HIGH','OFF: GPIO18 = LOW'],12,19)
f.arrow([(470,384),(470,416)])
f.diamond(372,416,196,66,['Đặt GPIO','thành công?'])
f.arrow([(470,482),(470,526)])
f.text(483,508,'Có',10.5,anchor='start')
f.box(360,526,220,60,['Cập nhật trạng thái','Ghi nhận thời gian thực thi'],12,19)
f.arrow([(470,586),(470,628)])
f.box(360,628,220,82,['Gửi bản tin status','Có ID: ACK phase="applied"','Không ID: LOCKED/UNLOCKED'],11.5,20)
f.arrow([(470,710),(470,752),(405,752),(405,815)])
f.terminal(320,815,170,44,'Chờ lệnh tiếp theo')
for y in [245,449]:
    f.arrow([(568,y),(620,y)])
    f.text(594,y-8,'Không',10.2)
f.arrow([(620,245),(620,790),(570,790),(570,815)])
f.box(510,815,120,64,['Báo BUSY','Có ID: ACK','phase="rejected"'],10.5,17)
f.save('05_luu_do_xu_ly_lenh_esp32')
print('Created ESP32 flow diagram.')
