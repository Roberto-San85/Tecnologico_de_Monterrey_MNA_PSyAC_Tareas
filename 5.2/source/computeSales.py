#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""
Script de línea de comandos para calcular el costo total de ventas.

Entrada:
1) Catálogo JSON con `title` (nombre) y `price` (>= 0).
2) Ventas JSON con `SALE_ID`, `SALE_Date` (dd/mm/yy),
   `Product` (nombre) y `Quantity` (entero, puede ser negativo).

Características:
- Acepta cantidades negativas (devoluciones o ajustes).
- Reporta errores sin detener la ejecución.
- Imprime un resumen y lo guarda en `SalesResults.txt`.
- Incluye tiempo total de ejecución.
- Búsqueda de producto sin sensibilidad a mayúsculas.

Uso:
    python computeSales.py priceCatalogue.json salesRecord.json
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime
from typing import Any, Dict, List, Tuple


def _leer_json_lista(ruta: str) -> List[Any]:
    """
    Lee un archivo JSON que debe contener una lista.

    Args:
        ruta: Ruta del archivo JSON.

    Returns:
        La lista cargada desde el JSON.

    Raises:
        SystemExit: Si el archivo no existe, si no es JSON válido
        o si el contenido no es una lista.
    """
    try:
        with open(ruta, "r", encoding="utf-8") as fobj:
            data = json.load(fobj)
    except FileNotFoundError as exc:
        print(f"[ERROR] No se encontró el archivo: {ruta} ({exc})")
        raise SystemExit(1) from exc
    except json.JSONDecodeError as exc:
        print(f"[ERROR] El archivo no es JSON válido: {ruta} ({exc})")
        raise SystemExit(1) from exc
    except OSError as exc:
        print(f"[ERROR] No se pudo abrir el archivo: {ruta} ({exc})")
        raise SystemExit(1) from exc

    if not isinstance(data, list):
        print(f"[ERROR] El contenido de {ruta} debe ser una lista JSON.")
        raise SystemExit(1)

    return data


def cargar_catalogo(ruta_catalogo: str) -> Dict[str, float]:
    """
    Carga el catálogo con formato:
    [{ "title": "Brown eggs", "price": 28.1, ... }]

    La clave del diccionario se normaliza a minúsculas.

    Args:
        ruta_catalogo: Ruta del archivo JSON.

    Returns:
        Diccionario { nombre_producto_lower: precio }.

    Raises:
        SystemExit: Si no se obtiene al menos un producto válido.
    """
    data = _leer_json_lista(ruta_catalogo)

    catalogo: Dict[str, float] = {}
    avisos = 0

    for idx, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            print(f"[WARN] Catálogo fila {idx}: no es objeto JSON. Se omite.")
            avisos += 1
            continue

        title = item.get("title")
        price = item.get("price")

        if not isinstance(title, str) or not title.strip():
            print(f"[WARN] Catálogo fila {idx}: 'title' inválido. Se omite.")
            avisos += 1
            continue

        if not isinstance(price, (int, float)) or price < 0:
            print(f"[WARN] Catálogo fila {idx}: 'price' inválido (>= 0). Se omite.")
            avisos += 1
            continue

        catalogo[title.strip().lower()] = float(price)

    if not catalogo:
        print("[ERROR] El catálogo no contiene productos válidos.")
        raise SystemExit(1)

    if avisos:
        msg = "[INFO] Catálogo cargado con "
        msg += f"{avisos} aviso(s). Productos válidos: {len(catalogo)}"
        print(msg)

    return catalogo


def validar_fecha_ddmmyy(fecha_txt: Any) -> Tuple[bool, str]:
    """
    Valida una fecha con formato 'dd/mm/yy'.

    Args:
        fecha_txt: Texto de fecha.

    Returns:
        (ok, valor):
          - ok = True y valor = 'YYYY-MM-DD' si es válida.
          - ok = False y valor = mensaje de error si no es válida.
    """
    if not isinstance(fecha_txt, str):
        return False, "Fecha no es texto"
    try:
        dt = datetime.strptime(fecha_txt.strip(), "%d/%m/%y")
        return True, dt.strftime("%Y-%m-%d")
    except ValueError:
        return False, "Formato de fecha inválido (esperado dd/mm/yy)"


