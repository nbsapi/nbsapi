"""Tests for SolutionRequestV2 pydantic model validation."""

import pytest
from pydantic import ValidationError

from nbsapi.api.v2.routers.naturebasedsolutions import SolutionRequestV2
from nbsapi.schemas.impact import ImpactIntensity


def test_solution_request_v2_valid_bbox():
    """Test SolutionRequestV2 with valid bbox."""
    request = SolutionRequestV2(bbox=[-6.2757665, 53.332055, -6.274319, 53.332553])
    assert request.bbox == [-6.2757665, 53.332055, -6.274319, 53.332553]


def test_solution_request_v2_no_bbox():
    """Test SolutionRequestV2 without bbox."""
    request = SolutionRequestV2()
    assert request.bbox is None


def test_solution_request_v2_invalid_bbox_length():
    """Test SolutionRequestV2 with invalid bbox length."""
    with pytest.raises(
        ValidationError, match="Bounding box must contain exactly 4 float values"
    ):
        SolutionRequestV2(bbox=[-6.2757665, 53.332055, -6.274319])


def test_solution_request_v2_invalid_west_coordinate():
    """Test SolutionRequestV2 with invalid west coordinate."""
    with pytest.raises(
        ValidationError, match="West value must be between -180 and 180 degrees"
    ):
        SolutionRequestV2(bbox=[-200, 53.332055, -6.274319, 53.332553])


def test_solution_request_v2_invalid_south_coordinate():
    """Test SolutionRequestV2 with invalid south coordinate."""
    with pytest.raises(
        ValidationError, match="South value must be between -90 and 90 degrees"
    ):
        SolutionRequestV2(bbox=[-6.2757665, -100, -6.274319, 53.332553])


def test_solution_request_v2_invalid_east_coordinate():
    """Test SolutionRequestV2 with invalid east coordinate."""
    with pytest.raises(
        ValidationError, match="East value must be between -180 and 180 degrees"
    ):
        SolutionRequestV2(bbox=[-6.2757665, 53.332055, 200, 53.332553])


def test_solution_request_v2_invalid_north_coordinate():
    """Test SolutionRequestV2 with invalid north coordinate."""
    with pytest.raises(
        ValidationError, match="North value must be between -90 and 90 degrees"
    ):
        SolutionRequestV2(bbox=[-6.2757665, 53.332055, -6.274319, 100])


def test_solution_request_v2_with_all_fields():
    """Test SolutionRequestV2 with all valid fields."""
    request = SolutionRequestV2(
        bbox=[-6.2757665, 53.332055, -6.274319, 53.332553],
        targets=["heat", "flooding"],  # deprecated but still allowed
        intensities=[ImpactIntensity(intensity="low")],
    )
    assert request.bbox == [-6.2757665, 53.332055, -6.274319, 53.332553]
    assert request.targets == ["heat", "flooding"]
    assert len(request.intensities) == 1
    assert request.intensities[0].intensity == "low"
