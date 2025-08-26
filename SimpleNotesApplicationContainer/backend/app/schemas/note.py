from typing import List, Optional
from pydantic import BaseModel, Field


class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

class TagCreate(TagBase):
    pass

class TagPublic(TagBase):
    id: int
    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

class CategoryCreate(CategoryBase):
    pass

class CategoryPublic(CategoryBase):
    id: int
    class Config:
        from_attributes = True


# PUBLIC_INTERFACE
class NoteCreate(BaseModel):
    """Schema for creating a note."""
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field("", description="Rich text content (HTML/Markdown)")
    is_private: bool = True
    category_id: Optional[int] = None
    tags: List[str] = Field(default_factory=list, description="List of tag names")

# PUBLIC_INTERFACE
class NoteUpdate(BaseModel):
    """Schema for updating a note."""
    title: Optional[str] = None
    content: Optional[str] = None
    is_private: Optional[bool] = None
    is_archived: Optional[bool] = None
    category_id: Optional[int] = None
    tags: Optional[List[str]] = None

# PUBLIC_INTERFACE
class AttachmentPublic(BaseModel):
    """Attachment response schema."""
    id: int
    filename: str
    url: str
    class Config:
        from_attributes = True

# PUBLIC_INTERFACE
class NotePublic(BaseModel):
    """Note response schema with tags and category."""
    id: int
    title: str
    content: str
    is_private: bool
    is_archived: bool
    category: CategoryPublic | None
    tags: List[TagPublic]
    attachments: List[AttachmentPublic]
    class Config:
        from_attributes = True

# PUBLIC_INTERFACE
class SearchQuery(BaseModel):
    """Advanced search query for notes."""
    query: str = ""
    tags: List[str] = []
    category_ids: List[int] = []
    include_archived: bool = False
    private_only: bool | None = None

# PUBLIC_INTERFACE
class BulkAction(BaseModel):
    """Bulk operation request schema."""
    note_ids: List[int]
    archive: bool | None = None
    delete: bool | None = None
    set_category_id: int | None = None
    set_private: bool | None = None
