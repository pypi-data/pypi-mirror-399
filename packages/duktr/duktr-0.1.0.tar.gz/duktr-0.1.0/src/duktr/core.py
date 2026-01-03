import sys
from typing import (
    Any,
    Callable,
    List,
    Optional,
    Set,
    Tuple,
)

from .utils import _partition_set, _validate_threshold


class RunStoppedError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        row_index: int,
        row: Any,
        partial_results: List[Set[Any]],
        catalog: Set[Any],
        original_exception: Exception,
    ) -> None:
        super().__init__(message)
        self.row_index = row_index
        self.row = row
        self.partial_results = partial_results
        self.catalog = catalog
        self.original_exception = original_exception


def run(
    rows: List[Any],
    func: Callable[[Any, Set[Any]], Set[Any]],
    threshold: int,
    input_catalog: Optional[Set[Any]] = None,
        *,
    progress: bool = False,
) -> Tuple[List[Set[Any]], Set[Any]]:
    """
    Evaluate rows against a concept catalog using progressive partitioning and carry-forward matches.

    For each row, this function calls `func(row, candidate_concepts)`, an LLM, to obtain concepts for the row.
    The global catalog is updated after each row with the row's final concept set.

    If the catalog size is at most `threshold`, `func` is called once with the full catalog.
    Otherwise, the catalog is partitioned and evaluated sequentially:
      - For each partition, call `func(row, partition ∪ carried_matched)`.
      - Carry forward only concepts that were already present in the input set
        (i.e., `output ∩ input_set`).
      - Early-stop (heuristic) when `output` is non-empty and `output ⊆ input_set`, under the
        assumption that additional partitions are unlikely to introduce new concepts for this row.
      - If no early-stop occurs, the output of the last partition is used as the base result and
        is unioned with `carried_matched`.

    Args:
        rows: list of input rows to process.
        func: Callable that takes `(row, input_set)` and returns a set of concepts for the row.
              Returned concepts may include concepts not present in `input_set` (i.e., "new" concepts).
        threshold: Maximum catalog size to process in a single call; above this, the catalog is
            partitioned into chunks of size up to `threshold`.
        input_catalog: Optional initial concept catalog. If not provided, starts empty.
        progress: If True, display progress updates to stderr.

    Returns:
        A tuple `(per_row_results, catalog)` where:
          - `per_row_results` is a list of sets, one per row, containing the final concepts for that row.
          - `catalog` is the updated catalog after processing all rows (initial catalog plus all
            concepts added from row results).

    Raises:
        RunStoppedError: If `func` raises an exception for any row. The exception includes the failing
            row index and row value, as well as partial results and the catalog state at failure.
    """
    _validate_threshold(threshold)

    catalog = set() if input_catalog is None else set(input_catalog)
    per_row_results: List[Set[Any]] = []

    total = len(rows)

    for i, row in enumerate(rows):
        row_no = i + 1

        if progress:
            sys.stderr.write(f"\rProcessing text {row_no}/{total} ...")
            sys.stderr.flush()

        try:
            # -------------------------------------------------
            # Simple path: one call with the full catalog
            # -------------------------------------------------
            if len(catalog) <= threshold:
                final_set = set(func(row, catalog))
                per_row_results.append(final_set)
                catalog.update(final_set)
                continue

            # -------------------------------------------------
            # Alternative partitioned path: progressive evaluation
            # -------------------------------------------------
            carried_matched: Set[Any] = set()
            last_output: Set[Any] = set()

            for s_j in _partition_set(catalog, threshold):
                # Build the input for this partition call:
                # include concepts matched from earlier partitions
                input_set = set(s_j)
                input_set.update(carried_matched)
                o_j = set(func(row, input_set))

                # Always keep the most recent output;
                # if we reach the last partition without early-stop, this becomes the row result.
                last_output = o_j

                # carry forward only the concepts that were already present in the input_set
                carried_matched.update(o_j.intersection(input_set))

                # Early-stop:
                # If the model returned only concepts from input_set, then it did not introduce new concepts.
                # Under this assumption, further partitions are unnecessary for this row.
                if o_j and o_j.issubset(input_set):
                    break

            # After the loop:
            # - If we broke early, last_output is the “complete using existing concepts” explanation.
            # - If we did not break, last_output is from the last partition and may contain new concepts.
            last_output.update(carried_matched) # extra insurance: ensure carried matched are included
            per_row_results.append(last_output)
            catalog.update(last_output)

        except Exception as e:
            # Stop immediately, preserve partial work, raise.
            raise RunStoppedError(
                f"Processing stopped at row {i} due to error: {e}",
                row_index=i,
                row=row,
                partial_results=per_row_results,
                catalog=catalog,
                original_exception=e,
            ) from None
        
    if progress:
        sys.stderr.write(f"\rProcessing complete: {total} total.\n")
        sys.stderr.flush()

    return per_row_results, catalog