from pathlib import Path

import pyogrio

SHP = Path("data/raw/manual/Q100_2Ciclo_PB_20260114.shp")

# Leemos solo atributos, sin geometrías: rápido aunque el .shp pese 1,7 GB
df = pyogrio.read_dataframe(
    SHP,
    columns=["DEMARCACIO", "ID_DEMAR", "TIPO_ZONA", "CICLO"],
    read_geometry=False,
)

print(df.dtypes, "\n")
print(df.groupby(["ID_DEMAR", "DEMARCACIO"]).size().sort_values(ascending=False))
print("\nTIPO_ZONA:\n", df["TIPO_ZONA"].value_counts())
