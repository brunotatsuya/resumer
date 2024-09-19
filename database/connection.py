import inject
from pymongo import MongoClient
from pymongo.synchronous.database import Database

from config.config import Config


class MongoConnection:
    """
    A connection to the MongoDB database.
    """

    @inject.autoparams()
    def __init__(self, config: Config):
        self.config = config
        self.client = self.__create_client()

    def __create_client(self) -> Database:
        """
        Creates a MongoClient instance.

        Returns:
            Database: A MongoClient instance.
        """
        return MongoClient(self.config.MONGODB_URI).jobfinder

    def get_collection(self, collection_name: str):
        """
        Gets a collection from the database.

        Args:
            collection_name (str): The name of the collection to get.

        Returns:
            Collection: The collection instance.
        """
        return self.client[collection_name]
