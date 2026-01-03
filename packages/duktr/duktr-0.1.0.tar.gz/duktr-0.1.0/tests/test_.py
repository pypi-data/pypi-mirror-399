from duktr import run, ConceptMiner
from duktr.utils import _partition_set
from duktr.core import RunStoppedError
from duktr.llm_providers import FunctionProvider
import pytest


class FuncSpy:
    def __init__(self, behavior):
        """
        behavior: callable(row, input_set) -> iterable
        """
        self.behavior = behavior
        self.calls = []

    def __call__(self, row, input_set):
        self.calls.append(set(input_set))
        return self.behavior(row, input_set)
    

def test_simple_path_no_partitioning():

    def behavior(row, input_set):
        return {"topic_a"}

    spy = FuncSpy(behavior)

    rows = ["row1"]
    threshold = 5
    input_catalog = {"t1", "t2"}  # len <= threshold

    results, g = run(rows, spy, threshold, input_catalog=input_catalog)

    assert results == [{"topic_a"}]
    assert g == {"t1", "t2", "topic_a"}
    assert len(spy.calls) == 1


def test_early_stop_on_first_partition():

    def behavior(row, input_set):
        # Always explain using only provided topics
        return input_set

    spy = FuncSpy(behavior)

    rows = ["row1"]
    threshold = 3
    input_catalog = {"a", "b", "c", "d", "e"}  # forces partitioning

    results, g = run(rows, spy, threshold, input_catalog=input_catalog)

    # Should stop after first partition
    assert len(spy.calls) == 1
    assert results[0].issubset(input_catalog)


def test_carry_forward_matched_topics():

    def behavior(row, input_set):
        if len(spy.calls) == 1:
            return [next(iter(input_set)), "new1"]
        else:
            return input_set

    spy = FuncSpy(behavior)

    rows = ["row1"]
    threshold = 3 # forces partitioning of size 2 for each partition
    input_catalog = {"a", "b", "c", "d"}

    results, _ = run(rows, spy, threshold, input_catalog=input_catalog)

    assert len(spy.calls) == 2

    # Directly verify carry-forward affected the 2nd call input size
    assert len(spy.calls[1]) == 3

    # Ensure new topics are NOT carried forward
    assert "new1" not in spy.calls[1]

    # Results for one row
    assert len(results) == 1
    assert len(results[0]) == 3


def test_new_topics_only_added_at_end():

    def behavior(row, input_set):
        if len(spy.calls) == 1:
            return [next(iter(input_set)), "new1"]
        else:
            input_set.add("new2")
            return input_set

    spy = FuncSpy(behavior)

    rows = ["row1"]
    threshold = 3 # forces partitioning of size 2 for each partition
    input_catalog = {"a", "b", "c", "d"}

    results, g = run(rows, spy, threshold, input_catalog=input_catalog)

    assert len(spy.calls) == 2

    # Ensure new topics are NOT carried forward
    assert "new1" not in spy.calls[1]

    # Ensure new2 is only in final results
    assert "new2" in results[0]

    # Ensure the gobal set is updated correctly
    assert "new2" in g


def test_call_count_bounded_by_partitions():

    def behavior(row, input_set):
        return set()

    spy = FuncSpy(behavior)

    input_catalog = set(range(20))
    threshold = 5

    partitions = list(_partition_set(input_catalog, threshold))

    run(["row1"], spy, threshold, input_catalog=input_catalog)

    assert len(spy.calls) <= len(partitions)


def test_multiple_rows():

    def behavior(row, input_set):
        return ["topic_a"]

    spy = FuncSpy(behavior)

    rows = ["row1", "row2"]
    threshold = 5
    input_catalog = {"t1", "t2"}  # len <= threshold

    results, g = run(rows, spy, threshold, input_catalog=input_catalog)

    assert results == [{"topic_a"}, {"topic_a"}]
    assert g == {"t1", "t2", "topic_a"}
    assert len(spy.calls) == 2


