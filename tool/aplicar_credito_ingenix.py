#!/usr/bin/env python3
"""Add the INGENIX credit to extracted Vamos app sources before compilation."""
from pathlib import Path
import shutil
import sys

app = Path(sys.argv[1])
profile = app / "lib/screens/profile/profile_screen.dart"
text = profile.read_text(encoding="utf-8")
import_line = "import '../../widgets/ingenix_credit.dart';"
if import_line not in text:
    text = import_line + "\n" + text
if "const IngenixCredit()," not in text:
    anchor = "Widget content(BuildContext context) => ListView("
    start = text.find(anchor)
    if start < 0:
        raise SystemExit("No se encontró la pantalla Perfil. Revisar antes de compilar.")
    children = text.find("children: [", start)
    if children < 0:
        raise SystemExit("No se encontró la lista de Perfil.")
    position = children + len("children: [")
    text = text[:position] + "\n      const IngenixCredit()," + text[position:]
widget = app / "lib/widgets/ingenix_credit.dart"
widget.parent.mkdir(parents=True, exist_ok=True)
shutil.copyfile(Path(__file__).with_name("ingenix_credit.dart"), widget)
profile.write_text(text, encoding="utf-8")
print("Crédito INGENIX agregado en Perfil.")
