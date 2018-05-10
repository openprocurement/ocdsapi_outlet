from abc import ABC, abstractmethod


class BaseStaticStorage(ABC):

    @abstractmethod
    def list_objects():
        """ Returns list of present objects """

    @abstractmethod
    def upload_object():
        """ Uploads object to the store """

    def download_object():
        """ Downloads object from the store """