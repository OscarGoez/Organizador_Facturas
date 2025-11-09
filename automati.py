import os
import shutil
import PyPDF2
import datetime
import time
from pathlib import Path
from dotenv import load_dotenv


# CONFIGURACIÓN
load_dotenv()

RUTA_ORIGEN = Path(os.getenv("ORIGEN", "./pdfs"))
RUTAS_DESTINO = {
    "curazao": Path(os.getenv("DESTINO_CURAZAO", "./clasificados/Administracion")),
    "empresas públicas": Path(os.getenv("DESTINO_EPM", "./clasificados/Epm")),
    "epm factura": Path(os.getenv("DESTINO_EPM", "./clasificados/Epm")),
    "comcel s.a": Path(os.getenv("DESTINO_COMCEL", "./clasificados/Claro")),
    "davivienda": Path(os.getenv("DESTINO_DAVIVIENDA", "./clasificados/Davivienda")),
    "3823968217": Path(os.getenv("DESTINO_SOMOS", "./clasificados/Somos")),
}
CARPETA_NO_CLASIFICADOS = RUTA_ORIGEN / "No_clasificados"


# FUNCIONES
def crear_carpetas():
    """Crea todas las carpetas necesarias si no existen."""
    for carpeta in list(RUTAS_DESTINO.values()) + [CARPETA_NO_CLASIFICADOS]:
        carpeta.mkdir(parents=True, exist_ok=True)


def extraer_texto_pdf(ruta_pdf: Path) -> str:
    """Extrae texto de un PDF de forma segura."""
    try:
        with open(ruta_pdf, "rb") as archivo:
            lector_pdf = PyPDF2.PdfReader(archivo)
            texto = ""
            for pagina in lector_pdf.pages:
                texto += pagina.extract_text() or ""
            return texto.lower()
    except Exception as e:
        print(f"[ERROR] No se pudo leer {ruta_pdf.name}: {e}")
        return ""


def clasificar_pdf(ruta_pdf: Path):
    """Clasifica un solo PDF según las palabras clave."""
    texto = extraer_texto_pdf(ruta_pdf)
    fecha_mod = datetime.datetime.fromtimestamp(ruta_pdf.stat().st_mtime)
    base_nombre = fecha_mod.strftime("%Y-%m-%d_%H-%M-%S")
    nuevo_nombre = base_nombre + ".pdf"

    for palabra, carpeta in RUTAS_DESTINO.items():
        if palabra in texto:
            mover_pdf(ruta_pdf, carpeta, nuevo_nombre)
            print(f"📂 {ruta_pdf.name} → {carpeta}")
            return

    # Si no coincide con ninguna palabra clave
    mover_pdf(ruta_pdf, CARPETA_NO_CLASIFICADOS, nuevo_nombre)
    print(f"⚠️ {ruta_pdf.name} no clasificado → {CARPETA_NO_CLASIFICADOS}")


def mover_pdf(origen: Path, destino: Path, nuevo_nombre: str):
    """Mueve un archivo PDF evitando sobreescritura."""
    destino_final = destino / nuevo_nombre
    contador = 1
    while destino_final.exists():
        destino_final = destino / f"{destino_final.stem}_{contador}.pdf"
        contador += 1
    shutil.move(str(origen), str(destino_final))


def procesar_pdfs():
    """Procesa todos los PDFs de la carpeta de origen."""
    print("🔍 Analizando archivos PDF...")
    for archivo in RUTA_ORIGEN.iterdir():
        if archivo.suffix.lower() == ".pdf":
            clasificar_pdf(archivo)



# EJECUCIÓN PRINCIPAL


if __name__ == "__main__":
    print("🚀 Iniciando proceso de clasificación de PDFs...")
    crear_carpetas()
    procesar_pdfs()
    print("✅ Proceso completado.")
    time.sleep(3)
