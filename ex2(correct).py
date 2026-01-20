import vtk

def create_plane_slice(input_vtk="",
                                output_slice="",
                                plane_origin=(1.7, 0.65, 0),
                                plane_normal=(1, 1, 1)):
    reader = vtk.vtkStructuredGridReader()
    reader.SetFileName(input_vtk)
    reader.Update()

    structured_grid = reader.GetOutput()


    plane = vtk.vtkPlane()

    plane.SetOrigin(plane_origin[0], plane_origin[1], plane_origin[2])
    plane.SetNormal(plane_normal[0], plane_normal[1], plane_normal[2])

    cutter = vtk.vtkCutter()
    cutter.SetCutFunction(plane)
    cutter.SetInputData(structured_grid)
    cutter.GenerateCutScalarsOn()
    cutter.Update()
    slice_data = cutter.GetOutput()

    writer = vtk.vtkPolyDataWriter()
    writer.SetFileName(output_slice)
    writer.SetInputData(slice_data)
    writer.SetFileTypeToASCII()
    writer.Write()
    return output_slice

create_plane_slice("block_0.vtk", "slice1.vtk")