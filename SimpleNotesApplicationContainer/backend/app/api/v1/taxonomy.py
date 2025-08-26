from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.models.note import Tag, Category
from app.schemas.note import TagCreate, TagPublic, CategoryCreate, CategoryPublic
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/tags", response_model=List[TagPublic], summary="List tags")
def list_tags(db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return db.query(Tag).order_by(Tag.name.asc()).all()

@router.post("/tags", response_model=TagPublic, summary="Create tag")
def create_tag(payload: TagCreate, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    exists = db.query(Tag).filter(Tag.name == payload.name).first()
    if exists:
        raise HTTPException(status_code=400, detail="Tag exists")
    tag = Tag(name=payload.name)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag

@router.get("/categories", response_model=List[CategoryPublic], summary="List categories")
def list_categories(db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return db.query(Category).order_by(Category.name.asc()).all()

@router.post("/categories", response_model=CategoryPublic, summary="Create category")
def create_category(payload: CategoryCreate, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    exists = db.query(Category).filter(Category.name == payload.name).first()
    if exists:
        raise HTTPException(status_code=400, detail="Category exists")
    cat = Category(name=payload.name)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat
