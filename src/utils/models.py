from pydantic import BaseModel, Field, model_validator
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

    @model_validator(mode="after")
    def validate_map_logic(self) -> "LevelData":
        """
        Cross-validates everything simultaneously to accumulate
        all logical errors before raising them.
        """
        errors: list[str] = []

        # --- 1. Hubs Validation ---
        start_count = sum(1 for z in self.zones if z.type == "start_hub")
        end_count = sum(1 for z in self.zones if z.type == "end_hub")

        if start_count != 1 or end_count != 1:
            errors.append(
                f"Map must have exactly one start_hub (found {start_count}) "
                f"and one end_hub (found {end_count})."
            )

        seen_names_lower: set[str] = set()
        seen_coords: set[tuple[int, int]] = set()

        for z in self.zones:
            name_lower = z.name.lower()
            if name_lower in seen_names_lower:
                errors.append(
                    "Duplicate hub name detected (case-insensitive): "
                    f"'\033[93m{z.name}\033[0m'"
                )
            seen_names_lower.add(name_lower)

            coords = (z.x, z.y)
            if coords in seen_coords:
                errors.append(
                    f"Duplicate coordinates \033[93m{coords}\033[0m detected "
                    f"for hub: '\033[93m{z.name}\033[0m'"
                )
            seen_coords.add(coords)

        # --- 2. Connections Validation ---
        valid_hub_names = {z.name for z in self.zones}
        seen_connections: set[tuple[str, str]] = set()

        for conn in self.connections:
            if conn.from_hub not in valid_hub_names:
                errors.append(
                    "Connection references an unknown hub: "
                    f"'\033[93m{conn.from_hub}\033[0m'"
                )
            if conn.to_hub not in valid_hub_names:
                errors.append(
                    "Connection references an unknown hub: "
                    f"'\033[93m{conn.to_hub}\033[0m'"
                )

            if conn.from_hub == conn.to_hub:
                errors.append(
                    "A hub cannot connect to itself: "
                    f"'\033[93m{conn.from_hub}\033[0m'"
                )

            # Determine the alphabetical order of the two hubs
            first_hub = min(conn.from_hub, conn.to_hub)
            second_hub = max(conn.from_hub, conn.to_hub)

            # Create the normalized connection tuple
            normalized_conn: tuple[str, str] = (first_hub, second_hub)

            if normalized_conn in seen_connections:
                errors.append(
                    f"Duplicate connection detected between "
                    f"'\033[93m{conn.from_hub}\033[0m' and "
                    f"'\033[93m{conn.to_hub}\033[0m'"
                )
            seen_connections.add(normalized_conn)

        # --- Final Verdict ---
        if errors:
            raise ValueError("\n".join(errors))

        return self
