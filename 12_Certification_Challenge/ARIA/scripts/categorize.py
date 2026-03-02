"""
ARIA — Categorizar documentos y actualizar metadata en Qdrant.

Asigna categorías (agua/td) a los chunks existentes en Qdrant
basándose en el nombre del documento fuente. No requiere re-ingesta.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, SetPayloadOperation, SetPayload, PointIdsList
from rich.console import Console
from rich.table import Table

from aria.config import settings

console = Console(force_terminal=True)

CATEGORY_MAP = {
    # ── agua: water optimization + regulatory ──
    "2._Presentacion_Workshop_1_COSMEAU_020323":         ["agua"],
    "5._Presentacion_Workshop_2_COSMEAU_160323":         ["agua"],
    "COSMEAU_Catalogo_soluciones_DEF":                   ["agua"],
    "DF-FEBEA-GuideBPEau-WEB-DP_(1)":                   ["agua"],
    "Evaluation-EPR-UWWTD-ECT-for-Cosmetics-Europe-2025-12-05": ["agua"],
    "Ficha_resumen_proyecto_COSM-EAU_180722":            ["agua"],
    "Ficha_resumen_proyecto_CosmeWaterFootprint_260523": ["agua"],
    "Memoria_estudio_viabilidad_COSM_EAU":               ["agua"],
    "Memoria_Huella_hdrica_cosmtica_vDEF":               ["agua"],
    "OJ_L_202403019_ES_TXT":                             ["agua"],
    "PPT_CWF_Presentacion_de_resultados_100424_vf":      ["agua"],
    "Transicin_hdrica_en_el_sector_cosmtico_-_borrador": ["agua"],

    # ── td: digital transformation ──
    "DIGIPYC_-_Catlogo_de_soluciones_tecnolgicas_y_digitales": ["td"],
    "DOC_Memoria_Tecnica_Roadmap_Digitalizacion":              ["td"],
    "E5.2._Hoja_de_ruta_para_la_transformacin_digital_del_sector_de_la_PyC": ["td"],
    "Informe_Estado_Madurez_Digital_sector_PyC_DEF":           ["td"],
    "Memoria_tcnica_Justificacin_DIGIPYC":                    ["td"],
    "NdP_DIGIPYC_impulsa_la_digitalizacin_del_sector_de_perfumera_y_cosmtica": ["td"],
    "PPT_Sesion_Lanzamiento_DIGIPYC_201124_def":              ["td"],
    "Presentacin_IEdA_DIGIPYC":                               ["td"],
    "Roadmap_ltima_versin_-_Asamblea":                        ["td"],

    # ── ambas categorías ──
    "Cuestionario_de_diagnostico_sectorial":             ["agua", "td"],
    "E2.1_A1_Presentaciones_socios_1":                   ["agua", "td"],
    "E2.1_A2_Presentaciones_socios2":                    ["agua", "td"],
    "E2.2_A1_Cuestionario_Diagnostico":                  ["agua", "td"],
    "E3.1_Informe_de_potenciales_ideas_de_proyectos":    ["agua", "td"],
    "E4.1._Informe_de_resultados_del_estudio_viabilidad": ["agua", "td"],
    "fichas_diagnstico_fusionadas":                      ["agua", "td"],
    "Informe_Anlisis_estratgico_de_innovacin_vf":        ["agua", "td"],
    "Informes_anonimizados_unidos":                      ["agua", "td"],
    "Listado_de_temas_de_inters_para_el_sector":         ["agua", "td"],
    "Plan_Estrategico_AEI_2025-2028_FIbS":               ["agua", "td"],
    "Resumen_ejecutivo_Plan_Estratgico_Feeling_Innovation_by_Stanpa_2025-2028": ["agua", "td"],
}


def main():
    console.rule("[bold cyan]ARIA -- Categorizar chunks en Qdrant[/bold cyan]")

    client = QdrantClient(path="./qdrant_data")
    collection = settings.qdrant_collection

    info = client.get_collection(collection)
    total = info.points_count
    console.print(f"Chunks en coleccion: {total}")

    limit = 100
    offset = None
    updated = 0
    unmatched = set()

    while True:
        points, next_offset = client.scroll(
            collection_name=collection, limit=limit, offset=offset, with_payload=True
        )
        if not points:
            break

        for point in points:
            source_name = point.payload.get("source_name", "")
            categories = CATEGORY_MAP.get(source_name)

            if categories is None:
                unmatched.add(source_name)
                categories = ["agua", "td"]

            client.set_payload(
                collection_name=collection,
                payload={"category": categories},
                points=[point.id],
            )
            updated += 1

        offset = next_offset
        if offset is None:
            break

    console.print(f"\n[green]Actualizados {updated}/{total} chunks con categorias.[/green]")

    if unmatched:
        console.print(f"[yellow]Docs sin mapeo explicito (asignados a ambas): {unmatched}[/yellow]")

    table = Table(title="Distribucion de categorias")
    table.add_column("Categoria")
    table.add_column("Docs")

    agua_docs = [k for k, v in CATEGORY_MAP.items() if "agua" in v]
    td_docs = [k for k, v in CATEGORY_MAP.items() if "td" in v]
    table.add_row("agua", str(len(agua_docs)))
    table.add_row("td", str(len(td_docs)))
    table.add_row("ambas", str(len([k for k, v in CATEGORY_MAP.items() if len(v) == 2])))
    console.print(table)


if __name__ == "__main__":
    main()
