from __future__ import annotations

from dataclasses import dataclass
import math

from scipy.stats import poisson

STANDARD_CONFIDENCE_LEVELS = tuple(float(level) for level in range(50, 100, 5))


@dataclass(frozen=True)
class SpareQuantityResult:
    expected_removals: float
    recommended_spares: int
    requested_confidence: float
    achieved_confidence: float


def calculate_expected_removals(
    aircraft_count: int,
    annual_flight_hours: float,
    turnaround_days: float,
    quantity_per_aircraft: float,
    mtbur: float,
) -> float:
    """Calculate expected removals during TAT with a Poisson demand model."""
    aircraft = int(aircraft_count)
    annual_hours = float(annual_flight_hours)
    tat_days = float(turnaround_days)
    qpa = float(quantity_per_aircraft)
    mtbur_hours = float(mtbur)

    if aircraft <= 0:
        raise ValueError("Number of aircraft must be greater than zero.")
    for label, value in (
        ("Average annual flight hours", annual_hours),
        ("Turnaround time", tat_days),
    ):
        if not math.isfinite(value) or value < 0.0:
            raise ValueError(f"{label} must be a finite value of zero or more.")
    if not math.isfinite(qpa) or qpa <= 0.0:
        raise ValueError("Quantity per aircraft must be a finite value greater than zero.")
    if not math.isfinite(mtbur_hours) or mtbur_hours <= 0.0:
        raise ValueError("MTBUR must be a finite value greater than zero.")

    return annual_hours * qpa * aircraft * (tat_days / 365.0) / mtbur_hours


def recommend_spare_quantity(expected_removals: float, confidence_percent: float) -> SpareQuantityResult:
    """Return the least whole spare count that meets the Poisson confidence target."""
    demand = float(expected_removals)
    confidence = float(confidence_percent) / 100.0

    if not math.isfinite(demand) or demand < 0.0:
        raise ValueError("Expected removals must be a finite value of zero or more.")
    if not math.isfinite(confidence) or not 0.0 < confidence < 1.0:
        raise ValueError("Confidence must be greater than 0% and less than 100%.")

    recommended = 0 if demand == 0.0 else max(0, int(poisson.ppf(confidence, demand)))
    achieved = float(poisson.cdf(recommended, demand))
    return SpareQuantityResult(demand, recommended, confidence, achieved)


def spare_recommendations_by_confidence(
    expected_removals: float,
    confidence_levels: tuple[float, ...] = STANDARD_CONFIDENCE_LEVELS,
) -> tuple[SpareQuantityResult, ...]:
    """Return Poisson spare recommendations for each requested confidence level."""
    return tuple(recommend_spare_quantity(expected_removals, level) for level in confidence_levels)


def calculate_spare_quantity(
    aircraft_count: int,
    annual_flight_hours: float,
    turnaround_days: float,
    quantity_per_aircraft: float,
    mtbur: float,
    confidence_percent: float,
) -> SpareQuantityResult:
    expected_removals = calculate_expected_removals(
        aircraft_count,
        annual_flight_hours,
        turnaround_days,
        quantity_per_aircraft,
        mtbur,
    )
    return recommend_spare_quantity(expected_removals, confidence_percent)
