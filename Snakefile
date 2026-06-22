configfile: "config/config.yaml"


rule all:
    input:
        expand("results/{sample}_scores.json", sample=config["samples"]),
        expand("results/{sample}_generated.fasta", sample=config["samples"]),


rule score_sequence:
    input:
        fasta="data/{sample}.fasta",
    output:
        scores="results/{sample}_scores.json",
    params:
        model=config["evo2"]["model"],
        api_base=config["evo2"]["api_base"],
    log:
        "logs/{sample}_score.log",
    shell:
        """
        python scripts/score_sequence.py \
            --input {input.fasta} \
            --output {output.scores} \
            --model {params.model} \
            --api-base {params.api_base} \
            2> {log}
        """


rule generate_sequence:
    input:
        fasta="data/{sample}.fasta",
    output:
        generated="results/{sample}_generated.fasta",
    params:
        model=config["evo2"]["model"],
        api_base=config["evo2"]["api_base"],
        length=config["evo2"]["generation_length"],
    log:
        "logs/{sample}_generate.log",
    shell:
        """
        python scripts/generate_sequence.py \
            --input {input.fasta} \
            --output {output.generated} \
            --model {params.model} \
            --api-base {params.api_base} \
            --length {params.length} \
            2> {log}
        """
