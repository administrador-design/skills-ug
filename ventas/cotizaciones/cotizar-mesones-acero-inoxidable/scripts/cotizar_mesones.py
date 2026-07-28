from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal, InvalidOperation, ROUND_CEILING, ROUND_HALF_UP
from pathlib import Path

IVA = Decimal("0.19")
PATA_LARGA = Decimal("150000")
PATA_CORTA = Decimal("80000")
POZUELO_304_CAL_20 = Decimal("380000")
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


def techo(valor):
    return int(valor.to_integral_value(rounding=ROUND_CEILING))


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


def calcular_pozuelos(datos):
    pozuelos = datos.get("pozuelos", [])
    if not isinstance(pozuelos, list):
        raise ErrorCotizacion("pozuelos debe ser una lista")
    if pozuelos and not str(datos.get("salpicadero", "")).strip():
        raise ErrorCotizacion(
            "salpicadero es obligatorio cuando existe pozuelo; "
            "confirmar posterior, lateral o en U"
        )

    detalle = []
    unidades_totales = 0
    frentes_totales = Decimal("0")
    for indice, pozuelo in enumerate(pozuelos, 1):
        if not isinstance(pozuelo, dict):
            raise ErrorCotizacion(f"pozuelos[{indice}] debe ser un objeto")
        frente = positivo(pozuelo.get("frente_cm"), f"pozuelos[{indice}].frente_cm")
        fondo = positivo(pozuelo.get("fondo_cm"), f"pozuelos[{indice}].fondo_cm")
        profundidad = positivo(
            pozuelo.get("profundidad_cm"),
            f"pozuelos[{indice}].profundidad_cm",
        )
        ubicacion = str(pozuelo.get("ubicacion", "")).strip()
        if not ubicacion:
            raise ErrorCotizacion(f"pozuelos[{indice}].ubicacion es obligatoria")
        material = str(pozuelo.get("material", "304")).strip()
        try:
            calibre = int(pozuelo.get("calibre", 20))
        except (TypeError, ValueError):
            raise ErrorCotizacion(
                f"pozuelos[{indice}].calibre debe ser un entero"
            ) from None
        if material != "304" or calibre != 20:
            raise ErrorCotizacion(
                f"pozuelos[{indice}] requiere precio vigente: "
                f"material {material}, calibre {calibre}"
            )
        if profundidad == Decimal("17"):
            factor_profundidad = 1
        elif profundidad == Decimal("27"):
            factor_profundidad = 2
        else:
            raise ErrorCotizacion(
                f"pozuelos[{indice}].profundidad_cm debe ser 17 o 27; "
                "obtener regla o precio para otra profundidad"
            )

        modulos_frente = techo(frente / Decimal("50"))
        modulos_fondo = techo(fondo / Decimal("40"))
        modulos_superficie = modulos_frente * modulos_fondo
        unidades = modulos_superficie * factor_profundidad
        costo = unidades * int(POZUELO_304_CAL_20)
        unidades_totales += unidades
        frentes_totales += frente
        detalle.append(
            {
                "frente_cm": str(frente),
                "fondo_cm": str(fondo),
                "profundidad_cm": str(profundidad),
                "ubicacion": ubicacion,
                "material": material,
                "calibre": calibre,
                "modulos_frente": modulos_frente,
                "modulos_fondo": modulos_fondo,
                "factor_profundidad": factor_profundidad,
                "unidades_equivalentes": unidades,
                "formula": (
                    f"techo({frente}/50) x techo({fondo}/40) "
                    f"x {factor_profundidad}"
                ),
                "costo": costo,
                "costo_formateado": pesos(costo),
            }
        )
    costo_total = unidades_totales * int(POZUELO_304_CAL_20)
    return {
        "detalle": detalle,
        "unidades_equivalentes": unidades_totales,
        "frentes_totales_cm": frentes_totales,
        "tarifa_unidad": int(POZUELO_304_CAL_20),
        "costo": costo_total,
    }


