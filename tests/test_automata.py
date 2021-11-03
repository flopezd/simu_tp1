import numpy as np
import pytest

from automata import (
    BLOCK,
    CROSSWALK,
    PEDESTRIAN,
    PEDESTRIAN_WAIT,
    ROAD,
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

    def test_get_initial_system_state(self):
        pedestrian_conflict_parameters = PedestrianConflictParameters(
            car_start_point_length=1,
            road_width=2,
            crosswalk_width=2,
            fixed_pedestrian_waiting_length=1,
        )
        pedestrian_conflict_automata_model = PedestrianConflictAutomataModel(
            pedestrian_conflict_parameters
        )
        system_state = pedestrian_conflict_automata_model.get_initial_system_state(
            full_grid_length=pedestrian_conflict_parameters.full_grid_length,
            full_grid_width=pedestrian_conflict_parameters.full_grid_width,
            crosswalk_width=pedestrian_conflict_parameters.crosswalk_width,
            pedestrian_waiting_length=pedestrian_conflict_parameters.pedestrian_waiting_length,
            car_start_point_length=pedestrian_conflict_parameters.car_start_point_length,
            road_width=pedestrian_conflict_parameters.road_width,
        )
        expected_system_state = [
            [ROAD, ROAD, ROAD, ROAD],
            [PEDESTRIAN_WAIT, CROSSWALK, CROSSWALK, PEDESTRIAN_WAIT],
            [PEDESTRIAN_WAIT, CROSSWALK, CROSSWALK, PEDESTRIAN_WAIT],
            [BLOCK, ROAD, ROAD, BLOCK],
        ]

        assert np.array_equal(system_state, expected_system_state)
