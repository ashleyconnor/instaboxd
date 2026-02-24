default: generate

generate:
  @echo "Generating image..."
  uv run python generate.py
