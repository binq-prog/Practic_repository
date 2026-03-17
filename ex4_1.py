import numpy as np

ISO_VALUE = 0.15

def interpolate(p1, p2, v1, v2):
    t = (ISO_VALUE - v1) / (v2 - v1)
    return p1 + t * (p2 - p1)


def process_block(nodes, solution):

    p = solution[..., 0]
    p = p[1:-1, 1:-1, 1:-1]

    Nz, Ny, Nx = p.shape
    triangles = []

    for k in range(Nz - 1):
        for j in range(Ny - 1):
            for i in range(Nx - 1):

                pts = [
                    nodes[k, j, i],
                    nodes[k, j, i+1],
                    nodes[k, j+1, i+1],
                    nodes[k, j+1, i],
                    nodes[k+1, j, i],
                    nodes[k+1, j, i+1],
                    nodes[k+1, j+1, i+1],
                    nodes[k+1, j+1, i],
                ]

                vals = [
                    p[k, j, i],
                    p[k, j, i+1],
                    p[k, j+1, i+1],
                    p[k, j+1, i],
                    p[k+1, j, i],
                    p[k+1, j, i+1],
                    p[k+1, j+1, i+1],
                    p[k+1, j+1, i],
                ]

                if min(vals) > ISO_VALUE or max(vals) < ISO_VALUE:
                    continue

                edges = [
                    (0,1),(1,2),(2,3),(3,0),
                    (4,5),(5,6),(6,7),(7,4),
                    (0,4),(1,5),(2,6),(3,7)
                ]

                points = []

                for a, b in edges:
                    if (vals[a] - ISO_VALUE) * (vals[b] - ISO_VALUE) < 0:
                        points.append(
                            interpolate(
                                np.array(pts[a]),
                                np.array(pts[b]),
                                vals[a],
                                vals[b]
                            )
                        )

                if len(points) >= 3:
                    p0 = points[0]
                    for m in range(1, len(points) - 1):
                        triangles.append([p0, points[m], points[m+1]])

    return triangles


def save(triangles, filename="pressure1.txt"):
    with open(filename, "w") as f:
        for tri in triangles:
            for vertex in tri:
                f.write(f"{vertex[0]} {vertex[1]} {vertex[2]}\n")
            f.write("\n")
mesh = np.load("mesh.npz")
data = np.load("data.npz")

all_triangles = []

for block_key in mesh.files:
    nodes = mesh[block_key]
    solution = data[block_key]

    tris = process_block(nodes, solution)
    all_triangles.extend(tris)

save(all_triangles)
