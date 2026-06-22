# Genome Evo2 POC — Snakemake + NVIDIA NIM

A proof-of-concept Snakemake workflow that compares a human reference genome against a maternal assembly and augments selected sequence windows with [Evo2](https://build.nvidia.com/arc-institute/evo-2-40b) inference via NVIDIA NIM.

**Use case:** Ingest the GRCh38.p14 reference FASTA and the HG03492 maternal haplotype assembly (Karnataka Individual Genome Project, 2026), align them, select candidate windows, and run Evo2 scoring on those regions to surface biologically interesting variation.

---

## Table of contents

1. [What is Evo2?](#what-is-evo2)
2. [Pipeline stages](#pipeline-stages)
3. [Hello world results](#hello-world-results)
4. [Prerequisites](#prerequisites)
5. [Quickstart — conda](#quickstart--conda)
6. [Quickstart — Docker](#quickstart--docker)
7. [Bringing your own data](#bringing-your-own-data)
8. [Understanding the outputs](#understanding-the-outputs)
9. [Project structure](#project-structure)
10. [Troubleshooting](#troubleshooting)

---

## What is Evo2?

[Evo2](https://www.nature.com/articles/s41586-025-08903-1) is a 40-billion parameter **DNA language model** developed by the Arc Institute and NVIDIA. It was trained on 9.3 trillion nucleotides spanning bacteria, archaea, viruses, and eukaryotes — essentially the entire known diversity of genomic sequence.

Think of it as GPT for DNA: given a sequence of nucleotides as a prompt, it can:

- **Generate** — predict what nucleotides likely follow (continuation)
- **Score** — assign per-token probabilities that reflect how "expected" each nucleotide is given its context

In this pipeline Evo2 is used as an **augmentation layer**, not as the primary analysis tool. Standard bioinformatics steps (alignment, variant calling) run first; Evo2 then annotates selected regions with biological plausibility scores.

The model is served by NVIDIA via their cloud inference API — no GPU required on your machine.

---

## Pipeline stages

| Stage | Rule | Description |
|---|---|---|
| 1. Validate & index | *(planned)* | Check FASTA headers, sequence lengths, build indices |
| 2. FASTA stats | *(planned)* | N50, GC content, contig count for both assemblies |
| 3. Alignment | *(planned)* | Assembly-to-reference alignment with minimap2 |
| 4. Window selection | *(planned)* | Extract candidate regions from alignment output |
| 5. **Evo2 inference** | `score_sequence`, `generate_sequence` | Score and extend windows via NVIDIA NIM API |
| 6. Report | *(planned)* | Aggregate into summary TSV + JSON |

> Stages 1–4 and 6 are scaffolded in [CLAUDE.MD](CLAUDE.MD). The hello world in this repo focuses on stage 5 so you can validate the Evo2 API connection and understand its outputs before wiring in the full genomic data.

---

## Hello world results

We tested the pipeline against a 180 bp segment of the **pUC19 cloning vector** MCS (multiple cloning site) as a known, well-characterised reference sequence.

### Generation
Evo2 extended the 180 bp prompt by **100 new nucleotides**:

```
Input  (180 bp): ATGAAAGCAATTTTCGTACTGAAAGG...CTTGGCGTAATCATGGTCATAGCTGTTTC
Output (100 bp): CTGTGTGAAATTGTTATCCGCTCACAATTCCACACAACATACGAGCCGGAAGCATAAAGT
                 GTAAAGCCTGGGGTGCCTAATGAGTGAGCTAACTCACATT
```

The generated continuation is the **exact downstream pUC19 backbone sequence**. Evo2 recognised the vector from context and reproduced the correct biology — it is not generating random nucleotides.

### Confidence (sampled probabilities)
Each of the 100 generated tokens was assigned a probability by the model (`top_k=1`):

- **Range:** 0.9009 – 0.9985
- **Mean:** ~0.991
- **Lowest-confidence positions:** token 6 (0.9009) and token 96 (0.9083)

High, tight probabilities across the continuation confirm the model is highly certain about this well-known sequence. When you run against novel or divergent regions of your assembly, you expect to see lower and more variable probabilities — those are the biologically interesting windows.

### Latency
- Scoring (1 token): **88 ms**
- Generation (100 tokens): **4.2 seconds**

---

## Prerequisites

### Accounts and keys

- A free **NVIDIA NIM API key** — create one at [build.nvidia.com](https://build.nvidia.com/arc-institute/evo-2-40b). Click "Get API Key". You will need an NVIDIA account (also free).

### Software

**Option A — conda (recommended for local development)**
- [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Mamba](https://mamba.readthedocs.io)

**Option B — Docker**
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Mac/Windows) or Docker Engine (Linux)

### Hardware
No GPU required. All Evo2 inference runs on NVIDIA's cloud. A laptop with internet access is sufficient.

---

## Quickstart — conda

```bash
# 1. Clone the repository
git clone https://github.com/MayankTahil/snakemake-evo2-hello-world.git
cd snakemake-evo2-hello-world

# 2. Create and activate the Python environment
conda env create -f environment.yaml
conda activate snakemake-evo2

# 3. Set up your API key
cp .env.example .env
# Open .env in any text editor and replace nvapi-your-key-here with your real key

# 4. Run the hello world (uses data/example.fasta — no genome data needed)
snakemake --cores 2

# Results appear in results/
```

---

## Quickstart — Docker

```bash
# 1. Clone the repository
git clone https://github.com/MayankTahil/snakemake-evo2-hello-world.git
cd snakemake-evo2-hello-world

# 2. Set up your API key
cp .env.example .env
# Open .env and replace nvapi-your-key-here with your real key

# 3. Build the image
docker build -t snakemake-evo2 .

# 4. Run the hello world
docker run --rm \
  --env-file .env \
  -v "$(pwd)/data:/workflow/data" \
  -v "$(pwd)/results:/workflow/results" \
  -v "$(pwd)/logs:/workflow/logs" \
  snakemake-evo2 --cores 2 --nolock

# Or with docker-compose (same thing, shorter command)
docker-compose up
```

Expected output:
```
3 of 3 steps (100%) done
```

---

## Bringing your own data

### Step 1 — Get a reference genome

The GRCh38.p14 human reference genome is the standard for human genomics work.

Download from NCBI:
```bash
# ~1 GB compressed, ~3 GB uncompressed
mkdir -p data/Reference\ Genome
curl -L "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/001/405/GCF_000001405.40_GRCh38.p14/GCF_000001405.40_GRCh38.p14_genomic.fna.gz" \
  -o "data/Reference Genome/GCF_000001405.40_GRCh38.p14_genomic.fna.gz"
gunzip "data/Reference Genome/GCF_000001405.40_GRCh38.p14_genomic.fna.gz"
```

Or download a single chromosome for testing (much smaller):
```bash
# Chromosome 22 only — good for initial testing (~35 MB uncompressed)
curl -L "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/001/405/GCF_000001405.40_GRCh38.p14/GCF_000001405.40_GRCh38.p14_assembly_structure/Primary_Assembly/assembled_chromosomes/FASTA/chr22.fna.gz" \
  -o "data/Reference Genome/chr22.fna.gz"
gunzip "data/Reference Genome/chr22.fna.gz"
```

### Step 2 — Get or prepare an assembly genome

If you have your own assembly (e.g. a T2T haplotype or de novo assembly), place the FASTA file under `data/Karn-m/` or any subdirectory you choose.

For testing with a public dataset, the HG03492 maternal assembly used in this project is available from the Human Pangenome Reference Consortium:
```bash
mkdir -p data/Karn-m
curl -L "https://s3-us-west-2.amazonaws.com/human-pangenomics/working/HPRC/HG03492/assemblies/year1_freeze_assembly_v2/HG03492.maternal.f1_assembly_v2.fa.gz" \
  -o "data/Karn-m/HG03492.maternal.f1_assembly_v2.fa.gz"
# ~800 MB compressed
```

> **Note:** These files are gitignored (`data/Reference Genome/` and `data/Karn-m/`) and will never be uploaded to GitHub. They live only on your local machine.

### Step 3 — Point the config at your sequences

Edit `config/config.yaml` to add your sample:

```yaml
samples:
  - example          # the built-in hello world (always works, no genome data needed)
  - my_region        # your sequence — put my_region.fasta in data/

evo2:
  api_base: "https://health.api.nvidia.com/v1"
  generation_length: 100
```

Then place your FASTA file at `data/my_region.fasta`. Snakemake will automatically run both `score_sequence` and `generate_sequence` for every sample listed.

### What sequences make good inputs for Evo2?

Evo2 works at the level of individual sequences, not whole chromosomes. For meaningful results, extract **windows** from your alignment — typically 500 bp to 10 kb regions centred on a variant of interest. The full-genome alignment pipeline (stages 1–4 in the roadmap) will automate this window selection; for now you can extract regions manually with `samtools faidx`:

```bash
# Extract a 2 kb window around a position of interest
samtools faidx data/Reference\ Genome/GCF_000001405.40_GRCh38.p14_genomic.fna \
  "NC_000022.11:25,000,000-25,002,000" > data/my_region.fasta
```

---

## Understanding the outputs

After a successful run, `results/` contains:

| File | What it contains |
|---|---|
| `{sample}_scores.json` | Evo2 scoring result: sequence metadata, `sampled_probs` array, full raw API response |
| `{sample}_generated.fasta` | Original prompt sequence + Evo2-generated continuation, in FASTA format |
| `{sample}_generated.json` | Generation metadata: prompt length, generated length, per-token `sampled_probs`, API latency |

### Reading the scores

`sampled_probs` is a list of floating-point values between 0 and 1 — one per generated token. A **high value (~0.98–1.0)** means the model was confident about that nucleotide given its context. A **low value (~0.5–0.8)** means the model found that position unexpected or ambiguous.

In the context of comparing an assembly to a reference:
- Regions where the assembly scores **lower** than the reference are candidates for further biological investigation — the model has seen less of this sequence pattern in training.
- Regions that score **consistently high** are evolutionarily conserved or structurally constrained.

### Reading the generated sequence

The generated FASTA contains the original input sequence followed by Evo2's predicted continuation. This is useful for:
- Checking whether the model completes the sequence in a biologically plausible way
- Comparing the model's prediction against what the actual assembly contains downstream

---

## Project structure

```
.
├── Snakefile                       # Workflow entrypoint — defines rules and DAG
├── config/
│   └── config.yaml                 # Sample list and Evo2 API configuration
├── data/
│   ├── example.fasta               # Built-in hello world sequence (tracked in git)
│   ├── Reference Genome/           # GRCh38.p14 FASTA — gitignored, bring your own
│   └── Karn-m/                     # HG03492 maternal assembly — gitignored
├── scripts/
│   ├── score_sequence.py           # Calls Evo2 generate endpoint with sampled_probs
│   └── generate_sequence.py        # Calls Evo2 generate endpoint, writes FASTA + JSON
├── results/                        # All outputs — gitignored
├── logs/                           # Per-rule stderr logs — gitignored
├── .env.example                    # API key template — copy to .env and fill in
├── Dockerfile                      # Container definition
├── docker-compose.yml              # Compose file — mounts data/results/logs
├── environment.yaml                # Conda environment (Python 3.11, Snakemake, requests)
├── requirements.txt                # pip equivalent used by Dockerfile
└── CLAUDE.MD                       # Full project spec and pipeline roadmap
```

---

## Troubleshooting

**`401 Unauthorized` from the API**
Your `NVIDIA_API_KEY` is missing or expired. Check that `.env` exists, contains `NVIDIA_API_KEY=nvapi-...`, and that your key is still valid at [build.nvidia.com](https://build.nvidia.com).

**`404 Not Found` from the API**
The endpoint URL in `config/config.yaml` is wrong. It must be exactly:
```
https://health.api.nvidia.com/v1
```
The scripts append `/biology/arc/evo2-40b/generate` to whatever you set here.

**`MissingInputException` from Snakemake**
A sample listed in `config/config.yaml` doesn't have a corresponding `data/{sample}.fasta` file. Either add the file or remove the sample from the config.

**Docker `permission denied` on results/**
The container runs as root; your host may own `results/` differently. Run `chmod -R 777 results/ logs/` on the host, or add `--user $(id -u):$(id -g)` to the `docker run` command.

**`raise_for_status` / connection error**
Check your internet connection and that `health.api.nvidia.com` is reachable:
```bash
curl -I https://health.api.nvidia.com
```

---

## API endpoint reference

The pipeline calls a single NVIDIA NIM endpoint for both scoring and generation:

```
POST https://health.api.nvidia.com/v1/biology/arc/evo2-40b/generate
Authorization: Bearer <NVIDIA_API_KEY>
Content-Type: application/json

{
  "sequence": "<DNA string, uppercase ACGT>",
  "num_tokens": <integer>,
  "top_k": 1,
  "enable_sampled_probs": true
}
```

Response fields used by this pipeline:

| Field | Type | Description |
|---|---|---|
| `sequence` | string | Generated nucleotide continuation |
| `sampled_probs` | float[] | Per-token probability of each generated nucleotide |
| `elapsed_ms` | int | Server-side inference time in milliseconds |

---

## License

MIT
