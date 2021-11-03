from dataclasses import dataclass, field

import numpy as np

# 1 cell  = 0.5m, 1 step = 1 sec
ROAD_WIDTH = 42  # 21m
ROAD_LINE_WIDTH = 7  # 3.5m
ROAD_TOTAL_LINES = ROAD_WIDTH // ROAD_LINE_WIDTH
LINES_PER_DIRECTION = ROAD_TOTAL_LINES // 2
MAXIMUM_WAITING_PEDESTRIANS = 100
CAR_WIDTH = 5  # 2.5m
CAR_LENGTH = 6  # 3m
CAR_SPEED = 10  # 5m/s
EMPTY_LINE_WIDTH = (ROAD_LINE_WIDTH - CAR_WIDTH) // 2  # 0.5m
CAR_START_POINT_LENGTH = 10  # 5m
LAMBDA_V = 0.6

ROAD = 0
PEDESTRIAN_WAIT = 1
CROSSWALK = 2
PEDESTRIAN = 3
CAR = 4
GOING_RIGHT_PEDESTRIAN = 3
GOING_DOWN_CAR = 4
GOING_LEFT_PEDESTRIAN = 5
GOING_UP_CAR = 6
BLOCK = 7


@dataclass
class PedestrianConflictParameters:
    crosswalk_width: int = 5  # 2.5m
    lambda_p: float = 0.8
    # lambda_p: float = 0.13
    pedestrian_waiting_length: int = field(init=False)
    full_grid_length: int = field(init=False)
    full_grid_width: int = field(init=False)

    def __post_init__(self):
        self.pedestrian_waiting_length = int(
            np.ceil(MAXIMUM_WAITING_PEDESTRIANS / self.crosswalk_width)
        )
        self.full_grid_length = self.crosswalk_width + 2 * CAR_START_POINT_LENGTH
        self.full_grid_width = ROAD_WIDTH + 2 * self.pedestrian_waiting_length


