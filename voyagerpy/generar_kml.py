import math

# Configuraciones
input_file = "voyager1.txt"
output_file = "voyager1.kml"
line_skip = 2          # Tomar 1 de cada 10 líneas
min_distance = 1e2      # Distancia mínima entre puntos (en km, ajustar según escala)
factor_escala = 174000000

# Centro del Sol
sun_lat, sun_lon = -25.280945, -57.609083

def distance(p1, p2):
    """Distancia Euclídea 2D"""
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

# Leer archivo y filtrar por salto de línea
with open(input_file, "r") as f:
    lines = f.readlines()[::line_skip]

filtered_points = []
last_point = None

for line in lines:
    parts = line.split(",")
    # Coordenadas desde el archivo (usando X y Y)
    x = float(parts[2])
    y = float(parts[3])
    
    if last_point is None or distance((x, y), last_point) > min_distance:
        filtered_points.append((x, y))
        last_point = (x, y)

# Crear KML
with open(output_file, "w") as f:
    f.write("""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
  <name>Voyager 1 Trajectory</name>
  <Style id="yellowLine">
    <LineStyle>
      <color>ff00ffff</color>
      <width>2</width>
    </LineStyle>
  </Style>
  <Placemark>
    <name>Voyager 1 Path</name>
    <styleUrl>#yellowLine</styleUrl>
    <LineString>
      <tessellate>1</tessellate>
      <coordinates>
""")
    # Convertir coordenadas relativas al Sol a lat/lon simplificados
    for x, y in filtered_points:
        lon = sun_lon + x / factor_escala   # factor de escala arbitrario, ajustar a gusto
        lat = sun_lat + y / factor_escala
        f.write(f"        {lon},{lat}\n")

    f.write("""      </coordinates>
    </LineString>
  </Placemark>
</Document>
</kml>""")

print(f"KML generado: {output_file} con {len(filtered_points)} puntos.")
