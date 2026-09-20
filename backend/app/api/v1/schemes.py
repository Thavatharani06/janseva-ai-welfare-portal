from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.repositories.scheme_repository import SchemeRepository
from app.services.alias_service import AliasService
from app.schemas.scheme import SchemeResponse, CategoryResponse, AliasResolveResponse, AliasResponse
from app.api.v1.auth import get_current_admin

router = APIRouter(prefix="/schemes", tags=["Government Schemes & Alias Engine"])

@router.get("/categories", response_model=List[CategoryResponse])
async def list_categories(db: AsyncSession = Depends(get_db)):
    repo = SchemeRepository(db)
    return await repo.get_categories()

@router.get("", response_model=List[SchemeResponse])
async def list_schemes(
    search: Optional[str] = Query(None),
    category_id: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    gender: Optional[str] = Query(None),
    min_age: Optional[int] = Query(None),
    max_age: Optional[int] = Query(None),
    community: Optional[str] = Query(None),
    occupation: Optional[str] = Query(None),
    disability: Optional[bool] = Query(None),
    max_income: Optional[float] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    effective_category = category_id or category
    repo = SchemeRepository(db)
    return await repo.get_all(
        search=search,
        category_id=effective_category,
        state=state,
        gender=gender,
        min_age=min_age,
        max_age=max_age,
        community=community,
        occupation=occupation,
        disability=disability,
        max_income=max_income
    )

@router.get("/alias/search", response_model=AliasResolveResponse)
async def search_scheme_by_alias(alias: str = Query(..., description="Query phrase or scheme alias in Tamil, English, or Hindi"), db: AsyncSession = Depends(get_db)):
    alias_service = AliasService(db)
    scheme, confidence, matched_term = await alias_service.resolve_scheme_by_query(alias)
    
    scheme_res = SchemeResponse.model_validate(scheme) if scheme else None
    return AliasResolveResponse(
        query=alias,
        matched_scheme=scheme_res,
        confidence=confidence,
        matched_alias=matched_term
    )

@router.get("/{scheme_id}", response_model=SchemeResponse)
async def get_scheme(scheme_id: str, db: AsyncSession = Depends(get_db)):
    repo = SchemeRepository(db)
    scheme = await repo.get_by_id(scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return scheme

@router.post("/{scheme_id}/alias", response_model=AliasResponse)
async def add_alias(scheme_id: str, alias_text: str = Query(...), language_code: str = Query("en"), admin_user = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    alias_service = AliasService(db)
    new_alias = await alias_service.add_alias(scheme_id, alias_text, language_code)
    return AliasResponse.model_validate(new_alias)
