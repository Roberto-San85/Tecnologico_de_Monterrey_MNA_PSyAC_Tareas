#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Tuple, Any


def cargar_catalogo(ruta_catalogo: str) -> Dict[str, float]:
    """Carga el catálogo con formato:
    [
      { "title": "Brown eggs", "price": 28.1, ... }
    ]
    Retorna: { "brown eggs": 28.1 }
    """
    try:
        with open(ruta_catalogo, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as exc:
        print(f"[ERROR] No se pudo leer el catálogo: {exc}")
        sys.exit(1)

    catalogo: Dict[str, float] = {}
    errores = 0

    if not isinstance(data, list):
        print("[ERROR] El catálogo debe ser una lista.")
        sys.exit(1)

    for idx, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            print(f"[WARN] Fila {idx}: no es un objeto JSON.")
            errores += 1
            continue

        nombre = item.get("title")
        precio = item.get("price")

        if not isinstance(nombre, str) or not nombre.strip():
            print(f"[WARN] Fila {idx}: 'title' inválido.")
            errores += 1
            continue

        if not isinstance(precio, (int, float)) or precio < 0:
            print(f"[WARN] Fila {idx}: 'price' inválido.")
            errores += 1
            continue

        catalogo[nombre.strip().lower()] = float(precio)

    if not catalogo:
        print("[ERROR] El catálogo está vacío.")
        sys.exit(1)

    return catalogo


def validar_fecha(fecha_txt: Any) -> Tuple[bool, str]:
    """Valida 'dd/mm/yy'."""
    if not isinstance(fecha_txt, str):
        return False, "Fecha no válida"
    try:
        fecha = datetime.strptime(fecha_txt.strip(), "%d/%m/%y")
        return True, fecha.strftime("%Y-%m-%d")
    except Exception:
        return False, "Formato de fecha inválido (dd/mm/yy)"


def procesar_ventas(
    ruta_ventas: str,
    catalogo: Dict[str, float]
) -> Tuple[float, int, int, List[str]]:
    """Lee el registro de ventas y calcula el total.
    Ahora Quantity puede ser NEGATIVO.
    """

    try:
        with open(ruta_ventas, "r", encoding="utf-8") as f:
            ventas = json.load(f)
    except Exception as exc:
        print(f"[ERROR] No se pudo leer el archivo de ventas: {exc}")
        sys.exit(1)

    if not isinstance(ventas, list):
        print("[ERROR] El registro de ventas debe ser una lista.")
        sys.exit(1)

    total = 0.0
    procesadas = 0
    validas = 0
    mensajes: List[str] = []

    for idx, venta in enumerate(ventas, start=1):
        procesadas += 1

        if not isinstance(venta, dict):
            mensajes.append(f"[WARN] Venta {idx}: no es un JSON válido.")
            continue

        sale_id = venta.get("SALE_ID", "?")
        sale_date = venta.get("SALE_Date")
        product = venta.get("Product")
        quantity = venta.get("Quantity")

        # Fecha
        fecha_ok, fecha_msg = validar_fecha(sale_date)
        if not fecha_ok:
            mensajes.append(f"[WARN] Venta {idx} (ID {sale_id}): {fecha_msg}")

        # Producto
        if not isinstance(product, str) or not product.strip():
            mensajes.append(f"[WARN] Venta {idx} (ID {sale_id}): product inválido.")
            continue

        clave = product.strip().lower()

        if clave not in catalogo:
            mensajes.append(
                f"[WARN] Venta {idx} (ID {sale_id}): '{product}' no está en el catálogo."
            )
            continue

        # Cantidad → AHORA SE ACEPTAN NEGATIVOS
        if not isinstance(quantity, (int, float)) or int(quantity) != quantity:
            mensajes.append(
                f"[WARN] Venta {idx} (ID {sale_id}): quantity debe ser entero."
            )
            continue

        quantity = int(quantity)  # Puede ser negativo

        precio = catalogo[clave]
        subtotal = quantity * precio
        total += subtotal
        validas += 1

    return total, procesadas, validas, mensajes


def escribir_resultados(
    total: float,
    procesadas: int,
    validas: int,
    mensajes: List[str],
    segundos: float
) -> None:

    resumen = [
        "==== Resultados de Cómputo de Ventas ====",
        f"Ventas leídas: {procesadas}",
        f"Ventas válidas: {validas}",
        f"Registros con avisos/errores: {len(mensajes)}",
        f"Costo total: {total:,.2f}",
        f"Tiempo de ejecución (segundos): {segundos:.6f}"
    ]

    # Consola
    print("\n".join(resumen))
    if mensajes:
        print("\n---- Avisos / Errores ----")
        for m in mensajes:
            print(m)

    # Archivo
    with open("SalesResults.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(resumen))
        if mensajes:
            f.write("\n\n---- Avisos / Errores ----\n")
            for m in mensajes:
                f.write(m + "\n")

    print("\n[INFO] Archivo SalesResults.txt generado correctamente.")


def main():
    parser = argparse.ArgumentParser(
        description="Calcula el costo total de ventas."
    )
    parser.add_argument("price_catalogue")
    parser.add_argument("sales_record")
    args = parser.parse_args()

    inicio = time.perf_counter()

    catalogo = cargar_catalogo(args.price_catalogue)
    total, procesadas, validas, mensajes = procesar_ventas(
        args.sales_record,
        catalogo
    )

    fin = time.perf_counter()
    escribir_resultados(total, procesadas, validas, mensajes, fin - inicio)


if __name__ == "__main__":
    main()