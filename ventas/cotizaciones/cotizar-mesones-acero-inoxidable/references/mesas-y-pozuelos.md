# Mesas, muebles y pozuelos

## Tarifas de material

| Fondo | Acero 304 | Acero 430 |
|---|---:|---:|
| Hasta 70 cm, inclusive | $380.000 | $350.000 |
| Mayor de 70 cm | $410.000 | $380.000 |

Aplicar la tarifa mayor de 70 cm porque requiere otro formato de lámina. Cobrar como mínimo 1 metro lineal de material por producto. Mantener separados los metros reales y cobrados.

## Despiece

- Registrar por separado superficie, piso, entrepaño y cada tramo parcial.
- Usar el largo completo cuando el usuario mencione piso o entrepaño sin indicar reducción.
- No agregar piso ni entrepaño cuando el usuario no los mencione.
- Descontar espacios libres para equipos.
- Si existe un pozuelo sobre un entrepaño continuo, descontar del entrepaño únicamente el frente total de los pozuelos.
- No descontar el pozuelo del piso.
- Marcar `descontar_frentes_pozuelos: false` solamente cuando un tramo de entrepaño esté fuera de la zona de los pozuelos.

## Patas

- Mesa de hasta 180 cm, inclusive: 4 patas largas.
- Mesa de más de 180 cm: 6 patas largas.
- Pata larga: $150.000.
- Pata corta para muebles con laterales: $80.000.
- Agregar 2 patas cuando un vacío o cambio de tramo requiera un apoyo vertical nuevo.
- No duplicar apoyos que ya proporcionen las patas centrales.
- Un pozuelo no agrega patas por sí solo. Analizar los apoyos según la continuidad real.

## Amarres

- Aplicar solamente a mesas.
- No agregar amarre separado cuando la mesa tenga piso o entrepaño.
- Si no existe piso ni entrepaño, obtener la configuración del amarre antes de cotizar.
- Hasta 90 cm, inclusive: $150.000.
- Más de 90 cm: `150000 × longitud_cm ÷ 90`, redondeado al peso.

## Pozuelos

### Valores predeterminados

- Material: acero inoxidable 304.
- Calibre: 20.
- Tarifa por unidad equivalente: $380.000, sin depender del fondo ni del material de la mesa.

Detener la cotización y solicitar precio vigente cuando el pozuelo use otro material o calibre.

### Dimensiones y equivalencias

- Pozuelo sencillo base: 50 cm de frente × 40 cm de fondo × 17 cm de profundidad.
- Pozuelo de doble profundidad base: 50 cm de frente × 40 cm de fondo × 27 cm de profundidad.
- Calcular los módulos de superficie como `techo(frente/50) × techo(fondo/40)`.
- Usar factor 1 para 17 cm de profundidad.
- Usar factor 2 para 27 cm de profundidad.
- Calcular unidades equivalentes como `módulos de superficie × factor de profundidad`.
- Detener y solicitar una regla o precio si la profundidad no es 17 ni 27 cm.

Ejemplos:

- 50 × 40 × 17 cm: 1 unidad.
- 50 × 40 × 27 cm: 2 unidades.
- 150 × 40 × 17 cm: 3 unidades.
- 150 × 40 × 27 cm: 6 unidades.
- 100 × 80 × 17 cm: 4 unidades.

### Datos de fabricación

- Obtener ubicación: izquierda, derecha, centro u otra descripción inequívoca.
- Todo mesón con pozuelo lleva salpicadero posterior.
- Obtener si también lleva salpicadero lateral izquierdo, lateral derecho o en U por ir entre muros.
- Registrar el salpicadero sin modificar el precio.
- No ubicar entrepaño debajo del pozuelo, porque ese espacio se reserva para trampa de grasa y plomería.

## Entrada JSON

Campos principales:

| Campo | Regla |
|---|---|
| `tipo_producto` | `mesa` o `mueble` |
| `acero` | Predeterminado `304` |
| `calibre` | Predeterminado `20` |
| `largo_cm`, `fondo_cm`, `altura_cm` | Medidas positivas |
| `piezas` | Lista de superficie, piso, entrepaño o tramos |
| `pozuelos` | Lista opcional de pozuelos |
| `patas_adicionales_diseno` | Entero par |
| `patas_totales` | Obligatorio para muebles |
| `amarres` | Lista; vacía cuando piso o entrepaño cumplen esa función |
| `salpicadero` | Obligatorio si existe pozuelo |
| `entre_muros` | Dato de fabricación |
| `notas_fabricacion` | Lista |

Cada pieza contiene `concepto`, `longitud_cm`, `cantidad` y, si corresponde, `descontar_frentes_pozuelos`.

Cada pozuelo contiene:

- `frente_cm`
- `fondo_cm`
- `profundidad_cm`
- `ubicacion`
- `material`, predeterminado `304`
- `calibre`, predeterminado `20`

## Ejemplo validado

Mesa 304 calibre 20 de 160 × 70 × 90 cm, con piso completo, entrepaño continuo y pozuelo sencillo izquierdo:

```json
{
  "tipo_producto": "mesa",
  "largo_cm": 160,
  "fondo_cm": 70,
  "altura_cm": 90,
  "piezas": [
    {"concepto": "superficie", "longitud_cm": 160, "cantidad": 1},
    {
      "concepto": "entrepaño",
      "longitud_cm": 160,
      "cantidad": 1,
      "descontar_frentes_pozuelos": true
    },
    {"concepto": "piso", "longitud_cm": 160, "cantidad": 1}
  ],
  "pozuelos": [
    {
      "frente_cm": 50,
      "fondo_cm": 40,
      "profundidad_cm": 17,
      "ubicacion": "izquierda"
    }
  ],
  "patas_adicionales_diseno": 0,
  "amarres": [],
  "salpicadero": "posterior; confirmar si requiere lateral o en U"
}
```

Resultado esperado:

- Mesa, entrepaño y piso: 4,3 m.
- Pozuelo: 1 unidad equivalente.
- Total equivalente en acero 304: 5,3 m.
- Material y pozuelo: $2.014.000.
- Patas: $600.000.
- Subtotal: $2.614.000.
- IVA: $496.660.
- Total: $3.110.660.