def calcular(datos):
    tipo = str(datos.get("tipo_producto", "")).strip().lower()
    if tipo not in {"mesa", "mueble"}:
        raise ErrorCotizacion("tipo_producto debe ser 'mesa' o 'mueble'")

    acero = str(datos.get("acero", "304")).strip()
    if acero not in {"304", "430"}:
        raise ErrorCotizacion("acero debe ser '304' o '430'")
    try:
        calibre = int(datos.get("calibre", 20))
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
    altura = positivo(datos.get("altura_cm"), "altura_cm")
    formato = "estandar" if fondo <= Decimal("70") else "ancho"
    tarifa = TARIFAS[(acero, formato)]
    resultado_pozuelos = calcular_pozuelos(datos)
    frentes_pozuelos = resultado_pozuelos["frentes_totales_cm"]

    piezas = datos.get("piezas")
    if not isinstance(piezas, list) or not piezas:
        raise ErrorCotizacion("piezas debe ser una lista no vacía")

    metros_totales = Decimal("0")
    detalle_piezas = []
    tiene_piso_o_entrepano = False
    for indice, pieza in enumerate(piezas, 1):
        if not isinstance(pieza, dict):
            raise ErrorCotizacion(f"piezas[{indice}] debe ser un objeto")
        concepto = str(pieza.get("concepto", "")).strip()
        if not concepto:
            raise ErrorCotizacion(f"piezas[{indice}].concepto es obligatorio")
        concepto_normalizado = concepto.lower().replace("ñ", "n")
        longitud_base = positivo(
            pieza.get("longitud_cm"), f"piezas[{indice}].longitud_cm"
        )
        cantidad = entero_no_negativo(
            pieza.get("cantidad", 1), f"piezas[{indice}].cantidad"
        )
        if cantidad == 0:
            raise ErrorCotizacion(f"piezas[{indice}].cantidad debe ser positiva")

        es_entrepano = "entrepano" in concepto_normalizado
        es_piso = "piso" in concepto_normalizado
        tiene_piso_o_entrepano = tiene_piso_o_entrepano or es_entrepano or es_piso
        descontar = pieza.get("descontar_frentes_pozuelos", es_entrepano)
        if not isinstance(descontar, bool):
            raise ErrorCotizacion(
                f"piezas[{indice}].descontar_frentes_pozuelos debe ser booleano"
            )
        longitud_efectiva = (
            longitud_base - frentes_pozuelos if descontar else longitud_base
        )
        if longitud_efectiva <= 0:
            raise ErrorCotizacion(
                f"piezas[{indice}] queda sin longitud después de descontar "
                "los frentes de pozuelos"
            )
        metros = longitud_efectiva * cantidad / Decimal("100")
        metros_totales += metros
        detalle_piezas.append(
            {
                "concepto": concepto,
                "longitud_base_cm": str(longitud_base),
                "descuento_pozuelos_cm": str(
                    frentes_pozuelos if descontar else Decimal("0")
                ),
                "longitud_efectiva_cm": str(longitud_efectiva),
                "cantidad": cantidad,
                "metros": str(metros.normalize()),
                "formula": (
                    f"({longitud_base} - "
                    f"{frentes_pozuelos if descontar else Decimal('0')}) "
                    f"cm x {cantidad} / 100"
                ),
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
    if tiene_piso_o_entrepano and amarres:
        raise ErrorCotizacion(
            "No agregar amarres cuando existe piso o entrepaño"
        )

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
            detalle_amarres.append(
                {
                    "longitud_cm": str(longitud),
                    "cantidad": cantidad,
                    "costo_unitario": unitario,
                    "costo_unitario_formateado": pesos(unitario),
                    "costo_linea": linea,
                    "costo_linea_formateado": pesos(linea),
                }
            )

    costo_pozuelos = resultado_pozuelos["costo"]
    subtotal = costo_material + costo_pozuelos + costo_patas + costo_amarres
    valor_iva = redondear(Decimal(subtotal) * IVA)
    total = subtotal + valor_iva
    metros_equivalentes = (
        metros_totales + Decimal(resultado_pozuelos["unidades_equivalentes"])
    )

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
            "altura_cm": str(altura),
            "formato_lamina": formato,
        },
        "material": {
            "tarifa_metro": int(tarifa),
            "tarifa_metro_formateada": pesos(int(tarifa)),
            "metros_totales": str(metros_totales.normalize()),
            "metros_cobrados": str(metros_cobrados.normalize()),
            "costo": costo_material,
            "costo_formateado": pesos(costo_material),
            "despiece": detalle_piezas,
        },
        "pozuelos": {
            "detalle": resultado_pozuelos["detalle"],
            "unidades_equivalentes": resultado_pozuelos["unidades_equivalentes"],
            "tarifa_unidad": resultado_pozuelos["tarifa_unidad"],
            "tarifa_unidad_formateada": pesos(
                resultado_pozuelos["tarifa_unidad"]
            ),
            "costo": costo_pozuelos,
            "costo_formateado": pesos(costo_pozuelos),
        },
        "metros_equivalentes_totales": str(metros_equivalentes.normalize()),
        "patas": {
            "tipo": tipo_pata,
            "base": patas_base,
            "adicionales_por_diseno": adicionales,
            "total": patas_totales,
            "precio_unitario": int(precio_pata),
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
