import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src/python'))

from ngsolve import *
from netgen.occ import *
import radia as rad
import radia_ngsolve
import numpy as np

print("="*70)
print("L2 Norm Calculation Debug")
print("="*70)

# Create magnet
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

# Create mesh
box = Box((0.01, 0.01, 0.02), (0.06, 0.06, 0.08))
mesh = Mesh(OCCGeometry(box).GenerateMesh(maxh=0.010))

print(f"\nMesh: {mesh.ne} elements")
print(f"Domain: x=[0.01,0.06], y=[0.01,0.06], z=[0.02,0.08] meters")
print(f"Volume: {Integrate(1, mesh):.6e} m^3")

# Get B as CoefficientFunction
B_cf = radia_ngsolve.RadiaField(bg_field, 'b')

print(f"\nB_cf type: {type(B_cf)}")
print(f"B_cf dimensions: {B_cf.dim}")

# Project to HDiv
fes_hdiv = HDiv(mesh, order=2)
B_gf = GridFunction(fes_hdiv)
B_gf.Set(B_cf)

print(f"\nB_gf type: {type(B_gf)}")
print(f"B_gf space: {fes_hdiv}")

# Test point
test_point = (0.030, 0.020, 0.040)
mip = mesh(*test_point)

B_cf_val = B_cf(mip)
B_gf_val = B_gf(mip)

print(f"\nAt point {test_point}:")
print(f"  B_cf: {B_cf_val}")
print(f"  B_gf: {B_gf_val}")
print(f"  Difference: {np.array(B_gf_val) - np.array(B_cf_val)}")

# Method 1: Compute L2 norm of B_cf
print("\n" + "="*70)
print("Method 1: Direct integration of B_cf")
print("="*70)

B_cf_norm_sq_1 = Integrate(B_cf[0]**2 + B_cf[1]**2 + B_cf[2]**2, mesh)
B_cf_norm_1 = np.sqrt(B_cf_norm_sq_1)
print(f"  ||B_cf||_L2 = {B_cf_norm_1:.6e} T")

# Method 2: Using InnerProduct
print("\n" + "="*70)
print("Method 2: Using InnerProduct")
print("="*70)

B_cf_norm_sq_2 = Integrate(InnerProduct(B_cf, B_cf), mesh)
B_cf_norm_2 = np.sqrt(B_cf_norm_sq_2)
print(f"  ||B_cf||_L2 = {B_cf_norm_2:.6e} T")

# Method 3: Compute L2 norm of B_gf
print("\n" + "="*70)
print("Method 3: L2 norm of B_gf")
print("="*70)

B_gf_norm_sq = Integrate(InnerProduct(B_gf, B_gf), mesh)
B_gf_norm = np.sqrt(B_gf_norm_sq)
print(f"  ||B_gf||_L2 = {B_gf_norm:.6e} T")

# Method 4: Error computation - different approaches
print("\n" + "="*70)
print("Method 4: Error ||B_gf - B_cf||")
print("="*70)

# Approach A: Component-wise difference
print("\nApproach A: Component-wise")
error_sq_a = Integrate((B_gf[0]-B_cf[0])**2 + (B_gf[1]-B_cf[1])**2 + (B_gf[2]-B_cf[2])**2, mesh)
error_a = np.sqrt(error_sq_a)
rel_error_a = error_a / B_cf_norm_1 * 100
print(f"  ||error||_L2 = {error_a:.6e} T")
print(f"  Relative:      {rel_error_a:.2f}%")

# Approach B: Using InnerProduct with difference
print("\nApproach B: InnerProduct(B_gf - B_cf, B_gf - B_cf)")
error_vec = B_gf - B_cf
error_sq_b = Integrate(InnerProduct(error_vec, error_vec), mesh)
error_b = np.sqrt(error_sq_b)
rel_error_b = error_b / B_cf_norm_2 * 100
print(f"  ||error||_L2 = {error_b:.6e} T")
print(f"  Relative:      {rel_error_b:.2f}%")

# Check if error_vec is computed correctly
print("\n" + "="*70)
print("Verification: Check error_vec at test point")
print("="*70)

error_vec_at_point = error_vec(mip)
expected_error = np.array(B_gf_val) - np.array(B_cf_val)

print(f"  error_vec(mip):     {error_vec_at_point}")
print(f"  B_gf - B_cf (calc): {expected_error}")
print(f"  Match: {np.allclose(error_vec_at_point, expected_error, rtol=1e-5)}")

# Sanity check: L2 norm consistency
print("\n" + "="*70)
print("Sanity Check: L2 norm relations")
print("="*70)

print(f"  ||B_cf||_L2    = {B_cf_norm_1:.6e}")
print(f"  ||B_gf||_L2    = {B_gf_norm:.6e}")
print(f"  ||error||_L2   = {error_a:.6e}")
print(f"  Ratio: ||error||/||B|| = {error_a/B_cf_norm_1*100:.2f}%")

# Triangle inequality check: ||B_gf - B_cf|| <= ||B_gf|| + ||B_cf||
print(f"\n  Triangle inequality:")
print(f"    ||B_gf - B_cf|| = {error_a:.6e}")
print(f"    ||B_gf|| + ||B_cf|| = {B_gf_norm + B_cf_norm_1:.6e}")
print(f"    Valid: {error_a <= B_gf_norm + B_cf_norm_1}")
