from transformers import AutoTokenizer


class TokenCounter:
    def __init__(self, model_name: str):
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True,
        )

    def count(self, text: str) -> int:
        return len(
            self.tokenizer.encode(
                text,
                add_special_tokens=False,
                truncation=False,
            )
        )
