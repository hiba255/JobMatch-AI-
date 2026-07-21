import os
import uuid
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from core.config import settings
from modules.cv.models import CV


# ─── CONSTANTES ──────────────────────────────────────────────────────────────

ALLOWED_CONTENT_TYPES = ["application/pdf"]
PDF_MAGIC_BYTES = b"%PDF-"


# ─── HELPERS ─────────────────────────────────────────────────────────────────

def verify_pdf(file_content: bytes, filename: str) -> None:
    """
    Vérifie que le fichier est un vrai PDF.
    
    Pourquoi magic bytes ? L extension .pdf peut être falsifiée — 
    n importe qui peut renommer malware.exe en cv.pdf. 
    Les magic bytes sont les premiers octets du fichier qui identifient 
    son vrai format, impossible à falsifier sans corrompre le fichier.
    """
    # Vérifier la taille
    if len(file_content) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Fichier trop volumineux. Maximum {settings.MAX_FILE_SIZE_MB}Mo."
        )

    # Vérifier les magic bytes
    if not file_content.startswith(PDF_MAGIC_BYTES):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Le fichier n est pas un PDF valide."
        )


def save_file(file_content: bytes, filename: str) -> str:
    """
    Sauvegarde le PDF avec un nom UUID pour éviter les conflits
    et les attaques par path traversal.
    """
    upload_dir = settings.UPLOAD_DIR
    os.makedirs(upload_dir, exist_ok=True)

    # Nom de fichier sécurisé — UUID + extension .pdf uniquement
    safe_filename = f"{uuid.uuid4()}.pdf"
    file_path = os.path.join(upload_dir, safe_filename)

    with open(file_path, "wb") as f:
        f.write(file_content)

    return file_path


# ─── SERVICE FUNCTIONS ───────────────────────────────────────────────────────

def upload_cv(
    db: Session,
    user_id: str,
    file: UploadFile
) -> CV:
    """
    Reçoit un PDF, le valide, le sauvegarde, et crée un enregistrement DB.
    Le traitement NLP est déclenché en arrière-plan après cette étape.
    """
    # Lire le contenu
    file_content = file.file.read()

    # Vérifications sécurité
    verify_pdf(file_content, file.filename)

    # Sauvegarder le fichier
    file_path = save_file(file_content, file.filename)

    # Créer l enregistrement en base
    cv = CV(
        user_id=user_id,
        filename=file.filename,
        file_path=file_path,
        status="pending"
    )
    db.add(cv)
    db.commit()
    db.refresh(cv)

    return cv


def get_cv_status(db: Session, cv_id: str, user_id: str) -> CV:
    """
    Retourne le statut de traitement d un CV.
    Vérifie que le CV appartient bien à l utilisateur connecté.
    """
    cv = db.query(CV).filter(
        CV.id == cv_id,
        CV.user_id == user_id
    ).first()

    if not cv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV introuvable"
        )
    return cv


def get_user_cvs(db: Session, user_id: str) -> list:
    """Retourne tous les CVs d un utilisateur."""
    return db.query(CV).filter(CV.user_id == user_id).all()


def delete_cv(db: Session, cv_id: str, user_id: str) -> None:
    """
    Supprime un CV — fichier physique + enregistrement DB.
    Vérifie que le CV appartient bien à l utilisateur.
    """
    cv = get_cv_status(db, cv_id, user_id)

    # Supprimer le fichier physique
    if os.path.exists(cv.file_path):
        os.remove(cv.file_path)

    db.delete(cv)
    db.commit()