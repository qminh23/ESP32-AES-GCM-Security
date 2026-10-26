"""Create monochrome, report-ready figures from the repository implementation.
Run with Python + reportlab; render PNG using pdftoppm.
All drawing coordinates are specified from the top-left for maintainability.
"""
from pathlib import Path
from math import atan2, cos, sin, pi
from reportlab.graphics.shapes import Drawing, Group, Rect, Line, String, Polygon, PolyLine
from reportlab.graphics import renderPDF, renderSVG
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output'/'diagrams'
PDF=ROOT/'output'/'pdf'
FONT=Path('/System/Library/Fonts/Supplemental')
pdfmetrics.registerFont(TTFont('ReportArial',str(FONT/'Arial.ttf')))
pdfmetrics.registerFont(TTFont('ReportArialBold',str(FONT/'Arial Bold.ttf')))
BLACK=colors.black
WHITE=colors.white

class Figure:
    def __init__(self,w,h):
        self.w,self.h=w,h
        self.d=Drawing(w,h)
        self.rect(0,0,w,h,stroke=False)
    def rect(self,x,y,w,h,dash=None,stroke=True,lw=1):
        self.d.add(Rect(x,self.h-y-h,w,h,fillColor=WHITE,
                       strokeColor=BLACK if stroke else None,strokeWidth=lw,
                       strokeDashArray=dash))
    def text(self,x,y,s,size=11,bold=False,anchor='middle'):
        self.d.add(String(x,self.h-y,s,fontName='ReportArialBold' if bold else 'ReportArial',
                          fontSize=size,fillColor=BLACK,textAnchor=anchor))
    def lines(self,x,y,rows,size=11,leading=16,bold_first=False):
        for i,s in enumerate(rows): self.text(x,y+i*leading,s,size,bold_first and i==0)
    def line(self,x1,y1,x2,y2,dash=None,lw=1):
        self.d.add(Line(x1,self.h-y1,x2,self.h-y2,strokeColor=BLACK,strokeWidth=lw,strokeDashArray=dash))
    def arrow(self,pts,dash=None,both=False,lw=1.15):
        flat=[]
        for x,y in pts: flat.extend([x,self.h-y])
        self.d.add(PolyLine(flat,strokeColor=BLACK,strokeWidth=lw,fillColor=None,strokeDashArray=dash))
        def head(a,b):
            theta=atan2(b[1]-a[1],b[0]-a[0]); length=6; half=2.65
            bx,by=b[0]-length*cos(theta),b[1]-length*sin(theta)
            points=[b[0],self.h-b[1],bx+half*sin(theta),self.h-(by-half*cos(theta)),bx-half*sin(theta),self.h-(by+half*cos(theta))]
            self.d.add(Polygon(points,fillColor=BLACK,strokeColor=BLACK,strokeWidth=.4))
        head(pts[-2],pts[-1])
        if both: head(pts[1],pts[0])
    def box(self,x,y,w,h,rows,size=11,leading=16,title=True):
        self.rect(x,y,w,h)
        start=y+(h-(len(rows)-1)*leading)/2+size*.34
        self.lines(x+w/2,start,rows,size,leading,title)
    def trim(self,top=0,bottom=0):
        content=Group(*self.d.contents[1:])
        content.translate(0,-bottom)
        self.h-=top+bottom
        self.d=Drawing(self.w,self.h)
        self.rect(0,0,self.w,self.h,stroke=False)
        self.d.add(content)
    def save(self,name):
        renderPDF.drawToFile(self.d,str(OUT/(name+'.pdf')))
        renderSVG.drawToFile(self.d,str(OUT/(name+'.svg')))
        # Standard family names keep text editable in Word/Inkscape/browser SVG viewers.
        p=OUT/(name+'.svg')
        svg=p.read_text().replace('font-family: ReportArialBold;', 'font-family: Arial; font-weight: bold;').replace('font-family: ReportArial;', 'font-family: Arial;')
        p.write_text(svg)

