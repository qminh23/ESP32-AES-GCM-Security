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

