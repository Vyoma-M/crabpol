"""This is the tau-A package initialization file. It imports the main classes 
and functions from the submodules, making them accessible when you import tau-A."""
from .mapmaker import MapMaker
from .gettod import Get_TOD, GetTODConfig
from .utils import get_data_path

__all__ = ["MapMaker", "Get_TOD", "GetTODConfig", "get_data_path"]