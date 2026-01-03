#!/usr/bin/env python
"""
Test PrepareCache() performance with various point counts
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'build', 'Release'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'python'))

import radia as rad
import time

try:
    from ngsolve import *
    from netgen.occ import *
    import radia_ngsolve
except ImportError as e:
    print(f"ERROR: {e}")
    sys.exit(1)

print("="*80)
print("TEST: PrepareCache() Performance")
print("="*80)
print()

# Setup
rad.UtiDelAll()

# Set Radia to use meters (required for NGSolve integration)
rad.FldUnits('m')

magnet = rad.ObjRecMag([0, 0, 0], [0.04, 0.04, 0.06], [0, 0, 1.2])

def radia_field_with_A(coords):
    x, y, z = coords
    B = rad.Fld(magnet, 'b', [x, y, z])
    A = rad.Fld(magnet, 'a', [x, y, z])
    return {'B': list(B), 'A': list(A)}

bg_field = rad.ObjBckgCF(radia_field_with_A)
A_cf = radia_ngsolve.RadiaField(bg_field, 'a')

print("[Setup] Testing PrepareCache() performance")
print()

# Test different point counts
test_configs = [
    {"npts": 100, "label": "100 points"},
    {"npts": 500, "label": "500 points"},
    {"npts": 1000, "label": "1000 points"},
    {"npts": 2000, "label": "2000 points"},
    {"npts": 3000, "label": "3000 points"},
    {"npts": 5000, "label": "5000 points"},
]

print(f"{'Points':<10} {'Time (ms)':<12} {'us/point':<12} {'Status':<20}")
print("-" * 70)

for config in test_configs:
    npts = config["npts"]
    label = config["label"]

    # Generate test points
    test_points = []
    for i in range(npts):
        x = 0.02 + (i % 20) * 0.001
        y = 0.02 + ((i // 20) % 20) * 0.001
        z = 0.03 + (i // 400) * 0.001
        test_points.append([x, y, z])

    # Test PrepareCache()
    try:
        t0 = time.time()
        A_cf.PrepareCache(test_points)
        t1 = time.time()

        time_ms = (t1 - t0) * 1000
        time_per_point = time_ms * 1000 / npts  # us/point

        stats = A_cf.GetCacheStats()

        if stats['size'] == npts:
            status = "PASS"
        else:
            status = f"ERROR (size={stats['size']})"

        print(f"{npts:<10} {time_ms:<12.2f} {time_per_point:<12.2f} {status:<20}")

        A_cf.ClearCache()

    except Exception as e:
        print(f"{npts:<10} ERROR: {str(e)[:30]}")

print("-" * 70)
print()

print("="*80)
print("CONCLUSION")
print("="*80)
print()
print("If time/point is roughly constant:")
print("  -> Linear O(N) scaling (GOOD - expected)")
print()
print("If time/point increases with N:")
print("  -> Super-linear O(N^2) scaling (BAD - bottleneck)")
print()
print("Optimized PrepareCache() should handle 3000-5000 points in <1 second")
print("="*80)

rad.UtiDelAll()
