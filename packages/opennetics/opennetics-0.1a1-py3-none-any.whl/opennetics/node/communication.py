
# device/communication.py

#- Imports -----------------------------------------------------------------------------------------

from typing import Any

from ..typing import numeric_t
from ..utils.debug import alert, AlertLevel


#- Public Calls ------------------------------------------------------------------------------------

# placeholder: implement device connection
def connect(username: str, password:str) -> bool:
    alert("called")
    try:
        # try to connect to the device
        alert(f"Connected to {username}", backtrack=3)

    except Exception as e: # if connect isn't successful
        alert(f"unable to connect{e}", level=AlertLevel.ERROR, backtrack=3)
        # backtrack=3 because:
        #   backtrack=0 is the code in alert() function
        #   backtrack=1 is this call
        #   backtrack=2 is in Devices.connect(), where this function was called
        #   backtrack=3 is where Devices.connect() method was called
        return False

    return True


# placeholder: implement to get data from the source and return as numeric str
def get_data() -> list[numeric_t]:
    alert("called")
    Result: list[numeric_t] = []
    return Result


# placeholder: implement to send data to the device. Add more args to specify device n stuff
def send_data(data: Any) -> None:
    alert("called")
    # if fail
    try:
        pass

    except Exception as e:
        alert(f"failed to send data. {e}", backtrack=3, level=AlertLevel.ERROR)

