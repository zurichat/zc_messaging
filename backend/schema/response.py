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
