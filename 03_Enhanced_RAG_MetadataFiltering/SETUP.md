# 🔧 Setup Instructions

## ⚠️ Importante: OneDrive + UV

Debido a limitaciones de OneDrive con enlaces simbólicos, el entorno virtual (`.venv`) debe estar **fuera de OneDrive**.

### Configuración Recomendada:

```
C:\Dev\AIE9_Enhanced_RAG\          ← Entorno virtual aquí (.venv/)
C:\Users\...\OneDrive\...\03_Enhanced_RAG_MetadataFiltering\  ← Código aquí
```

---

## 📦 Instalación

### Opción 1: Usar el entorno ya creado en C:\Dev (Recomendado)

```bash
# El entorno ya existe en C:\Dev\AIE9_Enhanced_RAG
# Solo necesitas ejecutar Jupyter desde allí

# Desde C:\Dev\AIE9_Enhanced_RAG:
cd C:\Dev\AIE9_Enhanced_RAG
uv run jupyter notebook

# Luego abre: C:\Users\alber\OneDrive\...\03_Enhanced_RAG_MetadataFiltering\notebooks\Enhanced_RAG_Assignment.ipynb
```

### Opción 2: Crear un nuevo entorno fuera de OneDrive

```bash
# 1. Copiar el proyecto a C:\Dev
Copy-Item "C:\Users\alber\OneDrive\Documentos\AIE9\03_Enhanced_RAG_MetadataFiltering" -Destination "C:\Dev\AIE9_Enhanced_RAG" -Recurse -Force

# 2. Navegar al directorio
cd C:\Dev\AIE9_Enhanced_RAG

# 3. Instalar dependencias
uv sync -p 3.12 --link-mode=copy

# 4. Abrir Jupyter
uv run jupyter notebook
```

---

## 🚀 Uso Rápido

```bash
# Desde C:\Dev\AIE9_Enhanced_RAG
uv run jupyter notebook notebooks/Enhanced_RAG_Assignment.ipynb
```

O desde Python:

```bash
uv run python
```

```python
from aimakerspace import VectorDatabase, AVAILABLE_METRICS
from aimakerspace.categorizer import categorize_chunk

# Tu código aquí...
```

---

## 📁 Estructura del Proyecto

```
C:\Dev\AIE9_Enhanced_RAG\        (Entorno virtual)
├── .venv/                        ← Python y dependencias
├── aimakerspace/                 ← Código de la librería
├── notebooks/                    ← Notebooks
└── data/                         ← Datos

C:\Users\...\OneDrive\...\03_Enhanced_RAG_MetadataFiltering\
                                  (Respaldo sincronizado)
├── aimakerspace/
├── notebooks/
├── data/
├── README.md
└── uv.lock
```

---

## ⚡ Tips

1. **Trabaja en C:\Dev\AIE9_Enhanced_RAG** para editar código
2. **OneDrive sincroniza** automáticamente los cambios que hagas
3. **No subas .venv a OneDrive** (ya está en .gitignore)
4. Si actualizas dependencias: `uv sync` desde C:\Dev\AIE9_Enhanced_RAG

---

## 🆘 Troubleshooting

### Error: "OPENAI_API_KEY not set"

```bash
# Crear .env en C:\Dev\AIE9_Enhanced_RAG
echo "OPENAI_API_KEY=tu-key-aqui" > .env
```

### Error: "Module not found: aimakerspace"

```bash
# Asegúrate de estar en el directorio correcto
cd C:\Dev\AIE9_Enhanced_RAG

# Y usar uv run
uv run python tu_script.py
```

### Quiero actualizar el código en OneDrive

Los cambios se sincronizan automáticamente. Si necesitas copiar manualmente:

```bash
# Copiar solo el código (sin .venv)
Copy-Item "C:\Dev\AIE9_Enhanced_RAG\*" -Destination "C:\Users\alber\OneDrive\Documentos\AIE9\03_Enhanced_RAG_MetadataFiltering\" -Recurse -Exclude ".venv" -Force
```
