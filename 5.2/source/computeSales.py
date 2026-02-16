#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compute_sales.py

Programa de línea de comandos que calcula el costo total de ventas a partir de:
1) Un catálogo de productos en JSON con campos `title` (nombre) y `price` (precio >= 0).
2) Un registro de ventas en JSON con campos: `SALE_ID`, `SALE_Date` (dd/mm/yy),
   `Product` (nombre del producto) y `Quantity` (entero, puede ser negativo).

Características:
- Soporta cantidades negativas (devoluciones/ajustes).
- Maneja errores de datos sin detener la ejecución; los reporta en consola.
- Imprime un resumen en pantalla y lo guarda en `SalesResults.txt`.
- Incluye el tiempo total de ejecución.
- Comparación de productos insensible a mayúsculas/minúsculas.

Uso:
    python compute_sales.py priceCatalogue.json salesRecord.json
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
    Carga el catálogo de precios con formato:
    [
      { "title": "Brown eggs", "price": 28.1, ... },
      ...
    ]

    Se normaliza la clave del producto a minúsculas.

    Args:
        ruta_catalogo: Ruta del archivo JSON del catálogo.

    Returns:
        Diccionario { nombre_producto_lower: precio_unitario }.

    Raises:
        SystemExit: Si no se obtiene al menos un producto válido.
    """
    data = _leer_json_lista(ruta_catalogo)

    catalogo: Dict[str, float] = {}
    avisos = 0

    for idx, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            print(f"[WARN] Catálogo fila {idx}: no es un objeto JSON. Se omite.")
            avisos += 1
            continue

        title = item.get("title")
        price = item.get("price")

        if not isinstance(title, str) or not title.strip():
            print(f"[WARN] Catálogo fila {idx}: 'title' inválido. Se omite.")
            avisos += 1
            continue

        if not isinstance(price, (int, float)) or price < 0:
            print(f"[WARN] Catálogo fila {idx}: 'price' inválido (>= 0 requerido). Se omite.")
            avisos += 1
            continue

        catalogo[title.strip().lower()] = float(price)

    if not catalogo:
        print("[ERROR] El catálogo no contiene productos válidos.")
        raise SystemExit(1)

    if avisos:
        print(f"[INFO] Catálogo cargado con {avisos} aviso(s). Productos válidos: {len(catalogo)}")

    return catalogo


def validar_fecha_ddmmyy(fecha_txt: Any) -> Tuple[bool, str]:
    """
    Valida una fecha con formato 'dd/mm/yy'.

    Args:
        fecha_txt: Texto de fecha a validar.

    Returns:
        (ok, valor) donde:
          - ok = True y valor = fecha normalizada 'YYYY-MM-DD' si es válida.
          - ok = False y valor = mensaje de error si no es válida.
    """
    if not isinstance(fecha_txt, str):
        return False, "Fecha no es texto"
    try:
        dt = datetime.strptime(fecha_txt.strip(), "%d/%m/%y")
        return True, dt.strftime("%Y-%m-%d")
    except ValueError:
        return False, "Formato de fecha inválido (esperado dd/mm/yy)"


def _subtotal_venta(venta: Dict[str, Any], catalogo: Dict[str, float]) -> Tuple[bool, float, List[str]]:
    """
    Calcula el subtotal de una venta si es válida.

    Reglas:
    - `Product` debe existir en el catálogo (búsqueda case-insensitive).
    - `Quantity` debe ser entero (puede ser negativo).
    - La fecha se valida pero su error no impide el cálculo.

    Args:
        venta: Objeto JSON de la venta.
        catalogo: Diccionario de precios por producto en minúsculas.

    Returns:
        (valida, subtotal, avisos) donde:
            valida: True si se pudo calcular subtotal;
                    False si la venta se omite.
            subtotal: `quantity * price` (0.0 si no válida).
            avisos: Lista de mensajes de advertencia/errores.
    """
    avisos: List[str] = []

    if not isinstance(venta, dict):
        return False, 0.0, ["Venta inválida: no es objeto JSON"]

    sale_id = venta.get("SALE_ID", "?")
    sale_date = venta.get("SALE_Date")
    product = venta.get("Product")
    quantity = venta.get("Quantity")

    # Fecha (no bloqueante)
    fecha_ok, fecha_msg = validar_fecha_ddmmyy(sale_date)
    if not fecha_ok:
        avisos.append(f"[WARN] Venta (ID {sale_id}): {fecha_msg}")

    # Producto
    if not isinstance(product, str) or not product.strip():
        avisos.append(f"[WARN] Venta (ID {sale_id}): 'Product' inválido.")
        return False, 0.0, avisos

    key = product.strip().lower()
    if key not in catalogo:
        avisos.append(f"[WARN] Venta (ID {sale_id}): producto '{product}' no está en el catálogo. Se omite.")
        return False, 0.0, avisos

    # Cantidad (entero; puede ser negativo)
    if not isinstance(quantity, (int, float)) or int(quantity) != quantity:
        avisos.append(f"[WARN] Venta (ID {sale_id}): 'Quantity' debe ser entero.")
        return False, 0.0, avisos

    qty = int(quantity)
    price = catalogo[key]
    return True, float(qty * price), avisos


def procesar_ventas(ruta_ventas: str, catalogo: Dict[str, float]) -> Tuple[float, int, int, List[str]]:
    """
    Procesa el archivo de ventas y acumula el total.

    Args:
        ruta_ventas: Ruta al JSON de ventas.
        catalogo: Diccionario { producto_lower: precio }.

    Returns:
        total: Suma de los subtotales de ventas válidas.
        procesadas: Número de registros leídos.
        validas: Número de ventas válidas consideradas.
        mensajes: Lista de avisos/errores detectados.
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
        segundos: Tiempo de ejecución en segundos.
        ruta_salida: Nombre del archivo de salida.
    """
    resumen = [
        "==== Resultados de Cómputo de Ventas ====",
        f"Ventas leídas (total): {procesadas}",
        f"Ventas válidas procesadas: {validas}",
        f"Ventas con avisos/errores: {len(mensajes)}",
        f"Costo total acumulado: {total:,.2f}",
        f"Tiempo de ejecución (segundos): {segundos:.6f}",
    ]

    # Consola
    print("\n".join(resumen))
    if mensajes:
        print("\n---- Avisos / Errores detectados ----")
        for aviso in mensajes:
            print(aviso)

    # Archivo
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
    Define y parsea los argumentos de línea de comandos.

    Returns:
        Namespace con `price_catalogue` y `sales_record`.
    """
    parser = argparse.ArgumentParser(
        description="Calcula el costo total de ventas a partir de un catálogo y un registro de ventas."
    )
    parser.add_argument(
        "price_catalogue",
        help="Ruta al archivo JSON del catálogo de precios (priceCatalogue.json)",
    )
    parser.add_argument(
        "sales_record",
        help="Ruta al archivo JSON del registro de ventas (salesRecord.json)",
    )
    return parser.parse_args()


def main() -> None:
    """
    Punto de entrada principal del programa.
    """
    args = _parse_args()
    inicio = time.perf_counter()

    catalogo = cargar_catalogo(args.price_catalogue)
    total, procesadas, validas, mensajes = procesar_ventas(args.sales_record, catalogo)

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