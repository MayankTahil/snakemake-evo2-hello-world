FROM python:3.11-slim

LABEL org.opencontainers.image.title="snakemake-evo2" \
      org.opencontainers.image.description="Snakemake + Evo2 genomics pipeline via NVIDIA NIM" \
      org.opencontainers.image.source="https://github.com/MayankTahil/snakemake-evo2-hello-world"

WORKDIR /workflow

# System deps: git is required by Snakemake's source caching
RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy workflow files (genomic data is mounted at runtime, not baked in)
COPY Snakefile .
COPY config/ config/
COPY scripts/ scripts/
COPY data/example.fasta data/example.fasta

# Create output directories so Snakemake can write without root volume ownership issues
RUN mkdir -p data results logs

# Genome data and outputs are expected as volume mounts
VOLUME ["/workflow/data", "/workflow/results", "/workflow/logs"]

ENV NVIDIA_API_KEY=""

ENTRYPOINT ["snakemake"]
CMD ["--cores", "all", "--config", "demo=true"]
