"""A simple python sanitizer kickoff package."""

__version__ = "0.1.2"


from .maskers import mask_phone_number

__all__ = ["mask_phone_number"]
