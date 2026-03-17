import numpy as np

ISO_VALUE = 0.15

def cell_to_node_pressure(pc):

    nz, ny, nx = pc.shape

    pnodes = np.zeros((nz+1, ny+1, nx+1))

    pnodes[:-1, :-1, :-1] += pc
    pnodes[1:,  :-1, :-1] += pc
    pnodes[:-1, 1:,  :-1] += pc
    pnodes[:-1, :-1, 1:]  += pc
    pnodes[1:, 1:,  :-1]  += pc
    pnodes[1:,  :-1, 1:]  += pc
    pnodes[:-1, 1:,  1:]  += pc
    pnodes[1:,  1:,  1:]  += pc

    counts = np.zeros_like(pnodes)
    counts[:-1, :-1, :-1] += 1
    counts[1:,  :-1, :-1] += 1
    counts[:-1, 1:,  :-1] += 1
    counts[:-1, :-1, 1:]  += 1
    counts[1:, 1:,  :-1]  += 1
    counts[1:,  :-1, 1:]  += 1
    counts[:-1, 1:,  1:]  += 1
    counts[1:,  1:,  1:]  += 1

    pnodes /= counts

    return pnodes

def interpolate(p1, p2, val1, val2, iso):
    if abs(val2 - val1) < 1e-12:
        return p1
    t = (iso - val1) / (val2 - val1)
    return p1 + t * (p2 - p1)



def process_block(nodes, solution):

    pc = solution[..., 0]

    pc = pc[1:-1, 1:-1, 1:-1]

    pnodes = cell_to_node_pressure(pc)

    Nz, Ny, Nx, _ = nodes.shape
    triangles = []

    tets = [
        [0, 5, 1, 6],
        [0, 5, 6, 4],
        [0, 2, 6, 1],
        [0, 2, 3, 6],
        [0, 7, 4, 6],
        [0, 3, 7, 6]
    ]

    for k in range(Nz - 1):
        for j in range(Ny - 1):
            for i in range(Nx - 1):

                cube_pts = np.array([
                    nodes[k, j, i],
                    nodes[k, j, i+1],
                    nodes[k, j+1, i+1],
                    nodes[k, j+1, i],
                    nodes[k+1, j, i],
                    nodes[k+1, j, i+1],
                    nodes[k+1, j+1, i+1],
                    nodes[k+1, j+1, i],
                ])

                cube_vals = np.array([
                    pnodes[k, j, i],
                    pnodes[k, j, i+1],
                    pnodes[k, j+1, i+1],
                    pnodes[k, j+1, i],
                    pnodes[k+1, j, i],
                    pnodes[k+1, j, i+1],
                    pnodes[k+1, j+1, i+1],
                    pnodes[k+1, j+1, i],
                ])

                if cube_vals.min() > ISO_VALUE or cube_vals.max() < ISO_VALUE:
                    continue

                for tet in tets:
                    pts = cube_pts[tet]
                    vals = cube_vals[tet]

                    inside = vals < ISO_VALUE
                    n_inside = np.sum(inside)

                    if n_inside == 0 or n_inside == 4:
                        continue

                    edges = [(0,1),(1,2),(2,0),(0,3),(1,3),(2,3)]
                    intersect_pts = []

                    for a,b in edges:
                        if (vals[a] - ISO_VALUE) * (vals[b] - ISO_VALUE) < 0:
                            p = interpolate(pts[a], pts[b],
                                            vals[a], vals[b],
                                            ISO_VALUE)
                            intersect_pts.append(p)

                    if len(intersect_pts) == 3:
                        triangles.append(intersect_pts)
                    elif len(intersect_pts) == 4:
                        triangles.append([intersect_pts[0],
                                          intersect_pts[1],
                                          intersect_pts[2]])
                        triangles.append([intersect_pts[0],
                                          intersect_pts[2],
                                          intersect_pts[3]])

    return triangles
mesh = np.load("mesh.npz")
data = np.load("data.npz")

all_triangles = []

def save(triangles, filename="pressure.txt"):
    with open(filename, "w") as f:
        for tri in triangles:
            for vertex in tri:
                f.write(f"{vertex[0]} {vertex[1]} {vertex[2]}\n")
            f.write("\n")
for block_key in mesh.files:
    nodes = mesh[block_key]
    solution = data[block_key]

    tris = process_block(nodes, solution)
    all_triangles.extend(tris)

save(all_triangles, "pressure.txt")

print(len(all_triangles))