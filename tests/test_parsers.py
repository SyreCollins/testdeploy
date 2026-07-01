import os
import tempfile

from app.rag.parsers.csv import CsvParser
from app.rag.parsers.json import JsonParser
from app.rag.parsers.pdf import PdfParser
from app.rag.parsers.txt import TxtParser
from app.rag.parsers.xlsx import XlsxParser


def test_csv_parser_medicine_details() -> None:
    path = os.path.join(tempfile.gettempdir(), "test_med.csv")
    with open(path, "w") as f:
        f.write("Medicine Name,Composition,Uses,Side_effects,Manufacturer\n")
        f.write("Testacin,Testacin (500mg),Bacterial infections,Nausea,PharmaX\n")

    parser = CsvParser()
    sections = parser.parse(path)
    os.remove(path)

    assert len(sections) == 3
    assert sections[0]["section_path"] == "Testacin / Overview"
    assert sections[1]["section_path"] == "Testacin / Uses"
    assert sections[2]["section_path"] == "Testacin / Side Effects"
    assert sections[1]["metadata"]["chunk_type"] == "indication"


def test_csv_parser_nafdac_format() -> None:
    path = os.path.join(tempfile.gettempdir(), "test_nafdac.csv")
    with open(path, "w") as f:
        f.write("ID,name,genericname,strength,form,nafdacnumber,atccode,tags,unitsize\n")
        f.write("1,Amoxil,Amoxicillin,500mg,Tablet,04-1234,J01CA04,OTC,1x10\n")

    parser = CsvParser()
    sections = parser.parse(path)
    os.remove(path)

    assert len(sections) >= 1
    assert sections[0]["section_path"] == "Amoxil / Overview"
    assert "Amoxicillin" in sections[0]["text_content"]


def test_csv_parser_encoding_fallback() -> None:
    path = os.path.join(tempfile.gettempdir(), "test_enc.csv")
    with open(path, "w", encoding="cp1252") as f:
        f.write("Medicine Name,Composition\n")
        f.write("Test\xe9,Test (100mg)\n")

    parser = CsvParser()
    sections = parser.parse(path)
    os.remove(path)

    assert len(sections) == 1
    assert "Test\xe9" in sections[0]["text_content"]


def test_xlsx_parser_atc_format() -> None:
    import openpyxl

    path = os.path.join(tempfile.gettempdir(), "test_atc.xlsx")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Generic Name", "Generic ATC Code", "Level4 Name", "Level4 Code",
               "Level3 Name", "Level3 Code", "Level2 Name", "Level2 Code",
               "Level1 Name", "Level1 Code", "Level1 Alias"])
    ws.append(["amoxicillin", "J01CA04", "Penicillins", "J01CA",
               "Antibacterials", "J01C", "Systemic antimicro", "J01",
               "INFECTIOUS DISEASES", "J", "Infections"])
    wb.save(path)
    wb.close()

    parser = XlsxParser()
    sections = parser.parse(path)
    os.remove(path)

    assert len(sections) >= 2
    assert any("amoxicillin" in s["text_content"] for s in sections)
    assert any(s["metadata"]["chunk_type"] == "atc_entry" for s in sections)


def test_parser_auto_selection() -> None:
    from app.rag.parsers import get_parser

    pdf_path = os.path.join(tempfile.gettempdir(), "test.pdf")
    with open(pdf_path, "w") as f:
        f.write("fake pdf")
    parser = get_parser(pdf_path)
    assert isinstance(parser, PdfParser)
    os.remove(pdf_path)

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        f.write("{}")
        path = f.name
    parser = get_parser(path)
    assert isinstance(parser, JsonParser)
    os.remove(path)

    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
        f.write("a,b\n1,2")
        path = f.name
    parser = get_parser(path)
    assert isinstance(parser, CsvParser)
    os.remove(path)

    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as f:
        f.write("hello")
        path = f.name
    parser = get_parser(path)
    assert isinstance(parser, TxtParser)
    os.remove(path)

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
        path = f.name
    parser = get_parser(path)
    assert isinstance(parser, XlsxParser)
    os.remove(path)
