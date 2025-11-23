from dataclass_wizard import fromdict
from typing import Type
from valaw import objects

class Converter:
    def to_object(self, data: dict, object_class: Type):
        """
        Convert a dictionary to an object

        Parameters
        ----------
        data : dict
            The dictionary to convert
        object_class : type
            The class to convert the dictionary to

        Returns
        -------
        object
            The converted object
        """
        return fromdict(object_class, data)
    
    def to_dict(self, obj: object):
        """
        Recursively convert an object to a dictionary

        Parameters
        ----------
        obj : object
            The object to convert

        Returns
        -------
        dict
            The converted dictionary
        """
        if isinstance(obj, dict):
            return {k: self.to_dict(v) for k, v in obj.items()}
        elif hasattr(obj, "__dataclass_fields__"):  # Check if it's a dataclass
            return {k: self.to_dict(getattr(obj, k)) for k in obj.__dataclass_fields__.keys()}
        elif isinstance(obj, list):
            return [self.to_dict(i) for i in obj]
        elif isinstance(obj, tuple):
            return tuple(self.to_dict(i) for i in obj)
        elif isinstance(obj, set):
            return {self.to_dict(i) for i in obj}
        else:
            return obj