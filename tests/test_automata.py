import numpy as np
import pytest

from automata import (
    PEDESTRIAN,
    PedestrianConflictAutomataModel,
    PedestrianConflictParameters,
)


class TestPedestrianConflictAutomataModel:
    def test_creation_with_unknown(self):
        pedestrian_conflict_parameters = PedestrianConflictParameters(lambda_p=10)
        steps = [np.zeros(10)]
        while not PEDESTRIAN in steps[0]:
            pedestrian_conflict_automata_model = PedestrianConflictAutomataModel(
                pedestrian_conflict_parameters
            )
            steps = pedestrian_conflict_automata_model.run(2)
        assert not np.array_equal(steps[0], steps[1])
