"""Base model definitions for database operations."""

from datetime import datetime
from typing import Any, Dict, Optional, Type, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T", bound="BaseDBModel")


class BaseDBModel(BaseModel):
    """Base model for all database models."""

    id: Optional[str] = Field(default=None, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic config."""

        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {datetime: lambda v: v.isoformat()}

    def update(self, **kwargs) -> None:
        """Update model fields."""
        for field, value in kwargs.items():
            if hasattr(self, field):
                setattr(self, field, value)
        self.updated_at = datetime.utcnow()

    def dict(self, *args, **kwargs) -> Dict[str, Any]:
        """Convert model to dictionary."""
        data = super().dict(*args, **kwargs)
        if "_id" in data and "id" not in data:
            data["id"] = data.pop("_id")
        return data

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Create model from dictionary."""
        if "id" in data and "_id" not in data:
            data["_id"] = data.pop("id")
        return cls(**data)
