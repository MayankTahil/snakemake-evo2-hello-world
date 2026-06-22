# Genome Evo2 POC

This repository is a proof-of-concept Snakemake workflow for comparing a human reference genome input against a maternal assembly input and augmenting selected sequence windows with Evo2 inference via build.nvidia.com.

## Project goals
- Build a reproducible, inspectable genomics pipeline for testing and learning.
- Use standard sequence comparison steps first, then add Evo2 as an annotation/scoring step.
- Keep outputs easy to audit and trace from raw input to final report.

## Inputs
- Reference sequence: `/data/Reference Genome`
- Assembly sequence: `/data/Karn-m/`
    - this directory will have the maternal assembly sequence. There is a PDF there which outlines the context for the data set. 

## Workflow principles
- Use Snakemake as the orchestration layer.
- Keep rule definitions modular in `workflow/rules/*.smk`.
- Keep helper Python out of rules whenever possible; place helpers in `workflow/scripts/`.
- Use `config/config.yaml` for metadata and workflow behavior, not for runtime-specific thread/output tuning.
- Prefer explicit intermediate files over hidden in-memory transformations.
- Every major output should have a clear provenance path.

## Suggested stages
1. Input validation and indexing.
2. FASTA statistics for both inputs.
3. Assembly-to-reference comparison using a standard aligner.
4. Region/window selection for candidate analysis.
5. Evo2 API inference on selected windows.
6. Result aggregation and report generation.

## Evo2 integration rules
- Treat Evo2 as an augmentation step, not as the sole source of genomic truth.
- Save every Evo2 request input, normalized parameters, and response metadata to `results/evo2/`.
- Make API-dependent rules skippable via config.
- Do not hardcode secrets; read API credentials from environment variables.
- Keep sequence window size and selection logic configurable.

## Engineering conventions
- Prefer small, testable scripts with typed Python where practical.
- Emit tabular outputs in TSV or CSV and machine-readable JSON for metadata.
- Use stable filenames and avoid renaming outputs without good reason.
- Keep filenames short, descriptive, and consistent.

## Snakemake conventions
- Main entrypoint is `workflow/Snakefile`.
- Rules live in `workflow/rules/`.
- Environments live in `workflow/envs/`.
- Scripts live in `workflow/scripts/`.
- Run `snakemake --lint` before major commits.
- Add minimal test data and dry-run coverage before expanding scope.

## Reproducibility
- Prefer per-rule conda environments first.
- Keep the workflow runnable in a reduced demo mode on small inputs or sampled regions.
- Separate metadata config from runtime CLI arguments such as cores and resources.

## Logging and traceability
- Every result table should include source file, region/window identifier, and upstream rule provenance where practical.
- Log API usage and failures in a structured way.
- Preserve intermediate region-selection outputs for debugging.

## Guardrails
- Do not add large new workflow branches without updating `README.md` and `config/config.yaml`.
- Do not silently change biological assumptions such as window size, chromosome subset, or comparison algorithm.
- If a rule depends on an external API, make failure modes explicit and save partial outputs where possible.

## First tasks for Claude Code
- Scaffold the Snakemake repository structure.
- Create `config/config.yaml` and a minimal `samples.tsv`.
- Implement preprocessing and FASTA stats rules.
- Add a first comparison rule and save inspectable outputs.
- Add a stubbed Evo2 rule that can run in mock mode before enabling the live API.
- Produce a simple final summary table and report.