class PedestrianConflictAutomataModel:
    pedestrian_conflict_parameters: PedestrianConflictParameters

    def __init__(
        self,
        pedestrian_conflict_parameters: PedestrianConflictParameters = PedestrianConflictParameters(),
    ):
        self.pedestrian_conflict_parameters = pedestrian_conflict_parameters

    def get_initial_system_state(
        self,
        full_grid_length: int,
        full_grid_width: int,
        crosswalk_width: int,
        pedestrian_waiting_length: int,
    ):
        system_estate = np.zeros((full_grid_length, full_grid_width))
        for i in range(crosswalk_width):
            for j in range(pedestrian_waiting_length):
                system_estate[i + CAR_START_POINT_LENGTH, j] = PEDESTRIAN_WAIT
                system_estate[
                    i + CAR_START_POINT_LENGTH,
                    j + pedestrian_waiting_length + ROAD_WIDTH,
                ] = PEDESTRIAN_WAIT

            for j in range(ROAD_WIDTH):
                system_estate[
                    i + CAR_START_POINT_LENGTH, j + pedestrian_waiting_length
                ] = CROSSWALK

        for i in range(CAR_START_POINT_LENGTH):
            for j in range(pedestrian_waiting_length):
                system_estate[i + CAR_START_POINT_LENGTH + crosswalk_width, j] = BLOCK
                system_estate[
                    i + CAR_START_POINT_LENGTH + crosswalk_width,
                    j + pedestrian_waiting_length + ROAD_WIDTH,
                ] = BLOCK
        return system_estate

    def add_pedestrians(
        self,
        system_state,
        crosswalk_width,
        initial_length,
        final_length,
        length_increment,
        pedestrian_direction,
    ):
        i = 0
        j = initial_length
        while system_state[i + CAR_START_POINT_LENGTH, j] != PEDESTRIAN_WAIT:
            if i == crosswalk_width - 1:
                j = length_increment + j
                if j == final_length:
                    break
            i = (1 + i) % crosswalk_width

        if j != -1:
            system_state[i + CAR_START_POINT_LENGTH, j] = pedestrian_direction
        else:
            print("Max pedastrians in waiting space")

    def car_has_space(self, system_state, starting_i, starting_j):
        i = starting_i
        j = starting_j
        for i in range(starting_i, starting_i + CAR_LENGTH):
            for j in range(starting_j, starting_j + CAR_WIDTH):
                if system_state[i, j] != ROAD:
                    return False
        return True

    def add_car(self, system_state, starting_i, starting_j, max_j, car_direction):
        i = starting_i
        j = starting_j
        while not self.car_has_space(system_state, i, j):
            if j >= max_j:
                break
            j = j + ROAD_LINE_WIDTH

        if j < max_j:
            for c_i in range(CAR_LENGTH):
                for c_j in range(CAR_WIDTH):
                    system_state[i + c_i, j + c_j] = car_direction
        # else:
        #     print("Max cars in waiting space")

    def add_incoming_cars_and_pedestrians(
        self,
        system_state,
        lambda_p,
        crosswalk_width,
        pedestrian_waiting_length,
        full_grid_width,
    ):
        new_pedestrians_left = np.random.poisson(lambda_p)
        new_pedestrians_right = np.random.poisson(lambda_p)
        new_cars_up = np.random.poisson(LAMBDA_V)
        new_cars_down = np.random.poisson(LAMBDA_V)

        for _ in range(new_pedestrians_right):
            self.add_pedestrians(
                system_state,
                crosswalk_width,
                pedestrian_waiting_length,
                -1,
                -1,
                GOING_RIGHT_PEDESTRIAN,
            )

        for _ in range(new_pedestrians_left):
            self.add_pedestrians(
                system_state,
                crosswalk_width,
                pedestrian_waiting_length + ROAD_WIDTH,
                full_grid_width,
                1,
                GOING_LEFT_PEDESTRIAN,
            )

        for _ in range(new_cars_up):
            self.add_car(
                system_state,
                CAR_START_POINT_LENGTH - CAR_LENGTH,
                pedestrian_waiting_length + EMPTY_LINE_WIDTH,
                pedestrian_waiting_length
                + EMPTY_LINE_WIDTH
                + ROAD_LINE_WIDTH * LINES_PER_DIRECTION,
                GOING_DOWN_CAR,
            )

        for _ in range(new_cars_down):
            self.add_car(
                system_state,
                CAR_START_POINT_LENGTH + crosswalk_width,
                pedestrian_waiting_length
                + EMPTY_LINE_WIDTH
                + ROAD_LINE_WIDTH * LINES_PER_DIRECTION,
                pedestrian_waiting_length
                + EMPTY_LINE_WIDTH
                + ROAD_LINE_WIDTH * ROAD_TOTAL_LINES,
                GOING_UP_CAR,
            )

    def move_pedestrians(self, system_state, pedestrian_waiting_length):
        i_gr_pedestrians, j_gr_pedestrians = np.where(
            system_state == GOING_RIGHT_PEDESTRIAN
        )
        i_gl_pedestrians, j_gl_pedestrians = np.where(
            system_state == GOING_LEFT_PEDESTRIAN
        )
        gr_pedestrian_speeds = np.random.choice(
            list(range(2, 7)),
            len(i_gr_pedestrians),
            p=[0.273, 0.52, 0.137, 0.048, 0.022],
        )
        gl_pedestrian_speeds = np.random.choice(
            list(range(2, 7)),
            len(i_gl_pedestrians),
            p=[0.273, 0.52, 0.137, 0.048, 0.022],
        )

        gr_pedestrian_distances = []
        for p_i, p_j, preferred_speed in zip(
            i_gr_pedestrians, j_gr_pedestrians, gr_pedestrian_speeds
        ):
            for d in range(preferred_speed):
                if (
                    system_state[p_i, p_j + 1 + d] == GOING_LEFT_PEDESTRIAN
                    or system_state[p_i, p_j + d] == PEDESTRIAN_WAIT
                ):
                    gr_pedestrian_distances.append(d)
                    break
            else:
                gr_pedestrian_distances.append(pedestrian_waiting_length)

        gl_pedestrian_distances = []
        for p_i, p_j, preferred_speed in zip(
            i_gl_pedestrians, j_gl_pedestrians, gl_pedestrian_speeds
        ):
            for d in range(preferred_speed):
                if (
                    system_state[p_i, p_j - 1 - d] == GOING_RIGHT_PEDESTRIAN
                    or system_state[p_i, p_j - d] == PEDESTRIAN_WAIT
                ):
                    gl_pedestrian_distances.append(d)
                    break
            else:
                gl_pedestrian_distances.append(pedestrian_waiting_length)

        # acaba el if lados
        gr_updated_speeds = np.minimum(gr_pedestrian_speeds, gr_pedestrian_distances)
        gl_updated_speeds = np.minimum(gl_pedestrian_speeds, gl_pedestrian_distances)

        intended_positions = dict()

        for p_i, p_j, speed in zip(
            i_gr_pedestrians, j_gr_pedestrians, gr_updated_speeds
        ):
            if not p_i in intended_positions:
                intended_positions[p_i] = dict()

            if not p_j + speed in intended_positions[p_i]:
                intended_positions[p_i][p_j + speed] = (
                    p_i,
                    p_j,
                    GOING_RIGHT_PEDESTRIAN,
                )
            elif np.random.rand() > 0.5:
                prev_p_i, prev_p_j, prev_dir = intended_positions[p_i][p_j + speed]
                intended_positions[prev_p_i][prev_p_j] = (prev_p_i, prev_p_j, prev_dir)
                intended_positions[p_i][p_j + speed] = (
                    p_i,
                    p_j,
                    GOING_RIGHT_PEDESTRIAN,
                )
            else:
                intended_positions[p_i][p_j] = (p_i, p_j, GOING_RIGHT_PEDESTRIAN)

        for p_i, p_j, speed in zip(
            i_gl_pedestrians, j_gl_pedestrians, gl_updated_speeds
        ):
            if not p_i in intended_positions:
                intended_positions[p_i] = dict()

            if not p_j - speed in intended_positions[p_i]:
                intended_positions[p_i][p_j - speed] = (p_i, p_j, GOING_LEFT_PEDESTRIAN)
            elif np.random.rand() > 0.5:
                prev_p_i, prev_p_j, prev_dir = intended_positions[p_i][p_j - speed]
                intended_positions[prev_p_i][prev_p_j] = (prev_p_i, prev_p_j, prev_dir)
                intended_positions[p_i][p_j - speed] = (p_i, p_j, GOING_LEFT_PEDESTRIAN)
            else:
                intended_positions[p_i][p_j] = (p_i, p_j, GOING_LEFT_PEDESTRIAN)

        for i, j_dict in intended_positions.items():
            for j, (prev_p_i, prev_p_j, prev_dir) in j_dict.items():
                if i != prev_p_i or j != prev_p_j:
                    system_state[prev_p_i, prev_p_j] = (
                        CROSSWALK
                        if (
                            (
                                prev_p_j > pedestrian_waiting_length
                                and prev_dir == GOING_RIGHT_PEDESTRIAN
                            )
                            or (
                                prev_p_j < ROAD_WIDTH + pedestrian_waiting_length
                                and prev_dir == GOING_LEFT_PEDESTRIAN
                            )
                        )
                        else PEDESTRIAN_WAIT
                    )
                    if not (
                        (
                            j > ROAD_WIDTH + pedestrian_waiting_length
                            and GOING_RIGHT_PEDESTRIAN
                        )
                        or (
                            j > ROAD_WIDTH + pedestrian_waiting_length
                            and GOING_LEFT_PEDESTRIAN
                        )
                    ):
                        system_state[i, j] = prev_dir

    def run(self, iterations: int):
        system_state = self.get_initial_system_state(
            self.pedestrian_conflict_parameters.full_grid_length,
            self.pedestrian_conflict_parameters.full_grid_width,
            self.pedestrian_conflict_parameters.crosswalk_width,
            self.pedestrian_conflict_parameters.pedestrian_waiting_length,
        )
        result = []
        for _ in range(iterations):
            result.append(system_state)
            self.add_incoming_cars_and_pedestrians(
                system_state,
                self.pedestrian_conflict_parameters.lambda_p,
                self.pedestrian_conflict_parameters.crosswalk_width,
                self.pedestrian_conflict_parameters.pedestrian_waiting_length,
                self.pedestrian_conflict_parameters.full_grid_width,
            )
            self.move_pedestrians(
                system_state,
                self.pedestrian_conflict_parameters.pedestrian_waiting_length,
            )

        return result
