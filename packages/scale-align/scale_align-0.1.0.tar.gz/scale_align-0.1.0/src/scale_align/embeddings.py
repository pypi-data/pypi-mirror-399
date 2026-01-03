"""E5 Embedder module for asymmetric retrieval."""

from typing import List, Optional, Union

import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer


class E5Embedder:
    """Wrapper for intfloat/e5-large-instruct model with asymmetric prompting."""

    MODEL_NAME = "intfloat/e5-large-instruct"
    QUERY_INSTRUCTION = "Instruct: retrieve parallel sentences; Query: "

    def __init__(
        self,
        model_name: Optional[str] = None,
        device: Optional[str] = None,
        batch_size: int = 32,
    ):
        """Initialize the E5 embedder.

        Args:
            model_name: HuggingFace model name. Defaults to e5-large-instruct.
            device: Device to use ('cuda', 'cpu', or 'auto'). Defaults to auto.
            batch_size: Batch size for encoding. Defaults to 32.
        """
        self.model_name = model_name or self.MODEL_NAME
        self.batch_size = batch_size

        # Auto-detect device
        if device is None or device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        # Load model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name).to(self.device)
        self.model.eval()

    def _mean_pooling(
        self, model_output: torch.Tensor, attention_mask: torch.Tensor
    ) -> torch.Tensor:
        """Apply mean pooling to get sentence embeddings."""
        token_embeddings = model_output[0]
        input_mask_expanded = (
            attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        )
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(
            input_mask_expanded.sum(1), min=1e-9
        )

    def _encode_batch(
        self, texts: List[str], is_query: bool = False
    ) -> np.ndarray:
        """Encode a batch of texts.

        Args:
            texts: List of texts to encode.
            is_query: If True, prepend query instruction for asymmetric retrieval.

        Returns:
            NumPy array of embeddings with shape (len(texts), embedding_dim).
        """
        if is_query:
            texts = [f"{self.QUERY_INSTRUCTION}{t}" for t in texts]

        encoded = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt",
        ).to(self.device)

        with torch.no_grad():
            model_output = self.model(**encoded)
            embeddings = self._mean_pooling(model_output, encoded["attention_mask"])
            # Normalize embeddings
            embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)

        return embeddings.cpu().numpy()

    def encode(
        self, texts: Union[str, List[str]], is_query: bool = False
    ) -> np.ndarray:
        """Encode texts into embeddings.

        Args:
            texts: Single text or list of texts to encode.
            is_query: If True, prepend query instruction for asymmetric retrieval.
                     Use True for "queries" and False for "passages".

        Returns:
            NumPy array of embeddings.
        """
        if isinstance(texts, str):
            texts = [texts]

        all_embeddings = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            embeddings = self._encode_batch(batch, is_query=is_query)
            all_embeddings.append(embeddings)

        return np.vstack(all_embeddings) if len(all_embeddings) > 1 else all_embeddings[0]

    def encode_queries(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Encode texts as queries (with instruction prefix).

        Args:
            texts: Single text or list of texts.

        Returns:
            NumPy array of query embeddings.
        """
        return self.encode(texts, is_query=True)

    def encode_passages(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Encode texts as passages (without instruction prefix).

        Args:
            texts: Single text or list of texts.

        Returns:
            NumPy array of passage embeddings.
        """
        return self.encode(texts, is_query=False)
