"""Generate a DNA sequence using Evo2 via NVIDIA cloud API."""

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


def write_fasta(path: str, header: str, sequence: str, line_width: int = 60):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write(f">{header}\n")
        for i in range(0, len(sequence), line_width):
            f.write(sequence[i : i + line_width] + "\n")


def generate_sequence(prompt: str, num_tokens: int, api_base: str, api_key: str) -> dict:
    url = f"{api_base.rstrip('/')}/biology/arc/evo2-40b/generate"
    r = requests.post(
        url=url,
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "sequence": prompt,
            "num_tokens": num_tokens,
            "top_k": 1,
            "enable_sampled_probs": True,
        },
        timeout=120,
    )
    r.raise_for_status()

    if "application/zip" in r.headers.get("Content-Type", ""):
        raise RuntimeError("Received zip response — sequence may be too long for JSON transport")

    return r.json()


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Generate a DNA sequence with Evo2")
    parser.add_argument("--input", required=True, help="Input FASTA file (used as prompt)")
    parser.add_argument("--output", required=True, help="Output FASTA file")
    parser.add_argument("--api-base", required=True, help="Evo2 API base URL")
    parser.add_argument("--length", type=int, default=100, help="Number of tokens to generate")
    args = parser.parse_args()

    api_key = os.environ.get("NVIDIA_API_KEY", "")
    if not api_key:
        print("ERROR: NVIDIA_API_KEY not set. Copy .env.example to .env and add your key.", file=sys.stderr)
        sys.exit(1)

    header, sequence = read_fasta(args.input)
    print(f"Generating {args.length} tokens from: {header} ({len(sequence)} bp prompt)", file=sys.stderr)

    result = generate_sequence(sequence, args.length, args.api_base, api_key)

    generated = result.get("sequence", "")
    full_sequence = sequence + generated
    output_header = f"{header}_generated length={len(full_sequence)}"
    write_fasta(args.output, output_header, full_sequence)

    meta_path = Path(args.output).with_suffix(".json")
    with open(meta_path, "w") as f:
        json.dump({"prompt_length": len(sequence), "generated_length": len(generated), "api_response": result}, f, indent=2)

    print(f"Generated sequence written to {args.output}", file=sys.stderr)
    print(f"API response metadata written to {meta_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
