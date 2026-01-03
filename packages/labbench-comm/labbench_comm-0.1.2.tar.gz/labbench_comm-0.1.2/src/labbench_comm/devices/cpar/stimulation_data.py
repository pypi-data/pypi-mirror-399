from dataclasses import dataclass
from typing import List


@dataclass(slots=True)
class StimulationSample:
    actual_pressure_01: float
    target_pressure_01: float
    final_pressure_01: float

    actual_pressure_02: float
    target_pressure_02: float
    final_pressure_02: float

    vas_score: float
    final_vas_score: float


class StimulationData:
    """
    Collected data from a single stimulation cycle.
    """

    def __init__(self) -> None:
        self.samples: List[StimulationSample] = []

    def add_sample(self, sample: StimulationSample) -> None:
        self.samples.append(sample)

    def __len__(self) -> int:
        return len(self.samples)
    
    # ------------------------------------------------------------------
    # Time axis
    # ------------------------------------------------------------------

    @property
    def time(self) -> List[float]:
        """
        Time axis in seconds for each sample, derived from sample index
        using the protocol update rate.
        """
        dt = 1.0 / 20
        return [i * dt for i in range(len(self.samples))]
        
   # ------------------------------------------------------------------
    # Vectorized / list-based accessors
    # ------------------------------------------------------------------

    @property
    def actual_pressure_01(self) -> List[float]:
        return [s.actual_pressure_01 for s in self.samples]

    @property
    def target_pressure_01(self) -> List[float]:
        return [s.target_pressure_01 for s in self.samples]

    @property
    def final_pressure_01(self) -> List[float]:
        return [s.final_pressure_01 for s in self.samples]

    @property
    def actual_pressure_02(self) -> List[float]:
        return [s.actual_pressure_02 for s in self.samples]

    @property
    def target_pressure_02(self) -> List[float]:
        return [s.target_pressure_02 for s in self.samples]

    @property
    def final_pressure_02(self) -> List[float]:
        return [s.final_pressure_02 for s in self.samples]

    @property
    def vas_scores(self) -> List[float]:
        return [s.vas_score for s in self.samples]

    @property
    def final_vas_scores(self) -> List[float]:
        return [s.final_vas_score for s in self.samples]

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    @property
    def has_data(self) -> bool:
        return bool(self.samples)

    def as_dict(self) -> dict[str, List[float]]:
        """
        Return all data as a dict of lists (useful for pandas / JSON).
        """
        return {
            "time": self.time,
            "actual_pressure_01": self.actual_pressure_01,
            "target_pressure_01": self.target_pressure_01,
            "final_pressure_01": self.final_pressure_01,
            "actual_pressure_02": self.actual_pressure_02,
            "target_pressure_02": self.target_pressure_02,
            "final_pressure_02": self.final_pressure_02,
            "vas_score": self.vas_scores,
            "final_vas_score": self.final_vas_scores,
        }    
