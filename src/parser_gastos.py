import argparse, json, os
from collections import defaultdict
from xml.etree import ElementTree as ET

def parse(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    mes = root.find("mes")
    moneda = root.get("moneda", "USD")

    # presupuestos
    presup_cat = {c.get("nombre"): float(c.get("limite", "0"))
                  for c in mes.find("presupuestos").iterfind("categoria")}

    # ingresos
    total_ingresos = 0.0
    for ing in mes.find("ingresos").iterfind("ingreso"):
        total_ingresos += float(ing.findtext("monto", "0"))

    # egresos
    por_categoria = defaultdict(float)
    total_egresos = 0.0
    for e in mes.find("egresos").iterfind("egreso"):
        cat = e.get("categoria", "Otros")
        monto = float(e.findtext("monto", "0"))
        por_categoria[cat] += monto
        total_egresos += monto

    # alertas
    alertas = []
    for cat, limite in presup_cat.items():
        gastado = por_categoria.get(cat, 0.0)
        if gastado > limite:
            alertas.append({"categoria": cat, "estado": "excedido",
                            "detalle": f"{gastado:.2f}/{limite:.2f} {moneda}"})
        else:
            alertas.append({"categoria": cat, "estado": "ok",
                            "detalle": f"{gastado:.2f}/{limite:.2f} {moneda}"})

    saldo = total_ingresos - total_egresos
    return {
        "moneda": moneda,
        "ingresos": round(total_ingresos, 2),
        "egresos": round(total_egresos, 2),
        "saldo": round(saldo, 2),
        "por_categoria": {k: round(v, 2) for k, v in por_categoria.items()},
        "presupuestos": presup_cat,
        "alertas": alertas
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--xml", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    resumen = parse(args.xml)
    with open(os.path.join(args.out, "resumen.json"), "w", encoding="utf-8") as f:
        json.dump(resumen, f, ensure_ascii=False, indent=2)
    print("OK - resumen guardado en", os.path.join(args.out, "resumen.json"))

if __name__ == "__main__":
    main()
