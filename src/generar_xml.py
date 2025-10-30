import argparse, json, xml.dom.minidom as minidom
from xml.etree import ElementTree as ET

def prettify(elem):
    rough = ET.tostring(elem, encoding="utf-8")
    return minidom.parseString(rough).toprettyxml(indent="  ", encoding="utf-8")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--json", required=True)
    p.add_argument("--xml", required=True)
    args = p.parse_args()

    with open(args.json, "r", encoding="utf-8") as f:
        data = json.load(f)

    meta = data["meta"]; presup = data["presupuestos"]
    root = ET.Element("gastos", attrib={
        "version": "1.0",
        "moneda": meta.get("moneda", "USD"),
        "propietario": meta.get("propietario", "N/D"),
        "id_estudiante": str(meta.get("id_estudiante", "")),
    })

    mes = ET.SubElement(root, "mes", attrib={
        "anio": str(meta["anio"]),
        "numero": f"{int(meta['mes']):02d}",
        "presupuesto_mensual": str(meta.get("presupuesto_mensual", 0))
    })

    xpres = ET.SubElement(mes, "presupuestos")
    for nombre, limite in presup.items():
        ET.SubElement(xpres, "categoria", attrib={"nombre": nombre, "limite": str(limite)})

    xing = ET.SubElement(mes, "ingresos")
    for i, r in enumerate(data.get("ingresos", []), start=1):
        xi = ET.SubElement(xing, "ingreso", attrib={"id": f"i{i}", "fecha": r["fecha"], "fuente": r.get("fuente","")})
        ET.SubElement(xi, "monto").text = f"{float(r['monto']):.2f}"

    xeg = ET.SubElement(mes, "egresos")
    for j, r in enumerate(data.get("egresos", []), start=1):
        xe = ET.SubElement(xeg, "egreso", attrib={"id": f"e{j}", "fecha": r["fecha"], "categoria": r["categoria"]})
        ET.SubElement(xe, "descripcion").text = r.get("descripcion", "")
        ET.SubElement(xe, "monto").text = f"{float(r['monto']):.2f}"

    xml_bytes = prettify(root)
    with open(args.xml, "wb") as f:
        f.write(xml_bytes)

if __name__ == "__main__":
    main()
