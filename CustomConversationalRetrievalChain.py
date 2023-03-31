from __future__ import annotations

import warnings
from abc import abstractmethod
# from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel, Extra, Field, root_validator

# from langchain.chains.base import Chain
# from langchain.chains.combine_documents.base import BaseCombineDocumentsChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.conversational_retrieval.prompts import CONDENSE_QUESTION_PROMPT
from langchain.chains.conversational_retrieval.base import BaseConversationalRetrievalChain
from langchain.chains.llm import LLMChain

from langchain.prompts.base import BasePromptTemplate
from langchain.schema import BaseLanguageModel, BaseRetriever, Document
# from langchain.vectorstores.base import VectorStore
from Custom_load_qa_chain import custom_load_qa_chain
from CommonHelper import *


class CustomConversationalRetrievalChain(BaseConversationalRetrievalChain, BaseModel):
    """Chain for chatting with an index."""

    retriever: BaseRetriever
    """Index to connect to."""
    max_tokens_limit: Optional[int] = None
    """If set, restricts the docs to return from store based on tokens, enforced only
    for StuffDocumentChain"""

    def _reduce_tokens_below_limit(self, docs: List[Document]) -> List[Document]:
        num_docs = len(docs)

        # if self.max_tokens_limit and isinstance(self.combine_docs_chain, StuffDocumentsChain):
        if self.max_tokens_limit > 0:
            tokens = [
                # self.combine_docs_chain.llm_chain.llm.get_num_tokens(doc.page_content)
                get_rough_token_len(doc.page_content)
                for doc in docs
            ]
            token_count = sum(tokens[:num_docs])
            while token_count > self.max_tokens_limit:
                num_docs -= 1
                token_count -= tokens[num_docs]

        return docs[:num_docs]

    def _get_docs(self, question: str, inputs: Dict[str, Any]) -> List[Document]:
        docs = self.retriever.get_relevant_documents(question)
        return self._reduce_tokens_below_limit(docs)

    async def _aget_docs(self, question: str, inputs: Dict[str, Any]) -> List[Document]:
        docs = await self.retriever.aget_relevant_documents(question)
        return self._reduce_tokens_below_limit(docs)

    @classmethod
    def from_llm(
        cls,
        llm: BaseLanguageModel,
        retriever: BaseRetriever,
        condense_question_prompt: BasePromptTemplate = CONDENSE_QUESTION_PROMPT,
        # qa_prompt: Optional[BasePromptTemplate] = None,
        chain_type: str = "refine",
        **kwargs: Any,
    ) -> BaseConversationalRetrievalChain:
        """Load chain from LLM."""
        doc_chain = custom_load_qa_chain(
            llm,
            chain_type=chain_type,
            # question_prompt=qa_prompt,
        )
        condense_question_chain = LLMChain(
            llm=llm, prompt=condense_question_prompt)
        return cls(
            retriever=retriever,
            combine_docs_chain=doc_chain,
            question_generator=condense_question_chain,
            **kwargs,
        )
