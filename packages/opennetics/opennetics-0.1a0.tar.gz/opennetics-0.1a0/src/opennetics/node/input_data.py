
# node/input_data.py

#- Imports -----------------------------------------------------------------------------------------

import time
from dataclasses import dataclass
from typing import Optional

from ..typing import numeric_t
from ..utils.debug import alert


#- Local Defines -----------------------------------------------------------------------------------

@dataclass
class Record:
    timestamp: float
    reading: list[numeric_t]


#- InputData Class ---------------------------------------------------------------------------------

class InputData:

    def __init__(self):
        self._data_record: list[Record] = []   # [( time: data_read )]
        self._start_time = time.time()


    #- Getter/Setter -------------------------------------------------------------------------------

    @property
    def total(self) -> int: return len(self._data_record)


    #- Public Methods ------------------------------------------------------------------------------

    #
    def add_data(self, data:list[numeric_t]) -> None:
        alert("called")
        self._data_record.append(Record(
            timestamp = time.time() - self._start_time,
            reading = data
        ))


    #
    def get_data_window(
        self,
        batchsize: int,
        sources:dict[str, int],
        start_index:int
    ) -> Optional[tuple[list[float], dict[str, list[numeric_t]]]]:
        alert("called")
        if (batchsize * 2) > self.total - start_index: return None

        end_index = start_index + (2 * batchsize)

        timeframe: list[float] = []
        requested_data: dict[str, list[numeric_t]] = {index: [] for index in sources.keys()}

        for record in self._data_record[start_index:end_index]:
            timeframe.append(record.timestamp)

            for key in sources.keys():  # set to remove duplicates
                requested_data[key].append(record.reading[sources[key]])

        return (timeframe, requested_data)


    #
    def cleanup(self, index: int) -> None:
        del self._data_record[0:index]

