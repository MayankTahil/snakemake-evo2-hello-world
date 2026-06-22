"""Generate a DNA sequence using Evo2 on NVIDIA NIM."""

import argparse
import os
from dotenv import load_dotenv
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


def write_fasta(path: str, header: str, sequence: str, line_width: int = 60):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write(f">{header}\n")
        for i in range(0, len(sequence), line_width):
            f.write(sequence[i : i + line_width] + "\n")


def generate_sequence(prompt: str, length: int, model: str, client: OpenAI) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        max_tokens=length,
        extra_body={
            "task": "generate",
        },
    )
    return response.choices[0].message.content


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Generate a DNA sequence with Evo2")
    parser.add_argument("--input", required=True, help="Input FASTA file (used as prompt)")
    parser.add_argument("--output", required=True, help="Output FASTA file")
    parser.add_argument("--model", required=True, help="Evo2 model name")
    parser.add_argument("--api-base", required=True, help="NVIDIA NIM API base URL")
    parser.add_argument("--length", type=int, default=100, help="Number of tokens to generate")
    args = parser.parse_args()

    api_key = os.environ.get("NVIDIA_API_KEY")
    if not api_key:
        print("ERROR: NVIDIA_API_KEY environment variable not set.", file=sys.stderr)
        print("Get your key at: https://build.nvidia.com/arc-institute/evo-2-40b", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(base_url=args.api_base, api_key=api_key)

    header, sequence = read_fasta(args.input)
    print(f"Generating {args.length} tokens from: {header} ({len(sequence)} bp prompt)", file=sys.stderr)

    generated = generate_sequence(sequence, args.length, args.model, client)

    full_sequence = sequence + generated
    output_header = f"{header}_generated length={len(full_sequence)}"
    write_fasta(args.output, output_header, full_sequence)

    print(f"Generated sequence written to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
