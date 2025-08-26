from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, select
from pathlib import Path
import shutil
import uuid

from app.db.session import get_session
from app.core.config import settings
from app.core.security import get_current_user
from app.models.user import User
from app.models.note import Note, Tag, Category, Attachment
from app.schemas.note import NoteCreate, NoteUpdate, NotePublic, SearchQuery, BulkAction, AttachmentPublic
from app.core.integrations import AnalyticsService

router = APIRouter()

def _get_or_create_tags(db: Session, names: List[str]) -> List[Tag]:
    tags: List[Tag] = []
    for name in set(n.strip() for n in names if n.strip()):
        tag = db.query(Tag).filter(Tag.name == name).first()
        if not tag:
            tag = Tag(name=name)
            db.add(tag)
            db.flush()
        tags.append(tag)
    return tags

@router.post("", response_model=NotePublic, summary="Create note", description="Create a new note with optional tags & category.")
def create_note(payload: NoteCreate, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    note = Note(
        title=payload.title,
        content=payload.content,
        is_private=payload.is_private,
        owner_id=current_user.id,
        category_id=payload.category_id,
    )
    note.tags = _get_or_create_tags(db, payload.tags)
    db.add(note)
    db.commit()
    db.refresh(note)
    AnalyticsService().track(current_user.id, "note_created", {"note_id": note.id})
    return note

@router.get("", response_model=List[NotePublic], summary="List my notes", description="List current user's notes.")
def list_notes(db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    notes = db.query(Note).filter(Note.owner_id == current_user.id).order_by(Note.updated_at.desc()).all()
    return notes

@router.get("/{note_id}", response_model=NotePublic, summary="Get note", description="Get a note by ID, owned by the current user.")
def get_note(note_id: int, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    note = db.get(Note, note_id)
    if not note or note.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@router.patch("/{note_id}", response_model=NotePublic, summary="Update note", description="Update fields of a note.")
def update_note(note_id: int, payload: NoteUpdate, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    note = db.get(Note, note_id)
    if not note or note.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Note not found")
    if payload.title is not None:
        note.title = payload.title
    if payload.content is not None:
        note.content = payload.content
    if payload.is_private is not None:
        note.is_private = payload.is_private
    if payload.is_archived is not None:
        note.is_archived = payload.is_archived
    if payload.category_id is not None:
        note.category_id = payload.category_id
    if payload.tags is not None:
        note.tags = _get_or_create_tags(db, payload.tags)
    db.add(note)
    db.commit()
    db.refresh(note)
    AnalyticsService().track(current_user.id, "note_updated", {"note_id": note.id})
    return note

@router.delete("/{note_id}", summary="Delete note", description="Delete a note by ID.")
def delete_note(note_id: int, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    note = db.get(Note, note_id)
    if not note or note.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.commit()
    AnalyticsService().track(current_user.id, "note_deleted", {"note_id": note_id})
    return {"status": "ok"}

@router.post("/{note_id}/attachments", response_model=AttachmentPublic, summary="Upload attachment", description="Upload a file attachment to a note.")
def upload_attachment(note_id: int, file: UploadFile = File(...), db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    note = db.get(Note, note_id)
    if not note or note.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Note not found")

    # Save file
    safe_name = f"{uuid.uuid4().hex}_{file.filename}"
    dest: Path = settings.UPLOADS_DIR / safe_name
    with dest.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    url = f"/uploads/{safe_name}"

    att = Attachment(note_id=note.id, filename=file.filename, url=url)
    db.add(att)
    db.commit()
    db.refresh(att)
    return att

@router.post("/search", response_model=List[NotePublic], summary="Search notes", description="Advanced search by query, tags, categories, and flags.")
def search_notes(payload: SearchQuery, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    q = db.query(Note).filter(Note.owner_id == current_user.id)
    if payload.query:
        q = q.filter(or_(Note.title.ilike(f"%{payload.query}%"), Note.content.ilike(f"%{payload.query}%")))
    if payload.category_ids:
        q = q.filter(Note.category_id.in_(payload.category_ids))
    if payload.private_only is True:
        q = q.filter(Note.is_private.is_(True))
    elif payload.private_only is False:
        q = q.filter(Note.is_private.is_(False))
    if not payload.include_archived:
        q = q.filter(Note.is_archived.is_(False))
    if payload.tags:
        # notes that have all of the tags provided (simplified: any of tags)
        q = q.join(Note.tags).filter(Tag.name.in_(payload.tags))
    return q.order_by(Note.updated_at.desc()).all()

@router.post("/bulk", summary="Bulk operations", description="Perform bulk operations on multiple notes: archive, delete, set category, set privacy.")
def bulk_action(payload: BulkAction, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    if not payload.note_ids:
        return {"updated": 0}
    q = db.query(Note).filter(Note.owner_id == current_user.id, Note.id.in__(payload.note_ids))
    notes = q.all()
    updated = 0
    for note in notes:
        if payload.delete:
            db.delete(note)
            updated += 1
            continue
        if payload.archive is not None:
            note.is_archived = payload.archive
        if payload.set_category_id is not None:
            note.category_id = payload.set_category_id
        if payload.set_private is not None:
            note.is_private = payload.set_private
        db.add(note)
        updated += 1
    db.commit()
    return {"updated": updated}
