---
name: "cotizar-mesones-acero-inoxidable"
description: "Cotiza mesones 304/430 con despiece, mínimo de 1 m, patas, amarres e IVA."
---

# Skill para cotizar mesones

Usar esta skill como archivo autónomo. No depender de scripts, referencias, fotografías ni archivos externos. Ejecutar siempre el código Python incluido en este documento para obtener los valores numéricos.

## Flujo obligatorio

1. Obtener tipo de producto, acero, calibre, largo, fondo, altura y configuración.
2. No deducir medidas numéricas de una fotografía. Usarla solo para reconocer piezas y solicitar las dimensiones faltantes.
3. Detener la cotización si el calibre no es 20. Solicitar el precio vigente por metro antes de continuar.
4. Despiezar toda la estructura. Registrar por separado superficie, pisos, entrepaños y tramos parciales.
5. Determinar automáticamente las patas adicionales requeridas por espacios libres, equipos bajo counter o discontinuidades.
6. Preparar el JSON descrito más adelante.
7. Extraer el bloque Python de esta skill a un archivo temporal llamado `cotizar_mesones.py`.
8. Ejecutar `python cotizar_mesones.py --input entrada.json`.
9. Usar la salida del programa como única fuente de los cálculos.
10. Entregar el precio total y explicar cada decisión.

No inventar dimensiones, precios, piezas ni configuraciones faltantes.

## Reglas de negocio

### Material y tarifas

- Usar acero inoxidable 304 o 430.
- Admitir calibres 16, 18, 20 y 22, pero calcular automáticamente solo calibre 20.
- Para calibre 16, 18 o 22, detener la cotización y obtener un precio vigente por metro.
- Registrar el acabado como dato de fabricación sin modificar el precio.

| Fondo | Acero 304 | Acero 430 |
|---|---:|---:|
| Hasta 70 cm, inclusive | $380.000 | $350.000 |
| Mayor de 70 cm | $410.000 | $380.000 |

Aplicar la tarifa de fondo mayor de 70 cm porque se requiere otro formato de lámina.

### Despiece

- Obtener largo, fondo y altura.
- Sumar los metros lineales reales de todas las piezas.
- Cobrar como mínimo 1 metro lineal de material por cada producto, aunque el despiece real sea menor. Conservar y mostrar por separado los metros reales y los metros cobrados.
- No asumir que un piso o entrepaño ocupa el 100 % del largo.
- Descontar zonas libres para canecas, trampas de grasa, lavavajillas, máquinas de hielo u otros equipos bajo counter.
- Registrar por separado cada pieza parcial.
- Registrar el salpicadero como especificación sin costo.

### Patas

- Usar patas largas de $150.000 en mesones tipo mesa.
- Usar patas cortas de $80.000 en mesones tipo mueble con laterales de lámina.
- Para mesas de hasta 180 cm, inclusive, usar 4 patas.
- Para mesas de más de 180 cm, usar 6 patas.
- Agregar 2 patas cuando un espacio libre o cambio de tramo necesite un nuevo apoyo.
- No duplicar patas si las patas centrales requeridas por el largo también soportan la discontinuidad.
- Para muebles, obtener el número total de patas del diseño.

### Amarre de patas

- Aplicar solo a mesas. Los muebles no requieren amarre.
- Hasta 90 cm, inclusive, cobrar $150.000.
- Para más de 90 cm, calcular `150000 x longitud_cm / 90`.
- Redondear al peso colombiano.

### Especificaciones sin costo

- No cobrar adicional por acabado ni salpicadero.
- Retrasar las patas 8 cm por la media caña.
- Si el producto va entre muros, revisar también el retraso lateral.
- No modificar el precio por el retraso de patas ni por la condición entre muros.

### Totales

- Considerar que las tarifas ya incluyen todos los costos internos.
- No agregar mano de obra, margen, transporte, instalación u otros rubros.
- Calcular subtotal neto con material, patas y amarres.
- Calcular IVA del 19 % sobre el subtotal.
- Calcular total final como subtotal más IVA.

## Criterio para patas adicionales

- Empezar con 4 patas si el largo es hasta 180 cm y con 6 si es mayor.
- Revisar si un vacío para equipo elimina la continuidad de un piso o entrepaño.
- Revisar si un tramo parcial termina en un punto sin apoyo.
- Agregar un par de patas cuando sea necesario crear un nuevo apoyo vertical.
- No agregar el par si las patas centrales ya proporcionan ese apoyo.
- Registrar la decisión en `patas_adicionales_diseno`.
- Explicar por qué el valor es 0, 2 o un número par mayor.

