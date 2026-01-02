from __future__ import annotations

import csv
import gzip
import os
from collections import OrderedDict
from contextlib import contextmanager
from dataclasses import dataclass
import base64
import uuid
from html import escape
from typing import Any, Dict, Hashable, Iterable, List, Mapping, Optional, Sequence, Tuple

import pysam
import streamlit as st

from proletract.modules.viz import parsers, utils
from proletract.modules.viz.vis_helper import motif_legend_html, parse_motif_range


REQUIRED_COLUMNS_WITH_REGION: Tuple[str, ...] = (
    "region",
    "read_name",
    "cluster",
    "hp",
    "sequence",
    "intervals",
)
REQUIRED_COLUMNS_WITH_COORDS: Tuple[str, ...] = (
    "chrom",
    "start",
    "end",
    "read_name",
    "cluster",
    "hp",
    "sequence",
    "intervals",
)
HEADERLESS_COORD_COLUMN_NAMES: Tuple[str, ...] = (
    "chrom",
    "start",
    "end",
    "read_name",
    "cluster",
    "hp",
    "sequence",
    "cigar",
    "intervals",
)



@dataclass(frozen=True)
class ReadInterval:
    start: int
    end: int
    motif_id: int

    def to_span_token(self) -> str:
        return f"({self.start}-{self.end})"


@dataclass
class ReadEntry:
    read_name: str
    cluster: str
    hp: str
    sequence: str
    intervals_raw: str
    intervals: List[ReadInterval]
    spans: str
    motif_ids: List[str]
    cigar: str = ""


def _parse_interval_token(token: str) -> Optional[ReadInterval]:
    if not token:
        return None

    try:
        range_part, motif_part = token.split(":", 1)
        start_str, end_str = range_part.split("-", 1)
        start = int(start_str)
        end = int(end_str)
        motif_id = int(motif_part)
        if start <= 0 or end <= 0 or end < start:
            return None
        return ReadInterval(start=start, end=end, motif_id=motif_id)
    except ValueError:
        return None


def _parse_intervals(intervals_str: str) -> List[ReadInterval]:
    tokens = [token.strip() for token in str(intervals_str).split(",")]
    intervals: List[ReadInterval] = []
    for token in tokens:
        interval = _parse_interval_token(token)
        if interval is not None:
            intervals.append(interval)
    intervals.sort(key=lambda iv: (iv.start, iv.end))
    return intervals



def _create_read_entry(row: Mapping[str, str]) -> Optional[ReadEntry]:
    sequence = (row.get("sequence") or "").strip()
    if not sequence:
        return None

    intervals_raw = (row.get("intervals") or "").strip()
    intervals = _parse_intervals(intervals_raw)

    spans = "_".join(interval.to_span_token() for interval in intervals)
    motif_ids: List[str] = []
    for interval in intervals:
        motif_id = interval.motif_id
        if motif_id < 0:
            motif_id = 0
        motif_ids.append(str(motif_id))

    cigar = (row.get("cigar") or "").strip()

    return ReadEntry(
        read_name=(row.get("read_name") or "").strip(),
        cluster=(row.get("cluster") or "").strip(),
        hp=(row.get("hp") or "").strip(),
        sequence=sequence,
        intervals_raw=intervals_raw,
        intervals=intervals,
        spans=spans,
        motif_ids=motif_ids,
        cigar=cigar,
    )


def _collect_regions(tsv_path: str) -> List[str]:
    regions: List[str] = []
    seen: set[str] = set()
    structure = _detect_read_support_structure(tsv_path)
    st.session_state.read_support_columns = list(structure.column_names)
    st.session_state.read_support_format = structure.format_variant
    st.session_state.read_support_has_header = structure.has_header

    if structure.format_variant == "coords" and _has_tabix_index(tsv_path):
        vcf_regions = _regions_from_vcf_records()
        if vcf_regions:
            return vcf_regions

    with _create_dict_reader(tsv_path, structure) as reader:
        for row in reader:
            region = _extract_region_from_row(row, structure.format_variant)
            if region and region not in seen:
                seen.add(region)
                regions.append(region)
    return regions


def _ensure_read_support_ready() -> Optional[Tuple[str, List[str]]]:
    tsv_path: Optional[str] = st.session_state.get("read_tsv_path")
    if not tsv_path:
        return None

    if not os.path.exists(tsv_path):
        st.error(f"Read-level TSV file not found at '{tsv_path}'.")
        st.session_state.pop("read_support_source", None)
        st.session_state.pop("read_regions", None)
        st.session_state.pop("read_region_cache", None)
        return None

    cached_path: Optional[str] = st.session_state.get("read_support_source")
    regions: Optional[List[str]] = st.session_state.get("read_regions")
    if cached_path != tsv_path or not regions:
        try:
            regions = sorted(_collect_regions(tsv_path))
        except Exception as exc:  # pragma: no cover - UI feedback path
            st.error(f"Could not read read-level TSV: {exc}")
            st.session_state.pop("read_support_source", None)
            st.session_state.pop("read_regions", None)
            st.session_state.pop("read_region_cache", None)
            return None
        st.session_state.read_support_source = tsv_path
        st.session_state.read_regions = regions
        st.session_state.read_region_cache = OrderedDict()
    regions_list: List[str] = list(st.session_state.get("read_regions", []))
    return tsv_path, regions_list


def _load_region_entries(tsv_path: str, region: str) -> List[ReadEntry]:
    format_variant: str = st.session_state.get("read_support_format", "")
    column_names: List[str] = st.session_state.get("read_support_columns", [])
    has_header: Optional[bool] = st.session_state.get("read_support_has_header")
    if not column_names or not format_variant:
        structure = _detect_read_support_structure(tsv_path)
        st.session_state.read_support_columns = list(structure.column_names)
        st.session_state.read_support_format = structure.format_variant
        st.session_state.read_support_has_header = structure.has_header
        column_names = list(structure.column_names)
        format_variant = structure.format_variant
        has_header = structure.has_header
    structure = ReadSupportStructure(
        format_variant=format_variant,
        column_names=tuple(column_names),
        has_header=bool(has_header),
    )
    if format_variant == "coords":
        entries = _load_entries_with_tabix(tsv_path, region, structure)
        if entries:
            return entries
        # Fallback to streaming if tabix lookup fails
    entries: List[ReadEntry] = []
    with _create_dict_reader(tsv_path, structure) as reader:
        for row in reader:
            if format_variant == "coords":
                inferred_region = _extract_region_from_row(row, "coords")
            else:
                inferred_region = (row.get("region") or "").strip()
            if inferred_region != region:
                continue
            if "region" not in row or not row["region"]:
                row["region"] = inferred_region
            entry = _create_read_entry(row)
            if entry is not None:
                entries.append(entry)
    return entries


def _open_tabular_file(path: str):
    if path.endswith(".gz"):
        return gzip.open(path, "rt")
    return open(path, "r", newline="")


def _extract_region_from_row(row: Mapping[str, str], format_variant: str) -> str:
    if format_variant == "coords":
        chrom = (row.get("chrom") or "").strip()
        start = (row.get("start") or "").strip()
        end = (row.get("end") or "").strip()
        if not (chrom and start and end):
            return ""
        try:
            start_int = int(start)
            end_int = int(end)
        except ValueError:
            return ""
        if end_int <= start_int:
            return ""
        return f"{chrom}:{start_int}-{end_int}"
    return (row.get("region") or "").strip()


class ReadSupportStructure:
    __slots__ = ("format_variant", "column_names", "has_header")

    def __init__(self, format_variant: str, column_names: Sequence[str], has_header: bool):
        self.format_variant = format_variant
        self.column_names = tuple(column_names)
        self.has_header = has_header


