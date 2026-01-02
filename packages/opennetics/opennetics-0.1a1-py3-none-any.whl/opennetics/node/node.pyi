
# node/node.pyi

#- Imports -----------------------------------------------------------------------------------------

from typing import Any, Callable, Final

from ..typing import numeric_t
from ..utils.defaults import READ_INTERVAL_DEFAULT, WRITE_INTERVAL_DEFAULT


#- Local Defines -----------------------------------------------------------------------------------

INPUT_ONLY: Final[int] = ... # only enables input operations and reserves only input buffers
OUTPUT_ONLY: Final[int] = ... # only enables output operations and reserves only output buffers
INPUT_OUTPUT: Final[int] = ... # reserve memory for both input-output operations and buffers (default)


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
        """
        Control reading process loop. Set to False to pause reading process.
        """
        ...


    @reading.setter
    def reading(self, status: bool) -> None:
        """
        Control reading process loop. Set to False to pause reading process.
        """
        ...


    @property
    def read_interval(self) -> numeric_t:
        f"""
        Short pause between serial read iterations to reduce CPU usage and allow other tasks to run
        Default is {READ_INTERVAL_DEFAULT} seconds.
        """
        ...


    @read_interval.setter
    def read_interval(self, interval: numeric_t) -> None:
        f"""
        Short pause between serial read iterations to reduce CPU usage. Default is
        {READ_INTERVAL_DEFAULT} seconds.
        """
        ...


    @property
    def write_interval(self) -> numeric_t:
        f"""
        Short pause between two subsequent write calls to reduce CPU usage. Default is
        {WRITE_INTERVAL_DEFAULT} seconds.
        """
        ...


    @write_interval.setter
    def write_interval(self, interval: numeric_t) -> None:
        f"""
        Short pause between two subsequent write calls to reduce CPU usage. Default is
        {WRITE_INTERVAL_DEFAULT} seconds.
        """
        ...


    #- Public Methods ------------------------------------------------------------------------------

    def connect(self, username: str, password: str) -> bool:
        """
        Establish connection to the node using provided credentials.

        :param username: Username for authentication
        :type username: str

        :param password: Password for authentication
        :type password: str

        :return:  True if connection is successful, else False.
        :rtype: bool
        """
        ...


    def write(self, command: Any, rank: int = 0) -> None:
        """
        Queue a command to be written back to the node during the next write cycle.

        :param command: Command data to be sent to the node
        :type command: Any

        :param rank: Priority rank of the command in the write queue. Higher rank commands are sent first.
        :type rank: int
        """
        ...


    def new_gesture(
        self,
        gesturefile: str,
        match: dict[str,int],
        action: Callable[[], None]
    ) -> bool:
        """
        Create a new gesture from a gesture file and associate it with an action.

        :param gesturefile: Path to the `.ges` gesture file
        :type gesturefile: str

        :param match: Dictionary matching input array index with sensor labels
        :type match: dict[str,int]

        :param action: Callable function to be executed when the gesture is recognised
        :type action: Procedure with no parameters and no return value, Callable[[], None]

        :return: True if gesture is successfully created, else False.
        :rtype: bool
        """
        ...

