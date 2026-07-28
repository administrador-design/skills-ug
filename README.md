# Skills de Universo Gastronómico

Repositorio oficial de las skills desarrolladas específicamente para Universo
Gastronómico S.A.S.

Aquí se publican las skills empresariales enseñadas por David, Harol u otras
personas autorizadas. Las skills generales o no relacionadas con Universo
Gastronómico se mantienen en el entorno interno hasta recibir una instrucción
expresa para publicarlas.

## Organización

Las skills se clasifican por área y proceso.

El árbol de carpetas de este README es el índice estructural oficial. Toda
creación, traslado, ampliación o eliminación de una skill debe actualizar este
árbol y la lista de skills publicadas como parte del mismo cambio.

```text
skills-ug/
├── AGENTS.md
├── README.md
└── ventas/
    └── cotizaciones/
        └── cotizar-mesones-acero-inoxidable/
            ├── SKILL.md
            ├── agents/
            │   └── openai.yaml
            ├── references/
            │   └── mesas-y-pozuelos.md
            └── scripts/
                └── cotizar_mesones.py
```

Cada skill debe conservar su propio directorio autónomo y un archivo `SKILL.md`
válido. Los recursos indispensables deben organizarse dentro de `agents/`,
`scripts/`, `references/`, `assets/` o `templates/`, según corresponda.

## Flujo obligatorio para crear o ampliar skills

1. Leer completamente este README antes de crear, trasladar o ampliar una skill.
2. Identificar el área y el proceso empresarial de la skill.
3. Elegir la ruta más específica dentro del árbol oficial. Si la categoría no
   existe, crear la jerarquía mínima necesaria por área y proceso.
4. Mantener todos los recursos propios dentro del directorio autónomo de la
   skill.
5. Actualizar en este README el árbol de carpetas y la lista de skills publicadas
   como parte del mismo cambio.
6. Validar que `SKILL.md`, los recursos y las rutas documentadas coincidan con el
   contenido publicado.
7. Validar la skill antes de instalarla o publicarla.

## Skills publicadas

### Ventas / Cotizaciones

- `cotizar-mesones-acero-inoxidable`: cotiza mesas y muebles en acero inoxidable
  304 o 430, incluidos pozuelos de lavado, con despiece, mínimo facturable,
  patas, amarres e IVA.
