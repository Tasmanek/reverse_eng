"""Renderuje lokalne SVG do PNG przez librsvg/cairo. Nie wymaga sieci."""
from pathlib import Path
import ctypes as c
import ctypes.util
r=c.CDLL(ctypes.util.find_library('rsvg-2'));a=c.CDLL(ctypes.util.find_library('cairo'));g=c.CDLL(ctypes.util.find_library('gobject-2.0'))
r.rsvg_handle_new_from_file.argtypes=[c.c_char_p,c.c_void_p];r.rsvg_handle_new_from_file.restype=c.c_void_p
r.rsvg_handle_render_cairo.argtypes=[c.c_void_p,c.c_void_p];r.rsvg_handle_render_cairo.restype=c.c_int
class Dim(c.Structure):_fields_=[('width',c.c_int),('height',c.c_int),('em',c.c_double),('ex',c.c_double)]
r.rsvg_handle_get_dimensions.argtypes=[c.c_void_p,c.POINTER(Dim)]
a.cairo_image_surface_create.argtypes=[c.c_int,c.c_int,c.c_int];a.cairo_image_surface_create.restype=c.c_void_p
a.cairo_create.argtypes=[c.c_void_p];a.cairo_create.restype=c.c_void_p
a.cairo_surface_write_to_png.argtypes=[c.c_void_p,c.c_char_p]
a.cairo_destroy.argtypes=[c.c_void_p];a.cairo_surface_destroy.argtypes=[c.c_void_p];g.g_object_unref.argtypes=[c.c_void_p]
for key in ['ckan','xml','manual']:
 p=Path(__file__).resolve().parent/f'{key}_uzupelniony_01.svg';h=r.rsvg_handle_new_from_file(str(p).encode(),None);d=Dim();r.rsvg_handle_get_dimensions(h,c.byref(d));s=a.cairo_image_surface_create(0,d.width,d.height);ctx=a.cairo_create(s)
 assert r.rsvg_handle_render_cairo(h,ctx)
 assert a.cairo_surface_write_to_png(s,str(p.with_suffix('.png')).encode())==0
 a.cairo_destroy(ctx);a.cairo_surface_destroy(s);g.g_object_unref(h)
 print(p.with_suffix('.png').name,d.width,d.height)
