#!/usr/bin/env python
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'build', 'Release'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'python'))

print("[1] Starting test...")

import radia as rad
print("[2] Radia imported")

from radia_field_cached import CachedRadiaField
print("[3] CachedRadiaField imported")

rad.UtiDelAll()
magnet = rad.ObjRecMag([0, 0, 0], [40, 40, 60], [0, 0, 1.2])
print("[4] Magnet created")

def radia_field_with_A(coords):
    x, y, z = coords
    B = rad.Fld(magnet, 'b', [x, y, z])
    A = rad.Fld(magnet, 'a', [x, y, z])
    return {'B': list(B), 'A': list(A)}

bg_field = rad.ObjBckgCF(radia_field_with_A)
print("[5] Background field created")

npts = 100
print(f"[6] Generating {npts} test points...")
test_points = []
for i in range(npts):
    x = 0.02 + (i % 20) * 0.001
    y = 0.02 + ((i // 20) % 20) * 0.001
    z = 0.03 + (i // 400) * 0.001
    test_points.append([x, y, z])
print(f"[7] Generated {len(test_points)} points")

A_cf = CachedRadiaField(bg_field, 'a')
print("[8] CachedRadiaField instance created")

print("[9] Calling prepare_cache...")
t0 = time.time()
A_cf.prepare_cache(test_points, verbose=False)
t1 = time.time()
print("[10] prepare_cache completed")

stats = A_cf.get_cache_stats()
time_ms = (t1 - t0) * 1000
time_per_point = time_ms * 1000 / npts if npts > 0 else 0

print()
print(f"Points: {npts}")
print(f"Time: {time_ms:.2f} ms")
print(f"Time/point: {time_per_point:.2f} us")
print(f"Cache size: {stats['size']}")
print(f"Status: {'PASS' if stats['size'] == npts else 'FAIL'}")

rad.UtiDelAll()