def test_run_rejects_threshold_less_than_2():
    with pytest.raises(ValueError):
        run(rows=["row1"], func=lambda r, s: [], threshold=1, input_catalog=set())

def test_run_rejects_threshold_non_int():
    with pytest.raises(ValueError):
        run(rows=["row1"], func=lambda r, s: [], threshold="3", input_catalog=set())  # type: ignore


def test_run_input_catalog_none_starts_empty_and_accumulates():
    def func(_row, _input_set):
        return {"x"}

    results, g = run(rows=["r1", "r2"], func=func, threshold=10, input_catalog=None)
    assert results == [{"x"}, {"x"}]
    assert g == {"x"}


def test_partitioning_threshold_2_calls_all_partitions_when_no_early_stop():
    def behavior(_row, _input_set):
        return set()  # empty output => no early stop condition (o_j is falsy)

    spy = FuncSpy(behavior)
    input_catalog = {"a", "b", "c", "d", "e"}
    threshold = 2  # partitions of size 1

    partitions = list(_partition_set(input_catalog, threshold))
    run(["row1"], spy, threshold, input_catalog=input_catalog)

    assert len(spy.calls) == len(partitions)
    assert all(len(call) == 1 for call in spy.calls)  # each input_set is singleton


def test_last_output_includes_carried_matched_even_if_last_partition_empty():
    def behavior(_row, input_set):
        # First partition: return one matched concept plus a "new" concept (prevents early-stop)
        if len(spy.calls) == 1:
            matched = next(iter(input_set))
            return {matched, "new_concept"}  # not subset => no early stop
        # Later partitions: return empty, causing last_output to become empty unless insured
        return set()

    spy = FuncSpy(behavior)

    input_catalog = {"a", "b", "c", "d"}  # forces partitioning with threshold=3 (chunk_size=2)
    results, g = run(["row1"], spy, threshold=3, input_catalog=input_catalog)

    assert len(results) == 1
    # Must include at least the carried matched concept, even though last partition output was empty
    assert len(results[0].intersection(input_catalog)) >= 1
    # "new_concept" should NOT be present because it was introduced in an early partition
    # and later partitions overwrote last_output (current algorithm behavior)
    assert "new_concept" not in results[0]
    assert "new_concept" not in g


def test_run_wraps_exception_and_preserves_partials():
    def func(row, _input_set):
        if row == "bad":
            raise ValueError("boom")
        return {"ok"}

    with pytest.raises(RunStoppedError) as excinfo:
        run(rows=["good", "bad", "never"], func=func, threshold=10, input_catalog={"seed"})

    e = excinfo.value
    assert e.row_index == 1
    assert e.row == "bad"
    assert e.partial_results == [{"ok"}]
    assert e.catalog == {"seed", "ok"}  # state after processing "good"
    assert isinstance(e.original_exception, ValueError)
    assert str(e.original_exception) == "boom"


def test_concept_miner_persists_partials_and_wraps_exception():
    calls = {"n": 0}

    def flaky_llm(_prompt: str) -> str:
        calls["n"] += 1
        if calls["n"] == 1:
            return '["alpha", "beta"]'   # valid JSON list of strings
        raise ValueError("boom")

    td = ConceptMiner(
        llm=flaky_llm,
        prompt="Existing:\n{existing_list}\nText:\n{text}",
        threshold=1400,
    )

    texts = ["doc 1", "doc 2", "doc 3"]

    with pytest.raises(RuntimeError) as excinfo:
        td.mine(texts)

    msg = str(excinfo.value)
    assert "boom" in msg
    assert "stopped at row 1" in msg
    assert "Access them via `<your_miner>.results`" in msg
    assert "and `<your_miner>.catalog`" in msg

    # Partials preserved on the instance
    assert td.results == [{"alpha", "beta"}]
    assert td.catalog == {"alpha", "beta"}

    # ConceptMiner.mine *does* chain the original exception
    assert isinstance(excinfo.value.__cause__, ValueError)
    assert str(excinfo.value.__cause__) == "boom"


