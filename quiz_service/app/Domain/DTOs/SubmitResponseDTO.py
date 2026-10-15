from dataclasses import dataclass


@dataclass
class SubmitResponseDTO:
    """Answer to the player right after submitting"""
    result_id: str
    status: str
    message: str
