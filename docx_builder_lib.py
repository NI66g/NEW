# -*- coding: utf-8 -*-
"""
大學專題成果技術報告書 Word (.docx) 自動生成腳本
專案名稱：電腦周邊智慧售後退換貨與人機協同爭議風控平台
技術標準：Office Open XML (WordprocessingML) 規範，零額外外部依賴
"""

import zipfile
import html
import os
import sys

class DocxBuilder:
    def __init__(self):
        self.body_xml = []
        
    def _escape(self, text):
        return html.escape(str(text))
        
    def add_page_break(self):
        self.body_xml.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')
        
    def add_title_block(self, title, subtitle, dept, date_str, authors):
        p_title = f'''<w:p>
          <w:pPr>
            <w:jc w:val="center"/>
            <w:spacing w:before="960" w:after="240"/>
          </w:pPr>
          <w:r>
            <w:rPr>
              <w:rFonts w:ascii="Segoe UI" w:hAnsi="Segoe UI" w:eastAsia="Microsoft JhengHei"/>
              <w:b/>
              <w:sz w:val="52"/>
              <w:color w:val="1E3A8A"/>
            </w:rPr>
            <w:t>{self._escape(title)}</w:t>
          </w:r>
        </w:p>'''
        self.body_xml.append(p_title)
        
        p_sub = f'''<w:p>
          <w:pPr>
            <w:jc w:val="center"/>
            <w:spacing w:before="0" w:after="480"/>
          </w:pPr>
          <w:r>
            <w:rPr>
              <w:rFonts w:ascii="Segoe UI" w:hAnsi="Segoe UI" w:eastAsia="Microsoft JhengHei"/>
              <w:b/>
              <w:sz w:val="26"/>
              <w:color w:val="0284C7"/>
            </w:rPr>
            <w:t>{self._escape(subtitle)}</w:t>
          </w:r>
        </w:p>'''
        self.body_xml.append(p_sub)
        
        p_line = '''<w:p>
          <w:pPr>
            <w:pBdr>
              <w:bottom w:val="single" w:sz="18" w:space="12" w:color="1E3A8A"/>
            </w:pBdr>
            <w:spacing w:before="0" w:after="720"/>
          </w:pPr>
        </w:p>'''
        self.body_xml.append(p_line)
        
        meta_items = [
            ("專題類別", "資訊管理學系 / 資訊工程學系 畢業專題技術成果報告書"),
            ("系統架構", "前後台獨立雙程式架構 (買家獨立前台 + 商家管理後台)"),
            ("研發單位", dept),
            ("專題成員", authors),
            ("指導教授", "專題指導委員會"),
            ("完成日期", date_str)
        ]
        
        for label, val in meta_items:
            p_m = f'''<w:p>
              <w:pPr>
                <w:ind w:left="1440"/>
                <w:spacing w:before="80" w:after="80" w:line="320" w:lineRule="auto"/>
              </w:pPr>
              <w:r>
                <w:rPr>
                  <w:rFonts w:ascii="Segoe UI" w:hAnsi="Segoe UI" w:eastAsia="Microsoft JhengHei"/>
                  <w:b/>
                  <w:sz w:val="24"/>
                  <w:color w:val="334155"/>
                </w:rPr>
                <w:t>{self._escape(label)}：</w:t>
              </w:r>
              <w:r>
                <w:rPr>
                  <w:rFonts w:ascii="Segoe UI" w:hAnsi="Segoe UI" w:eastAsia="Microsoft JhengHei"/>
                  <w:sz w:val="24"/>
                  <w:color w:val="0F172A"/>
                </w:rPr>
                <w:t>{self._escape(val)}</w:t>
              </w:r>
            </w:p>'''
            self.body_xml.append(p_m)
            
        self.add_page_break()

    def add_heading(self, text, level=1):
        sizes = {1: "36", 2: "28", 3: "24"} # 18pt, 14pt, 12pt
        colors = {1: "1E3A8A", 2: "0369A1", 3: "1E293B"}
        befores = {1: "400", 2: "280", 3: "200"}
        afters = {1: "180", 2: "120", 3: "80"}
        
        sz = sizes.get(level, "24")
        col = colors.get(level, "1E293B")
        bf = befores.get(level, "200")
        af = afters.get(level, "80")
        
        p = f'''<w:p>
          <w:pPr>
            <w:spacing w:before="{bf}" w:after="{af}"/>
            <w:outlineLvl w:val="{level-1}"/>
          </w:pPr>
          <w:r>
            <w:rPr>
              <w:rFonts w:ascii="Segoe UI" w:hAnsi="Segoe UI" w:eastAsia="Microsoft JhengHei"/>
              <w:b/>
              <w:sz w:val="{sz}"/>
              <w:color w:val="{col}"/>
            </w:rPr>
            <w:t>{self._escape(text)}</w:t>
          </w:r>
        </w:p>'''
        self.body_xml.append(p)

    def add_paragraph(self, text, bold_prefix="", italic=False, color="1E293B", align="both", space_after=140):
        prefix_xml = ""
        if bold_prefix:
            prefix_xml = f'''<w:r>
              <w:rPr>
                <w:rFonts w:ascii="Segoe UI" w:hAnsi="Segoe UI" w:eastAsia="Microsoft JhengHei"/>
                <w:b/>
                <w:sz w:val="22"/>
                <w:color w:val="0F172A"/>
              </w:rPr>
              <w:t xml:space="preserve">{self._escape(bold_prefix)} </w:t>
            </w:r>'''
            
        italic_xml = "<w:i/>" if italic else ""
        
        p = f'''<w:p>
          <w:pPr>
            <w:jc w:val="{align}"/>
            <w:spacing w:before="40" w:after="{space_after}" w:line="380" w:lineRule="auto"/>
          </w:pPr>
          {prefix_xml}
          <w:r>
            <w:rPr>
              <w:rFonts w:ascii="Segoe UI" w:hAnsi="Segoe UI" w:eastAsia="Microsoft JhengHei"/>
              <w:sz w:val="22"/>
              {italic_xml}
              <w:color w:val="{color}"/>
            </w:rPr>
            <w:t xml:space="preserve">{self._escape(text)}</w:t>
          </w:r>
        </w:p>'''
        self.body_xml.append(p)

    def add_bullet(self, text, prefix=""):
        prefix_xml = ""
        if prefix:
            prefix_xml = f'''<w:r>
              <w:rPr>
                <w:rFonts w:ascii="Segoe UI" w:hAnsi="Segoe UI" w:eastAsia="Microsoft JhengHei"/>
                <w:b/>
                <w:sz w:val="22"/>
                <w:color w:val="0284C7"/>
              </w:rPr>
              <w:t xml:space="preserve">{self._escape(prefix)} </w:t>
            </w:r>'''
            
        p = f'''<w:p>
          <w:pPr>
            <w:ind w:left="480" w:hanging="240"/>
            <w:spacing w:before="40" w:after="90" w:line="340" w:lineRule="auto"/>
          </w:pPr>
          <w:r>
            <w:rPr>
              <w:rFonts w:ascii="Segoe UI" w:hAnsi="Segoe UI" w:eastAsia="Microsoft JhengHei"/>
              <w:b/>
              <w:color w:val="2563EB"/>
              <w:sz w:val="22"/>
            </w:rPr>
            <w:t>✦ </w:t>
          </w:r>
          {prefix_xml}
          <w:r>
            <w:rPr>
              <w:rFonts w:ascii="Segoe UI" w:hAnsi="Segoe UI" w:eastAsia="Microsoft JhengHei"/>
              <w:sz w:val="22"/>
              <w:color w:val="334155"/>
            </w:rPr>
            <w:t xml:space="preserve">{self._escape(text)}</w:t>
          </w:r>
        </w:p>'''
        self.body_xml.append(p)

    def add_callout(self, text, title="重點摘要 / 設計亮點", border_color="2563EB", bg_color="F0F9FF"):
        tbl = f'''<w:tbl>
          <w:tblPr>
            <w:tblW w:w="5000" w:type="pct"/>
            <w:tblBorders>
              <w:top w:val="none"/>
              <w:left w:val="single" w:sz="24" w:space="0" w:color="{border_color}"/>
              <w:bottom w:val="none"/>
              <w:right w:val="none"/>
              <w:insideH w:val="none"/>
              <w:insideV w:val="none"/>
            </w:tblBorders>
            <w:tblCellMar>
              <w:top w:w="160" w:type="dxa"/>
              <w:left w:w="240" w:type="dxa"/>
              <w:bottom w:w="160" w:type="dxa"/>
              <w:right w:w="240" w:type="dxa"/>
            </w:tblCellMar>
          </w:tblPr>
          <w:tr>
            <w:tc>
              <w:tcPr>
                <w:shd w:val="clear" w:color="auto" w:fill="{bg_color}"/>
              </w:tcPr>
              <w:p>
                <w:pPr><w:spacing w:before="40" w:after="80"/></w:pPr>
                <w:r>
                  <w:rPr>
                    <w:rFonts w:ascii="Segoe UI" w:hAnsi="Segoe UI" w:eastAsia="Microsoft JhengHei"/>
                    <w:b/>
                    <w:sz w:val="22"/>
                    <w:color w:val="1E3A8A"/>
                  </w:rPr>
                  <w:t>💡 {self._escape(title)}</w:t>
                </w:r>
              </w:p>
              <w:p>
                <w:pPr><w:spacing w:before="0" w:after="40" w:line="340" w:lineRule="auto"/></w:pPr>
                <w:r>
                  <w:rPr>
                    <w:rFonts w:ascii="Segoe UI" w:hAnsi="Segoe UI" w:eastAsia="Microsoft JhengHei"/>
                    <w:sz w:val="20"/>
                    <w:color w:val="1E293B"/>
                  </w:rPr>
                  <w:t>{self._escape(text)}</w:t>
                </w:r>
              </w:p>
            </w:tc>
          </w:tr>
        </w:tbl>
        <w:p><w:pPr><w:spacing w:before="0" w:after="140"/></w:pPr></w:p>'''
        self.body_xml.append(tbl)

    def add_code_block(self, code, caption="程式碼片段"):
        lines = code.strip().split('\n')
        runs = []
        for i, line in enumerate(lines):
            br = "<w:br/>" if i > 0 else ""
            runs.append(f'{br}<w:r><w:rPr><w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/><w:sz w:val="18"/><w:color w:val="0F172A"/></w:rPr><w:t xml:space="preserve">{self._escape(line)}</w:t></w:r>')
        runs_xml = "".join(runs)
        
        cap_p = f'''<w:p>
          <w:pPr><w:spacing w:before="120" w:after="40"/></w:pPr>
          <w:r>
            <w:rPr>
              <w:rFonts w:ascii="Segoe UI" w:hAnsi="Segoe UI" w:eastAsia="Microsoft JhengHei"/>
              <w:b/>
              <w:sz w:val="19"/>
              <w:color w:val="475569"/>
            </w:rPr>
            <w:t>📄 {self._escape(caption)}：</w:t>
          </w:r>
        </w:p>'''
        self.body_xml.append(cap_p)
        
        tbl = f'''<w:tbl>
          <w:tblPr>
            <w:tblW w:w="5000" w:type="pct"/>
            <w:tblBorders>
              <w:top w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
              <w:left w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
              <w:bottom w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
              <w:right w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
            </w:tblBorders>
            <w:tblCellMar>
              <w:top w:w="120" w:type="dxa"/>
              <w:left w:w="160" w:type="dxa"/>
              <w:bottom w:w="120" w:type="dxa"/>
              <w:right w:w="160" w:type="dxa"/>
            </w:tblCellMar>
          </w:tblPr>
          <w:tr>
            <w:tc>
              <w:tcPr>
                <w:shd w:val="clear" w:color="auto" w:fill="F8FAFC"/>
              </w:tcPr>
              <w:p>
                <w:pPr><w:spacing w:before="40" w:after="40" w:line="240" w:lineRule="auto"/></w:pPr>
                {runs_xml}
              </w:p>
            </w:tc>
          </w:tr>
        </w:tbl>
        <w:p><w:pPr><w:spacing w:before="0" w:after="140"/></w:pPr></w:p>'''
        self.body_xml.append(tbl)

    def add_table(self, headers, rows):
        header_cells = []
        for h in headers:
            header_cells.append(f'''<w:tc>
              <w:tcPr>
                <w:shd w:val="clear" w:color="auto" w:fill="1E3A8A"/>
              </w:tcPr>
              <w:p>
                <w:pPr><w:jc w:val="center"/><w:spacing w:before="80" w:after="80"/></w:pPr>
                <w:r>
                  <w:rPr>
                    <w:rFonts w:ascii="Segoe UI" w:hAnsi="Segoe UI" w:eastAsia="Microsoft JhengHei"/>
                    <w:b/>
                    <w:sz w:val="20"/>
                    <w:color w:val="FFFFFF"/>
                  </w:rPr>
                  <w:t>{self._escape(h)}</w:t>
                </w:r>
              </w:p>
            </w:tc>''')
        header_tr = f'''<w:tr>
          <w:trPr><w:tblHeader/></w:trPr>
          {"".join(header_cells)}
        </w:tr>'''
        
        row_trs = []
        for row_idx, row in enumerate(rows):
            bg_col = "F8FAFC" if (row_idx % 2 == 1) else "FFFFFF"
            cells = []
            for col_idx, cell in enumerate(row):
                align = "center" if col_idx == 0 or len(str(cell)) <= 6 else "left"
                cells.append(f'''<w:tc>
                  <w:tcPr>
                    <w:shd w:val="clear" w:color="auto" w:fill="{bg_col}"/>
                  </w:tcPr>
                  <w:p>
                    <w:pPr><w:jc w:val="{align}"/><w:spacing w:before="60" w:after="60"/></w:pPr>
                    <w:r>
                      <w:rPr>
                        <w:rFonts w:ascii="Segoe UI" w:hAnsi="Segoe UI" w:eastAsia="Microsoft JhengHei"/>
                        <w:sz w:val="19"/>
                        <w:color w:val="1E293B"/>
                      </w:rPr>
                      <w:t>{self._escape(cell)}</w:t>
                    </w:r>
                  </w:p>
                </w:tc>''')
            row_trs.append(f'<w:tr>{"".join(cells)}</w:tr>')
            
        tbl = f'''<w:tbl>
          <w:tblPr>
            <w:tblW w:w="5000" w:type="pct"/>
            <w:tblBorders>
              <w:top w:val="single" w:sz="8" w:space="0" w:color="94A3B8"/>
              <w:bottom w:val="single" w:sz="8" w:space="0" w:color="94A3B8"/>
              <w:left w:val="none"/>
              <w:right w:val="none"/>
              <w:insideH w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>
              <w:insideV w:val="none"/>
            </w:tblBorders>
            <w:tblCellMar>
              <w:top w:w="100" w:type="dxa"/>
              <w:left w:w="140" w:type="dxa"/>
              <w:bottom w:w="100" w:type="dxa"/>
              <w:right w:w="140" w:type="dxa"/>
            </w:tblCellMar>
          </w:tblPr>
          {header_tr}
          {"".join(row_trs)}
        </w:tbl>
        <w:p><w:pPr><w:spacing w:before="0" w:after="160"/></w:pPr></w:p>'''
        self.body_xml.append(tbl)

    def save(self, filepath):
        content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>'''

        rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>'''

        doc_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>'''

        styles_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults>
    <w:rPrDefault>
      <w:rPr>
        <w:rFonts w:ascii="Segoe UI" w:hAnsi="Segoe UI" w:eastAsia="Microsoft JhengHei" w:cs="Segoe UI"/>
        <w:sz w:val="22"/>
        <w:color w:val="1E293B"/>
      </w:rPr>
    </w:rPrDefault>
  </w:docDefaults>
</w:styles>'''

        doc_body = "".join(self.body_xml)
        doc_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <w:body>
    {doc_body}
    <w:sectPr>
      <w:pgSz w:w="11906" w:h="16838"/>
      <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="720" w:footer="720" w:gutter="0"/>
    </w:sectPr>
  </w:body>
</w:document>'''

        with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('[Content_Types].xml', content_types)
            zf.writestr('_rels/.rels', rels)
            zf.writestr('word/_rels/document.xml.rels', doc_rels)
            zf.writestr('word/styles.xml', styles_xml)
            zf.writestr('word/document.xml', doc_xml)
        print(f"[OK] Report successfully built and saved to: {filepath}")