# Figure 1: hierarchy follows the physical/software layers; only logical links shown.
a=Figure(540,744)
a.rect(12,49,516,141,dash=[5,3])
a.text(28,68,'MÁY TÍNH ĐIỀU KHIỂN VÀ GIÁM SÁT',10,True,'start')
a.box(26,101,111,60,['Trình duyệt','Dashboard Web'],10.5,17)
a.box(180,84,190,92,['Máy chủ Python','Flask / MQTT client','Mã hóa AES-128-GCM','Xử lý ACK và số đo'],11,17)
a.box(413,101,101,60,['SQLite','Lịch sử, số đo'],10.5,17)
a.arrow([(137,132),(180,132)],both=True)
a.text(158.5,121,'HTTP',9)
a.arrow([(370,132),(413,132)],both=True)
a.text(391.5,121,'SQL',9)
# Data paths use separate parallel arrows to distinguish commands from reports.
a.arrow([(241,176),(241,262)])
a.arrow([(299,262),(299,176)],dash=[5,3])
a.text(222,219,'Lệnh',10,anchor='end')
a.text(316,215,'ACK / trạng thái',10,anchor='start')
a.text(316,230,'và số đo',10,anchor='start')
a.box(155,262,230,66,['MQTT BROKER','Định tuyến bản tin theo topic','MQTT qua TLS (cổng 8883)'],11,17)
a.arrow([(241,328),(241,408)])
a.arrow([(299,408),(299,328)],dash=[5,3])
a.text(222,371,'Lệnh',10,anchor='end')
a.text(316,367,'ACK / trạng thái',10,anchor='start')
a.text(316,382,'và số đo',10,anchor='start')
a.rect(65,408,410,132,lw=1.25)
a.text(270,431,'THIẾT BỊ ESP32 / ESP-IDF',12,True)
a.line(65,444,475,444)
a.lines(270,465,['Wi-Fi / MQTT qua TLS','Xác thực, giải mã lệnh / hàng đợi / điều khiển GPIO','Thu thập số đo thời gian, bộ nhớ và năng lượng'],10.8,22)
# Peripheral links are logical data/control connections, not power wiring.
a.box(18,615,161,62,['CẢM BIẾN INA219','Điện áp / dòng / công suất'],10.5,18)
a.box(229,615,104,62,['RELAY','Đóng / ngắt'],10.5,18)
a.box(390,615,132,62,['KHÓA ĐIỆN','Solenoid 12 V'],10.5,18)
a.arrow([(98.5,615),(98.5,540)])
a.text(111,573,'I2C',10,anchor='start')
a.text(111,588,'GPIO25 / GPIO26',9.5,anchor='start')
a.arrow([(281,540),(281,615)])
a.text(293,582,'GPIO18',10,anchor='start')
a.arrow([(333,646),(390,646)])
a.text(361.5,635,'Tiếp điểm',9)
a.line(18,699,522,699,lw=.7)
a.arrow([(22,714),(49,714)])
a.text(57,717,'Lệnh / điều khiển / dữ liệu cảm biến',9,anchor='start')
a.arrow([(308,714),(335,714)],dash=[5,3])
a.text(343,717,'ACK / trạng thái / số đo',9,anchor='start')
a.text(270,737,'INA219 đo nhánh nguồn bo ESP32; khóa dùng nguồn 12 V riêng.',9.5)
a.trim(top=39)
a.save('01_kien_truc_tong_the')

# Figure 2: application-level ACK, not the MQTT protocol PUBACK.
b=Figure(560,856)
xs=[95,280,465]
for x in xs: b.line(x,117,x,686,dash=[4,4],lw=.7)
b.box(16,71,158,46,['DASHBOARD','Python / Flask'],11,17)
b.box(210,71,140,46,['MQTT BROKER','Định tuyến bản tin'],11,17)
b.box(386,71,158,46,['ESP32','Firmware ESP-IDF'],11,17)
b.box(16,151,158,95,['Chuẩn bị lệnh','Tạo command_id','ON/OFF + mã lệnh','Mã hóa AES-GCM (nếu bật)','Đăng ký lệnh chờ'],10.6,16)
b.arrow([(95,289),(280,289)])
b.text(187.5,262,'1. Gửi lệnh (control)',10.5,True)
b.text(187.5,277,'QoS 0; retain=false',10)
b.arrow([(280,332),(465,332)])
b.text(372.5,320,'2. Chuyển tiếp lệnh',10.5,True)
b.box(386,359,158,112,['3. Xử lý và thực thi','AES bật: giải mã, xác thực','AES bật: kiểm tra timestamp','Kiểm tra cấu trúc lệnh','Đưa vào hàng đợi','Cập nhật GPIO18'],10.4,16)
b.arrow([(465,527),(280,527)],dash=[5,3])
b.text(372.5,500,'4. Gửi ACK (status)',10.5,True)
b.text(372.5,515,'JSON; QoS 1; retain=false',10)
b.arrow([(280,574),(95,574)],dash=[5,3])
b.text(187.5,562,'5. Chuyển tiếp ACK',10.5,True)
b.box(16,601,222,85,['6. Đối chiếu và cập nhật','Khớp command_id, lệnh và chế độ','phase="applied"; trạng thái khớp','Lưu SQLite; cập nhật dashboard'],10.5,17)
b.trim(top=61,bottom=160)
b.save('02_luong_lenh_ack_mqtt')

# Two portrait A4 pages, each with a figure at a comfortable report insertion width.
c=canvas.Canvas(str(PDF/'so_do_he_thong_A4.pdf'),pagesize=A4)
c.setTitle('Sơ đồ kiến trúc và luồng lệnh MQTT - ESP32 AES-GCM')
c.setAuthor('ESP32 AES-GCM Security')
for fig in [a,b]:
    scale=min(475/fig.w,744/fig.h)
    x=(A4[0]-fig.w*scale)/2
    y=A4[1]-35-fig.h*scale
    c.saveState(); c.translate(x,y); c.scale(scale,scale)
    renderPDF.draw(fig.d,c,0,0); c.restoreState()
    c.showPage()
c.save()
print('Created two SVG/PDF figures and the two-page A4 PDF.')
