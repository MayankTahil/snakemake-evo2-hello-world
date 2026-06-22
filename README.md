# Snakemake + Evo2 Hello World

A minimal Snakemake workflow demonstrating how to call [Evo2](https://build.nvidia.com/arc-institute/evo-2-40b) — the Arc Institute / NVIDIA genomic foundation model — via NVIDIA NIM.

The workflow takes a DNA sequence in FASTA format and runs two tasks in parallel:

- **Score** — returns log-likelihood scores for each token in the sequence
- **Generate** — continues the sequence by generating new tokens

## Prerequisites

- [Conda](https://docs.conda.io/en/latest/miniconda.html) or [Mamba](https://mamba.readthedocs.io)
- An NVIDIA NIM API key — get one free at [build.nvidia.com](https://build.nvidia.com/arc-institute/evo-2-40b)

## Quickstart

```bash
# 1. Clone the repo
git clone https://github.com/MayankTahul/snakemake-evo2-hello-world.git
cd snakemake-evo2-hello-world

# 2. Create and activate the environment
conda env create -f environment.yaml
conda activate snakemake-evo2

# 3. Set your NVIDIA API key
export NVIDIA_API_KEY="nvapi-..."

# 4. Run the workflow
snakemake --cores 2
```

Results are written to `results/`:

| File | Description |
|---|---|
| `results/example_scores.json` | Per-token log-likelihood scores |
| `results/example_generated.fasta` | Prompt + model-generated continuation |

## Project Structure

```
.
├── Snakefile                  # Workflow definition
├── config/
│   └── config.yaml            # Model and sample configuration
├── data/
│   └── example.fasta          # Input DNA sequence
├── scripts/
│   ├── score_sequence.py      # Calls Evo2 scoring endpoint
│   └── generate_sequence.py   # Calls Evo2 generation endpoint
└── environment.yaml           # Conda environment
```

## Adding Your Own Sequences

Place your FASTA files in `data/` and add the sample names (without `.fasta`) to `config/config.yaml`:

```yaml
samples:
  - example
  - my_gene
  - another_sequence
```

Snakemake will automatically run both rules for each sample.

## Model

Evo2 (`arc-institute/evo-2-40b`) is a 40-billion parameter DNA language model trained on 9.3 trillion nucleotides spanning all domains of life. It is hosted on NVIDIA NIM at:

```
https://integrate.api.nvidia.com/v1
```

See the [NVIDIA NIM documentation](https://docs.nvidia.com/nim/) for rate limits and available endpoints.

## License

MIT
