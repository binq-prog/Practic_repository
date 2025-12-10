import numpy as np

blocks = []
with np.load('mesh.npz') as importMesh:
    for blockNumber in range(0, len(importMesh)):
        nodes = importMesh[f'block-{blockNumber}']
        block = nodes
        blocks.append(block)
blocks_data = []

with np.load('data.npz') as importData:
    for blockNumber in range(0, len(importData)):
        data = importData[f'block-{blockNumber}']
        blocks_data.append(data)
with np.load('mesh.npz') as importMesh:
    nodes = importMesh['block-0']

with np.load('data.npz') as importData:
    solution = importData['block-0']

with open('block_0.vtk', 'w') as f:
    f.write("# vtk DataFile Version 3.0\n")
    f.write("Block 0 Raw Data\n")
    f.write("ASCII\n")
    f.write("DATASET STRUCTURED_GRID\n")
    nz, ny, nx, _ = nodes.shape
    f.write(f"DIMENSIONS {nx} {ny} {nz}\n")
    total_points = nx * ny * nz
    f.write(f"POINTS {total_points} float\n")

    for k in range(nz):
        for j in range(ny):
            for i in range(nx):
                x, y, z = nodes[k, j, i, 0], nodes[k, j, i, 1], nodes[k, j, i, 2]
                f.write(f"{x} {y} {z}\n")

    f.write(f"POINT_DATA {total_points}\n")

    field_names = ['pressure', 'velocity_u', 'velocity_v', 'velocity_w', 'temperature']

    for field_id in range(5):
        field_name = field_names[field_id]
        f.write(f"SCALARS {field_name} float 1\n")
        f.write("LOOKUP_TABLE default\n")

        for k in range(nz):
            for j in range(ny):
                for i in range(nx):
                    value = solution[k, j, i, field_id]
                    f.write(f"{value}\n")