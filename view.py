import matplotlib.pyplot as plt
import numpy as np
from IPython.display import HTML
from matplotlib import animation
from matplotlib.colors import ListedColormap

from automata import CAR, GOING_LEFT_PEDESTRIAN, GOING_UP_CAR, PEDESTRIAN


def build_create_video(
    system_state_list, full_grid_width, full_grid_length, simulation_interval=100
):
    def create_video(n):
        fig, ax = plt.subplots(figsize=(20, 15))

        cmap = ListedColormap(["k", "b", "y", "g", "r", "m"], N=10)
        # agrid = ax.imshow(a, cmap=plt.cm.BuPu_r);
        # include state with all possible cells
        agrid = ax.imshow(system_state_list[0], interpolation="nearest", cmap=cmap)
        plt.close(fig)

        # Major ticks
        ax.set_xticks(np.arange(0, full_grid_width, 1))
        ax.set_yticks(np.arange(0, full_grid_length, 1))

        # Labels for major ticks
        ax.set_xticklabels(np.arange(1, full_grid_width + 1, 1))
        ax.set_yticklabels(np.arange(1, full_grid_length + 1, 1))

        # Minor ticks
        ax.set_xticks(np.arange(-0.5, full_grid_width, 1), minor=True)
        ax.set_yticks(np.arange(-0.5, full_grid_length, 1), minor=True)

        ax.grid(which="minor", color="w", linestyle="-", linewidth=2)
        plt.tight_layout()

        # initialization function: plot the background of each frame
        def init():
            agrid.set_data(system_state_list[0])
            return (agrid,)

        # animation function. This is called sequentially
        def animate(i):
            new_system_state = system_state_list[i]
            new_system_state[new_system_state == GOING_UP_CAR] = CAR
            new_system_state[new_system_state == GOING_LEFT_PEDESTRIAN] = PEDESTRIAN
            agrid.set_data(new_system_state)
            return (agrid,)

        # call the animator. blit=True means only re-draw the parts that have changed.
        anim = animation.FuncAnimation(
            fig,
            animate,
            init_func=init,
            frames=len(system_state_list),
            interval=simulation_interval,
            blit=True,
        )
        return HTML(anim.to_html5_video())

    return create_video
