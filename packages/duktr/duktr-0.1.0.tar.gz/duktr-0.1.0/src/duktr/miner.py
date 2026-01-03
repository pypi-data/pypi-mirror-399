"""ConceptMiner: High-level user-facing class for concept mining."""

from typing import List, Set, Optional, Iterable, Callable, Union
from .llm_providers import BaseLLMProvider, FunctionProvider
from .prompt import generate_prompt
from .utils import _validate_prompt_required_vars
from .core import run, RunStoppedError
import warnings
import json

LLMFunction = Callable[[str], str]
LLMInput = Optional[Union["BaseLLMProvider", LLMFunction]]

MAX_CHARS = 2000 # Max chars to show in error messages for LLM output
DEFAULT_CATALOG_THRESHOLD = 300 # Default partition size for concept set


class ConceptMiner:
    """
    High-level interface for concept discovery using LLMs.
    """
    
    def __init__(
        self,
        llm: LLMInput = None,
        prompt: Optional[str] = None,
        task: Optional[str] = None, 
        concept: Optional[str] = None, 
        rules: Optional[str] = None,
        threshold: int = DEFAULT_CATALOG_THRESHOLD,
        initial_catalog: Optional[Set[str]] = None
    ):
        """
        Initialize ConceptMiner.
        
        Args:
            llm: Custom LLM provider instance
            prompt: prompt (must include {text} and {existing_list})
            task: Task description for prompt generation (if prompt not provided)
            concept: Concept type for prompt generation (if prompt not provided)
            rules: Rules for prompt generation (if prompt not provided)
            threshold: Partition size for large concept sets
            initial_catalog: Starting set of concepts (optional)
        """

        # Setup llm:
        if llm is not None:
            if isinstance(llm, BaseLLMProvider):
                self.llm = llm
            elif callable(llm):
                self.llm = FunctionProvider(llm_function=llm)
            else:
                raise TypeError(
                    "llm must be a BaseLLMProvider or a callable (prompt: str) -> str"
                )
        else:
            raise ValueError("Must provide an llm")
        
        # Setup prompt
        if prompt is not None: # Prompt takes priority
            self.prompt = prompt
            # Warn if other parameters were also provided
            if any([task, concept, rules]):
                warnings.warn(
                    "Both 'prompt' and task/concept/rules parameters were provided. "
                    "Using 'prompt' and ignoring task/concept/rules.",
                    UserWarning,
                    stacklevel=2
                )
        elif all([task, concept, rules]):
            # Generate prompt from components
            self.prompt = generate_prompt(task=task, concept=concept, rules=rules)
        else:
            # Not enough information to create a prompt
            raise ValueError(
                "Must provide either 'prompt' or all of 'task', 'concept', and 'rules'"
            )
        
        _validate_prompt_required_vars(self.prompt)

        self.threshold = threshold
        self.initial_catalog = set(initial_catalog) if initial_catalog else set()
        self.catalog: Optional[Set[str]] = None
        self.results: Optional[List[Set[str]]] = None
    
    def _miner_llm(self, text: str, input_catalog: Set[str]) -> Iterable[str]:
        """Internal LLM call for concept mining."""

        # Format input catalog
        formatted_catalog = "\n".join([f"- {x}" for x in input_catalog]) if input_catalog else ""
        
        # Create prompt
        prompt = self.prompt.format(text=text, existing_list=formatted_catalog)
        
        # Get LLM response
        output = self.llm.generate(prompt)

        try:
            parsed = json.loads(output)
        except json.JSONDecodeError as e:
            # Show the exact output (bounded) so users can see what went wrong.
            # repr() preserves hidden characters like \n, \t, etc.
            out_repr = repr(output)
            truncated = out_repr if len(out_repr) <= MAX_CHARS else (out_repr[:MAX_CHARS] + "...(truncated)")
            raise ValueError(
                "LLM output is not valid JSON. The provider must return ONLY a JSON array of strings "
                'like ["<concept 1>", "<concept 2>", ...] with no extra text.\n'
                f"JSONDecodeError: {e.msg} (line {e.lineno}, col {e.colno}, char {e.pos})\n"
                f"Raw LLM output (repr, max {MAX_CHARS} chars): {truncated}\n"
            ) from e

        if not isinstance(parsed, list) or not all(isinstance(x, str) for x in parsed):
            out_repr = repr(output)
            truncated = out_repr if len(out_repr) <= MAX_CHARS else (out_repr[:MAX_CHARS] + "...(truncated)")
            raise TypeError(
                "LLM output parsed as JSON but does not match the required schema: "
                'a JSON array of strings like ["<concept 1>", "<concept 2>", ...].\n'
                f"Parsed type: {type(parsed).__name__}\n"
                f"Raw LLM output (repr, max {MAX_CHARS} chars): {truncated}\n"
            )

        return parsed

    
    def mine(
        self,
        texts: Iterable[str],
        progress: bool = False
    ) -> List[Set[str]]:
        """
        Discover concepts from texts.

        Args:
            texts: Iterable of text documents
            progress: Whether to show a progress tracker

        Returns:
            Per-text results as a list of sets of concepts.

        Side effects:
            Sets `self.results` and `self.catalog`. After calling, the consolidated catalog
            is available via `self.catalog`.
        """

        texts_list = list(texts)
        
        try:
            # Run core algorithm
            self.results, self.catalog = run(
                rows=texts_list,
                func=self._miner_llm,
                threshold=self.threshold,
                input_catalog=self.initial_catalog,
                progress=progress,
            )

            return self.results
        
        except RunStoppedError as e:
            # Persist partial work onto the instance
            self.results = e.partial_results
            self.catalog = e.catalog

            orig = e.original_exception
            orig_msg = str(orig).strip() or orig.__class__.__name__

            hint = (
                f"{orig_msg} \n"
                f"(stopped at row {e.row_index}; partial results were preserved on the "
                f"ConceptMiner instance you called `.mine()` on. "
                f"Access them via `<your_miner>.results` and `<your_miner>.catalog`.)"
            )

            raise RuntimeError(hint) from orig