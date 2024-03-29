"""
Taxonomic classification of reads
"""

import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

from dataclasses_json import dataclass_json
from flytekit import task
from latch import large_task, map_task, message, small_task, workflow
from latch.types import LatchFile

from wf.types import Sample, TaxonRank


@dataclass_json
@dataclass
class KaijuSample:
    sample_name: str
    read1: LatchFile
    read2: LatchFile
    kaiju_ref_db: LatchFile
    kaiju_ref_nodes: LatchFile
    kaiju_ref_names: LatchFile
    taxon_rank: TaxonRank


@dataclass_json
@dataclass
class KaijuOut:
    sample_name: str
    kaiju_out: LatchFile
    kaiju_ref_nodes: LatchFile
    kaiju_ref_names: LatchFile
    taxon_rank: TaxonRank


@dataclass_json
@dataclass
class KronaInput:
    sample_name: str
    krona_txt: LatchFile


@small_task
def organize_kaiju_inputs(
    samples: Sample,
    kaiju_ref_db: LatchFile,
    kaiju_ref_nodes: LatchFile,
    kaiju_ref_names: LatchFile,
    taxon_rank: TaxonRank,
) -> KaijuSample:
    return KaijuSample(
        read1=samples.read1,
        read2=samples.read2,
        sample_name=samples.sample_name,
        kaiju_ref_db=kaiju_ref_db,
        kaiju_ref_nodes=kaiju_ref_nodes,
        kaiju_ref_names=kaiju_ref_names,
        taxon_rank=taxon_rank,
    )


@large_task
def taxonomy_classification_task(kaiju_input: KaijuSample) -> KaijuOut:
    """Classify metagenomic reads with Kaiju"""

    sample_name = kaiju_input.sample_name
    output_name = f"{sample_name}_kaiju.out"
    kaiju_out = Path(output_name).resolve()

    _kaiju_cmd = [
        "kaiju",
        "-t",
        kaiju_input.kaiju_ref_nodes.local_path,
        "-f",
        kaiju_input.kaiju_ref_db.local_path,
        "-i",
        kaiju_input.read1.local_path,
        "-j",
        kaiju_input.read2.local_path,
        "-z",
        "96",
        "-o",
        str(kaiju_out),
    ]
    message(
        "info",
        {
            "title": "Taxonomically classifying reads with Kaiju",
            "body": f"Command: {' '.join(_kaiju_cmd)}",
        },
    )
    subprocess.run(_kaiju_cmd)

    return KaijuOut(
        sample_name=kaiju_input.sample_name,
        kaiju_out=LatchFile(
            str(kaiju_out), f"latch:///kaiju/{sample_name}/{output_name}"
        ),
        kaiju_ref_nodes=kaiju_input.kaiju_ref_nodes,
        kaiju_ref_names=kaiju_input.kaiju_ref_names,
        taxon_rank=kaiju_input.taxon_rank,
    )


@small_task
def kaiju2table_task(kaiju_out: KaijuOut) -> LatchFile:
    """Convert Kaiju output to TSV format"""

    sample_name = kaiju_out.sample_name
    output_name = f"{sample_name}_kaiju.tsv"
    kaijutable_tsv = Path(output_name).resolve()

    _kaiju2table_cmd = [
        "kaiju2table",
        "-t",
        kaiju_out.kaiju_ref_nodes.local_path,
        "-n",
        kaiju_out.kaiju_ref_names.local_path,
        "-r",
        kaiju_out.taxon_rank.value,
        "-p",
        "-e",
        "-o",
        str(kaijutable_tsv),
        kaiju_out.kaiju_out.local_path,
    ]

    subprocess.run(_kaiju2table_cmd)

    return LatchFile(
        str(kaijutable_tsv),
        f"latch:///kaiju/{sample_name}/{output_name}",
    )


@small_task
def kaiju2krona_task(kaiju_out: KaijuOut) -> KronaInput:
    """Convert Kaiju output to Krona-readable format"""

    sample_name = kaiju_out.sample_name
    output_name = f"{sample_name}_kaiju2krona.out"
    krona_txt = Path(output_name).resolve()

    _kaiju2krona_cmd = [
        "kaiju2krona",
        "-t",
        kaiju_out.kaiju_ref_nodes.local_path,
        "-n",
        kaiju_out.kaiju_ref_names.local_path,
        "-i",
        kaiju_out.kaiju_out.local_path,
        "-o",
        str(krona_txt),
    ]

    subprocess.run(_kaiju2krona_cmd)

    return KronaInput(
        sample_name=sample_name,
        krona_txt=LatchFile(
            str(krona_txt), f"latch:///kaiju/{sample_name}/{output_name}"
        ),
    )


@small_task
def plot_krona_task(krona_input: KronaInput) -> LatchFile:
    """Make Krona plot from Kaiju results"""
    sample_name = krona_input.sample_name
    output_name = f"{sample_name}_krona.html"
    krona_html = Path(output_name).resolve()

    _kaiju2krona_cmd = [
        "ktImportText",
        "-o",
        str(krona_html),
        krona_input.krona_txt.local_path,
    ]

    subprocess.run(_kaiju2krona_cmd)

    return LatchFile(str(krona_html), f"latch:///kaiju/{sample_name}/{output_name}")


@workflow
def kaiju_wf(
    samples: Sample,
    kaiju_ref_db: LatchFile,
    kaiju_ref_nodes: LatchFile,
    kaiju_ref_names: LatchFile,
    taxon_rank: TaxonRank,
) -> Tuple[LatchFile, LatchFile]:
    kaiju_inputs = organize_kaiju_inputs(
        samples=samples,
        kaiju_ref_db=kaiju_ref_db,
        kaiju_ref_nodes=kaiju_ref_nodes,
        kaiju_ref_names=kaiju_ref_names,
        taxon_rank=taxon_rank,
    )

    kaiju_outfiles = taxonomy_classification_task(kaiju_input=kaiju_inputs)

    kaiju2table_out = kaiju2table_task(kaiju_out=kaiju_outfiles)
    kaiju2krona_out = kaiju2krona_task(kaiju_out=kaiju_outfiles)

    krona_plots = plot_krona_task(krona_input=kaiju2krona_out)

    return krona_plots, kaiju2table_out
