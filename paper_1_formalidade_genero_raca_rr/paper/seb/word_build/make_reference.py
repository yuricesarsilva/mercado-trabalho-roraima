"""reference.docx: A4, Times New Roman 12, entrelinhas 1,5, margens 2,5 cm."""
import os, subprocess
import pypandoc
from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

WB = os.path.dirname(os.path.abspath(__file__))
ref = os.path.join(WB, 'reference.docx')
subprocess.run([pypandoc.get_pandoc_path(), '-o', ref, '--print-default-data-file', 'reference.docx'], check=True)

d = Document(ref)
for s in d.sections:
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = s.top_margin = s.bottom_margin = Cm(2.5)

TNR = 'Times New Roman'
BLACK = RGBColor(0, 0, 0)

def font(st, size=12, bold=None, italic=None):
    st.font.name = TNR
    rpr = st.element.get_or_add_rPr()
    rf = rpr.find(qn('w:rFonts'))
    if rf is None:
        rf = rpr.makeelement(qn('w:rFonts'), {}); rpr.append(rf)
    for a in ('w:ascii', 'w:hAnsi', 'w:eastAsia', 'w:cs'):
        rf.set(qn(a), TNR)
    for a in ('w:asciiTheme', 'w:hAnsiTheme', 'w:eastAsiaTheme', 'w:cstheme'):
        if rf.get(qn(a)) is not None:
            del rf.attrib[qn(a)]
    st.font.size = Pt(size)
    st.font.color.rgb = BLACK
    if bold is not None: st.font.bold = bold
    if italic is not None: st.font.italic = italic

def para(st, align=None, spacing=1.5, before=0, after=0, first=None, hanging=None, keep=None):
    pf = st.paragraph_format
    if align is not None: pf.alignment = align
    pf.line_spacing = spacing
    pf.space_before, pf.space_after = Pt(before), Pt(after)
    if first is not None: pf.first_line_indent = first
    if hanging is not None:
        pf.left_indent = hanging; pf.first_line_indent = -hanging
    if keep is not None: pf.keep_with_next = keep

def get(name, base='Normal', kind=WD_STYLE_TYPE.PARAGRAPH):
    try:
        return d.styles[name]
    except KeyError:
        st = d.styles.add_style(name, kind)
        st.base_style = d.styles[base]
        return st

J, C = WD_ALIGN_PARAGRAPH.JUSTIFY, WD_ALIGN_PARAGRAPH.CENTER

# documento inteiro
font(d.styles['Normal']); para(d.styles['Normal'], J)
for n in ('Body Text', 'First Paragraph'):
    st = get(n); font(st); para(st, J, first=Cm(1.25))
st = get('Compact'); font(st, 10); para(st, None, spacing=1.0)

for n, sz in (('Heading 1', 12), ('Heading 2', 12), ('Heading 3', 12)):
    st = get(n); font(st, sz, bold=True, italic=False)
    para(st, WD_ALIGN_PARAGRAPH.LEFT, before=12, after=6, keep=True)

st = get('Title'); font(st, 14, bold=True); para(st, C, spacing=1.0, before=0, after=18)
st = get('Author'); font(st, 12, bold=False); para(st, C, spacing=1.0, after=0)
st = get('Cover Heading'); font(st, 12, bold=True); para(st, J, spacing=1.0, before=18, after=6, keep=True)
st = get('Cover Text'); font(st, 12); para(st, J, spacing=1.0, after=6, first=Cm(0))

st = get('Footnote Text'); font(st, 10); para(st, J, spacing=1.0)
st = get('Bibliography'); font(st, 11); para(st, WD_ALIGN_PARAGRAPH.LEFT, spacing=1.0, after=6, hanging=Cm(1.25))
for n in ('Caption', 'Image Caption', 'Table Caption'):
    st = get(n); font(st, 11, bold=False, italic=False); para(st, C, spacing=1.0, before=6, after=6)
st = get('Captioned Figure'); para(st, C, spacing=1.0, first=Cm(0))
st = get('Float Note'); font(st, 9); para(st, J, spacing=1.0, after=12, first=Cm(0))
for n in ('Hyperlink',):
    try:
        d.styles[n].font.color.rgb = BLACK
    except KeyError:
        pass

d.save(ref)
print('reference.docx ok')