def test_concept_miner_requires_llm():
    with pytest.raises(ValueError):
        ConceptMiner(prompt="Existing:\n{existing_list}\nText:\n{text}")  # llm missing



def test_concept_miner_requires_prompt_or_task_concept_rules():
    def llm(_prompt: str) -> str:
        return '[]'

    # Missing prompt and missing task/concept/rules
    with pytest.raises(ValueError):
        ConceptMiner(llm=llm)


def test_concept_miner_prompt_precedence_warns():
    def llm(_prompt: str) -> str:
        return '[]'

    with pytest.warns(UserWarning):
        ConceptMiner(
            llm=llm,
            prompt="Existing:\n{existing_list}\nText:\n{text}",
            task="ignored",
            concept="ignored",
            rules="ignored",
        )



def test_concept_miner_rejects_invalid_llm_type():
    with pytest.raises(TypeError):
        ConceptMiner(
            llm=123,  # type: ignore
            prompt="Existing:\n{existing_list}\nText:\n{text}",
        )



def test_concept_miner_prompt_includes_existing_list_and_empty_marker():
    seen = {"prompt": None}

    def llm(prompt: str) -> str:
        seen["prompt"] = prompt
        return '["x"]'

    miner = ConceptMiner(
        llm=llm,
        prompt="Existing:\n{existing_list}\nText:\n{text}",
        threshold=100,
    )

    miner.mine(["doc1"])

    assert "" in seen["prompt"]
    assert "doc1" in seen["prompt"]



def test_concept_miner_invalid_json_is_wrapped_and_chained():
    def llm(_prompt: str) -> str:
        return "alpha - beta"  # invalid JSON

    miner = ConceptMiner(
        llm=llm,
        prompt="Existing:\n{existing_list}\nText:\n{text}",
        threshold=100,
    )

    with pytest.raises(RuntimeError) as excinfo:
        miner.mine(["doc1", "doc2"])

    assert isinstance(excinfo.value.__cause__, ValueError)
    assert "LLM output is not valid JSON" in str(excinfo.value.__cause__)
    assert "stopped at row 0" in str(excinfo.value)



def test_concept_miner_json_schema_mismatch_is_wrapped_and_chained():
    def llm(_prompt: str) -> str:
        return '{"a": 1}'  # valid JSON, wrong schema (dict)

    miner = ConceptMiner(
        llm=llm,
        prompt="Existing:\n{existing_list}\nText:\n{text}",
        threshold=100,
    )

    with pytest.raises(RuntimeError) as excinfo:
        miner.mine(["doc1"])

    assert isinstance(excinfo.value.__cause__, TypeError)
    assert "does not match the required schema" in str(excinfo.value.__cause__)



def test_concept_miner_persists_partials_and_raises_runtimeerror():
    calls = {"n": 0}

    def flaky_llm(_prompt: str) -> str:
        calls["n"] += 1
        if calls["n"] == 1:
            return '["alpha", "beta"]'
        raise ValueError("boom")

    miner = ConceptMiner(
        llm=flaky_llm,
        prompt="Existing:\n{existing_list}\nText:\n{text}",
        threshold=1400,
    )

    with pytest.raises(RuntimeError) as excinfo:
        miner.mine(["doc 1", "doc 2", "doc 3"])

    msg = str(excinfo.value)
    assert "boom" in msg
    assert "stopped at row 1" in msg
    assert "ConceptMiner instance you called `.mine()` on" in msg

    assert miner.results == [{"alpha", "beta"}]
    assert miner.catalog == {"alpha", "beta"}

    assert isinstance(excinfo.value.__cause__, ValueError)
    assert str(excinfo.value.__cause__) == "boom"


def test_function_provider_rejects_non_str_output():
    def bad_llm(_prompt: str):
        return 123  # not a str

    fp = FunctionProvider(bad_llm)  # construction ok
    with pytest.raises(TypeError):
        fp.generate("hi")
