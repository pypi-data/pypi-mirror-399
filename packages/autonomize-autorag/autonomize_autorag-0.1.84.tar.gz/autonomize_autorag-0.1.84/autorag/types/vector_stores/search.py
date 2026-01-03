# pylint: disable=missing-class-docstring, missing-module-docstring

from typing import Any, Dict, Literal

from enum import Enum

from pydantic import BaseModel, Field


class VectorStoreQueryResult(BaseModel):
    """
    Pydantic model for vector store search result
    """

    metadata: Dict[str, Any] = Field(
        description="All metadata fields stored in a collection"
    )
    score: float = Field(description="Search similarity score")



class AdvancedQueryVectorDetails(BaseModel):
    kind : Literal["vector", "text"] = "vector"
    vector : list[float] = Field(..., description="The embedding  for the current vector")
    exhaustive : bool = Field(default=True, description="Whether to perform exhaustive KNN or not")
    fields : list[str] = Field(..., description="The vector feilds to use if there are multiple vector fields in the index")
    top_k : int  = Field(..., description="The top n count used for the current vector")
    weight : float = Field(default=1, description="The relative weight for the current vector in the list of vectors in the current input")


class SearchType(str, Enum):
    VECTOR = "VECTOR"
    FULL_TEXT = "FULL_TEXT",
    HYBRID = "HYBRID"
