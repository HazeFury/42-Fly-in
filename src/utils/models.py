from pydantic import BaseModel, Field, field_validator
from typing import Literal


class ZoneMetadata(BaseModel):
    """
    Validates and stores metadata for a specific zone.
    Provides default values as defined in the subject.
    """
    zone: Literal[
        "normal", "blocked", "restricted", "priority"
        ] = Field(default="normal")
    color: str = Field(default="none")
    max_drones: int = Field(default=1, gt=0)  # Must be greater than 0


class ConnectionMetadata(BaseModel):
    """
    Validates and stores metadata for a connection between two zones.
    """
    max_link_capacity: int = Field(default=1, gt=0)


class ZoneData(BaseModel):
    """
    Represents a raw zone parsed from the file before graph instantiation.
    """
    type: Literal["start_hub", "hub", "end_hub"]
    name: str
    x: int
    y: int
    metadata: ZoneMetadata


class ConnectionData(BaseModel):
    """
    Represents a raw connection parsed from the file.
    """
    from_hub: str
    to_hub: str
    metadata: ConnectionMetadata


class LevelData(BaseModel):
    """
    The root model that validates the entire parsed dictionary.
    """
    level_name: str
    nb_drones: int = Field(gt=0)
    zones: list[ZoneData]
    connections: list[ConnectionData]

    @field_validator("zones")
    @classmethod
    def validate_hubs(cls, zones: list[ZoneData]) -> list[ZoneData]:
        """
        Ensures there is exactly one start_hub and one end_hub.
        """
        start_count = sum(1 for z in zones if z.type == "start_hub")
        end_count = sum(1 for z in zones if z.type == "end_hub")

        if start_count != 1 or end_count != 1:
            raise ValueError(
                f"Map must have exactly one start_hub (found {start_count}) "
                f"and one end_hub (found {end_count})."
            )
        return zones
