from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from typing import List

from ..models.schemas import ParkingLotCreate, ParkingLotUpdate, ParkingLotCreateOut, ParkingLotOut
from ..models.models import ParkingLot
from ..dependencies.db_connection import DatabaseDependency
from ..dependencies.oauth2 import CurrentActiveUserDependency

router = APIRouter(
    prefix='/parking_lots',
    tags=['ParkingLots']
)

@router.get('/', response_model=List[ParkingLotOut], status_code=status.HTTP_200_OK)
def get_all_parking_lots(_: CurrentActiveUserDependency, db: DatabaseDependency):
    parking_lots = db.query(ParkingLot).filter(ParkingLot.is_deleted == False).all()
    return parking_lots

@router.post('/', response_model=ParkingLotCreateOut, status_code=status.HTTP_201_CREATED)
def create_parking_lot(_: CurrentActiveUserDependency, parking_lot: ParkingLotCreate, db: DatabaseDependency):
    try:
        new_parking_lot = ParkingLot(**parking_lot.model_dump())

        # Check if the record with the same name exists
        existing_parking_lot = db.query(ParkingLot).filter(ParkingLot.name == new_parking_lot.name, ParkingLot.is_deleted == True).first()
        if existing_parking_lot:
            # Generate a new name for the existing record
            i = 1
            new_name = f'{new_parking_lot.name} ({i})'
            while db.query(ParkingLot).filter(ParkingLot.name == new_name).first():
                i += 1
                new_name = f'{new_parking_lot.name} ({i})'

            # Update the existing record
            existing_parking_lot.name = new_name

        db.add(new_parking_lot)
        db.commit()
        db.refresh(new_parking_lot)
        return new_parking_lot
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Parking lot already exists')

@router.get('/{parking_lot_id}', response_model=ParkingLotOut, status_code=status.HTTP_200_OK)
def get_parking_lot_id(_: CurrentActiveUserDependency, parking_lot_id: int, db:DatabaseDependency):
    parking_lot = db.query(ParkingLot).filter(ParkingLot.id == parking_lot_id, ParkingLot.is_deleted == False).first()
    if not parking_lot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Parking lot not found')
    return parking_lot

@router.put('/{parking_lot_id}', response_model=ParkingLotOut, status_code=status.HTTP_200_OK)
def update_parking_lot(parking_lot_id: int,
                       parking_lot_update: ParkingLotUpdate,
                       _: CurrentActiveUserDependency, 
                       db: DatabaseDependency):
    parking_lot = db.query(ParkingLot).filter(ParkingLot.id == parking_lot_id, ParkingLot.is_deleted == False).first()
    if not parking_lot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Parking lot not found')
    parking_lot.name = parking_lot_update.name
    parking_lot.address = parking_lot_update.address
    parking_lot.updated_at = datetime.now()
    db.commit()
    db.refresh(parking_lot)
    return parking_lot

@router.delete('/{parking_lot_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_parking_lot(parking_lot_id: int,_: CurrentActiveUserDependency, db:DatabaseDependency):
    parking_lot = db.query(ParkingLot).filter(ParkingLot.id == parking_lot_id, ParkingLot.is_deleted == False).first()
    if not parking_lot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Parking lot not found')
    parking_lot.is_deleted = True
    parking_lot.deleted_at = datetime.now()
    db.commit()
    return