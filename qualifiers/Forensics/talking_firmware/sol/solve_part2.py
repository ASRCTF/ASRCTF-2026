import pikepdf
from pathlib import Path

pdf_path = Path(__file__).parent / "recovered.pdf"

with pikepdf.open(pdf_path) as pdf:
    for obj in pdf.objects:
        try:
            if obj.get("/Type") == pikepdf.Name("/FontDescriptor"):
                notice = obj.get("/Notice")
                if notice:
                    print(str(notice))
        except Exception:
            continue
