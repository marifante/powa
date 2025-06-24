from collections import namedtuple
from enum import Enum


electrical_data = namedtuple('electrical_data', ['time', 'voltage', 'current', 'power'])


class PowerDomain(Enum):
    """ Enum for available power domains. """
    VBAT = "VBAT"
    USB = "USB"
