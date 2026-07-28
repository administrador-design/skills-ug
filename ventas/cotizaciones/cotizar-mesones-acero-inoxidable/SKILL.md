---
name: "cotizar-mesones-acero-inoxidable"
description: "Cotiza mesas y muebles en acero inoxidable 304/430, incluidos pozuelos de lavado, con despiece, patas, amarres, mínimos e IVA. Usar para cotizaciones de mesones, mesas de trabajo, muebles y mesas con pozuelo."
---

# Cotizar mesones y carpintería en acero inoxidable

Aplicar las reglas empresariales de Universo Gastronómico y ejecutar el programa incluido en esta skill. No calcular totales manualmente.

## Flujo obligatorio

1. Identificar el tipo de producto, medidas y configuración.
2. Usar acero 304 y calibre 20 cuando el usuario no indique otros.
3. Leer [references/mesas-y-pozuelos.md](references/mesas-y-pozuelos.md) para mesas, muebles, pisos, entrepaños, amarres o pozuelos.
4. No deducir medidas numéricas de fotografías. Usarlas solo para reconocer piezas y solicitar datos faltantes.
5. Despiezar superficie, pisos, entrepaños, tramos parciales y pozuelos por separado.
6. Preparar el JSON descrito en la referencia.
7. Ejecutar `python scripts/cotizar_mesones.py --input entrada.json`.
8. Usar la salida del programa como única fuente de valores numéricos.
9. Entregar especificaciones, despiece, decisiones estructurales, subtotal, IVA y total.

No inventar precios, medidas, piezas ni configuraciones faltantes.

## Valores predeterminados confirmados

- Usar acero inoxidable 304 salvo indicación contraria.
- Usar calibre 20 salvo indicación contraria.
- Si el usuario menciona piso o entrepaño sin indicar un tramo parcial, usar el largo completo.
- Si el usuario no menciona piso o entrepaño, no agregarlos.
- No cobrar amarre independiente cuando exista piso o entrepaño, porque cumplen esa función.
- Registrar el acabado y el salpicadero como datos de fabricación sin costo.

## Calibres sin tarifa automática

Detener la cotización si la mesa, el mueble o el pozuelo usa calibre 16, 18 o 22. Solicitar el precio vigente antes de continuar.

## Formato de respuesta

Presentar:

- Especificaciones y valores predeterminados aplicados.
- Despiece y metros reales.
- Metros cobrados y tarifa.
- Pozuelos y unidades equivalentes.
- Patas y amarres.
- Subtotal neto, IVA del 19 % y total.
- Detalles de fabricación sin costo.
- Datos pendientes de producción.

Usar pesos colombianos con punto como separador de miles.
