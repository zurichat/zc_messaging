from bson.objectid import ObjectId


class ObjId(ObjectId):
    """Provides a custom ObjectId class that can be used in the schema.

    This class serves a custom parser to validate if a string is
    is a valid mongo object id.
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        """validates string as monogo object id

        Args:
            str (str): takes a string and validates if it is a valid mongo object id.

        Raises:
            TypeError: if the input string is not a valid mongo object id.

        Returns:
            [str]: returns an output string.
        """
        if not ObjectId.is_valid(value):
            raise TypeError("str not valid object id")
        return str(value)