## Entrada JSON

| Campo | Tipo | Regla |
|---|---|---|
| `tipo_producto` | texto | `mesa` o `mueble` |
| `acero` | texto | `304` o `430` |
| `calibre` | entero | Cálculo automático solo para `20` |
| `largo_cm` | número | Largo total positivo |
| `fondo_cm` | número | Fondo total positivo |
| `piezas` | lista | Una entrada por pieza o tramo |
| `patas_adicionales_diseno` | entero | Número par decidido por el análisis |
| `patas_totales` | entero | Obligatorio para muebles |
| `amarres` | lista | Solo para mesas |
| `acabado` | texto | Dato sin costo |
| `salpicadero` | texto | Dato sin costo |
| `entre_muros` | booleano | Dato sin costo |
| `notas_fabricacion` | lista | Otros detalles sin costo |

Cada pieza debe contener `concepto`, `longitud_cm` y `cantidad`. Cada amarre debe contener `longitud_cm` y puede contener `cantidad`.

Ejemplo:

```json
{
  "tipo_producto": "mesa",
  "acero": "304",
  "calibre": 20,
  "largo_cm": 160,
  "fondo_cm": 70,
  "piezas": [
    {"concepto": "superficie", "longitud_cm": 160, "cantidad": 1},
    {"concepto": "entrepaño", "longitud_cm": 160, "cantidad": 1},
    {"concepto": "piso", "longitud_cm": 160, "cantidad": 1}
  ],
  "patas_adicionales_diseno": 0,
  "amarres": [],
  "acabado": "satinado",
  "salpicadero": "posterior",
  "entre_muros": false,
  "notas_fabricacion": ["Retrasar patas 8 cm"]
}
```

## Código Python incorporado

Copiar exactamente este bloque a `cotizar_mesones.py`. Usar Python 3 y únicamente la biblioteca estándar.