def _detect_read_support_structure(tsv_path: str) -> ReadSupportStructure:
    with _open_tabular_file(tsv_path) as handle:
        first_line = handle.readline()
        if not first_line:
            raise ValueError("Read-level data file is empty.")
        first_line = first_line.strip("\n")
        columns = first_line.split("\t")
        lower_columns = [col.lower() for col in columns]
        has_header = False
        format_variant = "region"
        if "region" in lower_columns:
            has_header = True
            format_variant = "region"
            column_names = columns
        elif {"chrom", "start", "end"}.issubset(lower_columns):
            has_header = True
            format_variant = "coords"
            column_names = columns
        else:
            # Assume headerless BED-like structure with coordinates
            format_variant = "coords"
            has_header = False
            column_names = HEADERLESS_COORD_COLUMN_NAMES[: len(columns)]

        handle.seek(0)

        if format_variant == "region":
            missing = [col for col in REQUIRED_COLUMNS_WITH_REGION if col not in column_names]
        else:
            missing = [col for col in REQUIRED_COLUMNS_WITH_COORDS if col not in column_names]
            # Allow headerless files where required fields are supplied via defaults
            if not has_header:
                missing = [col for col in missing if col not in HEADERLESS_COORD_COLUMN_NAMES[: len(columns)]]

        if missing:
            raise ValueError(
                f"Read-level data file is missing required columns: {', '.join(missing)}"
            )

        return ReadSupportStructure(format_variant, column_names, has_header)


@contextmanager
def _create_dict_reader(tsv_path: str, structure: ReadSupportStructure):
    handle = _open_tabular_file(tsv_path)
    try:
        if structure.has_header:
            reader = csv.DictReader(handle, delimiter="\t")
        else:
            reader = csv.DictReader(
                handle,
                delimiter="\t",
                fieldnames=list(structure.column_names),
            )
        yield reader
    finally:
        handle.close()


def _split_region(region: str) -> Tuple[str, int, int]:
    try:
        chrom, coords = region.split(":", 1)
        start_str, end_str = coords.split("-", 1)
        start_1_based = int(start_str)
        end_1_based = int(end_str)
        if end_1_based <= start_1_based:
            raise ValueError
        return chrom, start_1_based, end_1_based
    except ValueError as exc:
        raise ValueError(f"Invalid region identifier '{region}'. Expected format chrom:start-end.") from exc


def _load_entries_with_tabix(
    bed_path: str, region: str, structure: ReadSupportStructure
) -> List[ReadEntry]:
    if not _has_tabix_index(bed_path):
        return []
    chrom, start_1_based, end_1_based = _split_region(region)
    fetch_start = max(start_1_based - 1, 0)
    fetch_end = max(end_1_based, fetch_start + 1)
    entries: List[ReadEntry] = []
    try:
        with pysam.TabixFile(bed_path) as tabix:
            try:
                iterator = tabix.fetch(chrom, fetch_start, fetch_end)
            except ValueError:
                return []
            for line in iterator:
                values = line.rstrip("\n").split("\t")
                row_dict = {
                    structure.column_names[idx]: values[idx]
                    for idx in range(min(len(structure.column_names), len(values)))
                }
                derived_region = _extract_region_from_row(row_dict, "coords")
                row_dict["region"] = derived_region or region
                entry = _create_read_entry(row_dict)
                if entry is not None:
                    entries.append(entry)
    except (OSError, ValueError) as exc:
        st.error(f"Failed to query read-level BED with tabix: {exc}")
        return []
    return entries


def _has_tabix_index(path: str) -> bool:
    potential = [f"{path}.tbi", f"{path}.csi"]
    return any(os.path.exists(candidate) for candidate in potential)


def _regions_from_vcf_records() -> List[str]:
    records_obj = st.session_state.get("records")
    if isinstance(records_obj, dict):
        return sorted({value for value in records_obj.values() if value})
    return []


def _get_region_entries(tsv_path: str, region: str) -> List[ReadEntry]:
    cache_obj = st.session_state.get("read_region_cache")
    if not isinstance(cache_obj, OrderedDict):
        cache_obj = OrderedDict(cache_obj or {})
        st.session_state.read_region_cache = cache_obj
    cache: OrderedDict[str, List[ReadEntry]] = cache_obj
    cache_key = f"{tsv_path}::{region}"
    if cache_key in cache:
        entries_cached = cache[cache_key]
        needs_refresh = any(
            entry.intervals_raw and not entry.intervals for entry in entries_cached
        )
        if not needs_refresh:
            cache.move_to_end(cache_key)
            return entries_cached
        cache.pop(cache_key, None)
    entries = _load_region_entries(tsv_path, region)
    cache[cache_key] = entries
    cache.move_to_end(cache_key)
    while len(cache) > 8:
        cache.popitem(last=False)
    return entries


def _prepare_multiselect_default(
    widget_key: str,
    options: Sequence[Any],
    fallback: Iterable[Any],
) -> List[Any]:
    options_set = {option for option in options}

    current_value = st.session_state.get(widget_key)
    if isinstance(current_value, list):
        filtered_current = [item for item in current_value if item in options_set]
        if filtered_current:
            return filtered_current
        if current_value:
            st.session_state.pop(widget_key, None)

    fallback_filtered = [item for item in fallback if item in options_set]
    if fallback_filtered:
        return fallback_filtered
    return list(options)


