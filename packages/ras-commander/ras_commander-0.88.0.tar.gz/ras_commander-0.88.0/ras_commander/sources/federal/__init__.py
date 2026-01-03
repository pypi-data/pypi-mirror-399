"""Federal HEC-RAS model sources (USGS, FEMA, USACE)."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ras_commander.sources.federal.usgs_sciencebase import UsgsScienceBase

__all__ = ["UsgsScienceBase"]
