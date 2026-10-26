from pathlib import Path
from PIL import Image
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

root=Path(__file__).resolve().parents[2]
images=root/'output'/'diagrams'
out=root/'output'/'docx'/'Bo_5_so_do_ESP32_AES_GCM.docx'
figures=[
('01_kien_truc_tong_the.png','Ảnh 1. Sơ đồ kiến trúc tổng thể hệ thống'),
('02_luong_lenh_ack_mqtt.png','Ảnh 2. Sơ đồ luồng gửi lệnh và nhận ACK qua MQTT'),
('03_cau_truc_goi_tin_aes_gcm.png','Ảnh 3. Sơ đồ cấu trúc gói tin AES-GCM'),
('04_luu_do_ma_hoa_giai_ma_aes_gcm.png','Ảnh 4. Lưu đồ mã hóa và giải mã AES-GCM'),
('05_luu_do_xu_ly_lenh_esp32.png','Ảnh 5. Lưu đồ xử lý lệnh trên ESP32'),
]
doc=Document()
sec=doc.sections[0]
sec.page_width=Cm(21); sec.page_height=Cm(29.7)
sec.top_margin=sec.bottom_margin=Cm(2)
sec.left_margin=sec.right_margin=Cm(2)
sec.header_distance=sec.footer_distance=Cm(.8)
for name in ['Normal','Caption','Title']:
    style=doc.styles[name]
    style.font.name='Times New Roman'
    style.font.size=Pt(12)
    style.font.color.rgb=RGBColor(0,0,0)
    style.font.italic=False
    style.paragraph_format.space_before=Pt(0)
    style.paragraph_format.space_after=Pt(0)
    style.paragraph_format.line_spacing=1
    rpr=style.element.get_or_add_rPr()
    fonts=rpr.find(qn('w:rFonts'))
    if fonts is not None:
        for key in ('ascii','hAnsi','eastAsia','cs'): fonts.set(qn('w:'+key),'Times New Roman')
caption_style=doc.styles['Caption']
caption_style.paragraph_format.space_before=Pt(8)
caption_style.paragraph_format.keep_together=True
# Preserve original high-resolution figures inside the DOCX package.
compress=OxmlElement('w:doNotAutoCompressPictures')
doc.settings.element.append(compress)
for idx,(filename,caption) in enumerate(figures):
    p=doc.add_paragraph()
    p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next=True
    p.paragraph_format.page_break_before=idx>0
    p.paragraph_format.line_spacing=1
    path=images/filename
    with Image.open(path) as im: w,h=im.size
    width_cm=min(17,23.8*w/h)
    pic=p.add_run().add_picture(str(path),width=Cm(width_cm))
    pic._inline.docPr.set('descr',caption)
    pic._inline.docPr.set('title',caption)
    cap=doc.add_paragraph(style='Caption')
    cap.alignment=WD_ALIGN_PARAGRAPH.CENTER
    number,title=caption.split('. ',1)
    cap.add_run(number+'. ').bold=True
    cap.add_run(title)
props=doc.core_properties
props.title='Bộ sơ đồ hệ thống ESP32 AES GCM'
props.subject='Năm sơ đồ đen trắng phục vụ báo cáo'
props.author=''
props.keywords='ESP32, AES-GCM, MQTT, sơ đồ'
props.comments=''
doc.save(out)
print(out)