def _ensure_full_width_layout() -> None:
    key = "read_visualization_layout_css_v2"
    if st.session_state.get(key):
        return

    st.markdown(
        """
        <style>
        html, body, .stApp {
            width: 100%;
            min-height: 100%;
            overflow-x: hidden;
        }
        body {
            font-size: 16px;
        }
        [data-testid="stAppViewContainer"] {
            padding: 0 !important;
        }
        main .block-container {
            width: 100%;
            max-width: min(1600px, 100vw);
            padding: 1.6rem 2.6rem 3rem;
        }
        @media (max-width: 1280px) {
            main .block-container {
                padding: 1.2rem 1.4rem 2.4rem;
            }
        }
        @media (max-width: 900px) {
            main .block-container {
                padding: 1rem 1.1rem 2rem;
            }
        }
        [data-testid="stVerticalBlock"], [data-testid="stHorizontalBlock"], .element-container {
            width: 100%;
        }
        [data-testid="stTabs"] button {
            flex: 1;
            max-width: 100%;
        }
        .stTabs, .stTabs [role="tablist"] {
            width: 100%;
        }
        [data-testid="stSidebar"] {
            width: clamp(250px, 22vw, 320px) !important;
            padding: 1.4rem 1.1rem 2.8rem !important;
            background: linear-gradient(180deg, #eef2ff 0%, #e0f2fe 100%);
            box-shadow: 4px 0 16px rgba(15,23,42,0.12);
        }
        [data-testid="stSidebar"] * {
            max-width: 100%;
        }
        [data-testid="stSidebar"] section[data-testid="stSidebarContent"] {
            width: 100%;
        }
        [data-testid="stSidebar"] [data-testid="stSidebarNav"] {
            width: 100%;
        }
        [data-testid="stSidebar"] .element-container {
            width: 100%;
            margin-bottom: 1.1rem;
        }
        label, [data-testid="stWidgetLabel"] > div {
            font-size: 0.92rem;
            font-weight: 500;
            color: #334155;
        }
        .stTextInput > div > div > input,
        .stNumberInput input,
        .stTextArea textarea,
        div[data-baseweb="select"] > div,
        div[data-baseweb="slider"] {
            width: 100% !important;
        }
        div[data-testid="stSlider"] > div {
            padding-left: 4px;
            padding-right: 4px;
        }
        .stButton > button, .stDownloadButton > button {
            width: 100%;
            border-radius: 999px !important;
            padding: 0.6rem 1rem;
            font-weight: 600;
        }
        .stMultiSelect, .stSelectbox, .stRadio {
            width: 100%;
        }
        .stRadio > div {
            width: 100%;
        }
        .stRadio label {
            display: flex;
            align-items: center;
            gap: 6px;
        }
        @media (max-width: 900px) {
            [data-testid="stSidebar"] {
                width: 100% !important;
                position: relative;
                box-shadow: none;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.session_state[key] = True


def _normalize_zoom_profile(
    profile: Optional[Mapping[str, Any]],
) -> Dict[str, float]:
    base: Dict[str, float] = {
        "scale": 1.0,
        "font_multiplier": 1.0,
        "letter_spacing": 0.016,
        "line_height": 1.48,
        "flex_scale": 1.0,
        "step_multiplier": 1.6,
    }
    mode = "balanced"
    scrollable = False
    clamp_inner = False
    if profile:
        for key, value in profile.items():
            if key in {"scrollable", "mode"}:
                continue
            if isinstance(value, (int, float)):
                base[key] = float(value)
        mode = str(profile.get("mode", mode))
        scrollable = bool(profile.get("scrollable", scrollable))
        clamp_inner = bool(profile.get("clamp_inner", clamp_inner))

    base["scale"] = max(base.get("scale", 1.0), 0.35)
    base["font_multiplier"] = max(base.get("font_multiplier", 1.0), 0.4)
    base["letter_spacing"] = max(base.get("letter_spacing", 0.004), 0.004)
    base["line_height"] = max(base.get("line_height", 1.2), 1.1)
    base["flex_scale"] = max(base.get("flex_scale", 1.0), 0.25)
    base["step_multiplier"] = max(base.get("step_multiplier", 1.0), 0.8)

    base["mode"] = mode
    base["scrollable"] = scrollable or base["flex_scale"] > 1.34
    base["clamp_inner"] = clamp_inner and not base["scrollable"]
    return base


def _select_region(regions: Sequence[str]) -> Optional[str]:
    regions = list(regions)
    if not regions:
        return None

    default_region = st.session_state.get("previous_region", regions[0])
    default_index = regions.index(default_region) if default_region in regions else 0

    return st.selectbox(
        "Select genomic region",
        options=regions,
        index=default_index,
        key="read_visualization_region",
    )


def _filter_reads(entries: Sequence[ReadEntry], region: str) -> List[ReadEntry]:
    if not entries:
        return []

    clusters = sorted({str(entry.cluster) for entry in entries if str(entry.cluster)})
    haps = sorted({str(entry.hp) for entry in entries if str(entry.hp)})

    cluster_key = f"{region}_clusters"
    hap_key = f"{region}_haps"

    has_haplotype_only_zero = set(haps) == {"0"} and bool(haps)

    if has_haplotype_only_zero:
        col1, col3, col4 = st.columns([1, 1, 1])
        col2 = None
    else:
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    with col1:
        # Remove 'noise' from the default clusters if it exists
        default_clusters = [c for c in clusters if c.lower() != "noise"]
        default_cluster_selection = _prepare_multiselect_default(
            cluster_key,
            clusters,
            default_clusters if default_clusters else clusters,
        )
        selected_clusters = st.multiselect(
            "Clusters",
            options=clusters,
            default=default_cluster_selection,
            key=cluster_key,
        )
    if col2 is not None:
        with col2:
            default_hap_selection = _prepare_multiselect_default(
                hap_key,
                haps,
                haps,
            )
            selected_haps = st.multiselect(
                "Haplotypes",
                options=haps,
                default=default_hap_selection,
                key=hap_key,
            )
    else:
        selected_haps = ["0"]
    with col3:
        search_query = st.text_input(
            "Search read name",
            key=f"{region}_read_search",
            placeholder="Type to filter",
        ).strip()
    with col4:
        max_reads = st.number_input(
            "Reads to display",
            min_value=1,
            max_value=len(entries),
            value=min(30, len(entries)),
            step=1,
            key=f"{region}_max_reads",
        )
    filtered = [
        entry
        for entry in entries
        if str(entry.cluster) in selected_clusters and str(entry.hp) in selected_haps
    ]

    if search_query:
        filtered = [entry for entry in filtered if search_query.lower() in entry.read_name.lower()]

    return filtered[: int(max_reads)]


def _render_summary_panel(
    record: Dict[str, object],
    motif_colors: Dict[int, str],
    motif_names: Sequence[str],
) -> None:
    def _format_stat(value: object) -> str:
        if value is None:
            return "—"
        value_str = str(value)
        return value_str if value_str.strip() not in {"", "."} else "—"

    if "igv_summary_css_v13" not in st.session_state:
        st.markdown(
            """
            <style>
            .igv-summary-panel {
                margin: 12px 0 16px 0;
                display: grid;
                gap: 10px;
                grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
                align-items: stretch;
            }
            .igv-summary-card {
                position: relative;
                background: radial-gradient(circle at top left, rgba(59,130,246,0.16), rgba(191,219,254,0.08) 60%, rgba(241,245,249,0.4));
                border: 1px solid rgba(96,165,250,0.42);
                border-radius: 12px;
                padding: 10px 14px;
                box-shadow:
                    inset 0 0 0 1px rgba(255,255,255,0.5),
                    0 6px 14px rgba(15,23,42,0.06),
                    0 1px 3px rgba(59,130,246,0.08);
                display: flex;
                flex-direction: column;
                gap: 4px;
                overflow: hidden;
            }
            .igv-summary-card::after {
                content: "";
                position: absolute;
                inset: 0;
                background: linear-gradient(120deg, transparent, rgba(59,130,246,0.18), transparent);
                opacity: 0;
                transition: opacity 0.25s ease;
            }
            .igv-summary-card:hover::after {
                opacity: 1;
            }
            .igv-summary-card:hover {
                transform: translateY(-1px);
                box-shadow:
                    inset 0 0 0 1px rgba(255,255,255,0.5),
                    0 10px 18px rgba(15,23,42,0.08),
                    0 2px 4px rgba(59,130,246,0.12);
            }
            .igv-summary-card .label {
                font-size: 0.64rem;
                font-weight: 650;
                letter-spacing: 0.05em;
                text-transform: uppercase;
                color: rgba(51,65,85,0.78);
            }
            .igv-summary-card .value {
                font-size: 1.02rem;
                font-weight: 720;
                color: rgba(15,23,42,0.9);
            }
            .igv-summary-card .subtext {
                font-size: 0.62rem;
                color: rgba(71,85,105,0.66);
            }
            .igv-scale-bar,
            .igv-scale-track,
            .igv-scale-track-inner,
            .igv-scale-tick,
            .igv-scale-tick-label {
                display: none !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        st.session_state["igv_summary_css_v11"] = True

    summary_cards = [
        ("Reference CN", _format_stat(record.get("ref_CN") or record.get("CN_ref")), "region copy"),
        (
            "Haplotype 1 CN",
            _format_stat(record.get("CN_H1") or record.get("CN_H")),
            "reads: " + _format_stat(record.get("supported_reads_h1")),
        ),
        (
            "Haplotype 2 CN",
            _format_stat(record.get("CN_H2")),
            "reads: " + _format_stat(record.get("supported_reads_h2")),
        ),
        ("Genotype", _format_stat(record.get("gt")), None),
    ]
    summary_html_parts: List[str] = ['<div class="igv-summary-panel">']
    for label, value, subtext in summary_cards:
        summary_html_parts.append(
            f'<div class="igv-summary-card">'
            f'<span class="label">{escape(label)}</span>'
            f'<span class="value">{escape(value)}</span>'
        )
        if subtext and "—" in subtext:
            subtext = None
        if subtext:
            summary_html_parts.append(f'<span class="subtext">{escape(subtext)}</span>')
        summary_html_parts.append("</div>")
    summary_html_parts.append("</div>")
    st.markdown("".join(summary_html_parts), unsafe_allow_html=True)

    motif_legend_html(
        record.get("motif_ids_ref", []),
        motif_colors,
        motif_names,
    )




def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return f"rgba({r}, {g}, {b}, {alpha})"
    return f"rgba(102, 126, 234, {alpha})"


def _build_scale_bar(
    length: int,
    *,
    label: Optional[str] = None,
    compact: bool = False,
    leading_padding: int = 0,
    trailing_padding: int = 0,
) -> str:
    del length, label, compact, leading_padding, trailing_padding
    return ""


def _render_read_sequences(
    region: str,
    record: Dict[str, object],
    entries: Sequence[ReadEntry],
) -> None:
    motif_names = record.get("motifs", [])
    if not motif_names:
        st.info("No motif annotations available for this region.")
        return
    motif_colors = utils.get_color_palette(len(record['motifs']))
    motif_colors = {idx: color for idx, color in enumerate(motif_colors)}

    reference_track = {
        "sequence": record.get("ref_allele", ""),
        "motif_ids": record.get("motif_ids_ref", []),
        "spans": record.get("spans", [""])[0],
        "label": "Reference",
    }

    clustered: Dict[str, List[ReadEntry]] = {}
    for entry in entries:
        clustered.setdefault(entry.cluster, []).append(entry)

    # force CSS to reinject after UI changes so styles stay in sync
    st.session_state.pop("_igv_track_css_v10", None)

    cluster_palette = utils.get_color_palette(max(len(clustered), 1) + 2)
    cluster_backgrounds: Dict[str, str] = {}
    for idx, cluster_name in enumerate(sorted(clustered.keys())):
        cluster_backgrounds[cluster_name] = _hex_to_rgba(cluster_palette[(idx + 1) % len(cluster_palette)], 0.22)

    read_tracks: List[Dict[str, object]] = []
    for cluster_name in sorted(clustered.keys()):
        for entry in sorted(clustered[cluster_name], key=lambda e: (e.hp, e.read_name)):
            if not entry.sequence:
                continue
            read_tracks.append(
                {
                    "sequence": entry.sequence,
                    "motif_ids": entry.motif_ids,
                    "spans": entry.spans,
                    "cluster": cluster_name,
                    "meta": f"Read: {entry.read_name} | Cluster: {cluster_name} | hp{entry.hp}",
                }
            )

    max_sequence_length = len(reference_track["sequence"] or "")
    for track in read_tracks:
        max_sequence_length = max(max_sequence_length, len(track.get("sequence", "") or ""))
    max_sequence_length = max(max_sequence_length, 1)

    tab_segments, tab_sequences = st.tabs(
        ["Segment blocks", "Sequence strings"]
    )

    with tab_segments:
        _render_summary_panel(record, motif_colors, motif_names)
        _render_igv_tracks(
            reference_track,
            read_tracks,
            motif_colors,
            motif_names,
            cluster_backgrounds,
            max_sequence_length,
            show_sequences=False,
            zoom_profile={"mode": "segments"},
        )

    with tab_sequences:
        _render_summary_panel(record, motif_colors, motif_names)
        view_presets: Dict[str, Dict[str, object]] = {
            "Whole sequence fit": {
                "scale": 1.0,
                "font_multiplier": 1.0,
                "letter_spacing": 0.06,
                "line_height": 1.44,
                "flex_scale": 1.0,
                "step_multiplier": 1.0,
                "mode": "fit",
                "scrollable": False,
                "clamp_inner": True,
            },
            "Scroll to explore": {
                "scale": 1.0,
                "font_multiplier": 1.18,
                "letter_spacing": 0.022,
                "line_height": 1.64,
                "flex_scale": 1.0,
                "step_multiplier": 2.15,
                "mode": "scroll",
                "scrollable": True,
            },
        }
        view_key = f"{region}_sequence_view_mode"
        default_view = st.session_state.get(view_key, "Whole sequence fit")
        if default_view not in view_presets:
            default_view = "Whole sequence fit"
        sequence_view_mode = st.radio(
            "Sequence view mode",
            options=list(view_presets.keys()),
            index=list(view_presets.keys()).index(default_view),
            key=view_key,
            help="Fit full sequences inside the panel or switch to a scrollable, high-detail layout.",
        )
        zoom_profile = dict(view_presets[sequence_view_mode])
        st.caption(
            "Showing full width" if sequence_view_mode == "Whole sequence fit"
            else "Scroll horizontally to inspect the sequence in detail"
        )
        _render_igv_tracks(
            reference_track,
            read_tracks,
            motif_colors,
            motif_names,
            cluster_backgrounds,
            max_sequence_length,
            show_sequences=True,
            zoom_profile=zoom_profile,
        )

def _render_igv_tracks(
    reference_track: Dict[str, str],
    read_tracks: Sequence[Dict[str, object]],
    motif_colors: Dict[int, str],
    motif_names: Sequence[str],
    cluster_backgrounds: Dict[str, str],
    max_sequence_length: int,
    show_sequences: bool,
    zoom_profile: Optional[Mapping[str, Any]] = None,
) -> None:
    profile = _normalize_zoom_profile(zoom_profile)
    sequence_zoom = profile["scale"]
    hover_group = f"igv-hover-{uuid.uuid4().hex}"
    container_id = f"igv-stack-{uuid.uuid4().hex}"
    default_banner_text = "Hover a sequence block to see details"
    default_banner_text_html = escape(default_banner_text)
    
    html_parts: List[str] = [
        """
        <style>
            .igv-stack {
                display: flex;
                flex-direction: column;
                gap: 26px;
                margin: 12px 0 28px 0;
                position: relative;
                z-index: 1;
            }
            .igv-track-body {
                position: relative;
                height: 22px;
                width: 100%;
                border-radius: 1px;
                background: linear-gradient(180deg, rgba(255,255,255,1) 0%, rgba(241,245,249,0.9) 100%);
                border: 1px solid rgba(148, 163, 184, 0.55);
                box-shadow: inset 0 0 0 1px rgba(148,163,184,0.18);
                overflow: visible;
                z-index: 1;
            }
            .igv-track-body.reference {
                border: 1px solid rgba(51,65,85,0.85);
                box-shadow: inset 0 0 0 1px rgba(51,65,85,0.45), 0 10px 18px rgba(15,23,42,0.12);
            }
            .igv-track-entry {
                display: flex;
                flex-direction: column;
                gap: 0;
                width: 100%;
                min-width: 0;
                overflow: hidden;
            }
            .igv-sequence-group {
                width: 100%;
                max-width: 100%;
                overflow-x: hidden;
                padding: 10px 12px 12px;
                border-radius: 12px;
                border: 1px solid rgba(148,163,184,0.32);
                background: linear-gradient(180deg, rgba(248,250,252,0.98), rgba(226,232,240,0.58));
                box-shadow:
                    inset 0 0 0 1px rgba(255,255,255,0.55),
                    0 16px 34px rgba(15,23,42,0.08);
                box-sizing: border-box;
                --igv-sequence-length: 1;
                --igv-sequence-font: 0.74rem;
                --igv-sequence-step: 12px;
                --igv-sequence-letter-spacing: 0.018em;
                --igv-sequence-line-height: 1.52;
                --igv-sequence-flex-scale: 1;
            }
            .igv-sequence-group.is-zoomed {
                overflow-x: auto;
            }
            .igv-sequence-group.is-scrollable {
                background: linear-gradient(180deg, rgba(248,250,252,0.98), rgba(203,213,225,0.6));
            }
            .igv-sequence-group.is-clamped {
                overflow-x: hidden;
            }
            .igv-sequence-group::-webkit-scrollbar {
                height: 6px;
            }
            .igv-sequence-group::-webkit-scrollbar-thumb {
                background: rgba(100,116,139,0.35);
                border-radius: 999px;
            }
            .igv-sequence-group-inner {
                min-width: calc(var(--igv-sequence-length, 1) * var(--igv-sequence-step, 12px));
                display: flex;
                flex-direction: column;
                gap: 6px;
                transition: transform 0.25s ease;
            }
            .igv-sequence-group-inner.is-clamped {
                min-width: 100% !important;
                max-width: 100%;
            }
            .igv-sequence-group-inner.is-scrollable {
                padding-bottom: 4px;
            }
            .igv-sequence-row {
                display: flex;
                flex-direction: column;
                gap: 4px;
                transform-origin: left center;
                transition: transform 0.24s ease;
            }
            .igv-sequence-group[data-zoom-mode="fit"] .igv-sequence-row {
                transform: scaleY(0.96);
            }
            .igv-sequence-group[data-zoom-mode="scroll"] .igv-sequence-row {
                transform: scaleY(1.05);
            }
            .igv-sequence-group .igv-scale-bar {
                display: none;
            }
            .igv-sequence-line {
                display: flex;
                align-items: stretch;
                gap: 1px;
                white-space: nowrap;
                font-family: "JetBrains Mono", "Fira Code", "Courier New", monospace;
                font-size: var(--igv-sequence-font, 0.74rem);
                line-height: var(--igv-sequence-line-height, 1.52);
                letter-spacing: var(--igv-sequence-letter-spacing, 0.018em);
                color: rgba(30,41,59,0.95);
                transition: font-size 0.22s ease, letter-spacing 0.22s ease;
                transform: scaleX(var(--igv-sequence-fit, 1));
                transform-origin: left center;
            }
            .igv-sequence-chunk {
                display: inline-flex;
                align-items: center;
                padding: 0 2px;
                margin-right: 1px;
                border-radius: 4px;
                border: 1px solid rgba(148,163,184,0.35);
                background: linear-gradient(180deg, rgba(148,163,184,0.22), rgba(148,163,184,0.35));
                transition: transform 0.18s ease, box-shadow 0.18s ease, opacity 0.18s ease;
                color: rgba(17,24,39,0.9);
            }
            .igv-sequence-group[data-zoom-mode="overview"] .igv-sequence-chunk {
                opacity: 0.9;
            }
            .igv-sequence-group[data-zoom-mode="inspect"] .igv-sequence-chunk {
                box-shadow: 0 6px 14px rgba(15,23,42,0.14);
            }
            .igv-sequence-padding {
                background: linear-gradient(180deg, rgba(148,163,184,0.08), rgba(148,163,184,0.14)) !important;
                border-color: rgba(148,163,184,0.22) !important;
            }
            .igv-block-padding {
                background: linear-gradient(180deg, rgba(148,163,184,0.12), rgba(148,163,184,0.18)) !important;
                border-color: rgba(148,163,184,0.25) !important;
            }
            .igv-sequence-chunk.interruption {
                background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%) !important;
                border-color: rgba(127, 29, 29, 0.9);
                color: #fef2f2;
                box-shadow: inset 0 0 0 1px rgba(254,226,226,0.8);
            }
            .igv-sequence-chunk:hover:not(.interruption),
            .igv-sequence-chunk:focus-visible:not(.interruption) {
                box-shadow: inset 0 0 0 1px rgba(255,255,255,0.75), 0 0 0 1px rgba(59,130,246,0.35);
                transform: translateY(-1px);
            }
            .igv-sequence-chunk.interruption:hover,
            .igv-sequence-chunk.interruption:focus-visible {
                box-shadow: inset 0 0 0 1px rgba(254,242,242,0.9), 0 0 0 1px rgba(127,29,29,0.55);
                transform: translateY(-1px);
            }
            .igv-sequence-placeholder {
                opacity: 0.65;
                font-style: italic;
            }
            .igv-reference-block,
            .igv-cluster-block {
                position: relative;
                display: flex;
                align-items: center;
                gap: 1px;
                padding: 6px 8px 8px;
                border-radius: 0px;
                background: linear-gradient(135deg, rgba(255,255,255,0.98), rgba(226,232,240,0.32));
                box-shadow: 0 1px 6px rgba(15,23,42,0.05);
                border: 1px solid rgba(148,163,184,0.15);
                overflow: visible;
                z-index: auto;
            }
            .igv-reference-block {
                border-color: rgba(51,65,85,0.3);
            }
            .igv-cluster-block {
                border-color: rgba(71,85,105,0.24);
            }
            .igv-side-label {
                min-width: 92px;
                display: flex;
                align-items: center;
                justify-content: flex-end;
                font-size: 0.76rem;
                font-weight: 700;
                color: rgba(30,41,59,0.72);
                letter-spacing: 0.08em;
                text-transform: uppercase;
                padding-right: 4px;
            }
            .igv-reference-block .igv-side-label {
                color: rgba(30,41,59,0.84);
            }
            .igv-reference-body,
            .igv-cluster-body {
                flex: 1;
                display: flex;
                flex-direction: column;
                gap: 0px;
                overflow: hidden;
            }
            .igv-hover-banner {
                align-self: stretch;
                padding: 10px 14px;
                border-radius: 10px;
                background: linear-gradient(180deg, rgba(241,245,249,0.92), rgba(226,232,240,0.6));
                border: 1px solid rgba(148,163,184,0.55);
                color: rgba(15,23,42,0.9);
                font-size: 0.8rem;
                line-height: 1.5;
                margin-bottom: 10px;
                box-shadow: inset 0 0 0 1px rgba(255,255,255,0.55), 0 8px 16px rgba(15,23,42,0.06);
                min-height: 32px;
                display: flex;
                align-items: center;
            }
            .igv-hover-banner.is-empty {
                color: rgba(30,41,59,0.62);
                border-style: dashed;
                background: linear-gradient(180deg, rgba(248,250,252,0.95), rgba(226,232,240,0.48));
            }
            .igv-hover-placeholder {
                opacity: 0.75;
            }
            .igv-track-body-inner {
                position: relative;
                width: 100%;
                height: 100%;
                display: flex;
                gap: 1px;
                align-items: stretch;
                padding: 0 1px;
                background: linear-gradient(180deg, rgba(17,24,39,0.02) 0%, rgba(148,163,184,0.08) 100%);
                border-radius: 4px;
                overflow: visible;
            }
            .igv-block {
                flex: 1 0 auto;
                border-radius: 3px;
                box-shadow: inset 0 0 0 1px rgba(15,23,42,0.08), 0 2px 3px rgba(15,23,42,0.12);
                position: relative;
                min-width: 1px;
                transition: transform 0.15s ease, box-shadow 0.15s ease, opacity 0.15s ease;
                overflow: visible;
                z-index: 1;
            }
            .igv-block-interruption {
                background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%) !important;
                border: 1px solid rgba(127, 29, 29, 0.95);
                box-shadow: inset 0 0 0 1px rgba(254, 226, 226, 0.85), 0 0 0 1px rgba(127, 29, 29, 0.4);
                min-width: 6px;
                position: relative;
            }
            .igv-block-interruption::before {
                content: "";
                position: absolute;
                inset: -2px;
                border-radius: 4px;
                border: 2px solid rgba(239, 68, 68, 0.6);
                opacity: 0;
                transition: opacity 0.15s ease;
                pointer-events: none;
            }
            .igv-block-interruption::after {
                content: attr(data-label);
                position: absolute;
                inset: 1px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 0.58rem;
                font-weight: 700;
                letter-spacing: 0.08em;
                color: rgba(248,250,252,0.95);
                text-transform: uppercase;
                pointer-events: none;
                text-shadow: 0 1px 2px rgba(15,23,42,0.45);
            }
            .igv-block-interruption:hover::before,
            .igv-block-interruption:focus-visible::before {
                opacity: 1;
            }
            .igv-hoverable {
                cursor: pointer;
            }
            .igv-track-body:hover .igv-block:not(.igv-block-interruption) {
                box-shadow: inset 0 0 0 1px rgba(255,255,255,0.5), 0 5px 12px rgba(15,23,42,0.18);
                transform: translateY(-1px);
            }
            .igv-scale-bar {
                width: 100%;
            }
            .igv-scale-label {
                font-size: 0.64rem;
                font-weight: 600;
                color: rgba(30,41,59,0.7);
                letter-spacing: 0.06em;
                margin-bottom: 3px;
            }
            .igv-scale-track {
                position: relative;
                width: 100%;
                height: 8px;
                border-radius: 999px;
                background: none;
            }
            .igv-scale-track-inner {
                position: absolute;
                top: 0;
                left: 0;
                height: 100%;
                border-radius: inherit;
                background: linear-gradient(90deg, rgba(148,163,184,0.22), rgba(59,130,246,0.32));
            }
            .igv-scale-tick {
                position: absolute;
                top: -3px;
                width: 1.5px;
                height: 14px;
                background: rgba(30,41,59,0.55);
                border-radius: 999px;
            }
            .igv-scale-tick-label {
                position: absolute;
                top: 14px;
                left: 50%;
                transform: translateX(-50%);
                font-size: 0.6rem;
                font-weight: 500;
                color: rgba(30,41,59,0.65);
                white-space: nowrap;
            }
            .igv-cluster-scale .igv-scale-tick-label {
                font-size: 0.54rem;
                color: rgba(30,41,59,0.58);
            }
            .igv-reference-block .igv-scale-bar {
                margin-top: 6px !important;
            }
            .igv-cluster-scale {
                margin-top: 8px;
                padding-top: 6px;
                border-top: 1px solid rgba(148,163,184,0.35);
            }
        </style>
        """
    ]
    
    html_parts.append(f'<div id="{container_id}" class="igv-stack">')
    html_parts.append(
        f'<div class="igv-hover-banner is-empty" id="{container_id}-banner">'
        f'{default_banner_text_html}</div>'
    )

    ref_entry_parts: List[str] = []
    ref_sequence_lines: List[str] = []
    ref_sequence_font = 0.9
    ref_sequence_length = len(reference_track["sequence"] or "")
    if not show_sequences:
        ref_segments = _build_segments_html(
            reference_track["sequence"],
            reference_track["motif_ids"],
            reference_track["spans"],
            motif_colors,
            motif_names,
            reference_track["label"],
            max_sequence_length,
            hover_group,
        )
        ref_entry_parts.append(
            f'<div class="igv-track-body reference">{ref_segments}</div>'
        )
    if show_sequences:
        ref_line_html, ref_line_font, ref_line_length = _build_sequence_text_html(
            reference_track["sequence"],
            reference_track["motif_ids"],
            reference_track["spans"],
            motif_colors,
            motif_names,
            reference_track["label"],
            hover_group,
            zoom_profile=profile,
        )
        ref_sequence_lines.append(ref_line_html)
        ref_sequence_font = max(ref_sequence_font, ref_line_font)
        ref_sequence_length = max(ref_sequence_length, ref_line_length)
    ref_entry_html = "".join(ref_entry_parts)
    ref_sequence_container = ""
    if show_sequences and ref_sequence_lines:
        ref_sequence_container = _wrap_sequence_group(
            ref_sequence_lines,
            sequence_length=max(ref_sequence_length, 1),
            sequence_font=ref_sequence_font,
            zoom_profile=profile,
        )
    elif not show_sequences:
        ref_sequence_container = ""

    html_parts.append(
        f"""
        <div class="igv-reference-block">
            <div class="igv-side-label">Reference</div>
            <div class="igv-reference-body">
                <div class="igv-track-entry">{ref_entry_html}{ref_sequence_container}</div>
            </div>
        </div>
        """
    )

    cluster_tracks: Dict[str, List[Dict[str, str]]] = {}
    for track in read_tracks:
        cluster_tracks.setdefault(track["cluster"], []).append(track)

    for cluster_name in sorted(cluster_tracks.keys()):
        cluster_entries = cluster_tracks[cluster_name]
        cluster_max_length = max(
            max(len(track.get("sequence", "") or "") for track in cluster_entries),
            1,
        )
        rgba_bg = cluster_backgrounds.get(cluster_name, "rgba(148,163,184,0.18)")
        cluster_body_parts: List[str] = []
        cluster_sequence_lines: List[str] = []
        cluster_sequence_font = 0.9
        for track in cluster_entries:
            track_entry_parts: List[str] = []
            if not show_sequences:
                segments_html = _build_segments_html(
                    track["sequence"],
                    track["motif_ids"],
                    track["spans"],
                    motif_colors,
                    motif_names,
                    track["meta"],
                    max_sequence_length,
                    hover_group,
                )
                track_entry_parts.append(
                    f'<div class="igv-track-body">{segments_html}</div>'
                )
            if show_sequences:
                line_html, line_font, line_length = _build_sequence_text_html(
                    track["sequence"],
                    track["motif_ids"],
                    track["spans"],
                    motif_colors,
                    motif_names,
                    track["meta"],
                    hover_group,
                    zoom_profile=profile,
                )
                cluster_sequence_lines.append(line_html)
                cluster_sequence_font = max(cluster_sequence_font, line_font)
                cluster_max_length = max(cluster_max_length, line_length)
            cluster_body_parts.append(
                f'<div class="igv-track-entry">{"".join(track_entry_parts)}</div>'
            )
        if show_sequences and cluster_sequence_lines:
            cluster_body_parts.append(
                _wrap_sequence_group(
                    cluster_sequence_lines,
                    sequence_length=max(cluster_max_length, 1),
                    sequence_font=cluster_sequence_font,
                    zoom_profile=profile,
                )
            )
        html_parts.append(
            f'''
            <div class="igv-cluster-block" style="background: linear-gradient(135deg, rgba(255,255,255,0.97), {rgba_bg}); box-shadow: inset 0 0 0 1px {rgba_bg}; border: 1px solid rgba(71,85,105,0.35);">
                <div class="igv-side-label">{escape(cluster_name)}</div>
                <div class="igv-cluster-body">
                    {''.join(cluster_body_parts)}
                </div>
            </div>
            '''
        )

    html_parts.append('</div>')
    
    script = f"""
    <script>
    (function() {{
        const container = document.getElementById('{container_id}');
        const banner = document.getElementById('{container_id}-banner');
        
        if (!container || !banner) return;
        
        // Store the original banner text for reset
        const originalBannerText = banner.innerHTML;
        
        function decodeBase64(encoded) {{
            try {{
                return atob(encoded);
            }} catch (e) {{
                try {{
                    return atob(decodeURIComponent(encoded));
                }} catch (e2) {{
                    return '';
                }}
            }}
        }}
        
        function handleMouseEnter(event) {{
            const block = event.target.closest('.igv-hoverable');
            if (!block) return;
            
            const tooltipEncoded = block.getAttribute('data-tooltip-b64');
            if (!tooltipEncoded) return;
            
            const tooltipHtml = decodeBase64(tooltipEncoded);
            if (tooltipHtml) {{
                banner.innerHTML = tooltipHtml;
                banner.classList.remove('is-empty');
            }}
        }}
        
        function handleMouseLeave(event) {{
            // Only reset if we're not entering another hoverable element
            const related = event.relatedTarget;
            if (!related || !related.closest || !related.closest('.igv-hoverable')) {{
                banner.innerHTML = originalBannerText;
                banner.classList.add('is-empty');
            }}
        }}
        
        function handleFocus(event) {{
            handleMouseEnter(event);
        }}
        
        function handleBlur(event) {{
            setTimeout(() => {{
                const active = document.activeElement;
                if (!active || !active.closest('.igv-hoverable')) {{
                    banner.innerHTML = originalBannerText;
                    banner.classList.add('is-empty');
                }}
            }}, 10);
        }}
        
        // Use event delegation on the container
        container.addEventListener('mouseover', handleMouseEnter);
        container.addEventListener('mouseout', handleMouseLeave);
        container.addEventListener('focusin', handleFocus);
        container.addEventListener('focusout', handleBlur);
        
        // Also add direct event listeners to hoverable elements for better reliability
        const hoverableElements = container.querySelectorAll('.igv-hoverable');
        hoverableElements.forEach(element => {{
            element.addEventListener('mouseenter', handleMouseEnter);
            element.addEventListener('mouseleave', handleMouseLeave);
            element.addEventListener('focus', handleFocus);
            element.addEventListener('blur', handleBlur);
        }});
        
        // Cleanup function
        window.cleanupHover_{container_id} = function() {{
            container.removeEventListener('mouseover', handleMouseEnter);
            container.removeEventListener('mouseout', handleMouseLeave);
            container.removeEventListener('focusin', handleFocus);
            container.removeEventListener('focusout', handleBlur);
            
            hoverableElements.forEach(element => {{
                element.removeEventListener('mouseenter', handleMouseEnter);
                element.removeEventListener('mouseleave', handleMouseLeave);
                element.removeEventListener('focus', handleFocus);
                element.removeEventListener('blur', handleBlur);
            }});
        }};
    }})();
    </script>
    """
    
    html_parts.append(script)
    st.html("".join(html_parts))

def get_region_from_record(record: Dict[str, object]) -> str:
    chrom = record.get("chr", "")
    pos = record.get("pos")
    stop = record.get("stop")
    if chrom and pos is not None and stop is not None:
        return f"{chrom}:{pos}-{stop}"
    return str(record.get("id", ""))


def render_read_visualization_tab(region: str, record: Dict[str, object]) -> None:
    _ensure_full_width_layout()
    ready = _ensure_read_support_ready()
    if not ready:
        st.info("Provide a read-level TSV alongside the VCF to view read-based visualization.")
        return
    tsv_path, regions = ready

    candidate_regions = [region]
    record_id = record.get("id")
    if record_id and record_id not in candidate_regions:
        candidate_regions.append(record_id)
    derived_region = get_region_from_record(record)
    if derived_region and derived_region not in candidate_regions:
        candidate_regions.append(derived_region)

    entries: List[ReadEntry] = []
    matched_region = None
    for candidate in candidate_regions:
        if not candidate:
            continue
        entries = _get_region_entries(tsv_path, candidate)
        if entries:
            matched_region = candidate
            break

    if not entries:
        st.info("No read-level data available for this region.")
        return

    # st.markdown(
    #     f"<div style='font-size:0.9rem; color:#4b5563;'>Displaying <strong>{len(entries)}</strong> reads for <code>{matched_region or region}</code></div>",
    #     unsafe_allow_html=True,
    # )
    # st.caption(
    #     f"{len(entries)} reads available • TSV source: {tsv_path}"
    # )

    filtered_entries = _filter_reads(entries, matched_region or region)
    _render_read_sequences(matched_region or region, record, filtered_entries)


def _build_segments_html(
    sequence: str,
    motif_ids: Sequence[str],
    spans: str,
    motif_colors: Dict[int, str],
    motif_names: Sequence[str],
    track_meta: str,
    max_sequence_length: int,
    hover_group: str,
) -> str:
    sequence = sequence or ""
    sequence_length = len(sequence)
    base_length = max(int(max_sequence_length), 1)
    effective_sequence_length = sequence_length + 60
    effective_max_length = base_length + 60
    width_ratio = (
        effective_sequence_length / effective_max_length if effective_max_length else 0
    )
    width_pct = max(width_ratio * 100, 4.0 if effective_sequence_length else 4.0)

    parts: List[str] = [
        f'<div class="igv-track-body-inner" '
        f'style="width:{width_pct:.4f}%; max-width:{width_pct:.4f}%; margin-right:auto;" '
        f'data-hover-group="{hover_group}">',
    ]
    def append_segment(
        length_bp: int,
        color: str,
        tooltip: str,
        extra_class: str = "",
        include_meta: bool = True,
        extra_attrs: Optional[Mapping[str, str]] = None,
    ) -> None:
        if include_meta and track_meta:
            payload = f"{track_meta}\\n{tooltip}" if tooltip else track_meta
        else:
            payload = tooltip
        safe_lines = [escape(line) for line in payload.split("\\n")]
        tooltip_html = "<br>".join(safe_lines)
        tooltip_encoded = base64.b64encode(tooltip_html.encode("utf-8")).decode("ascii")
        tooltip_attr = escape(tooltip_encoded, quote=True)
        class_tokens = ["igv-block", "igv-hoverable"]
        if extra_class:
            class_tokens.append(extra_class)
        attr_pairs: List[Tuple[str, str]] = [
            ("class", " ".join(class_tokens)),
            (
                "style",
        f"flex:calc({length_bp} * var(--igv-sequence-flex-scale, 1)) 0 auto; background:{color};",
            ),
            ("data-hover-group", hover_group),
            ("tabindex", "0"),
            ("data-tooltip-b64", tooltip_attr),
        ]
        if extra_attrs:
            for attr_name, attr_value in extra_attrs.items():
                if attr_value is None:
                    continue
                attr_pairs.append((attr_name, escape(str(attr_value), quote=True)))
        attr_html = " ".join(f'{name}="{value}"' for name, value in attr_pairs)
        parts.append(f"<span {attr_html}></span>")

    padding_color = "rgba(148, 163, 184, 0.18)"
    append_segment(
        30,
        padding_color,
        "",
        extra_class="igv-block-padding",
        include_meta=False,
    )

    if sequence_length <= 0:
        tooltip = track_meta or "No sequence data"
        append_segment(
            1,
            "rgba(107,114,128,0.45)",
            tooltip,
            "igv-block-interruption",
            include_meta=False,
            extra_attrs={"data-label": ""},
        )
        parts.append("</div>")
        return "".join(parts)

    motif_ranges = parse_motif_range(spans) if spans else []
    pointer = 0

    for idx, (start, end) in enumerate(motif_ranges):
        start = max(0, start)
        end = min(sequence_length - 1, end)
        if start > pointer:
            interruption_seq = sequence[pointer:start]
            tooltip = (
                f"Interruption\\nBases: {pointer + 1}-{start}\\n"
                f"Sequence: {interruption_seq}"
            )
            append_segment(
                start - pointer,
                "rgba(239,68,68,0.65)",
                tooltip,
                "igv-block-interruption",
                extra_attrs={"data-label": ""},
            )

        motif_id = 0
        if idx < len(motif_ids):
            try:
                motif_id = int(motif_ids[idx])
            except (TypeError, ValueError):
                motif_id = 0
        color = motif_colors.get(motif_id)
        if color is None:
            color = motif_colors[motif_id]
            motif_colors[motif_id] = color
        motif_name = (
            motif_names[motif_id]
            if 0 <= motif_id < len(motif_names)
            else f"Motif {motif_id}"
        )
        tooltip = (
            f"{motif_name}\\nBases: {start + 1}-{end + 1}\\n"
            f"Length: {end - start + 1} bp\\n"
            f"Sequence: {sequence[start:end+1]}"
        )
        append_segment(end - start + 1, color, tooltip)
        pointer = end + 1

    if pointer < sequence_length:
        tail_seq = sequence[pointer:]
        tooltip = (
            f"Interruption\\nBases: {pointer + 1}-{sequence_length}\\n"
            f"Sequence: {tail_seq}"
        )
        append_segment(
            sequence_length - pointer,
            "rgba(239,68,68,0.65)",
            tooltip,
            "igv-block-interruption",
            extra_attrs={"data-label": ""},
        )

    append_segment(
        30,
        padding_color,
        "",
        extra_class="igv-block-padding",
        include_meta=False,
    )

    parts.append("</div>")
    return "".join(parts)


def _build_sequence_text_html(
    sequence: str,
    motif_ids: Sequence[str],
    spans: str,
    motif_colors: Dict[int, str],
    motif_names: Sequence[str],
    track_meta: str,
    hover_group: str,
    *,
    zoom_profile: Mapping[str, Any],
) -> Tuple[str, float, int]:
    sequence = sequence or ""
    sequence_length = len(sequence)
    sequence_zoom = float(zoom_profile.get("scale", 1.0))
    if sequence_length <= 0:
        base_fit_font = 0.9
    else:
        base_fit_font = min(0.9, max(0.12, 72.0 / sequence_length))
    zoomed_font = min(3.0, max(0.12, base_fit_font * sequence_zoom))
    clamp_inner = bool(zoom_profile.get("clamp_inner", False))
    scrollable = bool(zoom_profile.get("scrollable", False))

    if not sequence:
        line_html = (
            '<div class="igv-sequence-line">'
            '<span class="igv-sequence-placeholder">No sequence data</span>'
            "</div>"
        )
        return line_html, zoomed_font, sequence_length

    def make_tooltip(payload: str, include_meta: bool = True) -> str:
        base_payload = payload or ""
        if include_meta and track_meta:
            meta = track_meta.strip()
            if base_payload:
                combined = f"{meta}\\n{base_payload}"
            else:
                combined = meta
        else:
            combined = base_payload or track_meta or ""
        safe_lines = [escape(line) for line in combined.split("\\n")]
        tooltip_html = "<br>".join(safe_lines)
        encoded = base64.b64encode(tooltip_html.encode("utf-8")).decode("ascii")
        return escape(encoded, quote=True)

    def make_chunk(
        text: str,
        tooltip_payload: str,
        *,
        class_name: str = "",
        style: str = "",
        include_meta: bool = True,
        length_units: Optional[int] = None,
    ) -> str:
        if text is None:
            return ""
        tooltip_attr = make_tooltip(tooltip_payload, include_meta=include_meta)
        classes = ["igv-sequence-chunk", "igv-hoverable"]
        if class_name:
            classes.append(class_name)
        attr_parts = [
            ("class", " ".join(classes)),
            ("data-hover-group", hover_group),
            ("tabindex", "0"),
            ("data-tooltip-b64", tooltip_attr),
        ]
        style_parts: List[str] = []
        if length_units is not None:
            units = max(int(length_units), 1)
            if clamp_inner:
                style_parts.append(
                    f"flex:calc({units} * var(--igv-sequence-flex-scale, 1)) 0 auto;"
                )
            else:
                if text:
                    style_parts.append("flex:0 0 auto;")
                    style_parts.append("min-width:max-content;")
                else:
                    style_parts.append(
                        f"flex:calc({units} * var(--igv-sequence-flex-scale, 1)) 0 auto;"
                    )
        if style:
            style_parts.append(style)
        if style_parts:
            attr_parts.append(("style", " ".join(style_parts)))
        attr_html = " ".join(
            f'{name}="{escape(value, quote=True)}"' for name, value in attr_parts
        )
        return f"<span {attr_html}>{escape(text)}</span>"

    def motif_chunk_style(base_color: str) -> str:
        top = _hex_to_rgba(base_color, 0.25)
        bottom = _hex_to_rgba(base_color, 0.48)
        border = _hex_to_rgba(base_color, 0.65)
        return (
            f"background: linear-gradient(180deg, {top} 0%, {bottom} 100%); "
            f"border-color: {border}; color: rgba(15,23,42,0.96);"
        )

    chunk_parts: List[str] = []
    padding_style = (
        "background: linear-gradient(180deg, rgba(148,163,184,0.12), rgba(148,163,184,0.18)); "
        "border-color: rgba(148,163,184,0.25);"
    )
    chunk_parts.append(
        make_chunk(
            text="",
            tooltip_payload="",
            class_name="igv-sequence-padding",
            include_meta=False,
            length_units=30,
            style=padding_style,
        )
    )
    motif_ranges = parse_motif_range(spans) if spans else []
    sequence_length = len(sequence)

    if not motif_ranges:
        tooltip = f"Bases: 1-{sequence_length}\\nSequence: {sequence}"
        chunk_parts.append(
            make_chunk(
                sequence,
                tooltip,
                style=(
                    "background: linear-gradient(180deg, rgba(148,163,184,0.18) 0%, "
                    "rgba(148,163,184,0.3) 100%); border-color: rgba(148,163,184,0.45); "
                    "color: rgba(17,24,39,0.9);"
                ),
                length_units=sequence_length,
            )
        )
    else:
        pointer = 0
        for idx, (start, end) in enumerate(motif_ranges):
            start = max(0, start)
            end = min(sequence_length - 1, end)
            if start > pointer:
                interruption_seq = sequence[pointer:start]
                tooltip = (
                    f"Interruption\\nBases: {pointer + 1}-{start}\\n"
                    f"Sequence: {interruption_seq}"
                )
                chunk_parts.append(
                    make_chunk(
                        interruption_seq,
                        tooltip,
                        class_name="interruption",
                        style=(
                            "background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%); "
                            "border-color: rgba(127,29,29,0.9); color: #fef2f2;"
                        ),
                        length_units=start - pointer,
                    )
                )

            motif_id = 0
            if idx < len(motif_ids):
                try:
                    motif_id = int(motif_ids[idx])
                except (TypeError, ValueError):
                    motif_id = 0
            color = motif_colors.get(motif_id)
            if color is None:
                color = motif_colors[motif_id]
                motif_colors[motif_id] = color
            motif_name = (
                motif_names[motif_id]
                if 0 <= motif_id < len(motif_names)
                else f"Motif {motif_id}"
            )
            chunk_seq = sequence[start : end + 1]
            tooltip = (
                f"{motif_name}\\nBases: {start + 1}-{end + 1}\\n"
                f"Length: {end - start + 1} bp\\n"
                f"Sequence: {chunk_seq}"
            )
            chunk_parts.append(
                make_chunk(
                    chunk_seq,
                    tooltip,
                    class_name=f"motif-{motif_id}",
                    style=motif_chunk_style(color),
                    length_units=len(chunk_seq),
                )
            )
            pointer = end + 1

        if pointer < sequence_length:
            tail_seq = sequence[pointer:]
            tooltip = (
                f"Interruption\\nBases: {pointer + 1}-{sequence_length}\\n"
                f"Sequence: {tail_seq}"
            )
            chunk_parts.append(
                make_chunk(
                    tail_seq,
                    tooltip,
                    class_name="interruption",
                    style=(
                        "background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%); "
                        "border-color: rgba(127,29,29,0.9); color: #fef2f2;"
                    ),
                    length_units=sequence_length - pointer,
                )
            )

    chunk_parts.append(
        make_chunk(
            text="",
            tooltip_payload="",
            class_name="igv-sequence-padding",
            include_meta=False,
            length_units=30,
            style=padding_style,
        )
    )

    effective_length = sequence_length + 60

    sequence_html = "".join(chunk_parts)
    line_style = f"--igv-sequence-font:{zoomed_font:.4f}rem;"
    line_html = (
        f'<div class="igv-sequence-line" '
        f'style="{line_style}" '
        f'data-sequence-length="{effective_length}" '
        f'data-sequence-zoom="{sequence_zoom:.2f}">'
        f"{sequence_html}"
        "</div>"
    )
    return line_html, zoomed_font, effective_length


def _wrap_sequence_group(
    lines: Sequence[str],
    *,
    sequence_length: int,
    sequence_font: float,
    zoom_profile: Mapping[str, Any],
) -> str:
    sequence_length = max(int(sequence_length), 1)
    sequence_font = max(float(sequence_font), 0.12)
    flex_scale = max(float(zoom_profile.get("flex_scale", 1.0)), 0.25)
    font_multiplier = max(float(zoom_profile.get("font_multiplier", 1.0)), 0.4)
    effective_font = min(max(sequence_font * font_multiplier, 0.12), 2.8)
    letter_spacing = max(float(zoom_profile.get("letter_spacing", 0.016)), 0.004)
    line_height = max(float(zoom_profile.get("line_height", 1.45)), 1.1)
    step_multiplier = max(float(zoom_profile.get("step_multiplier", 1.6)), 0.8)
    step_length = max(effective_font * step_multiplier, 0.2)
    zoom_mode = str(zoom_profile.get("mode", "balanced"))
    scrollable = bool(zoom_profile.get("scrollable", False))
    clamp_inner = bool(zoom_profile.get("clamp_inner", False))

    group_classes = ["igv-sequence-group"]
    if scrollable:
        group_classes.append("is-zoomed")
    if scrollable:
        group_classes.append("is-scrollable")
    if clamp_inner:
        group_classes.append("is-clamped")

    style_tokens = [
        f"--igv-sequence-length:{sequence_length};",
        f"--igv-sequence-font:{effective_font:.4f}rem;",
        f"--igv-sequence-flex-scale:{flex_scale:.4f};",
        f"--igv-sequence-letter-spacing:{letter_spacing:.4f}em;",
        f"--igv-sequence-line-height:{line_height:.4f};",
        f"--igv-sequence-step:{step_length:.4f}rem;",
    ]
    fit_factor = 1.0
    if clamp_inner and sequence_length > 0:
        fit_factor = max(min(240.0 / max(sequence_length, 1), 1.0), 0.18)

    if clamp_inner:
        style_tokens.append("--igv-sequence-inner-max-width:100%;")
        style_tokens.append("--igv-sequence-scale-padding:0px;")
    else:
        style_tokens.append("--igv-sequence-scale-padding:30px;")
    style_tokens.append(f"--igv-sequence-fit:{fit_factor:.6f};")
    style_attr = " ".join(style_tokens)
    group_attr = (
        f'class="{" ".join(group_classes)}" '
        f'data-sequence-length="{sequence_length}" '
        f'data-zoom-mode="{escape(zoom_mode)}" '
        f'style="{style_attr}"'
    )
    rows_html = "".join(
        '<div class="igv-sequence-row">' + line + "</div>"
        for line in lines
    )
    inner_classes = ["igv-sequence-group-inner"]
    if clamp_inner:
        inner_classes.append("is-clamped")
    elif scrollable:
        inner_classes.append("is-scrollable")
    inner_parts = [
        f'<div class="{" ".join(inner_classes)}">'
        f"{rows_html}"
        "</div>"
    ]
    return f'<div {group_attr}>{"".join(inner_parts)}</div>'


def visualize_read_support() -> None:
    ready = _ensure_read_support_ready()
    if not ready:
        st.info("Provide a read-level TSV alongside the VCF to view read-based visualization.")
        return
    tsv_path, regions = ready
    if not regions:
        st.info("No read-level data found in the TSV.")
        return

    region = _select_region(regions)
    if not region:
        st.info("No regions found in the read-level TSV.")
        return

    vcf_path: Optional[str] = st.session_state.get("vcf_file_path")
    if not vcf_path:
        st.info("Load a VCF file to view read-level visualization.")
        return

    st.session_state.previous_region = region
    record = parsers.parse_record(vcf_path, region)
    if record is None:
        st.warning(f"No VCF record available for region {region}.")
        return

    entries = _get_region_entries(tsv_path, region)
    st.caption(
        f"{len(entries)} reads available • TSV source: {tsv_path}"
    )

    filtered_entries = _filter_reads(entries, region)
    _render_read_sequences(region, record, filtered_entries)


