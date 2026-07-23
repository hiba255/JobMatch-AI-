from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy.orm import Session
from core.database import get_db
from core.dependencies import get_current_user
from modules.cv.schemas import CVResponse, CVStatusResponse, CVListResponse
from modules.cv.service import upload_cv, get_cv_status, get_user_cvs, delete_cv

router = APIRouter(prefix="/cv", tags=["CV"])


@router.post("/upload", response_model=CVResponse, status_code=201)
def upload(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload un CV en PDF.
    Valide le fichier (magic bytes + taille) et démarre le traitement NLP.
    """
    cv = upload_cv(db, user_id, file)
    return CVResponse.model_validate(cv)


@router.get("/list", response_model=CVListResponse)
def list_cvs(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retourne tous les CVs de l utilisateur connecté."""
    cvs = get_user_cvs(db, user_id)
    return CVListResponse(
        cvs=[CVResponse.model_validate(cv) for cv in cvs],
        total=len(cvs)
    )


@router.get("/{cv_id}/status", response_model=CVStatusResponse)
def cv_status(
    cv_id: str,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retourne le statut de traitement d un CV."""
    cv = get_cv_status(db, cv_id, user_id)
    return CVStatusResponse.model_validate(cv)


@router.delete("/{cv_id}", status_code=204)
def remove_cv(
    cv_id: str,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Supprime un CV et son fichier physique."""
    delete_cv(db, cv_id, user_id)
    return None