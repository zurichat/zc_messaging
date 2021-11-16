from pydantic import BaseModel


class ResponseModel(BaseModel):
    """
    Creates a response model for the API.
    """

    status: str
    message: str
    data: dict

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

    @staticmethod
    def error(message, data=None):
        """Provides an error response data

        Args:
            message (str): error message
            data (dict, optional): [description]. Defaults to None.

        Returns:
            dict: key-value pair of status, message and data
        """
        return ResponseModel(status="error", message=message, data=data).dict()

    @staticmethod
    def fail(message, data=None):
        """Provides a fail response data

        Args:
            message (str): descriptive failure message
            data (dict, optional): key value pair of data returned. Defaults to None.

        Returns:
            dict: key-value pair of status, message and data
        """
        return ResponseModel(status="failed", message=message, data=data).dict()
