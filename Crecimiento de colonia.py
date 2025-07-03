#@ File (label="Selecciona la carpeta con las imágenes") folder
#@ String (label="Extensión de archivo (ej: .jpg, .png, .tif)") ext
#@ boolean (label="¿Invertir imágenes?", value=False) invert

from ij import IJ, ImagePlus, ImageStack
from ij.io import Opener
from ij.gui import Roi, GenericDialog
from ij.plugin import ImagesToStack, ZProjector
import os

# 1. Leer todas las imágenes de la carpeta y ordenarlas
img_files = sorted([f for f in os.listdir(folder.getAbsolutePath()) if f.lower().endswith(ext)])
imps = []
for fname in img_files:
    imp = Opener().openImage(os.path.join(folder.getAbsolutePath(), fname))
    if imp is not None:
        if invert:
            IJ.run(imp, "Invert", "")
        IJ.run(imp, "8-bit", "")
        imps.append(imp)

if len(imps) == 0:
    IJ.error("No se encontraron imágenes.")
    exit()

# 2. Crear un stack a partir de las imágenes
stack = ImagesToStack.run(imps)
stack.show()

# 3. Segmentación manual en la primera imagen
IJ.setSlice(1)
IJ.run(stack, "Threshold...", "")  # El usuario ajusta el umbral
IJ.wait(2000)

# 4. Aplicar la segmentación a todas las imágenes
IJ.run(stack, "Set Measurements...", "mean redirect=None decimal=3")

# 5. Medir intensidad de cada slice (cuadro)
n_slices = stack.getNSlices()
intensidades = []
for i in range(1, n_slices+1):
    stack.setSlice(i)
    stats = stack.getStatistics()
    intensidades.append(stats.mean)

# 6. Calcular diferencias de intensidad entre imágenes consecutivas
diferencias = []
for i in range(1, len(intensidades)):
    diferencias.append(intensidades[i] - intensidades[i-1])

# 7. Mostrar resultados
print("Archivo\tIntensidad media\tDiferencia con anterior")
for i, fname in enumerate(img_files):
    diff = diferencias[i-1] if i > 0 else ""
    print("%s\t%.3f\t%s" % (fname, intensidades[i], diff))

# 8. Guardar resultados a un archivo
results_path = os.path.join(folder.getAbsolutePath(), "resultados_cultivo.txt")
with open(results_path, "w") as f:
    f.write("Archivo\tIntensidad media\tDiferencia con anterior\n")
    for i, fname in enumerate(img_files):
        diff = diferencias[i-1] if i > 0 else ""
        f.write("%s\t%.3f\t%s\n" % (fname, intensidades[i], diff))

print("¡Análisis completado! Resultados guardados en:", results_path)