"""
ARIA — Categorizar documentos y actualizar metadata en Qdrant.

Categorías:
  - agua     : documentos de optimización hídrica y normativa ambiental
  - sector   : conocimiento sectorial (madurez, roadmaps, estrategia)
  - matching : catálogo de soluciones y proveedores tecnológicos
  - empresa  : informes de empresa individuales — reservados para fase 2
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from qdrant_client import QdrantClient
from rich.console import Console
from rich.table import Table

from aria.config import settings

console = Console(force_terminal=True)

CATEGORY_MAP = {
    # ── agua ──────────────────────────────────────────────────────────────────
    "2._Presentacion_Workshop_1_COSMEAU_020323":         ["agua"],
    "5._Presentacion_Workshop_2_COSMEAU_160323":         ["agua"],
    "COSMEAU_Catalogo_soluciones_DEF":                   ["agua", "matching"],
    "DF-FEBEA-GuideBPEau-WEB-DP_(1)":                   ["agua"],
    "Evaluation-EPR-UWWTD-ECT-for-Cosmetics-Europe-2025-12-05": ["agua"],
    "Ficha_resumen_proyecto_COSM-EAU_180722":            ["agua"],
    "Ficha_resumen_proyecto_CosmeWaterFootprint_260523": ["agua"],
    "Memoria_estudio_viabilidad_COSM_EAU":               ["agua"],
    "Memoria_Huella_hdrica_cosmtica_vDEF":               ["agua"],
    "OJ_L_202403019_ES_TXT":                             ["agua"],
    "PPT_CWF_Presentacion_de_resultados_100424_vf":      ["agua"],
    "Transicin_hdrica_en_el_sector_cosmtico_-_borrador": ["agua"],
    "Caso_exito_Loreal_agua":                            ["agua"],  # Suplemento con caso L'Oréal Burgos

    # ── sector: conocimiento sectorial general ────────────────────────────────
    "DOC_Memoria_Tecnica_Roadmap_Digitalizacion":              ["sector", "matching"],
    "E5.2._Hoja_de_ruta_para_la_transformacin_digital_del_sector_de_la_PyC": ["sector", "matching"],
    "Roadmap_ltima_versin_-_Asamblea":                        ["sector", "matching"],
    "Informe_Estado_Madurez_Digital_sector_PyC_DEF":           ["sector", "matching"],
    "Informe_Anlisis_estratgico_de_innovacin_vf":              ["sector", "matching"],
    "Memoria_tcnica_Justificacin_DIGIPYC":                    ["sector"],
    "NdP_DIGIPYC_impulsa_la_digitalizacin_del_sector_de_perfumera_y_cosmtica": ["sector"],
    "PPT_Sesion_Lanzamiento_DIGIPYC_201124_def":              ["sector"],
    "Presentacin_IEdA_DIGIPYC":                               ["sector"],
    "Plan_Estrategico_AEI_2025-2028_FIbS":                    ["sector"],
    "Resumen_ejecutivo_Plan_Estratgico_Feeling_Innovation_by_Stanpa_2025-2028": ["sector"],
    # Mixtos agua + sector
    "Cuestionario_de_diagnostico_sectorial":             ["agua", "sector"],
    "E2.1_A1_Presentaciones_socios_1":                   ["agua", "sector"],
    "E2.1_A2_Presentaciones_socios2":                    ["agua", "sector"],
    "E2.2_A1_Cuestionario_Diagnostico":                  ["agua", "sector"],
    "E3.1_Informe_de_potenciales_ideas_de_proyectos":    ["agua", "sector"],
    "E4.1._Informe_de_resultados_del_estudio_viabilidad": ["agua", "sector"],
    "Listado_de_temas_de_inters_para_el_sector":         ["agua", "sector"],

    # ── matching: catálogo de soluciones y proveedores ────────────────────────
    "DIGIPYC_-_Catlogo_de_soluciones_tecnolgicas_y_digitales": ["matching"],

    # ── empresa: informes individuales anonimizados (sin agente activo) ───────
    # Motivo: hablan de situaciones específicas de empresas concretas.
    # El agente los confundiría con conocimiento general del sector.
    # Reservados para fase 2: agente personalizado por empresa.
    "Informes_anonimizados_unidos":  ["empresa"],
    "fichas_diagnstico_fusionadas":  ["empresa"],
}


def main():
    console.rule("[bold cyan]ARIA -- Categorizar chunks en Qdrant[/bold cyan]")
    console.print()
    console.print("[bold]Nueva estructura de categorías:[/bold]")
    console.print("  [cyan]agua[/cyan]     → AguaAgent — optimización hídrica y normativa")
    console.print("  [cyan]sector[/cyan]   → SectorAgent — madurez digital, roadmaps, estrategia")
    console.print("  [cyan]matching[/cyan] → MatchingAgent — catálogo DIGIPYC de soluciones")
    console.print("  [yellow]empresa[/yellow]  → Sin agente activo — reservado para fase 2")
    console.print()

    client = QdrantClient(path="./qdrant_data")
    collection = settings.qdrant_collection

    info = client.get_collection(collection)
    total = info.points_count
    console.print(f"Chunks en colección: {total}")

    limit = 100
    offset = None
    updated = 0
    unmatched = set()
    category_counts = {"agua": 0, "sector": 0, "matching": 0, "empresa": 0, "fallback": 0}

    while True:
        points, next_offset = client.scroll(
            collection_name=collection, limit=limit, offset=offset, with_payload=True
        )
        if not points:
            break

        for point in points:
            meta = point.payload.get("metadata", {})
            source_name = meta.get("source_name", "") if isinstance(meta, dict) else ""
            categories = CATEGORY_MAP.get(source_name)

            if categories is None:
                unmatched.add(source_name)
                categories = ["sector"]  # fallback
                category_counts["fallback"] += 1
            else:
                for cat in categories:
                    if cat in category_counts:
                        category_counts[cat] += 1

            client.set_payload(
                collection_name=collection,
                payload={"category": categories},
                points=[point.id],
            )
            updated += 1

        offset = next_offset
        if offset is None:
            break

    console.print(f"\n[green]Actualizados {updated}/{total} chunks.[/green]\n")

    if unmatched:
        console.print(f"[yellow]Sin mapeo explícito (→ sector): {sorted(unmatched)}[/yellow]")

    table = Table(title="Distribución final de categorías")
    table.add_column("Categoría", style="bold")
    table.add_column("Chunks", justify="right")
    table.add_column("Agente activo")

    agua_docs   = [k for k, v in CATEGORY_MAP.items() if "agua"     in v]
    sector_docs = [k for k, v in CATEGORY_MAP.items() if "sector"   in v]
    match_docs  = [k for k, v in CATEGORY_MAP.items() if "matching" in v]
    emp_docs    = [k for k, v in CATEGORY_MAP.items() if "empresa"  in v]

    table.add_row("agua",     str(category_counts["agua"]),     f"agua_agent  ({len(agua_docs)} docs)")
    table.add_row("sector",   str(category_counts["sector"]),   f"sector_agent ({len(sector_docs)} docs)")
    table.add_row("matching", str(category_counts["matching"]), f"matching_agent ({len(match_docs)} docs)")
    table.add_row("empresa",  str(category_counts["empresa"]),  f"— sin agente — ({len(emp_docs)} docs)")

    console.print(table)


if __name__ == "__main__":
    main()
