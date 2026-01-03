from typing import List, TypeVar, Generic

from pydantic import BaseModel, Field

T  = TypeVar("T")

class ListSlice(BaseModel, Generic[T]):
    items: List[T] = Field(description="当前页的数据集合")
    total: int = Field(description="总记录数")
    page_num: int = Field(1, description="当前页面， 默认为1")
    page_size: int = Field(10, description="每页的数据量，默认为10")