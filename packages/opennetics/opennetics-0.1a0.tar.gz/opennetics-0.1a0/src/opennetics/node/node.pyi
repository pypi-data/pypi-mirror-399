
# node/node.pyi

#- Imports -----------------------------------------------------------------------------------------

from typing import Any, Callable

from ..typing import numeric_t


#- Local Defines -----------------------------------------------------------------------------------

INPUT_ONLY: int = ...
OUTPUT_ONLY: int = ...
INPUT_OUTPUT: int = ...

#- Node Class --------------------------------------------------------------------------------------

class Node:

    def __init__(self, profile: int = 0) -> None:
        """
        A device profile can be set as:
        - 0: InputOutput (default) - reserve memory for both input-output operations and buffers.
        - 1: InputOnly - only enables input operations and reserves only input buffers.
        - 2: OutputOnly - only enables output operations and reserves only output buffers.
        """
        ...

    #- Getter/Setter -------------------------------------------------------------------------------

    @property
    def reading(self) -> bool:
        ...

    @reading.setter
    def reading(self, status: bool) -> None:
        ...

    @property
    def read_interval(self) -> numeric_t:
        ...

    @read_interval.setter
    def read_interval(self, interval: numeric_t) -> None:
        ...

    @property
    def write_interval(self) -> numeric_t:
        ...

    @write_interval.setter
    def write_interval(self, interval: numeric_t) -> None:
        ...


    #- Public Methods ------------------------------------------------------------------------------

    #
    def connect(self, username: str, password: str) -> bool:
        ...


    # Send command to the device. return success status
    def write(self, command: Any, rank: int = 0) -> None:
        ...


    # Load GestureFile in record
    def new_gesture(
        self,
        gesturefile: str,
        match: dict[str,int],
        action: Callable[[], None]
    ) -> bool:
        ...

