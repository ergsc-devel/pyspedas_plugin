import numpy as np

from . import make_actor
from ..colorbar.build_lookup_table import build_lookup_table


def draw_colorbar(colorbar_property, v_array, renderer):
    lookup_table = build_lookup_table(colorbar_property.name)
    lookup_table.SetScaleToLog10()
    if colorbar_property.max is None:
        colorbar_property.max = v_array.max()
    if colorbar_property.min is None:
        colorbar_property.min = v_array.min()
    lookup_table.SetTableRange(colorbar_property.min, colorbar_property.max)
    lookup_table.SetNanColor(0, 0, 0, 1)  # nan to black
    lookup_table.Build()

    scalarBarActor = make_actor.make_scalar_bar_actor(lookup_table, colorbar_property.units)
    renderer.AddActor2D(scalarBarActor)

    return lookup_table

def draw_isosurface(isosurface_property, image_data, renderer):
    if isosurface_property.show:
        isosurface1_actor = make_actor.make_isosurface_actor(image_data, isosurface_property)
        renderer.AddActor(isosurface1_actor)

def draw_plane(slice_property, image_data, lookup_table, scale, renderer):
    if slice_property.show:
        cut_value = slice_property.cut_value
        plane, contour = make_actor.make_slice_actor(image_data, lookup_table, scale, cut_value=cut_value, axis=slice_property.cut_axis)
        if slice_property.show_image:
            renderer.AddActor(plane)
        if slice_property.show_contour:
            renderer.AddActor(contour)

def draw_vector(vector_property, renderer):
    if vector_property.show:
        arrow_ctor = make_actor.make_vector_actor(vector_property)
        renderer.AddActor(arrow_ctor)

def draw_outline(outline_property, scale, renderer):
    bounds = [outline_property.x_min/scale, outline_property.x_max/scale,
              outline_property.y_min/scale, outline_property.y_max/scale,
              outline_property.z_min/scale, outline_property.z_max/scale]
    center = [(bounds[0] + bounds[1])*0.5,
              (bounds[2] + bounds[3])*0.5,
              (bounds[4] + bounds[5])*0.5]
    # Box
    if outline_property.show_box:
        boxActor = make_actor.make_box_actor(center, bounds)
        renderer.AddActor(boxActor)

    # line
    if outline_property.show_center_lines:
        centerLineActors = make_actor.make_center_line_actors(bounds, center)
        for line in centerLineActors:
            renderer.AddActor(line)
    
    # Axes
    if outline_property.show_axis:
        if outline_property.axis_units == 'Velocity':
            axis_names = ['<- VX ->', '<- VY ->','<- VZ ->']
        elif outline_property.axis_units == 'Energy':
            axis_names = ['<- EX ->', '<- EY ->','<- EZ ->']
        # x axis and y axis
        cube_axes_actor_xy = make_actor.make_cube_axes_actor(axis_names, bounds, scale, is_zaxis=False)
        cube_axes_actor_xy.SetCamera(renderer.GetActiveCamera())
        cube_axes_actor_xy.SetScreenSize(outline_property.axis_screen_size)
        renderer.AddActor(cube_axes_actor_xy)
        # z axis
        cube_axes_actor_z = make_actor.make_cube_axes_actor(axis_names, bounds, scale, is_zaxis=True)
        cube_axes_actor_z.SetCamera(renderer.GetActiveCamera())
        cube_axes_actor_z.SetScreenSize(outline_property.axis_screen_size)
        renderer.AddActor(cube_axes_actor_z)

def draw_all(draw_property, draw_data, renderer):
    # color scale
    lookup_table = draw_colorbar(draw_property.colorbar, draw_data.value, renderer)

    # point cloud
    # point_cloud_actor = make_actor.make_point_cloud_actor(point_cloud_data, lookup_table, sphere_radius=0.005)
    # renderer.AddActor(point_cloud_actor)

    # isosurface
    draw_isosurface(draw_property.isosurface1, draw_data.image_data, renderer)
    draw_isosurface(draw_property.isosurface2, draw_data.image_data, renderer)

    # slice and contour
    draw_plane(draw_property.yz_plane, draw_data.image_data, lookup_table, draw_data.scale, renderer)
    draw_plane(draw_property.xz_plane, draw_data.image_data, lookup_table, draw_data.scale, renderer)
    draw_plane(draw_property.xy_plane, draw_data.image_data, lookup_table, draw_data.scale, renderer)

    # magnetic field vector
    draw_vector(draw_property.mag_vec, renderer)
    # velocity vector
    draw_vector(draw_property.vel_vec, renderer)
    # user vector
    draw_vector(draw_property.user_vec, renderer)

    # box, center lines, axes
    # draw_outline(draw_property.outline, draw_data.point_cloud_data, draw_data.scale, renderer)
    draw_outline(draw_property.outline, draw_data.scale, renderer)