```python
from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

IVA = Decimal("0.19")
PATA_LARGA = Decimal("150000")
PATA_CORTA = Decimal("80000")
TARIFAS = {
    ("304", "estandar"): Decimal("380000"),
    ("430", "estandar"): Decimal("350000"),
    ("304", "ancho"): Decimal("410000"),
    ("430", "ancho"): Decimal("380000"),
}


class ErrorCotizacion(ValueError):
    pass


def positivo(valor, campo):
    try:
        numero = Decimal(str(valor))
    except (InvalidOperation, TypeError):
        raise ErrorCotizacion(f"{campo} debe ser numérico") from None
    if numero <= 0:
        raise ErrorCotizacion(f"{campo} debe ser mayor que cero")
    return numero


def entero_no_negativo(valor, campo):
    if isinstance(valor, bool):
        raise ErrorCotizacion(f"{campo} debe ser un entero no negativo")
    try:
        numero = int(valor)
        exacto = Decimal(str(valor))
    except (TypeError, ValueError, InvalidOperation):
        raise ErrorCotizacion(f"{campo} debe ser un entero no negativo") from None
    if numero < 0 or exacto != Decimal(numero):
        raise ErrorCotizacion(f"{campo} debe ser un entero no negativo")
    return numero


def redondear(valor):
    return int(valor.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def pesos(valor):
    return f"${valor:,}".replace(",", ".")


def cargar(path):
    texto = Path(path).read_text(encoding="utf-8") if path else sys.stdin.read()
    try:
        datos = json.loads(texto)
    except json.JSONDecodeError as exc:
        raise ErrorCotizacion(f"JSON inválido: {exc.msg}") from None
    if not isinstance(datos, dict):
        raise ErrorCotizacion("La entrada debe ser un objeto JSON")
    return datos


def calcular(datos):
    tipo = str(datos.get("tipo_producto", "")).strip().lower()
    if tipo not in {"mesa", "mueble"}:
        raise ErrorCotizacion("tipo_producto debe ser 'mesa' o 'mueble'")

    acero = str(datos.get("acero", "")).strip()
    if acero not in {"304", "430"}:
        raise ErrorCotizacion("acero debe ser '304' o '430'")

    try:
        calibre = int(datos.get("calibre"))
    except (TypeError, ValueError):
        raise ErrorCotizacion("calibre debe ser 16, 18, 20 o 22") from None
    if calibre not in {16, 18, 20, 22}:
        raise ErrorCotizacion("calibre debe ser 16, 18, 20 o 22")
    if calibre != 20:
        return {
            "estado": "requiere_precio_material",
            "mensaje": (
                f"Detener la cotización: el calibre {calibre} no tiene tarifa "
                "automática. Obtener el precio vigente por metro."
            ),
        }

    largo = positivo(datos.get("largo_cm"), "largo_cm")
    fondo = positivo(datos.get("fondo_cm"), "fondo_cm")
    formato = "estandar" if fondo <= Decimal("70") else "ancho"
    tarifa = TARIFAS[(acero, formato)]

    piezas = datos.get("piezas")
    if not isinstance(piezas, list) or not piezas:
        raise ErrorCotizacion("piezas debe ser una lista no vacía")

    metros_totales = Decimal("0")
    detalle_piezas = []
    for indice, pieza in enumerate(piezas, 1):
        if not isinstance(pieza, dict):
            raise ErrorCotizacion(f"piezas[{indice}] debe ser un objeto")
        concepto = str(pieza.get("concepto", "")).strip()
        if not concepto:
            raise ErrorCotizacion(f"piezas[{indice}].concepto es obligatorio")
        longitud = positivo(
            pieza.get("longitud_cm"), f"piezas[{indice}].longitud_cm"
        )
        cantidad = entero_no_negativo(
            pieza.get("cantidad", 1), f"piezas[{indice}].cantidad"
        )
        if cantidad == 0:
            raise ErrorCotizacion(f"piezas[{indice}].cantidad debe ser positiva")
        metros = longitud * cantidad / Decimal("100")
        metros_totales += metros
        detalle_piezas.append(
            {
                "concepto": concepto,
                "longitud_cm": str(longitud),
                "cantidad": cantidad,
                "metros": str(metros.normalize()),
                "formula": f"{longitud} cm x {cantidad} / 100",
            }
        )

    metros_cobrados = max(metros_totales, Decimal("1"))
    costo_material = redondear(metros_cobrados * tarifa)
    adicionales = entero_no_negativo(
        datos.get("patas_adicionales_diseno", 0),
        "patas_adicionales_diseno",
    )
    if adicionales % 2:
        raise ErrorCotizacion("patas_adicionales_diseno debe ser un número par")

    if tipo == "mesa":
        patas_base = 4 if largo <= Decimal("180") else 6
        patas_totales = patas_base + adicionales
        tipo_pata = "larga"
        precio_pata = PATA_LARGA
    else:
        if datos.get("amarres"):
            raise ErrorCotizacion("Los muebles no requieren amarres")
        if "patas_totales" not in datos:
            raise ErrorCotizacion("patas_totales es obligatorio para muebles")
        patas_base = entero_no_negativo(datos["patas_totales"], "patas_totales")
        if patas_base == 0:
            raise ErrorCotizacion("patas_totales debe ser positivo")
        patas_totales = patas_base
        adicionales = 0
        tipo_pata = "corta"
        precio_pata = PATA_CORTA

    costo_patas = redondear(precio_pata * patas_totales)
    amarres = datos.get("amarres", [])
    if not isinstance(amarres, list):
        raise ErrorCotizacion("amarres debe ser una lista")

    detalle_amarres = []
    costo_amarres = 0
    if tipo == "mesa":
        for indice, amarre in enumerate(amarres, 1):
            if not isinstance(amarre, dict):
                raise ErrorCotizacion(f"amarres[{indice}] debe ser un objeto")
            longitud = positivo(
                amarre.get("longitud_cm"), f"amarres[{indice}].longitud_cm"
            )
            cantidad = entero_no_negativo(
                amarre.get("cantidad", 1), f"amarres[{indice}].cantidad"
            )
            if cantidad == 0:
                raise ErrorCotizacion(f"amarres[{indice}].cantidad debe ser positiva")
            valor = (
                PATA_LARGA
                if longitud <= Decimal("90")
                else PATA_LARGA * longitud / Decimal("90")
            )
            unitario = redondear(valor)
            linea = unitario * cantidad
            costo_amarres += linea
            formula = (
                "$150.000"
                if longitud <= Decimal("90")
                else f"$150.000 x {longitud} cm / 90 cm"
            )
            detalle_amarres.append(
                {
                    "longitud_cm": str(longitud),
                    "cantidad": cantidad,
                    "formula_unitaria": formula,
                    "costo_unitario": unitario,
                    "costo_unitario_formateado": pesos(unitario),
                    "costo_linea": linea,
                    "costo_linea_formateado": pesos(linea),
                }
            )

    subtotal = costo_material + costo_patas + costo_amarres
    valor_iva = redondear(Decimal(subtotal) * IVA)
    total = subtotal + valor_iva

    sin_costo = []
    for campo, etiqueta in (
        ("acabado", "Acabado"),
        ("salpicadero", "Salpicadero"),
        ("entre_muros", "Entre muros"),
    ):
        if campo in datos:
            sin_costo.append(f"{etiqueta}: {datos[campo]}")
    for nota in datos.get("notas_fabricacion", []):
        sin_costo.append(str(nota))

    return {
        "estado": "cotizacion_completa",
        "moneda": "COP",
        "especificaciones": {
            "tipo_producto": tipo,
            "acero": acero,
            "calibre": calibre,
            "largo_cm": str(largo),
            "fondo_cm": str(fondo),
            "formato_lamina": formato,
        },
        "material": {
            "tarifa_metro": int(tarifa),
            "tarifa_metro_formateada": pesos(int(tarifa)),
            "metros_totales": str(metros_totales.normalize()),
            "metros_cobrados": str(metros_cobrados.normalize()),
            "formula": f"{metros_cobrados} m x {pesos(int(tarifa))}",
            "costo": costo_material,
            "costo_formateado": pesos(costo_material),
            "despiece": detalle_piezas,
        },
        "patas": {
            "tipo": tipo_pata,
            "base": patas_base,
            "adicionales_por_diseno": adicionales,
            "total": patas_totales,
            "precio_unitario": int(precio_pata),
            "formula": f"{patas_totales} x {pesos(int(precio_pata))}",
            "costo": costo_patas,
            "costo_formateado": pesos(costo_patas),
        },
        "amarres": {
            "detalle": detalle_amarres,
            "costo": costo_amarres,
            "costo_formateado": pesos(costo_amarres),
        },
        "totales": {
            "subtotal_neto": subtotal,
            "subtotal_neto_formateado": pesos(subtotal),
            "iva_porcentaje": 19,
            "iva": valor_iva,
            "iva_formateado": pesos(valor_iva),
            "total_con_iva": total,
            "total_con_iva_formateado": pesos(total),
        },
        "detalles_fabricacion_sin_costo": sin_costo,
    }


def main():
    parser = argparse.ArgumentParser(description="Cotizar mesones desde JSON")
    parser.add_argument("--input", help="Ruta al JSON; omitir para usar stdin")
    args = parser.parse_args()
    try:
        resultado = calcular(cargar(args.input))
    except (ErrorCotizacion, OSError) as exc:
        resultado = {"estado": "error", "mensaje": str(exc)}
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
        return 2
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    return 0 if resultado["estado"] == "cotizacion_completa" else 3


if __name__ == "__main__":
    raise SystemExit(main())
```

