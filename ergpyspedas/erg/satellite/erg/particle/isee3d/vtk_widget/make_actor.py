
import numpy as np
import vtk


def make_point_cloud_actor(pointCloudData, lookup_table, sphere_radius=0.001):
    sphere_source = vtk.vtkSphereSource()
    sphere_source.SetRadius(sphere_radius)

    point_cloud_mapper = vtk.vtkGlyph3DMapper()
    point_cloud_mapper.SetInputData(pointCloudData)
    point_cloud_mapper.SetSourceConnection(sphere_source.GetOutputPort())
    point_cloud_mapper.SetLookupTable(lookup_table)
    point_cloud_mapper.SetScalarRange(lookup_table.GetRange())
    point_cloud_mapper.SetScalarVisibility(1)

    point_cloud_actor = vtk.vtkActor()
    point_cloud_actor.SetMapper(point_cloud_mapper)
    
    return point_cloud_actor

def get_axis_title_exponent_and_scale(min_value, max_value, scale, prec=3):
    max_abs_value = max(abs(min_value*scale), abs(max_value*scale))
    exponent = int(f'{max_abs_value:.0e}'.split('e')[1])
    if exponent >= 0:
        factor = exponent // prec
    else:
        factor = -(-exponent // prec)
    title_exponent = ''
    if factor != 0:
        title_exponent = f'x 10^{prec * factor} '
    axis_scale = scale/np.power(10., prec*factor)
    return title_exponent, axis_scale

def make_cube_axes_actor(axis_names, bounds, scale, is_zaxis):
    cube_axes_actor = vtk.vtkCubeAxesActor()

    cube_axes_actor.SetBounds(bounds)
    # label_format = '%-#6.3g'

    title_exponent, axis_scale = get_axis_title_exponent_and_scale(bounds[0], bounds[1], scale)
    cube_axes_actor.SetXTitle(axis_names[0].format(title_exponent))
    cube_axes_actor.SetXAxisRange(bounds[0]*axis_scale, bounds[1]*axis_scale)
    # cube_axes_actor.SetXLabelFormat(label_format)

    title_exponent, axis_scale = get_axis_title_exponent_and_scale(bounds[2], bounds[3], scale)
    cube_axes_actor.SetYTitle(axis_names[1].format(title_exponent))
    cube_axes_actor.SetYAxisRange(bounds[2]*axis_scale, bounds[3]*axis_scale)
    # cube_axes_actor.SetYLabelFormat(label_format)

    title_exponent, axis_scale = get_axis_title_exponent_and_scale(bounds[4], bounds[5], scale)
    cube_axes_actor.SetZTitle(axis_names[2].format(title_exponent))
    cube_axes_actor.SetZAxisRange(bounds[4]*axis_scale, bounds[5]*axis_scale)
    # cube_axes_actor.SetZLabelFormat(label_format)


    cube_axes_actor.XAxisMinorTickVisibilityOff()
    cube_axes_actor.YAxisMinorTickVisibilityOff()
    cube_axes_actor.ZAxisMinorTickVisibilityOff()

    axisColor = vtk.vtkNamedColors().GetColor3d("black")
    cube_axes_actor.GetTitleTextProperty(0).SetColor(axisColor)
    cube_axes_actor.GetLabelTextProperty(0).SetColor(axisColor)
    cube_axes_actor.GetXAxesLinesProperty().SetColor(axisColor)

    cube_axes_actor.GetTitleTextProperty(1).SetColor(axisColor)
    cube_axes_actor.GetLabelTextProperty(1).SetColor(axisColor)
    cube_axes_actor.GetYAxesLinesProperty().SetColor(axisColor)

    cube_axes_actor.GetTitleTextProperty(2).SetColor(axisColor)
    cube_axes_actor.GetLabelTextProperty(2).SetColor(axisColor)
    cube_axes_actor.GetZAxesLinesProperty().SetColor(axisColor)

    cube_axes_actor.SetFlyModeToStaticTriad()

    if is_zaxis:
        cube_axes_actor.SetUseAxisOrigin(True)
        cube_axes_actor.SetAxisOrigin(bounds[0], bounds[3], bounds[4])
        cube_axes_actor.XAxisVisibilityOff()
        cube_axes_actor.XAxisLabelVisibilityOff()
        cube_axes_actor.YAxisVisibilityOff()
        cube_axes_actor.YAxisLabelVisibilityOff()
    else:
        cube_axes_actor.ZAxisVisibilityOff()
        cube_axes_actor.ZAxisLabelVisibilityOff()

    return cube_axes_actor


def make_box_actor(center, bounds):
    box = vtk.vtkCubeSource()
    box.SetCenter(center)
    box.SetXLength(bounds[1] - bounds[0])
    box.SetYLength(bounds[3] - bounds[2])
    box.SetZLength(bounds[5] - bounds[4])

    box_outline = vtk.vtkOutlineFilter()
    box_outline.SetInputConnection(box.GetOutputPort())
    box_mapper = vtk.vtkPolyDataMapper()
    box_mapper.SetInputConnection(box_outline.GetOutputPort())
    box_actor = vtk.vtkActor()
    box_actor.SetMapper(box_mapper)
    boxColor = vtk.vtkNamedColors().GetColor3d("gainsboro")
    box_actor.GetProperty().SetColor(boxColor)

    return box_actor


def make_line_actor(p1, p2):
    line = vtk.vtkLineSource()
    line.SetPoint1(p1)
    line.SetPoint2(p2)
    line_mapper = vtk.vtkPolyDataMapper()
    line_mapper.SetInputConnection(line.GetOutputPort())
    line_actor = vtk.vtkActor()
    line_actor.SetMapper(line_mapper)
    lineColor = vtk.vtkNamedColors().GetColor3d("gainsboro")
    line_actor.GetProperty().SetColor(lineColor)
    line_actor.GetProperty().SetLineWidth(0.2)
    return line_actor

def make_center_line_actors(bounds, center):
    center_line_actors = []
    # xy plane
    margin = (bounds[5] - bounds[4])*0.33
    p1 = [center[0], center[1], bounds[4] - margin]
    p2 = [center[0], center[1], bounds[5] + margin]
    line_actor = make_line_actor(p1, p2)
    center_line_actors.append(line_actor)
    # yz plane
    margin = (bounds[1] - bounds[0])*0.33
    p1 = [bounds[0] - margin, center[1], center[2]]
    p2 = [bounds[1] + margin, center[1], center[2]]
    line_actor = make_line_actor(p1, p2)
    center_line_actors.append(line_actor)
    # zx plane
    margin = (bounds[3] - bounds[2])*0.33
    p1 = [center[0], bounds[2] - margin, center[2]]
    p2 = [center[0], bounds[3] + margin, center[2]]
    line_actor = make_line_actor(p1, p2)
    center_line_actors.append(line_actor)

    return center_line_actors


def make_arrow_actor(startPoint, endPoint, radius_scale=5):
    # refer to  OrientedArrow int vtk-examples

    # Create an arrow.
    tip_radius = 0.006 * radius_scale
    shaft_radius = 0.002 * radius_scale
    arrow_source = vtk.vtkArrowSource()
    arrow_source.SetTipRadius(tip_radius)
    arrow_source.SetShaftRadius(shaft_radius)
    arrow_source.SetTipLength(0.1)

    # Compute a basis
    normalizedX = [0] * 3
    normalizedY = [0] * 3
    normalizedZ = [0] * 3

    # The X axis is a vector from start to end
    vtk.vtkMath.Subtract(endPoint, startPoint, normalizedX)
    length = vtk.vtkMath.Norm(normalizedX)
    vtk.vtkMath.Normalize(normalizedX)

    # The Z axis is an arbitrary vector cross X
    # First, make arbitrary vector to [1, 0, 0]. If X axis near to [1, 0, 0], make arbitrary vector to [0, 1, 0]
    arbitrary = [1, 0, 0]
    cos = np.inner(normalizedX, arbitrary) / np.linalg.norm(normalizedX) / np.linalg.norm(arbitrary)
    angle = np.rad2deg(np.arccos(np.clip(cos, -1.0, 1.0)))
    if angle < 10:
        arbitrary = [0, 1, 0]
    vtk.vtkMath.Cross(normalizedX, arbitrary, normalizedZ)
    vtk.vtkMath.Normalize(normalizedZ)

    # The Y axis is Z cross X
    vtk.vtkMath.Cross(normalizedZ, normalizedX, normalizedY)
    matrix = vtk.vtkMatrix4x4()

    # Create the direction cosine matrix
    matrix.Identity()
    for i in range(0, 3):
        matrix.SetElement(i, 0, normalizedX[i])
        matrix.SetElement(i, 1, normalizedY[i])
        matrix.SetElement(i, 2, normalizedZ[i])

    # Apply the transforms
    transform = vtk.vtkTransform()
    transform.Translate(startPoint)
    transform.Concatenate(matrix)
    transform.Scale(length, length, length)

    # Transform the polydata
    transformPD = vtk.vtkTransformPolyDataFilter()
    transformPD.SetTransform(transform)
    transformPD.SetInputConnection(arrow_source.GetOutputPort())

    # Create a mapper and actor for the arrow
    mapper = vtk.vtkPolyDataMapper()
    actor = vtk.vtkActor()
    mapper.SetInputConnection(transformPD.GetOutputPort())
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(vtk.vtkNamedColors().GetColor3d('Cyan'))
    return actor

def make_vector_actor(vec_property):
    vec = vec_property.vector
    length = np.linalg.norm(vec)
    max_squared_length = vec_property.max_squared_length
    if max_squared_length is None:
        max_squared_length = np.sum(np.square(vec))

    scale = np.square(vec).sum() / max_squared_length
    if vec_property.length_scale == 'full':
        scale *= 1
    elif vec_property.length_scale == 'half':
        scale *= 0.5
    elif vec_property.length_scale == 'quarter':
        scale *= 0.25

    # Set max length of vector to 1. Notice start_point = -end_point.
    end_point = vec / length / 2 * scale
    start_point = -end_point
    radius_scale = vec_property.thick
    actor = make_arrow_actor(start_point, end_point, radius_scale)
    arrowColor = vtk.vtkNamedColors().GetColor3d(vec_property.color)
    actor.GetProperty().SetColor(arrowColor)
    return actor


def make_scalar_bar_actor(lookup_table, array_name):
    scalar_bar_actor = vtk.vtkScalarBarActor()
    scalar_bar_actor.SetOrientationToVertical()
    scalar_bar_actor.SetLookupTable(lookup_table)
    scalar_bar_actor.SetTitle(array_name)
    scalar_bar_actor.SetTextPositionToSucceedScalarBar ()
    scalar_bar_actor.SetNumberOfLabels(6)
    scalar_bar_actor.SetBarRatio(0.1)
    scalar_bar_actor.SetPosition2(0.15, 0.8)
 
    # Draw ticks method. This doesn't wok for bug. https://gitlab.kitware.com/vtk/vtk/-/issues/17751
    # scalar_bar_actor.DrawTickLabelsOn()

    text_property = vtk.vtkTextProperty()
    text_property.SetColor(0, 0, 0)
    text_property.SetFontSize(16)
    text_property.SetFontFamilyToArial()
    text_property.ItalicOff()
    text_property.BoldOff()
    scalar_bar_actor.UnconstrainedFontSizeOn()
    scalar_bar_actor.SetLabelTextProperty(text_property)

    text_property = vtk.vtkTextProperty()
    text_property.SetColor(0, 0, 0)
    text_property.SetFontSize(20)
    text_property.SetFontFamilyToArial()
    text_property.ItalicOff()
    text_property.BoldOff()
    scalar_bar_actor.UnconstrainedFontSizeOn()
    scalar_bar_actor.SetTitleTextProperty(text_property)

    scalar_bar_actor.SetLabelFormat("%.1e")
    return scalar_bar_actor


def calculate_contour_values_in_logscale(value_range, divide_num=8):
    min_val, max_val = value_range
    log_min = np.log10(min_val)
    log_max = np.log10(max_val)
    log_step = (log_max - log_min)/(divide_num - 1)
    log_values = [i*log_step + log_min for i in range(divide_num)]
    contour_values = np.power(10, log_values)
    return contour_values

def make_slice_actor(image_data, lookup_table, scale, cut_value, axis):
    cut_coord_value = cut_value / scale

    plane_origin = [0] * 3
    plane_normal = [0] * 3
    if axis=='x_axis':
        axis_index = 0
    elif  axis=='y_axis':
        axis_index = 1
    elif  axis=='z_axis':
        axis_index = 2
    plane_origin[axis_index] = cut_coord_value
    plane_normal[axis_index] = 1

    # make plane
    plane = vtk.vtkPlane()
    plane.SetOrigin(plane_origin)
    plane.SetNormal(plane_normal)

    cutter = vtk.vtkCutter()
    cutter.SetInputData(image_data)
    cutter.SetCutFunction(plane)
    cutter.UpdateWholeExtent()

    plane_mapper = vtk.vtkPolyDataMapper()
    plane_mapper.SetInputConnection(cutter.GetOutputPort())
    plane_mapper.SetLookupTable(lookup_table)
    plane_mapper.SetColorModeToMapScalars()
    plane_mapper.SetScalarRange(lookup_table.GetRange())

    plane_actor = vtk.vtkActor()
    plane_actor.SetMapper(plane_mapper)

    # make contour
    min_lut, max_lut = lookup_table.GetRange()
    min_val, max_val = cutter.GetOutput().GetScalarRange()
    # min_val=1e+299 and max_val=-1e-299 in some environments and errors occur.
    low = min_val
    high = max_val
    if (min_val < min_lut) or (min_val >= max_val):
        low = min_lut
    if (max_val > max_lut) or (min_val >= max_val):
        high = max_lut
    value_range = [low, high]
    contour_values = calculate_contour_values_in_logscale(value_range, divide_num=8)

    contour = vtk.vtkContourFilter()
    contour.SetInputConnection(cutter.GetOutputPort())
    for i, v in enumerate(contour_values):
        contour.SetValue(i, v)
    contour_mapper = vtk.vtkPolyDataMapper()
    contour_mapper.SetInputConnection(contour.GetOutputPort())
    contour_mapper.ScalarVisibilityOff()

    contour_actor = vtk.vtkActor()
    contour_actor.SetMapper(contour_mapper)
    contour_color = vtk.vtkNamedColors().GetColor3d('black')
    contour_actor.GetProperty().SetDiffuseColor(contour_color)
    contour_actor.GetProperty().SetLineWidth(1.5)

    return plane_actor, contour_actor

def make_isosurface_actor(image_data, isosurface_property):
    surface_extractor = vtk.vtkContourFilter()
    surface_extractor.SetInputData(image_data)
    surface_extractor.SetValue(0, isosurface_property.value)

    surface_mapper = vtk.vtkPolyDataMapper()
    surface_mapper.SetInputConnection(surface_extractor.GetOutputPort())
    surface_mapper.ScalarVisibilityOff()

    surface_actor = vtk.vtkActor()
    surface_actor.SetMapper(surface_mapper)
    if isosurface_property.mesh:
        surface_actor.GetProperty().SetRepresentationToWireframe()
    surface_color = vtk.vtkNamedColors().GetColor3d(isosurface_property.color)
    surface_actor.GetProperty().SetColor(surface_color)

    return surface_actor



