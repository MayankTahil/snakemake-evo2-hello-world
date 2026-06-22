# Genome Evo2 POC — Snakemake + NVIDIA NIM

A proof-of-concept Snakemake workflow that compares a human reference genome against a maternal assembly and augments selected sequence windows with [Evo2](https://build.nvidia.com/arc-institute/evo-2-40b) inference via NVIDIA NIM.

**Use case:** The workflow ingests the GRCh38.p14 reference FASTA and the HG03492 maternal haplotype assembly (Karnataka Individual Genome Project, 2026), aligns them, selects candidate windows, and runs Evo2 scoring on those regions to surface biologically interesting variation.

## Pipeline stages

| Stage | Description |
|---|---|
| 1. Validate & index | Check inputs, validate FASTA headers, build indices |
| 2. FASTA stats | Sequence length, N50, GC content for both assemblies |
| 3. Alignment | Assembly-to-reference alignment (minimap2) |
| 4. Window selection | Extract candidate regions from alignment output |
| 5. Evo2 inference | Score selected windows via NVIDIA NIM API |
| 6. Report | Aggregate results into a summary TSV and JSON report |

> **Hello world mode:** A small `data/example.fasta` is included for dry-run and API testing without the full genome inputs. Run with `--config demo=true` to use it.

## Prerequisites

- [Conda](https://docs.conda.io/en/latest/miniconda.html) or [Mamba](https://mamba.readthedocs.io)  
  _or_ Docker (see below)
- An NVIDIA NIM API key — get one free at [build.nvidia.com](https://build.nvidia.com/arc-institute/evo-2-40b)
- Genomic inputs (not included in this repo — see [Data](#data))

## Quickstart (conda)

```bash
# 1. Clone
git clone https://github.com/MayankTahil/snakemake-evo2-hello-world.git
cd snakemake-evo2-hello-world

# 2. Create environment
conda env create -f environment.yaml
conda activate snakemake-evo2

# 3. Set your NVIDIA API key
cp .env.example .env
# Edit .env and replace nvapi-your-key-here with your real key

# 4. Dry run (hello world example)
snakemake --cores 2 --config demo=true

# 5. Full run (requires genome data mounted under data/)
snakemake --cores all
```

## Quickstart (Docker)

```bash
# Build image
docker build -t snakemake-evo2 .

# Ensure .env exists with your key (docker-compose reads it automatically)
cp .env.example .env  # then edit .env

# Hello world demo (no genome data needed)
docker run --rm \
  -e NVIDIA_API_KEY="nvapi-..." \
  snakemake-evo2 --cores 2 --config demo=true

# Full run — mount your local data/ and results/ directories
docker run --rm \
  -e NVIDIA_API_KEY="nvapi-..." \
  -v "$(pwd)/data:/workflow/data" \
  -v "$(pwd)/results:/workflow/results" \
  -v "$(pwd)/logs:/workflow/logs" \
  snakemake-evo2 --cores all

# Or with docker-compose (handles mounts and env automatically)
NVIDIA_API_KEY="nvapi-..." docker-compose up
```

## Data

Genomic datasets are **not** tracked in this repository (too large for public git hosting).

| Dataset | Path | Source |
|---|---|---|
| GRCh38.p14 reference | `data/Reference Genome/` | [NCBI RefSeq GCF_000001405.40](https://www.ncbi.nlm.nih.gov/datasets/genome/GCF_000001405.40/) |
| HG03492 maternal assembly | `data/Karn-m/` | Karnataka Individual Genome Project 2026 |

Place the files under those paths before running the full pipeline.

## Project structure

```
.
├── Snakefile                       # Main workflow entrypoint
├── config/
│   └── config.yaml                 # Workflow configuration
├── data/
│   ├── example.fasta               # Small demo sequence (tracked)
│   ├── Reference Genome/           # GRCh38.p14 FASTA (gitignored)
│   └── Karn-m/                     # HG03492 maternal assembly (gitignored)
├── scripts/
│   ├── score_sequence.py           # Evo2 scoring via NVIDIA NIM
│   └── generate_sequence.py        # Evo2 generation via NVIDIA NIM
├── results/                        # All outputs (gitignored)
├── Dockerfile
├── docker-compose.yml
└── environment.yaml
```

## Model

Evo2 (`arc-institute/evo-2-40b`) is a 40-billion parameter DNA language model trained on 9.3 trillion nucleotides spanning all domains of life, hosted on NVIDIA NIM:

```
https://integrate.api.nvidia.com/v1
```

Evo2 is used here as an **augmentation step** — not as the sole source of genomic truth. Every API request, normalized parameters, and response metadata are saved to `results/evo2/` for auditability.

## License

MIT
