from dataclasses import dataclass


@dataclass
class SubmitResponseDTO:
    """Answer to the player right after submitting - the processing continues in the background."""
    result_id: str
    status: str
    message: str
