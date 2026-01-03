<img src="assets/logo.png" align="left" height="150" alt="duktr logo" />
<h3 align="center"><strong>deduct + induct via LLMs</strong></h3>

`duktr` is an LLM-powered Python package for **dynamic concept mining** and **mixed-membership (multi-label) assignment/clustering** over text. It maintains an evolving catalog of concepts and, for each input text, returns the set of concepts that describe it, reusing existing concepts where possible and introducing new concepts when needed.

This is useful when the concept set cannot be pre-defined and will evolve over time (e.g., news topics, issues in tickets, patients’ symptoms, canonical product identities). You define what a “concept” means for your use case, and `duktr` provides the flexibility to extract the concepts you have in mind to cluster textual information based on the specified concept.

![Demo](https://github.com/user-attachments/assets/333ae6bb-5074-4482-81d1-cb326651fe17)

---

## Features

- **Mixed-membership labeling:** each text can map to zero, one, or many concepts.
- **Dynamic concept discovery:** concepts are discovered from data and the catalog grows over time.
- **Catalog-aware prompting:** prompts reuse of existing concepts to avoid drift/duplication and to support clustering.
- **Scales to large catalogs:** progressive partitioning keeps LLM inputs bounded as the catalog grows.
- **Pluggable LLM backends:** OpenAI, Gemini, or a custom Python function (including your LLM of choice, e.g., Hugging Face).
- **Advantage over traditional clustering:** Leverages LLM reasoning to capture semantic similarity beyond surface-level text features and density-based methods (e.g., DBSCAN), enabling finer-grained and more subtle concepts and better performance in low-density settings.

---

## Installation

```bash
pip install duktr
```

---

## Quick Start

```python
from duktr import ConceptMiner, GeminiProvider

# Initialize a miner that extracts "symptom" as the target concept from text records.
miner = ConceptMiner(
    llm=GeminiProvider(api_key="YOUR_API_KEY"),
    task="Extract the symptom(s) of the patient from their record.",
    concept="symptom",
    rules="""
    - Use short noun phrases (2–6 words)
    - Symptom(s) must be independent; no duplicates
    - Output in English
    """,
)

# Example inputs (note: the third record paraphrases the first).
texts = [
     "Patient reports frequent headaches and occasional dizziness.",
     "The individual is experiencing shortness of breath during exertion.",
     "The patient describes recurrent head pain along with vertigo." # paraphrased version of first text
]

# Mine concepts per text.
per_text_concepts = miner.mine(texts)

print(per_text_concepts)  # concepts found in each record
print(miner.catalog)      # global catalog across all records  
```

Expected output:

```python
[{"Headache", "Dizziness"}, {"Shortness of breath"}, {"Headache", "Dizziness"}]
{"Headache", "Dizziness", "Shortness of breath"}
```

**Notes:**

- There are multiple ways to configure the prompt used by the `ConceptMiner`. See the [documentation](docs/quickstart.md#2-initialize-the-conceptminer) for more details.
- Runtime is mainly determined by the computational speed of the underlying LLM.
- Test different prompt templates and rules with a small sample of your data to see what works best for your use case before running on the full dataset.

---

## Documentation

For more detailed information, see the [full documentation](docs/index.md).

---

## License and contributing

- **License:** MIT License. See the `LICENSE` file for full terms.
- **Contributing:** Issues and pull requests are welcome. 

---