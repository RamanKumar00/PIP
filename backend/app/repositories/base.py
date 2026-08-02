from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from sqlalchemy.orm import Session

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        """Base repository class with default methods to Create, Read, Update, Delete (CRUD).

        Args:
            model: A SQLAlchemy model class.
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """Fetch a single record by its primary key ID.

        Args:
            db: SQLAlchemy Database Session.
            id: Primary key ID of the record.

        Returns:
            Optional[ModelType]: Found record or None.
        """
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """Fetch multiple records with offset and limit pagination.

        Args:
            db: SQLAlchemy Database Session.
            skip: Offset of records to skip.
            limit: Maximum count of records to fetch.

        Returns:
            List[ModelType]: List of fetched records.
        """
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: Any) -> ModelType:
        """Insert a new record into the database.

        Args:
            db: SQLAlchemy Database Session.
            obj_in: Pydantic schema or Dictionary containing new record fields.

        Returns:
            ModelType: The newly created model instance.
        """
        if isinstance(obj_in, dict):
            db_obj = self.model(**obj_in)
        else:
            db_obj = self.model(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: ModelType, obj_in: Union[Any, Dict[str, Any]]
    ) -> ModelType:
        """Update an existing record in the database.

        Args:
            db: SQLAlchemy Database Session.
            db_obj: The existing database model instance.
            obj_in: Pydantic schema or Dictionary containing updated fields.

        Returns:
            ModelType: The updated model instance.
        """
        obj_data = db_obj.__dict__
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
            
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
                
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: Any) -> Optional[ModelType]:
        """Remove a record by its primary key ID from the database.

        Args:
            db: SQLAlchemy Database Session.
            id: Primary key ID of the record to delete.

        Returns:
            Optional[ModelType]: The deleted record instance if found, else None.
        """
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj
