# Copyright 2019 Zhushi Tech, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import numpy as np


def findHomography(src, dst):
    in_matrix = []
    for (x, y), (X, Y) in zip(src, dst):
        in_matrix.extend([
            [x, y, 1, 0, 0, 0, -X * x, -X * y],
            [0, 0, 0, x, y, 1, -Y * x, -Y * y],
        ])

    A = np.array(in_matrix, dtype=np.float)
    B = np.array(dst, dtype=np.float).reshape(8)
    # H = np.dot(np.linalg.inv(A.T * A) * A.T, B)
    H = np.linalg.solve(A, B)
    return np.append(H, 1.).reshape((3, 3))


def perspectiveTransform(src, m, *, inv=False):
    if isinstance(m, list):
        m = np.array(m).reshape((3, 3))
    if inv:
        m = np.linalg.inv(m)
    src = np.array([(x, y, 1.) for x, y in src])
    dst = np.dot(src, m.T)
    return [(x / z, y / z) for (x, y, z) in dst]


def getNewHomography(src, dst, m, *, remap=None):
    if isinstance(m, list):
        m = np.array(m).reshape((3, 3))
    src = perspectiveTransform(src, m, inv=True)
    m = findHomography(src, dst)
    if remap is None:
        return m
    x0, x1, y0, y1 = remap
    src = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    dst = perspectiveTransform(src, m)
    x = [d[0] for d in dst]
    y = [d[1] for d in dst]
    min_x = min(x)
    max_x = max(x)
    delta_x = (min_x + max_x) / 2.
    min_y = min(y)
    dst = [(x - delta_x, y - min_y) for x, y in dst]
    m = findHomography(src, dst)
    return m.ravel().tolist()


def getBound(m, remap):
    if isinstance(m, list):
        m = np.array(m).reshape((3, 3))
    x0, x1, y0, y1 = remap
    src = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    d = perspectiveTransform(src, m)
    a = [d[0][0], d[1][0]]
    b = [d[0][1], d[1][1]]
    c = [d[3][0], d[2][0]]
    d = [d[3][1], d[2][1]]
    return a, b, c, d
