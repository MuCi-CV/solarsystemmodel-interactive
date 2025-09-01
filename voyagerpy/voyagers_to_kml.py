# voyagers_to_kml.py
# Convert HORIZONS heliocentric vectors (AU) to non-geographic KML at scale 1:174,000,000.
# See usage instructions at the bottom if run without arguments.

import sys
import argparse
import math
import pandas as pd
from pathlib import Path

SCALE_DENOMINATOR = 174_000_000  # 1 : 174,000,000
AU_METERS = 149_597_870_000.0    # meters per AU
SCALE_M_PER_AU = AU_METERS / SCALE_DENOMINATOR  # meters at target scale per AU

KML_HEADER = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2"
     xmlns:gx="http://www.google.com/kml/ext/2.2">
  <Document>
    <name>Solar System Trajectories (Scale 1:{SCALE_DENOMINATOR})</name>
    <Snippet>Heliocentric positions mapped to non-geographic KML. AltitudeMode=absolute.</Snippet>
    <open>1</open>
"""

KML_FOOTER = """  </Document>
</kml>
"""

STYLE_TEMPLATE = """
    <Style id="{style_id}">
      <LineStyle>
        <width>{width}</width>
      </LineStyle>
      <PolyStyle>
        <fill>0</fill>
        <outline>1</outline>
      </PolyStyle>
    </Style>
"""

PLACEMARK_TEMPLATE = """
    <Placemark>
      <name>{name}</name>
      <styleUrl>#{style_id}</styleUrl>
      <gx:Track>
{when_coords}
      </gx:Track>
    </Placemark>
"""

def infer_xyz_columns(df):
    cols = {c.lower(): c for c in df.columns}
    for k in ("x", "y", "z"):
        if k not in cols:
            raise ValueError(f"Missing '{k.upper()}' column in CSV: has {list(df.columns)}")
    return cols["x"], cols["y"], cols["z"]

""" def load_vectors(csv_path: Path):
    # Robust CSV loader (HORIZONS CSV sometimes has leading spaces or comment rows)
    df = pd.read_csv(csv_path, comment="#")
    x_col, y_col, z_col = infer_xyz_columns(df)
    # Time: prefer "Datetime" if present; else JDTDB/JDCT; else index
    time_col = None
    for cand in ["Datetime", "Calendar Date (TDB)", "Calendar Date (UTC)", "Date", "JDTDB", "JDCT"]:
        if cand in df.columns:
            time_col = cand
            break
    if time_col is None:
        # fabricate simple indices
        df["_time_index_"] = range(len(df))
        time_col = "_time_index_"
    X = df[x_col].astype(float).to_numpy()
    Y = df[y_col].astype(float).to_numpy()
    Z = df[z_col].astype(float).to_numpy()
    T = df[time_col].astype(str).to_numpy()
    return T, X, Y, Z """

def load_vectors(csv_path):
    df = pd.read_csv(csv_path, header=None, comment="#")
    # Columnas: 0=JD, 1=Fecha, 2=X, 3=Y, 4=Z
    df = df.iloc[:, [1, 2, 3, 4]]
    df.columns = ["Datetime", "X", "Y", "Z"]
    df["X"] = df["X"].astype(float)
    df["Y"] = df["Y"].astype(float)
    df["Z"] = df["Z"].astype(float)
    return df["Datetime"].tolist(), df["X"].tolist(), df["Y"].tolist(), df["Z"].tolist()


def xyz_to_lonlatalt(x, y, z):
    r_xy = math.hypot(x, y)
    r = math.sqrt(x*x + y*y + z*z)
    lon = math.degrees(math.atan2(y, x))  # [-180, 180]
    lat = math.degrees(math.atan2(z, r_xy)) if r_xy != 0 else (90.0 if z > 0 else -90.0)
    alt_m = r * SCALE_M_PER_AU  # meters
    return lon, lat, alt_m

def make_when_coords(times, X, Y, Z):
    # Build alternating <when> and <gx:coord> entries
    lines = []
    for t, x, y, z in zip(times, X, Y, Z):
        lon, lat, alt_m = xyz_to_lonlatalt(x, y, z)
        lines.append(f"        <when>{t}</when>")
        # KML coord order is lon,lat,alt (in meters)
        lines.append(f"        <gx:coord>{lon:.9f} {lat:.9f} {alt_m:.3f}</gx:coord>")
    return "\n".join(lines)

def build_kml(series):
    parts = [KML_HEADER]
    # styles
    for idx, _ in enumerate(series):
        width = 1.5
        parts.append(STYLE_TEMPLATE.format(style_id=f"s{idx+1}", width=width))
    # placemarks
    for idx, (name, T, X, Y, Z) in enumerate(series):
        when_coords = make_when_coords(T, X, Y, Z)
        parts.append(PLACEMARK_TEMPLATE.format(name=name, style_id=f"s{idx+1}", when_coords=when_coords))
    parts.append(KML_FOOTER)
    return "".join(parts)

def main():
    parser = argparse.ArgumentParser(description="Convert HORIZONS heliocentric vectors (AU) to non-geographic KML at scale 1:174,000,000.")
    parser.add_argument("--inputs", nargs="+", required=True, help="CSV paths exported from HORIZONS (with X,Y,Z in AU).")
    parser.add_argument("--names", nargs="+", required=True, help="Display names corresponding 1:1 to --inputs.")
    parser.add_argument("--output", required=True, help="Output KML path.")
    args = parser.parse_args()

    if len(args.inputs) != len(args.names):
        raise SystemExit("--inputs and --names must have the same length.")

    series = []
    for inp, name in zip(args.inputs, args.names):
        T, X, Y, Z = load_vectors(Path(inp))
        series.append((name, T, X, Y, Z))

    kml = build_kml(series)
    out_path = Path(args.output)
    out_path.write_text(kml, encoding="utf-8")
    print(f"✔ KML escrito en: {out_path.resolve()}")
    print(f"Escala: 1:{SCALE_DENOMINATOR}  |  {SCALE_M_PER_AU:.6f} m por UA")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        msg = (
            "Uso:\n"
            "  python voyagers_to_kml.py --inputs voyager1.csv voyager2.csv jupiter.csv saturn.csv uranus.csv neptune.csv ceres.csv pluto.csv \\\n"
            "         --names \"Voyager 1\" \"Voyager 2\" \"Júpiter\" \"Saturno\" \"Urano\" \"Neptuno\" \"Ceres\" \"Plutón\" \\\n"
            "         --output solar_trajectories.kml\n\n"
            "CSV esperado (HORIZONS, vectores heliocéntricos): columnas X,Y,Z en AU + fecha (Datetime/JDTDB/etc.).\n"
            "Opciones HORIZONS recomendadas:\n"
            "- Target: Voyager 1 (spacecraft), Voyager 2 (spacecraft), Mercury..Neptune, Ceres, Pluto system barycenter.\n"
            "- Center: Sun (body center)\n"
            "- Coordinate: Ecliptic & Mean Equinox of Reference Epoch (o Equatorial J2000; ambas sirven para esta proyección).\n"
            "- Output: Vector Table, CSV, paso 1 día.\n\n"
            "Nota: KML no geográfico. Usamos la esfera de la Tierra como 'globo solar'. La geometría y distancias relativas son correctas a escala 1:174,000,000.\n"
        )
        print(msg)
    else:
        main()
