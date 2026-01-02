
# node/node.py

#- Imports -----------------------------------------------------------------------------------------

import threading
from dataclasses import dataclass
from time import sleep
from typing import Any, Callable

from .input_data import InputData
from .communication import get_data, connect, send_data
from ..typing import numeric_t
from ..file import GestureFile
from ..utils.debug import alert, AlertLevel


#- Local Defines -----------------------------------------------------------------------------------

@dataclass
class GestureRecord:
    gesture: GestureFile
    call: Callable[[], None]
    match: dict[str, int]
    input_index: int
    running: bool = False

INPUT_ONLY = 0
OUTPUT_ONLY = 1
INPUT_OUTPUT = 2


#- Node Class --------------------------------------------------------------------------------------

class Node:

    def __init__(self, profile: int = INPUT_OUTPUT):
        self._profile: int = profile
        self._input_data: InputData = InputData()       # organised record of read data
        self._gesture_record: list[GestureRecord] = []  # record of all gesture calls

        self._write_buffer: dict[int, Any] = {}         # commands to write back to the node

        self._reading_loop: bool = False                # control reading process loop
        self._read_interval: numeric_t = 1              # pause duration in reading process loop
        self._write_interval: numeric_t = 1             # interval between two subsequent writes


    #- Getter/Setter -------------------------------------------------------------------------------

    @property
    def reading(self) -> bool: return self._reading_loop


    @reading.setter
    def reading(self, status: bool) -> None: self._reading_loop = status


    @property
    def read_interval(self) -> numeric_t: return self._read_interval


    @read_interval.setter
    def read_interval(self, interval: numeric_t) -> None:
        # accept only positive values
        # else keep the value unchanged
        if interval >= 0:
            self._read_interval = interval
        else:
            alert(
                f"{interval} not valid read_interval; must be a positive float|int." +
                f" Using previous set, {self._read_interval}",
                backtrack=2, level=AlertLevel.WARNING
            )


    @property
    def write_interval(self) -> numeric_t: return self._write_interval


    @write_interval.setter
    def write_interval(self, interval: numeric_t) -> None:
        # accept only positive values
        # else keep the value unchanged
        if interval >= 0:
            self._read_interval = interval
        else:
            alert(
                f"{interval} not valid write_interval; must be a positive float|int." +
                f" Using previous set, {self._read_interval}",
                backtrack=2, level=AlertLevel.WARNING
            )


    #- Private Methods -----------------------------------------------------------------------------

    #
    def _read_process(self) -> None:
        while True:
            sleep(self._read_interval) # not clog CPU
            if not self._reading_loop: continue # if requested to pause

            read_data = get_data()
            self._input_data.add_data(read_data)

            for record in self._gesture_record:
                if (self._input_data.total - record.input_index) % record.gesture.batchsize == 0:
                    result = self._input_data.get_data_window(
                        batchsize = record.gesture.batchsize,
                        sources = record.match,
                        start_index = record.input_index
                    )

                    if result is None: continue

                    timestamps, data_window = result

                    if record.gesture.has_gesture(timestamps, data_window) and not record.running:
                        record.running = True
                        # start new process
                        record.call()
                        record.running = False

                    record.input_index += record.gesture.batchsize


    #
    def _write_process(self) -> None:
        while True:
            rank_order = reversed(self._write_buffer.keys())

            for rank in rank_order:
                if not self._write_buffer[rank]: continue # skip if this rank buffer is empty

                content = self._write_buffer[rank].pop(0)
                send_data(content)
                break

            sleep(self._write_interval)


    #
    def _cleanup_process(self) -> None:
        while True:
            sleep(120)

            lowest_index = min([x.input_index for x in self._gesture_record])
            for x in self._gesture_record: x.input_index -= lowest_index
            self._input_data.cleanup(lowest_index)


    #
    def _read(self) -> None:
        # start the read loop with the first entry in _gesture_record
        # the loop must be started only once, and it should when [_gesture_record] is not empty
        if len(self._gesture_record) != 1: return

        read_thread = threading.Thread(target=self._read_process)
        read_thread.daemon = True # exit when the main program does
        read_thread.start()

        cleanup_thread = threading.Thread(target=self._cleanup_process)
        cleanup_thread.daemon = True # exit when the main program does
        cleanup_thread.start()


    #- Public Methods ------------------------------------------------------------------------------

    #
    def connect(self, username: str, password: str) -> bool:
        ok = connect(username, password)
        self._reading_loop = ok

        alert("Connected ", backtrack=2)

        if ok and (self._profile != OUTPUT_ONLY):
            # start write thread
            write_thread = threading.Thread(target=self._write_process)
            write_thread.daemon = True # exit when the main program does
            write_thread.start()

        return ok


    # Send command to the device. return success status
    def write(self, command: Any, rank: int = 0) -> None:
        if self._profile == INPUT_ONLY:
            alert(".write not supported for InputOnly devices", backtrack=2)
            return

        if rank < 0:
            alert("rank must be a positive integer", level=AlertLevel.ERROR, backtrack=2)
            return

        if rank not in self._write_buffer.keys():
            self._write_buffer[rank] = []

        self._write_buffer[rank].append(command)


    # Load GestureFile in record
    def add_gesture(
        self,
        gesturefile: str,
        match: dict[str,int],
        action: Callable[[], None]
    ) -> bool:
        if self._profile == OUTPUT_ONLY:
            alert("GestureFiles not supported for OutputOnly devices", backtrack=2)
            return False

        try:
            self._gesture_record.append(GestureRecord(
                gesture = GestureFile(gesturefile),
                call  = action,
                match = match,
                input_index = self._input_data.total
            ))

            self._read()
            return True

        except Exception as e:
            alert(f"Unable to process GestureFile. {e}", backtrack=2, level=AlertLevel.ERROR)
            return False

