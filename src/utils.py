import os
from datetime import datetime

# Función para extraer metadatos de un archivo
def extract_metadata_from_file(filepath):
    return {
        "source": filepath,
        "filename": os.path.basename(filepath),
        "extension": os.path.splitext(filepath)[-1].lower(),
        "created_at": datetime.fromtimestamp(os.path.getctime(filepath)).isoformat(),
        "modified_at": datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat(),
        "size_kb": round(os.path.getsize(filepath) / 1024, 2)
    }
