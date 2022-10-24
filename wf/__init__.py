from dataclasses import dataclass
from typing import List, Tuple, Union

from dataclasses_json import dataclass_json
from latch import map_task, small_task, workflow
from latch.resources.launch_plan import LaunchPlan
from latch.types import LatchDir, LatchFile

from .docs import megs_DOCS
from .kaiju import kaiju_wf
from .types import Sample, TaxonRank


@dataclass_json
@dataclass
class WfResults:
    krona_plots: LatchFile
    kaiju2table_outs: LatchFile


@small_task
def organize_final_outputs(
    krona_plots: LatchFile,
    kaiju2table_outs: LatchFile,
) -> WfResults:

    return WfResults(krona_plots=krona_plots, kaiju2table_outs=kaiju2table_outs)


@workflow(megs_DOCS)
def taxonomy(
    samples: Sample,
    kaiju_ref_db: LatchFile,
    kaiju_ref_nodes: LatchFile,
    kaiju_ref_names: LatchFile,
    taxon_rank: TaxonRank = TaxonRank.species,
) -> WfResults:
    """Metagenomic taxonomic read classification with Kaiju

    taxonomy
    ----------

    taxonomy performs taxonomic classification of reads with Kaiju.
    """

    kaiju2table_outs, krona_plots = kaiju_wf(
        samples=samples,
        kaiju_ref_db=kaiju_ref_db,
        kaiju_ref_nodes=kaiju_ref_nodes,
        kaiju_ref_names=kaiju_ref_names,
        taxon_rank=taxon_rank,
    )

    return organize_final_outputs(
        krona_plots=krona_plots, kaiju2table_outs=kaiju2table_outs
    )


LaunchPlan(
    taxonomy,  # workflow name
    "Example Metagenome (Crohn's disease gut microbiome)",  # name of test data
    {
        "samples": Sample(
            sample_name="SRR579291",
            read1=LatchFile("s3://latch-public/test-data/4318/SRR579291_1.fastq"),
            read2=LatchFile("s3://latch-public/test-data/4318/SRR579291_2.fastq"),
        ),
        "kaiju_ref_db": LatchFile(
            "s3://latch-public/test-data/4318/kaiju_db_viruses.fmi"
        ),
        "kaiju_ref_nodes": LatchFile(
            "s3://latch-public/test-data/4318/virus_nodes.dmp"
        ),
        "kaiju_ref_names": LatchFile(
            "s3://latch-public/test-data/4318/virus_names.dmp"
        ),
        "taxon_rank": TaxonRank.species,
    },
)
