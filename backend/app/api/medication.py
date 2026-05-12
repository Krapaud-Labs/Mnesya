from datetime import date, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from app import get_db
from app.api.authentication import verify_token, require_caregiver_role
from app.schemas.medication_schema import (
    MedicationCreate,
    MedicationUpdate,
    MedicationResponse,
    WeekResponse,
)
from app.models.medication import MedicationModel
from app.services.medication_facade import MedicationFacade

router = APIRouter(prefix="/api/medication", tags=["Medication"])


def get_medication_facade(db: Session = Depends(get_db)) -> MedicationFacade:
    return MedicationFacade(db)


def get_caregiver_id(token: dict = Depends(require_caregiver_role)) -> str:
    return token.get("sub")


# ==================== CAREGIVER ENDPOINTS ====================

@router.post(
    "",
    response_model=MedicationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a medication and auto-generate its reminders",
)
def create_medication(
    payload: MedicationCreate,
    caregiver_id: str = Depends(get_caregiver_id),
    facade: MedicationFacade = Depends(get_medication_facade),
):
    try:
        medication = facade.create_medication(payload.model_dump(), UUID(caregiver_id))
        return _build_response(medication)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/user/{user_id}",
    response_model=List[MedicationResponse],
    summary="List medications for a user (caregiver view)",
)
def list_medications_for_user(
    user_id: UUID,
    _: dict = Depends(require_caregiver_role),
    facade: MedicationFacade = Depends(get_medication_facade),
):
    return [_build_response(m) for m in facade.get_by_user(user_id)]


@router.get(
    "/{medication_id}",
    response_model=MedicationResponse,
    summary="Get a medication by ID",
)
def get_medication(
    medication_id: UUID,
    _: dict = Depends(verify_token),
    facade: MedicationFacade = Depends(get_medication_facade),
):
    medication = facade.get_medication(medication_id)
    if not medication:
        raise HTTPException(status_code=404, detail="Medication not found")
    return _build_response(medication)


@router.put(
    "/{medication_id}",
    response_model=MedicationResponse,
    summary="Update a medication (regenerates reminders if schedule changed)",
)
def update_medication(
    medication_id: UUID,
    payload: MedicationUpdate,
    _: dict = Depends(require_caregiver_role),
    facade: MedicationFacade = Depends(get_medication_facade),
):
    data = {k: v for k, v in payload.model_dump().items() if v is not None}
    medication = facade.update_medication(medication_id, data)
    if not medication:
        raise HTTPException(status_code=404, detail="Medication not found")
    return _build_response(medication)


@router.delete(
    "/{medication_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a medication and its linked reminders",
)
def delete_medication(
    medication_id: UUID,
    _: dict = Depends(require_caregiver_role),
    facade: MedicationFacade = Depends(get_medication_facade),
):
    if not facade.delete_medication(medication_id):
        raise HTTPException(status_code=404, detail="Medication not found")


# ==================== USER ENDPOINT ====================

@router.get(
    "/week",
    response_model=WeekResponse,
    summary="Get 7-day semainier for the authenticated user",
    description=(
        "Returns the current week (Mon→Sun) with each medication scheduled per day "
        "and its status (PENDING / DONE / MISSED / etc.). "
        "Pass `date` (YYYY-MM-DD) to navigate to another week."
    ),
)
def get_week(
    date_param: Optional[str] = None,
    token: dict = Depends(verify_token),
    facade: MedicationFacade = Depends(get_medication_facade),
):
    user_id = UUID(token.get("sub"))

    if date_param:
        try:
            ref_date = date.fromisoformat(date_param)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Expected YYYY-MM-DD")
    else:
        ref_date = date.today()

    # Always start on Monday
    week_start = ref_date - timedelta(days=ref_date.weekday())
    return facade.get_week(user_id, week_start)


# ==================== HELPER ====================

def _build_response(medication: MedicationModel) -> MedicationResponse:
    return MedicationResponse(
        id=medication.id,
        caregiver_id=medication.caregiver_id,
        user_id=medication.user_id,
        name=medication.name,
        dosage=medication.dosage,
        times=medication.times,
        frequency=medication.frequency,
        recurrence_days=medication.recurrence_days,
        start_date=medication.start_date,
        end_date=medication.end_date,
    )
