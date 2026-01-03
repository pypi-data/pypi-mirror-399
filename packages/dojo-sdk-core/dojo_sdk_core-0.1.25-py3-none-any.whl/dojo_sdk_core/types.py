from enum import Enum
from typing import Annotated, List, Literal, Union

from pydantic import BaseModel, Discriminator

"""Type definitions for Dojo."""


class ActionType(str, Enum):
    KEY = "key"
    CLICK = "click"
    RIGHT_CLICK = "right_click"
    SCROLL = "scroll"
    TYPE = "type"
    DOUBLE_CLICK = "double_click"
    TRIPLE_CLICK = "triple_click"
    DRAG = "drag"
    MOVE_TO = "move_to"
    PRESS = "press"
    HOTKEY = "hotkey"
    MIDDLE_CLICK = "middle_click"
    DONE = "done"
    WAIT = "wait"


class KeyAction(BaseModel):
    type: Literal[ActionType.KEY] = ActionType.KEY
    key: str


class ClickAction(BaseModel):
    type: Literal[ActionType.CLICK] = ActionType.CLICK
    x: int
    y: int


class RightClickAction(BaseModel):
    type: Literal[ActionType.RIGHT_CLICK] = ActionType.RIGHT_CLICK
    x: int
    y: int


class ScrollAction(BaseModel):
    type: Literal[ActionType.SCROLL] = ActionType.SCROLL
    direction: str = "up"
    amount: int = 100


class TypeAction(BaseModel):
    type: Literal[ActionType.TYPE] = ActionType.TYPE
    text: str


class DoubleClickAction(BaseModel):
    type: Literal[ActionType.DOUBLE_CLICK] = ActionType.DOUBLE_CLICK
    x: int
    y: int


class TripleClickAction(BaseModel):
    type: Literal[ActionType.TRIPLE_CLICK] = ActionType.TRIPLE_CLICK
    x: int
    y: int


class DragAction(BaseModel):
    type: Literal[ActionType.DRAG] = ActionType.DRAG
    from_x: int
    from_y: int
    to_x: int
    to_y: int
    duration: float = 1.0


class MoveToAction(BaseModel):
    type: Literal[ActionType.MOVE_TO] = ActionType.MOVE_TO
    x: int
    y: int
    duration: float = 0.0


class PressAction(BaseModel):
    type: Literal[ActionType.PRESS] = ActionType.PRESS
    key: str


class HotkeyAction(BaseModel):
    type: Literal[ActionType.HOTKEY] = ActionType.HOTKEY
    keys: List[str]


class MiddleClickAction(BaseModel):
    type: Literal[ActionType.MIDDLE_CLICK] = ActionType.MIDDLE_CLICK
    x: int
    y: int


class DoneAction(BaseModel):
    type: Literal[ActionType.DONE] = ActionType.DONE


class WaitAction(BaseModel):
    type: Literal[ActionType.WAIT] = ActionType.WAIT
    seconds: int = 1


Action = Annotated[
    Union[
        KeyAction,
        ClickAction,
        RightClickAction,
        ScrollAction,
        TypeAction,
        DoubleClickAction,
        TripleClickAction,
        DragAction,
        MoveToAction,
        PressAction,
        HotkeyAction,
        MiddleClickAction,
        DoneAction,
        WaitAction,
    ],
    Discriminator("type"),
]


class Score(BaseModel):
    task_name: str
    score: float
    status: str
    success: bool
    steps_taken: int
    reward: float
    completion_reason: str
