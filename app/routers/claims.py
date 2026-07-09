import uuid
from app.schema import ClaimCreate, ClaimRead
from app.models.claim import Claim
from app.routers import claims
from app.db import SessionDep
from fastapi import APIRouter, HTTPException 
from sqlalchemy import select


router = APIRouter()

@router.post("/claims/", response_model = ClaimRead)
def create_claim(claim: ClaimCreate, session: SessionDep) -> Claim:
    claim_dict = claim.model_dump(exclude_unset=True)
    claim_dict["status"] = "Submitted"
    claim_dict["reference_number"] = str(uuid.uuid4())

    db_claim = Claim(**claim_dict)
    session.add(db_claim)
    session.commit()
    session.refresh(db_claim)
    return db_claim

@router.get("/claims/{claim_id}", response_model = ClaimRead)
def get_claim(claim_id: uuid.UUID, session: SessionDep):
    stmt = select(Claim).where(Claim.id == claim_id)
    claim = session.execute(stmt).scalar_one_or_none()
    if claim is None:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim

@router.get("/claims/", response_model = list[ClaimRead])
def list_claim(session: SessionDep):
    stmt = select(Claim)
    claims = session.execute(stmt).scalars().all()
    return claims