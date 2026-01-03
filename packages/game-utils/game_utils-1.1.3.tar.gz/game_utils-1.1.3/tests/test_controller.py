from pygame import Vector2

from game_utils.controller import *

VALUES = [0.1, 2.2, 4.7]
DIRECTIONS = [
    Vector2(0.1, 2.2),
    Vector2(2.2, 4.7),
    Vector2(0.1, 4.7),
]


class MockActions(Enum):
    ACTION_A = 0
    ACTION_B = 1
    ACTION_C = 2
    ACTION_Z = -1


class MockController(Controller):
    def __init__(self, *args: VectorAction, **kwargs: VectorAction):
        super().__init__(0, *args, **kwargs)
        self.action_: MockActions | None = None

    def direction(self) -> Vector2:
        if not self.action_:
            self.action_ = MockActions.ACTION_Z

        return DIRECTIONS[self.action_.value]

    def action(self, key: str) -> float:
        assert self.actions.get(key)
        return VALUES[self.actions[key]["input_id"]]


def test_controller():
    c = MockController(
        {
            "input_id": MockActions.ACTION_A.value,
            "action_type": "hat",
            "action_name": MockActions.ACTION_A.name,
        },
        {
            "input_id": MockActions.ACTION_B.value,
            "action_type": "axis",
            "action_name": MockActions.ACTION_B.name,
        },
        {
            "input_id": MockActions.ACTION_C.value,
            "action_type": "button",
            "action_name": MockActions.ACTION_C.name,
        },
    )

    assert c.action(MockActions.ACTION_A.name) == VALUES[MockActions.ACTION_A.value]
    assert c.action(MockActions.ACTION_C.name) == VALUES[MockActions.ACTION_Z.value]

    assert c.direction() == DIRECTIONS[-1]
    c.action_ = MockActions.ACTION_B
    assert c.direction() == DIRECTIONS[1]