## Ejemplos de control

1. Mesa 304 calibre 20 de 160 x 70 x 90 cm, con superficie, entrepaño completo y piso completo:
   - Acero: 4,8 m.
   - Patas: 4 largas.
   - Subtotal neto: $2.424.000.
   - IVA: $460.560.
   - Total con IVA: $2.884.560.
2. Mesa 304 calibre 20 de 230 x 70 x 90 cm, con superficie, medio entrepaño y piso completo:
   - Acero: 5,75 m.
   - Patas: 6 largas.
   - Subtotal neto: $3.085.000.
   - IVA: $586.150.
   - Total con IVA: $3.671.150.

## Referencias visuales descritas

- Ejemplo 1: mesa con superficie, un entrepaño completo, un piso completo y 4 patas.
- Ejemplo 2: mesa con superficie, dos entrepaños completos, un piso completo y 4 patas.
- Ejemplo 3: mesa con poceta de lavado, un entrepaño central que termina antes de la poceta, otros dos entrepaños que ocupan la mitad de la mesa y 6 patas.

Usar estas descripciones solo para reconocer configuraciones. Solicitar siempre las dimensiones reales.

## Formato de respuesta

Presentar especificaciones, despiece, metros reales, metros cobrados, tarifa, patas, amarres, subtotal neto, IVA, total, detalles sin costo, explicación de patas adicionales y datos faltantes. Usar pesos colombianos con punto como separador de miles.
