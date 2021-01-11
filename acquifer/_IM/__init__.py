"""
This is a private package which contains functions used by the IM class, ie common to all version of the IM
This package should not be used as such but through the IM class exclusively

from import below to be able to do (as in acquifer package _init_)
from acquifer import _IM
_IM.tcpip.getStatus(IM_TCPIP)

not sure if this is because it is a private package with leading _
"""
from . import tcpip
