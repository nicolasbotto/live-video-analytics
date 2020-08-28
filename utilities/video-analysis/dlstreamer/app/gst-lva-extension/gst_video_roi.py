
import ctypes
import gi
gi.require_version('GstVideo', '1.0')
gi.require_version('GLib', '2.0')
gi.require_version('Gst', '1.0')
from gi.repository import GstVideo, GLib, GObject, Gst

# libgstreamer
libgst = ctypes.CDLL("libgstreamer-1.0.so.0")

libgst.gst_buffer_iterate_meta_filtered.argtypes = [
    ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p), ctypes.c_void_p]
libgst.gst_buffer_iterate_meta_filtered.restype = ctypes.c_void_p

libgst.gst_structure_get_name.argtypes = [ctypes.c_void_p]
libgst.gst_structure_get_name.restype = ctypes.c_char_p
libgst.gst_structure_get_field_type.argtypes = [
    ctypes.c_void_p, ctypes.c_char_p]
libgst.gst_structure_get_field_type.restypes = ctypes.c_size_t
libgst.gst_structure_get_string.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
libgst.gst_structure_get_string.restype = ctypes.c_char_p
libgst.gst_structure_get_value.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
libgst.gst_structure_get_value.restype = ctypes.c_void_p
libgst.gst_structure_get_int.argtypes = [
    ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int)]
libgst.gst_structure_get_int.restype = ctypes.c_int
libgst.gst_structure_get_double.argtypes = [
    ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_double)]
libgst.gst_structure_get_double.restype = ctypes.c_int


class GList(ctypes.Structure):
    pass

GLIST_POINTER = ctypes.POINTER(GList)

GList._fields_ = [
    ('data', ctypes.c_void_p),
    ('next', GLIST_POINTER),
    ('prev', GLIST_POINTER)
]

# VideoRegionOfInterestMeta
class VideoRegionOfInterestMeta(ctypes.Structure):
    _fields_ = [
        ('_meta_flags', ctypes.c_int),
        ('_info', ctypes.c_void_p),
        ('roi_type', ctypes.c_int),
        ('id', ctypes.c_int),
        ('parent_id', ctypes.c_int),
        ('x', ctypes.c_int),
        ('y', ctypes.c_int),
        ('w', ctypes.c_int),
        ('h', ctypes.c_int),
        ('_params', GLIST_POINTER)
    ]

class RegionOfInterest(object):  

    ## @brief Iterate by VideoRegionOfInterestMeta instances attached to buffer
    # @param buffer buffer with GstVideoRegionOfInterestMeta instances attached
    # @return generator for VideoRegionOfInterestMeta instances attached to buffer
    @classmethod
    def _iterate(self, buffer: Gst.Buffer):
        try:
            meta_api = hash(GObject.GType.from_name("GstVideoRegionOfInterestMetaAPI"))
        except:
            return
        gpointer = ctypes.c_void_p()
        while True:
            try:
                value = libgst.gst_buffer_iterate_meta_filtered(hash(buffer), ctypes.byref(gpointer), meta_api)
            except:
                value = None

            if not value:
                return

            roi_meta = ctypes.cast(value, ctypes.POINTER(VideoRegionOfInterestMeta)).contents
            yield RegionOfInterest(roi_meta)

    @classmethod
    def _getname(self, roi_gst_structure):
        name = libgst.gst_structure_get_name(roi_gst_structure)
        if name:
            return name.decode('utf-8')
        return None

    ## @brief Get item by the field name 
    #  @param key Field name
    #  @return Item, None if failed to get
    def _getitem(self, roi_gst_structure, key):
        key = key.encode('utf-8')
        gtype = libgst.gst_structure_get_field_type(roi_gst_structure, key)
        if gtype == hash(GObject.TYPE_INVALID):  # key is not found
            return None
        elif gtype == hash(GObject.TYPE_STRING):
            res = libgst.gst_structure_get_string(roi_gst_structure, key)
            return res.decode("utf-8") if res else None
        elif gtype == hash(GObject.TYPE_DOUBLE):
            value = ctypes.c_double()
            res = libgst.gst_structure_get_double(roi_gst_structure, key, ctypes.byref(value))
            return value.value if res else None            
        elif gtype == hash(GObject.TYPE_INT):            
            value = ctypes.c_int()
            res = libgst.gst_structure_get_int(roi_gst_structure, key, ctypes.byref(value))
            return value.value if res else None
        else:
            return None


    ## @brief Construct RegionOfInterest instance from VideoRegionOfInterestMeta. After this, RegionOfInterest will
    # obtain all tensors (detection & inference results) from VideoRegionOfInterestMeta
    # @param roi_meta VideoRegionOfInterestMeta containing bounding box information and tensors
    def __init__(self, roi_meta: VideoRegionOfInterestMeta):
        self.roimeta = roi_meta    

    ## @brief Get class label of this RegionOfInterest
    #  @return Class label of this RegionOfInterest
    def label(self) -> str:
        return GLib.quark_to_string(self.roimeta.roi_type)    

    ## @brief Get all GstStructures added to this RegionOfInterest
    # @return list of GstStructure pointers added to this RegionOfInterest
    def data_structs(self):
        param = self.roimeta._params
        while param:
            roi_gst_structure = param.contents.data
            yield roi_gst_structure

            param = param.contents.next        