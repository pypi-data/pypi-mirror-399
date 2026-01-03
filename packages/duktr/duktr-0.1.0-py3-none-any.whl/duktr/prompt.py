"""Default prompt boilerplate"""

def generate_prompt(task: str, concept: str, rules: str) -> str:

    prompt = f"""{task}

    You MUST first try to describe the document using ONLY {concept} from the existing list.
    - If an existing {concept} applies, output it using the exact wording.
    - If the list is missing a {concept} needed to describe the document, create a new one.

    Rules:
    {rules}

    Existing list:
    {{existing_list}}

    Document text:
    {{text}}

    Constraints:
    You must output the extracted {concept}(s) in a valid format exactly as follows:

    ["<{concept} 1>", "<{concept} 2>", ...]
    """
    
    return prompt

