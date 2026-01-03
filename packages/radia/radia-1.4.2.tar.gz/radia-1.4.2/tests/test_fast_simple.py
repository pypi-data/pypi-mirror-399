#!/usr/bin/env python
"""
Simple fast PrepareCache test (small point counts)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'build', 'Release'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'python'))

import radia as rad

try:
    from ngsolve import *
    from netgen.occ import *
    import radia_ngsolve
    import radia_ngsolve_fast
except ImportError as e:
    print(f"ERROR: {e}")
    sys.exit(1)

print("="*80)
print("TEST: Fast PrepareCache (Simple)")
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

# Test with 100, 200, 300 points
for npts in [100, 200, 300]:
    print(f"Testing {npts} points...")

    # Generate points
    points = []
    for i in range(npts):
        x = 0.02 + (i % 10) * 0.001
        y = 0.02 + ((i // 10) % 10) * 0.001
        z = 0.03 + (i // 100) * 0.001
        points.append([x, y, z])

    # Test
    timing = rad_ngsolve_fast.prepare_cache_silent(A_cf, points)

    print(f"  Time: {timing['time_total']:.2f} ms")
    print(f"  Time/point: {timing['time_total']*1000/npts:.2f} us")

    stats = A_cf.GetCacheStats()
    print(f"  Cache size: {stats['size']}")

    if stats['size'] == npts:
        print(f"  Status: PASS")
    else:
        print(f"  Status: FAIL (expected {npts}, got {stats['size']})")

    A_cf.ClearCache()
    print()

print("="*80)
print("If time/point is < 10 us: EXCELLENT performance")
print("If time/point is < 100 us: GOOD performance")
print("If time/point is > 1000 us: SLOW (needs optimization)")
print("="*80)

rad.UtiDelAll()