def _subtotal_venta(
    venta: Dict[str, Any],
    catalogo: Dict[str, float]
) -> Tuple[bool, float, List[str]]:
    """
    Calcula el subtotal de una venta si es válida.

    Reglas:
    - `Product` debe existir en el catálogo (case-insensitive).
    - `Quantity` debe ser entero (puede ser negativo).
    - La fecha se valida, pero su error no bloquea.

    Returns:
        (valida, subtotal, avisos).
    """
    avisos: List[str] = []

    if not isinstance(venta, dict):
        return False, 0.0, ["Venta inválida: no es objeto JSON"]

    sale_id = venta.get("SALE_ID", "?")
    sale_date = venta.get("SALE_Date")
    product = venta.get("Product")
    quantity = venta.get("Quantity")

    ok_fecha, msg_fecha = validar_fecha_ddmmyy(sale_date)
    if not ok_fecha:
        avisos.append(f"[WARN] Venta (ID {sale_id}): {msg_fecha}")

    if not isinstance(product, str) or not product.strip():
        avisos.append(f"[WARN] Venta (ID {sale_id}): 'Product' inválido.")
        return False, 0.0, avisos

    key = product.strip().lower()
    if key not in catalogo:
        msg = f"[WARN] Venta (ID {sale_id}): "
        msg += f"producto '{product}' no está en el catálogo. Se omite."
        avisos.append(msg)
        return False, 0.0, avisos

    if not isinstance(quantity, (int, float)) or int(quantity) != quantity:
        avisos.append(
            f"[WARN] Venta (ID {sale_id}): 'Quantity' debe ser entero."
        )
        return False, 0.0, avisos

    qty = int(quantity)
    price = catalogo[key]
    return True, float(qty * price), avisos


def procesar_ventas(
    ruta_ventas: str,
    catalogo: Dict[str, float]
) -> Tuple[float, int, int, List[str]]:
    """
    Procesa el archivo de ventas y acumula el total.

    Args:
        ruta_ventas: Ruta al JSON de ventas.
        catalogo: Diccionario { producto_lower: precio }.

    Returns:
        total, procesadas, validas, mensajes.
    """
    data = _leer_json_lista(ruta_ventas)

    total = 0.0
    procesadas = 0
    validas = 0
    mensajes: List[str] = []

    for venta in data:
        procesadas += 1
        ok, subtotal, avisos = _subtotal_venta(venta, catalogo)
        mensajes.extend(avisos)
        if ok:
            total += subtotal
            validas += 1

    return total, procesadas, validas, mensajes


def escribir_resultados(
    total: float,
    procesadas: int,
    validas: int,
    mensajes: List[str],
    segundos: float,
    ruta_salida: str = "SalesResults.txt",
) -> None:
    """
    Escribe e imprime el resumen de resultados.

    Args:
        total: Total acumulado (puede ser negativo).
        procesadas: Registros leídos.
        validas: Ventas válidas.
        mensajes: Avisos/errores.
        segundos: Tiempo de ejecución.
        ruta_salida: Archivo de salida.
    """
    resumen = [
        "==== Resultados de Cómputo de Ventas ====",
        f"Ventas leídas (total): {procesadas}",
        f"Ventas válidas procesadas: {validas}",
        f"Ventas con avisos/errores: {len(mensajes)}",
        f"Costo total acumulado: {total:,.2f}",
        f"Tiempo de ejecución (segundos): {segundos:.6f}",
    ]

    print("\n".join(resumen))
    if mensajes:
        print("\n---- Avisos / Errores detectados ----")
        for aviso in mensajes:
            print(aviso)

    try:
        with open(ruta_salida, "w", encoding="utf-8") as fout:
            fout.write("\n".join(resumen))
            if mensajes:
                fout.write("\n\n---- Avisos / Errores detectados ----\n")
                for aviso in mensajes:
                    fout.write(aviso + "\n")
        print(f"\n[INFO] Resultados escritos en: {ruta_salida}")
    except OSError as exc:
        print(f"[ERROR] No fue posible escribir {ruta_salida}: {exc}")


def _parse_args() -> argparse.Namespace:
    """
    Define y parsea los argumentos de la línea de comandos.

    Returns:
        Namespace con `price_catalogue` y `sales_record`.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Calcula el costo total de ventas a partir de un catálogo y un "
            "registro de ventas."
        )
    )
    parser.add_argument(
        "price_catalogue",
        help=(
            "Ruta al archivo JSON del catálogo de precios "
            "(priceCatalogue.json)"
        ),
    )
    parser.add_argument(
        "sales_record",
        help=(
            "Ruta al archivo JSON del registro de ventas "
            "(salesRecord.json)"
        ),
    )
    return parser.parse_args()


def main() -> None:
    """
    Punto de entrada principal del programa.
    """
    args = _parse_args()
    inicio = time.perf_counter()

    catalogo = cargar_catalogo(args.price_catalogue)
    total, procesadas, validas, mensajes = procesar_ventas(
        args.sales_record,
        catalogo,
    )

    fin = time.perf_counter()
    escribir_resultados(
        total=total,
        procesadas=procesadas,
        validas=validas,
        mensajes=mensajes,
        segundos=fin - inicio,
        ruta_salida="SalesResults.txt",
    )


if __name__ == "__main__":
    main()
