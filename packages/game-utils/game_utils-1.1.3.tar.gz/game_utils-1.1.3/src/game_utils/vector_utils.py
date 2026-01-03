from collections.abc import Callable

from numpy.random import choice, rand
from pygame import Vector2


def get_random_vector(scalar_mag: float = 1.0, non_negative: bool = False) -> Vector2:
    def rand_sign() -> int:
        return choice([-1, 1]) if not non_negative else 1

    return Vector2(
        x=rand() * rand_sign() * scalar_mag,
        y=rand() * rand_sign() * scalar_mag,
    )


def apply_vector_actions(
    vector: Vector2, *actions: Callable[[Vector2], Vector2]
) -> Vector2:
    for action in actions:
        vector = action(vector)

    return vector
