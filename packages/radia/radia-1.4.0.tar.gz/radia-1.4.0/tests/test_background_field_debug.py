#!/usr/bin/env python
"""
Test: Debug background field behavior

Compare magnetization and field with/without background field.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../build/Release'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src/python'))

import numpy as np
import radia as rad

print("=" * 80)
print("Test: Background Field Debug")
print("=" * 80)

mu0 = 4 * np.pi * 1e-7  # T/(A/m)
mu_r = 10.0
chi = mu_r - 1.0

# Background field: H0 = [0, 1, 0] A/m
H0_Am = np.array([0, 1.0, 0])
B0_T = mu0 * H0_Am

print(f"\nSetup:")
print(f"  mu_r = {mu_r}")
print(f"  chi = {chi}")
print(f"  H0 = {H0_Am} A/m")
print(f"  B0 = {B0_T} T")

# Test 1: Permanent magnet (no background field)
print("\n" + "=" * 80)
print("Test 1: Permanent Magnet Field Source (No ObjBckgCF)")
print("=" * 80)

rad.UtiDelAll()
rad.FldUnits('m')

# Create permanent magnet with M = 1 A/m in y-direction
# B = mu0 * M = mu0 * 1 = 1.257e-6 T
permanent = rad.ObjRecMag([0.2, 0, 0], [0.02, 0.02, 0.02], [0, mu0, 0])  # Tiny M to match B0
print(f"\nPermanent magnet at [0.2, 0, 0]:")
print(f"  Magnetization M = [0, {mu0}, 0] T")
print(f"  (Chosen to produce B ~= B0 at origin)")

linear1 = rad.ObjRecMag([0, 0, 0], [0.1, 0.1, 0.1], [0, 0, 0])
mat1 = rad.MatLin([chi, chi], [0, 0, 1])
rad.MatApl(linear1, mat1)

system1 = rad.ObjCnt([permanent, linear1])

result1 = rad.Solve(system1, 0.0001, 10000)
print(f"\nSolve result: {result1}")

M1 = rad.ObjM(linear1)
print(f"Magnetization M: {M1}")

H1 = rad.Fld(system1, 'h', [0, 0, 0])
B1 = rad.Fld(system1, 'b', [0, 0, 0])
print(f"H at origin: {H1}")
print(f"B at origin: {B1}")

# Test 2: Background field (ObjBckgCF)
print("\n" + "=" * 80)
print("Test 2: Background Field (ObjBckgCF)")
print("=" * 80)

rad.UtiDelAll()
rad.FldUnits('m')

def uniform_field(pos):
    """Returns B in Tesla"""
    return [float(B0_T[0]), float(B0_T[1]), float(B0_T[2])]

print(f"\nBackground field callback returns B = {B0_T} T")

background = rad.ObjBckgCF(uniform_field)
print(f"ObjBckgCF created: {background}")

linear2 = rad.ObjRecMag([0, 0, 0], [0.1, 0.1, 0.1], [0, 0, 0])
mat2 = rad.MatLin([chi, chi], [0, 0, 1])
rad.MatApl(linear2, mat2)

system2 = rad.ObjCnt([linear2, background])

result2 = rad.Solve(system2, 0.0001, 10000)
print(f"\nSolve result: {result2}")

M2 = rad.ObjM(linear2)
print(f"Magnetization M: {M2}")

H2 = rad.Fld(system2, 'h', [0, 0, 0])
B2 = rad.Fld(system2, 'b', [0, 0, 0])
print(f"H at origin: {H2}")
print(f"B at origin: {B2}")

# Test 3: Background field evaluated standalone
print("\n" + "=" * 80)
print("Test 3: Background Field Alone (No Linear Material)")
print("=" * 80)

rad.UtiDelAll()
rad.FldUnits('m')

background_only = rad.ObjBckgCF(uniform_field)

H_bg = rad.Fld(background_only, 'h', [0, 0, 0])
B_bg = rad.Fld(background_only, 'b', [0, 0, 0])

print(f"\nBackground field only:")
print(f"  H at origin: {H_bg}")
print(f"  B at origin: {B_bg}")
print(f"  Expected: B = {B0_T} T")
print(f"  Expected: H = {H0_Am} A/m")

# Comparison
print("\n" + "=" * 80)
print("Comparison")
print("=" * 80)

print("\n" + "-" * 80)
print(f"{'Source':<30} {'M (T)':<30} {'H (A/m)':<30}")
print("-" * 80)

M1_vec = np.array(M1[1])
M2_vec = np.array(M2[1])
H1_arr = np.array(H1)
H2_arr = np.array(H2)
H_bg_arr = np.array(H_bg)

print(f"{'Permanent magnet':<30} [{M1_vec[0]:.6f}, {M1_vec[1]:.6f}, {M1_vec[2]:.6f}] [{H1_arr[0]:.6f}, {H1_arr[1]:.6f}, {H1_arr[2]:.6f}]")
print(f"{'Background field (w/ MatLin)':<30} [{M2_vec[0]:.6f}, {M2_vec[1]:.6f}, {M2_vec[2]:.6f}] [{H2_arr[0]:.6f}, {H2_arr[1]:.6f}, {H2_arr[2]:.6f}]")
print(f"{'Background field (alone)':<30} {'N/A':<30} [{H_bg_arr[0]:.6f}, {H_bg_arr[1]:.6f}, {H_bg_arr[2]:.6f}]")
print("-" * 80)

# Analysis
print("\n" + "=" * 80)
print("Analysis")
print("=" * 80)

# Expected magnetization: M = chi * H0 for linear material
M_expected = chi * H0_Am
H_expected = np.array([0, 0.25, 0])  # Inside sphere: H = (3/(mu_r+2)) * H0

print(f"\nExpected magnetization: M = chi * H0 = {chi} * {H0_Am} = {M_expected}")
print(f"Expected H field (sphere): H = (3/12) * H0 = {H_expected}")

print(f"\nActual (background field):")
print(f"  M = {M2_vec}")
print(f"  H = {H2_arr}")

# Check if M direction is wrong
M2_dir = M2_vec / np.linalg.norm(M2_vec) if np.linalg.norm(M2_vec) > 0 else np.array([0,0,0])
print(f"\nMagnetization direction:")
print(f"  Expected: [0, 1, 0] (y-direction)")
print(f"  Actual:   [{M2_dir[0]:.3f}, {M2_dir[1]:.3f}, {M2_dir[2]:.3f}]")

# Check H direction
H2_dir = H2_arr / np.linalg.norm(H2_arr) if np.linalg.norm(H2_arr) > 0 else np.array([0,0,0])
print(f"\nH field direction:")
print(f"  Expected: [0, 1, 0] (y-direction)")
print(f"  Actual:   [{H2_dir[0]:.3f}, {H2_dir[1]:.3f}, {H2_dir[2]:.3f}]")

print("\n" + "=" * 80)
print("Conclusion")
print("=" * 80)

# Check if magnetization is in wrong direction
if abs(M2_dir[2]) > 0.5:  # Magnetization is primarily in z-direction
    print("\n[BUG IDENTIFIED] Magnetization is in WRONG direction!")
    print("  Expected: y-direction (background field direction)")
    print("  Actual:   z-direction")
    print("\nPossible cause:")
    print("  MatLin([chi, chi], [0, 0, 1]) 'easy axis' [0,0,1] may be")
    print("  overriding the background field direction!")
elif np.linalg.norm(M2_vec) < 0.01:
    print("\n[BUG IDENTIFIED] Magnetization magnitude is too small!")
    print(f"  Expected: ~{np.linalg.norm(M_expected):.3f} T")
    print(f"  Actual:   {np.linalg.norm(M2_vec):.6f} T")
else:
    print("\n[UNKNOWN] Magnetization magnitude and direction seem reasonable,")
    print("  but H field still doesn't match analytical solution.")

print("=" * 80)
