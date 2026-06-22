"""Score a DNA sequence using Evo2 on NVIDIA NIM."""

import argparse
import json
import os
import sys
from pathlib import Path

from openai import OpenAI


def read_fasta(path: str) -> tuple[str, str]:
    header, sequence = "", []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith(">"):
                header = line[1:]
            else:
                sequence.append(line)
    return header, "".join(sequence)


def score_sequence(sequence: str, model: str, client: OpenAI) -> dict:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": sequence,
            }
        ],
        extra_body={
            "task": "score",
        },
    )
    return response.model_dump()


def main():
    parser = argparse.ArgumentParser(description="Score a DNA sequence with Evo2")
    parser.add_argument("--input", required=True, help="Input FASTA file")
    parser.add_argument("--output", required=True, help="Output JSON file")
    parser.add_argument("--model", required=True, help="Evo2 model name")
    parser.add_argument("--api-base", required=True, help="NVIDIA NIM API base URL")
    args = parser.parse_args()

    api_key = os.environ.get("NVIDIA_API_KEY")
    if not api_key:
        print("ERROR: NVIDIA_API_KEY environment variable not set.", file=sys.stderr)
        print("Get your key at: https://build.nvidia.com/arc-institute/evo-2-40b", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(base_url=args.api_base, api_key=api_key)

    header, sequence = read_fasta(args.input)
    print(f"Scoring sequence: {header} ({len(sequence)} bp)", file=sys.stderr)

    result = score_sequence(sequence, args.model, client)

    output = {
        "header": header,
        "sequence_length": len(sequence),
        "model": args.model,
        "scores": result,
    }

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Scores written to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
