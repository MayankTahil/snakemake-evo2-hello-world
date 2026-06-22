"""Score a DNA sequence using Evo2 via NVIDIA cloud API."""

import argparse
import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv


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


def score_sequence(sequence: str, api_base: str, api_key: str) -> dict:
    # Use generate with num_tokens=1 and sampled probs to get per-token log-likelihoods
    url = f"{api_base.rstrip('/')}/biology/arc/evo2-40b/generate"
    r = requests.post(
        url=url,
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "sequence": sequence,
            "num_tokens": 1,
            "top_k": 1,
            "enable_sampled_probs": True,
        },
        timeout=120,
    )
    r.raise_for_status()
    return r.json()


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Score a DNA sequence with Evo2")
    parser.add_argument("--input", required=True, help="Input FASTA file")
    parser.add_argument("--output", required=True, help="Output JSON file")
    parser.add_argument("--api-base", required=True, help="Evo2 API base URL")
    args = parser.parse_args()

    api_key = os.environ.get("NVIDIA_API_KEY", "")
    if not api_key:
        print("ERROR: NVIDIA_API_KEY not set. Copy .env.example to .env and add your key.", file=sys.stderr)
        sys.exit(1)

    header, sequence = read_fasta(args.input)
    print(f"Scoring sequence: {header} ({len(sequence)} bp)", file=sys.stderr)

    result = score_sequence(sequence, args.api_base, api_key)

    output = {
        "header": header,
        "sequence_length": len(sequence),
        "api_base": args.api_base,
        "sampled_probs": result.get("sampled_probs"),
        "raw_response": result,
    }

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Scores written to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
