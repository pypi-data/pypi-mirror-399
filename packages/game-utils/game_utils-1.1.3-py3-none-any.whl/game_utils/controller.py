from abc import abstractmethod
from collections.abc import Callable
from enum import Enum
from typing import Any, Literal, TypedDict

import pygame.joystick
import pygame.key
from pygame import K_DOWN, K_ESCAPE, K_LEFT, K_RIGHT, K_UP, Vector2


class VectorAction(TypedDict):
    """Mapping of controller ID to action

    Args:
        input_id (int): The unique id of the button or axis
        action_type (str): Axis or button type. Only [axis, button] allowed
        action_name (str): The name of the action. Should be unique
    """

    input_id: int
    action_type: Literal["axis", "button", "hat"]
    action_name: str


class Controller:
    """Abstract class for controller
    Must implement 'direction' method
    Optional rotation and action methods
    """

    def __init__(
        self,
        speed: float,
        *args: VectorAction,
        **kwargs: VectorAction,
    ):
        """Creates new instance of Controller object.

        Args:
            speed (float, optional): Scalar multiple applied to controller output. Defaults to 1.
            *args (VectorAction): A list of action metadata for the controller
            **kwargs (VectorAction): A mapping of metadata for the controller
        """
        self.speed: float = speed

        self.actions: dict[str, VectorAction] = {v["action_name"]: v for v in args}
        self.actions.update(kwargs)

    @abstractmethod
    def direction(self) -> Vector2:
        """Applies direction from controller input

        Raises:
            NotImplementedError: Abstract method

        Returns:
            Vector2: The new direction vector
        """
        raise NotImplementedError()

    def rotation(self, axis: Literal["x", "y", "z"]) -> Vector2:
        """Applies rotation from controller input

        Args:
            axis (Literal[&quot;x&quot;, &quot;y&quot;, &quot;z&quot;]): The axis of rotation

        Raises:
            NotImplementedError: Abstract method

        Returns:
            Vector2: the new rotation vector
        """
        raise NotImplementedError()

    def action(self, key: str) -> float:
        """Applies Vector Action for the given key, if it exists

        Args:
            key (str): The unique key(name) of the action

        Raises:
            NotImplementedError: Abstract method

        Returns:
            float: The value from the controller output for this action
        """
        raise NotImplementedError()


class JoystickController(Controller):
    """Joystick base class.  Implements Controller class action(key) method.
    Abstract class that requires implementation for direction() method.
    """

    def __init__(
        self,
        input: pygame.joystick.JoystickType,
        speed: float,
        *args: VectorAction,
        **kwargs: VectorAction,
    ):
        """_summary_

        Args:
            input (pygame.JoystickType): The pygame Joystick reference
            speed (float, optional): Scalar multiple applied to controller output. Defaults to 1.
            *args (VectorAction): A list of action metadata for the controller
            **kwargs (VectorAction): A mapping of metadata for the controller
        """
        super(JoystickController, self).__init__(speed, *args, **kwargs)
        self.input = input

    def action(self, key: str) -> float:
        """Vector actions for Keyboard input

        Args:
            key (str): The unique key of the action. Can be a Pygame local

        Returns:
            float: The result of the Vector Action
        """
        vector_action = self.actions.get(key)

        if vector_action is not None:
            id = vector_action["input_id"]
            action_type = vector_action["action_type"]
            if action_type == "axis":
                axis = self.input.get_axis(id)
                return axis
            else:
                return 1.0 if self.input.get_button(id) else 0.0

        else:
            return 0.0

    @staticmethod
    def get_controllers(
        speed: float,
        *args: VectorAction,
        **kwargs: VectorAction,
    ):
        return [
            JoystickController(pygame.joystick.Joystick(i), speed, *args, **kwargs)
            for i in range(pygame.joystick.get_count())
        ]


class KeyboardController(Controller):
    """Keyboard base class.  Implements Controller class action(key) method.
    Abstract class that requires implementation for direction() method.
    Adds get_keys() method that gets all keyboard keys pressed
    """

    def action(self, key: str) -> float:
        vector_action = self.actions.get(key)

        if vector_action is not None:
            id = vector_action["input_id"]
            if pygame.key.get_pressed()[id]:
                return 1.0

        return 0.0


class DefaultKeyboardController(KeyboardController):
    class Commands(Enum):
        """Constant keyboard commands"""

        X_AXIS_POS = "x_axis_pos"
        X_AXIS_NEG = "x_axis_neg"
        Y_AXIS_POS = "y_axis_pos"
        Y_AXIS_NEG = "y_axis_neg"
        QUIT = "quit"

    """A simple Keyboard Controller implementation"""

    def direction(self) -> Vector2:
        """Applies direction from keyboard input

        Returns:
            Vector2: The new directional vector
        """
        vx = (
            self.action(self.Commands.X_AXIS_POS.value)
            - self.action(self.Commands.X_AXIS_NEG.value)
        ) * self.speed

        vy = (
            self.action(self.Commands.Y_AXIS_POS.value)
            - self.action(self.Commands.Y_AXIS_NEG.value)
        ) * self.speed

        return Vector2(vx, vy)


DEFAULT_KEYBOARD_ACTIONS: list[VectorAction] = [
    {
        "input_id": K_RIGHT,
        "action_name": DefaultKeyboardController.Commands.X_AXIS_POS.value,
        "action_type": "button",
    },
    {
        "input_id": K_LEFT,
        "action_name": DefaultKeyboardController.Commands.X_AXIS_NEG.value,
        "action_type": "button",
    },
    {
        "input_id": K_DOWN,
        "action_name": DefaultKeyboardController.Commands.Y_AXIS_POS.value,
        "action_type": "button",
    },
    {
        "input_id": K_UP,
        "action_name": DefaultKeyboardController.Commands.Y_AXIS_NEG.value,
        "action_type": "button",
    },
    {
        "input_id": K_ESCAPE,
        "action_name": DefaultKeyboardController.Commands.QUIT.value,
        "action_type": "button",
    },
]
