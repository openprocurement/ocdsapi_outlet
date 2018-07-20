""" manifest.py - gather informaion about current dump process """
import json


class Manifest(object):
    """
    Simple class to hold gathered dump informaion
    Generates manifest.json to send by email and static serving
    """
    def __init__(self):
        self.version = '1'
        self.archive = ''
        self.releases = []
        self.example = ''

    def as_dict(self):
        """ Return metainfo as python dist """
        return {
            "version": self.version,
            "archive": self.archive,
            "releases": self.releases,
            "example": self.example
        }

    def as_str(self):
        """ Return metainfo as raw json string """
        return json.dumps(self.as_dict())
