from copy import deepcopy

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject

import sys
import ctypes

class GstLVAMessage(ctypes.Structure):
    _fields_ = [ 
                ('sequence_number', ctypes.c_uint64),                
                ('timestamp', ctypes.c_uint64)
                ]

# Pointer to LVAGstMessage structure
GstLVAMessagePtr = ctypes.POINTER(GstLVAMessage)

# Load C-lib
clib = ctypes.CDLL("build/libgst_lva_message.so")

# Map ctypes arguments to C-style arguments
clib.gst_lva_buffer_add_message.argtypes = [ctypes.c_void_p, GstLVAMessagePtr]
clib.gst_lva_buffer_add_message.restype = ctypes.c_void_p

clib.gst_lva_buffer_get_message.argtypes = [ctypes.c_void_p]
clib.gst_lva_buffer_get_message.restype = GstLVAMessagePtr

clib.gst_lva_buffer_remove_message.argtypes = [ctypes.c_void_p]
clib.gst_lva_buffer_remove_message.restype = ctypes.c_bool

def add_message(buffer, sequence_number, timestamp):
    msg = GstLVAMessage()
    msg.sequence_number = sequence_number    
    msg.timestamp = timestamp
    clib.gst_lva_buffer_add_message(hash(buffer), msg)

def get_message(buffer):
    res = clib.gst_lva_buffer_get_message(hash(buffer))
    return res.contents

def remove_message(buffer):
    return clib.gst_lva_buffer_remove_message(hash(buffer))