"""
GestureFile class interface for handling .ges file data. It encapsulates methods for reading,
writing, and analysing gesture data using Gaussian Mixture Models.
"""

#- Imports -----------------------------------------------------------------------------------------

from typing import Optional
from sklearn.mixture import GaussianMixture
from ..typing import GestureMatch, data_dict_t, numeric_t


#- GestureFile Class -------------------------------------------------------------------------------

class GestureFile:
    def __init__(self, filename: str) -> None:
        """
        GestureFile class constructor.

        :param filename: filename to process gesture data from and to
        :type filename: str
        """
        ...

    #- Getter/Setter -------------------------------------------------------------------------------

    @property
    def gesture_data(self) -> data_dict_t:
        """
        :return: dictionary containing raw data from the .ges file. This is the data sliced and
            processed for different operations.

        :rtype: data_dict_t, where keys are gesture labels and values are of class SensorData, which
            encapsulate Gaussian Mixture Models and their parameters.
        """
        ...


    @property
    def batchsize(self) -> int:
        """
        :return: Stored batch size for gesture readings. This indicates how many readings are
            grouped together for processing. More specifically, the buffer size for input data to
            search if it's the gesture.

        :rtype: int
        """
        ...


    def parameters(self, label: str) -> dict[str, numeric_t]:
        """
        Each data source (/sensor) has its own model parameters saved in the record. This method
        retrieves those parameters for a given sensor label.

        :param label: sensor label to retrieve parameters for
        :type label: str

        :return: dictionary of model parameters including 'n_components', 'random_state', and
            'threshold'
        :rtype: dict[str, numeric_t]
        """
        ...


    def keys(self) -> list[str]:
        """
        :return: Get names of all sensors in the record.
        :rtype: list[str]
        """
        ...


    def set_parameters(
            self, label: str,
            n_components: Optional[int] = ...,
            random_state: Optional[int] = ...,
            threshold: Optional[float] = ...
        ) -> None:
        """
        Update only a specific or all model parameters for a given sensor label.

        :param label: sensor label to set parameters for
        :type label: str

        :param n_components: number of Gaussian mixture components (clusters) used to model the data
        :type n_components: Optional[int]

        :param random_state: number of Gaussian mixture components (clusters) used to model the data
        :type random_state: Optional[int]

        :param threshold: number of Gaussian mixture components (clusters) used to model the data
        :type threshold: Optional[float]
        """
        ...


    #- Public Methods ------------------------------------------------------------------------------

    def create(self) -> bool:
        """
        Create a new gesture file with the set filename.
        """
        ...


    def append_reading(self, label: str, model: list[GaussianMixture]) -> bool:
        """
        Append new gesture models to the specific sensor label in the gesture file record.

        :param label: sensor label to append the model for
        :type label: str

        :param model: list of GaussianMixture models representing the gesture
        :type model: list[GaussianMixture]

        :return: True if append was successful, False otherwise
        :rtype: bool
        """
        ...


    def write(self, override: bool = ...) -> bool:
        """
        All operations made to the gesture record are stored only in memory. This method
        writes those changes back to the gesture file on disk.

        :param override: If True, overwrite existing file. If False and file exists then append to
        it.
        :type override: bool

        :return: True if write was successful, False otherwise
        :rtype: bool
        """
        ...


    def read(self) -> bool:
        """
        Read data stored in the specified gesture file into memory.

        :return: True if read was successful, False otherwise
        :rtype: bool
        """
        ...


    def is_gesture(self,
        timestamps: list[float], readings: dict[str, list[float]]
    ) -> tuple[bool, dict[str, GestureMatch]]:
        """
        Check if the readings and the corresponding timestamps triggers the stored gesture. reading
        array is checked as a whole for gesture.

        :param timestamps: array of timestamps corresponding to the readings
        :type timestamps: list[float]

        :param readings: dictionary where keys are sensor labels and values are lists of sensor
            readings
        :type readings: dict[str, list[float]]

        :return: tuple where first element is True if gesture is detected, False otherwise; secon
            element is a dictionary specifying which sensors were a match. Gesture is True only if
            all sensors match.
        :rtype: tuple[bool, dict[str, GestureMatch]]
        """
        ...


    def has_gesture(self,
        timestamps: list[float], readings: dict[str, list[float]]
    ) -> tuple[bool, dict[str, GestureMatch]]:
        """
        Check if the readings and the corresponding timestamps triggers the stored gesture. Gesture
        is checked in a sliding window manner over the readings. i.e. if any part of the readings
        matches the gesture, it returns True.

        :param timestamps: array of timestamps corresponding to the readings
        :type timestamps: list[float]

        :param readings: dictionary where keys are sensor labels and values are lists of sensor
            readings
        :type readings: dict[str, list[float]]

        :return: tuple where first element is True if gesture is detected, False otherwise; second
            element is a dictionary specifying which sensors were a match. Gesture is True only if
            all sensors match.
        :rtype: tuple[bool, dict[str, GestureMatch]]
        """
        ...

