from latch.types import LatchAuthor, LatchMetadata, LatchParameter

megs_DOCS = LatchMetadata(
    display_name="taxonomy",
    documentation="https://github.com/jvfe/megs_latch/blob/main/README.md",
    author=LatchAuthor(
        name="jvfe",
        github="https://github.com/jvfe",
    ),
    repository="https://github.com/jvfe/megs_latch",
    license="MIT",
    tags=["NGS", "metagenomics", "MAG"],
)

megs_DOCS.parameters = {
    "samples": LatchParameter(
        display_name="Sample data",
        description="Paired-end FASTQ files",
        batch_table_column=True,
    ),
    "kaiju_ref_db": LatchParameter(
        display_name="Kaiju reference database (FM-index)",
        description="Kaiju reference database '.fmi' file.",
        section_title="Kaiju parameters",
    ),
    "kaiju_ref_nodes": LatchParameter(
        display_name="Kaiju reference database nodes",
        description="Kaiju reference nodes, 'nodes.dmp' file.",
    ),
    "kaiju_ref_names": LatchParameter(
        display_name="Kaiju reference database names",
        description="Kaiju reference taxon names, 'names.dmp' file.",
    ),
    "taxon_rank": LatchParameter(
        display_name="Taxonomic rank (kaiju2table)",
        description="Taxonomic rank for summary table output (kaiju2table).",
    ),
}
