from typing import Any

from pydantic import BaseModel


class ResponseModel(BaseModel):
    """Creates a response model for the API.

    Provides a structure for providing a response to the API.
    Provides a static method for success responses

    Attributes:
        status: The status of the response.
        message: The message of the response.
        data: The data of the response.
    """

    status: str
    message: str
    data: Any

    @staticmethod
    def success(data, message="success"):
        """Provides a success response data

        Args:
            data (dict): data to be returned
            message (str, optional): Descriptive messaged. Defaults to "success".

        Returns:
            dict: key-value pair of status, message and data
        """
        return ResponseModel(status="success", message=message, data=data).dict()

class ErrorResponseModel(BaseModel):
    """Creates an error response model for the API.

    Provides a structure for providing an error response to the API.
    Provides a static method for error responses

    Attributes:
        status: The status of the response.
        detail: The message of the response.
    """

    status_code: int
    detail: str

    @staticmethod
    def error(status_code: str, message: str):
        """Provides a success response data

        Args:
            data (dict): data to be returned
            message (str, optional): Descriptive messaged. Defaults to "success".

        Returns:
            dict: key-value pair of status, message and data
        """
        return ErrorResponseModel(status_code=status_code, message=message).dict()
