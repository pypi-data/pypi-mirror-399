from typing import Any, Generator, Set
import string

def _validate_threshold(threshold: int) -> None:
    if not isinstance(threshold, int) or threshold < 2:
        raise ValueError(
            f"Threshold must be an integer >= 2, but got {threshold}."
        )
    

def _validate_prompt_required_vars(prompt: str) -> None:
    # Extract all placeholder field names from the format string
    fields = {fname for _, fname, _, _ in string.Formatter().parse(prompt) if fname is not None}

    required = {"text", "existing_list"}
    missing = required - fields
    extra = fields - required

    if missing or extra:
        parts = []
        if missing:
            parts.append("\nMissing: " + ", ".join("{" + m + "}" for m in sorted(missing)))
        if extra:
            parts.append("\nUnexpected: " + ", ".join("{" + e + "}" for e in sorted(extra)))
        raise ValueError(
            "Prompt template must contain exactly two placeholders: {text} and {existing_list}. "
            + " ".join(parts)
        )


def _partition_set(
    catalog: Set[Any], threshold: int
) -> Generator[Set[Any], None, None]:
    """
    Partitions a set into subsets of size < threshold.
    """
    chunk_size = threshold - 1
    if chunk_size <= 0:
        return

    chunk: Set[Any] = set()
    for item in catalog:
        chunk.add(item)
        if len(chunk) == chunk_size:
            yield chunk
            chunk = set()

    if chunk:
        yield chunk
