"""
Test script for pyXtal version 0.1dev. Tests core functions for all modules.
"""
import sys
sys.settrace(None)

outstructs = []
outstrings = []

def compare_wyckoffs(num1, num2, dim=3):
    """Given 2 groups, return whether the second point
    group has equal or greater symmetry than the first group."""
    from numpy import allclose
    if num1 == "???":
        print("Error: invalid value for num1 passed to compare_wyckoffs")
        return
    if num2 == "???":
        return False
    #Get general positions for both groups
    if dim == 3:
        from pyxtal.crystal import get_wyckoffs
        g1 = get_wyckoffs(num1)[0]
        g2 = get_wyckoffs(num2)[0]
    elif dim == 2:
        from pyxtal.crystal import get_layer
        g1 = get_layer(num1)[0]
        g2 = get_layer(num2)[0]
    elif dim == 1:
        from pyxtal.crystal import get_rod
        g1 = get_rod(num1)[0]
        g2 = get_rod(num2)[0]
    #If group 2 has higher symmetry
    if len(g2) > len(g1):
        return True
    #Compare point group operations
    for i, op2 in enumerate(g2):
        op1 = g1[i]
        m1 = op1.rotation_matrix
        m2 = op2.rotation_matrix
        if not allclose(m1, m2):
            return False
    return True

#Check if module and classes work correctly
def passed():
    global failed_module
    global failed
    if failed_module is False and failed is False:
        return True
    else:
        return False

#Reset flags for module and class
def reset():
    global failed_module
    global failed
    failed_module = False
    failed = False

#Set flags for package, module, class if error occurs
def fail(e):
    global failed_package
    global failed_module
    global failed
    failed_package = True
    failed_module = True
    failed = True
    try:
        print("~~~ Error:")
        import pdb, traceback
        extype, value, tb = sys.exc_info()
        traceback.print_exc()
    except:
        print("~~~ Error: ", e)

#Print whether module passed or failed
def check():
    if passed():
        pass#print("Success!")
    else:
        print("~~~ Failed module ~~~")

#Call at end of script, or if module fails
def end(condition=1):
    print("===")
    if failed_package is False:
        print("All modules passed!")
        if condition == 1:
            sys.exit(0)
        elif condition == 2:
            pass
    else:
        print("One or more modules failed. Try reinstalling the package.")
        sys.exit(0)

def test_atomic():
    global outstructs
    global outstrings
    print("=== Testing generation of atomic 3D crystals. This may take some time. ===")
    from time import time
    from spglib import get_symmetry_dataset
    from pyxtal.crystal import get_wyckoffs
    from pyxtal.crystal import random_crystal
    from pyxtal.crystal import cellsize
    from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
    slow = []
    print("  Spacegroup #  |Generated (SPG)|Generated (PMG)|  Time Elapsed")
    skip = [166, 202, 210, 216, 217, 219, 220, 221, 223, 225, 226, 227, 228, 229, 230] #slow to generate
    for sg in range(1, 231):
        if sg not in skip:
            multiplicity = len(get_wyckoffs(sg)[0]) / cellsize(sg)#multiplicity of the general position
            start = time()
            rand_crystal = random_crystal(sg, ['C'], [multiplicity], 1.0)
            end = time()
            timespent = np.around((end - start), decimals=2)
            t = str(timespent)
            if len(t) == 3:
                t += "0"
            t += " s"
            if timespent >= 1.0:
                t += " ~"
            if timespent >= 3.0:
                t += "~"
            if timespent >= 10.0:
                t += "~"
            if timespent >= 60.0:
                t += "~"
                slow.append(sg)
            if rand_crystal.valid:
                ans1 = get_symmetry_dataset(rand_crystal.spg_struct, symprec=1e-1)
                if ans1 is None:
                    ans1 = "???"
                else:
                    ans1 = ans1['number']
                sga = SpacegroupAnalyzer(rand_crystal.struct)
                ans2 = None
                if sga is not None:
                    ans2 = sga.get_space_group_number()
                if ans2 is None:
                    ans2 = "???"

                #Compare expected and detected groups
                if ans1 != "???" and ans2 == "???":
                    t += " xxxxx"
                elif ans1 == "???":
                    if ans2 > sg: pass
                elif ans2 == "???":
                    if ans1 > sg: pass
                else:
                    if compare_wyckoffs(sg, ans1) or compare_wyckoffs(sg, ans2): pass
                    else: t += " xxxxx"

                print("\t"+str(sg)+"\t|\t"+str(ans1)+"\t|\t"+str(ans2)+"\t|\t"+t)
                #output cif files for incorrect space groups
                if t[-1] == "x":
                    outstructs.append(rand_crystal.struct)
                    outstrings.append(str("3D_Atomic_"+str(sg)+".poscar"))
            else:
                print("~~~~ Error: Could not generate space group "+str(sg)+" after "+t)
    if slow != []:
        print("~~~~ The following space groups took more than 60 seconds to generate:")
        for i in slow:
            print("     "+str(i))

def test_molecular():
    global outstructs
    global outstrings
    print("=== Testing generation of molecular 3D crystals. This may take some time. ===")
    from time import time
    from spglib import get_symmetry_dataset
    from pyxtal.crystal import get_wyckoffs
    from pyxtal.crystal import cellsize
    from pyxtal.molecular_crystal import molecular_crystal
    from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
    slow = []
    print("  Spacegroup #  |Generated (SPG)|Generated (PMG)|  Time Elapsed")
    skip = [183, 202, 203, 209, 210, 216, 219, 225, 226, 227, 228, 229, 230] #slow
    for sg in range(1, 231):
        if sg not in skip:
            multiplicity = len(get_wyckoffs(sg)[0]) / cellsize(sg)#multiplicity of the general position
            start = time()
            rand_crystal = molecular_crystal(sg, ['H2O'], [multiplicity], 2.5)
            end = time()
            timespent = np.around((end - start), decimals=2)
            t = str(timespent)
            if len(t) == 3:
                t += "0"
            t += " s"
            if timespent >= 1.0:
                t += " ~"
            if timespent >= 3.0:
                t += "~"
            if timespent >= 10.0:
                t += "~"
            if timespent >= 60.0:
                t += "~"
                slow.append(sg)
            if rand_crystal.valid:
                ans1 = get_symmetry_dataset(rand_crystal.spg_struct, symprec=1e-1)
                if ans1 is None:
                    ans1 = "???"
                else:
                    ans1 = ans1['number']
                sga = SpacegroupAnalyzer(rand_crystal.struct)
                ans2 = None
                if sga is not None:
                    ans2 = sga.get_space_group_number()
                if ans2 is None:
                    ans2 = "???"

                #Compare expected and detected groups
                if ans1 != "???" and ans2 == "???":
                    t += " xxxxx"
                elif ans1 == "???":
                    if ans2 > sg: pass
                elif ans2 == "???":
                    if ans1 > sg: pass
                else:
                    if compare_wyckoffs(sg, ans1) or compare_wyckoffs(sg, ans2): pass
                    else: t += " xxxxx"

                print("\t"+str(sg)+"\t|\t"+str(ans1)+"\t|\t"+str(ans2)+"\t|\t"+t)
                #output cif files for incorrect space groups
                if t[-1] == "x":
                    outstructs.append(rand_crystal.struct)
                    outstrings.append(str("3D_Molecular_"+str(sg)+".poscar"))
            else:
                print("~~~~ Error: Could not generate space group "+str(sg)+" after "+t)
    if slow != []:
        print("~~~~ The following space groups took more than 60 seconds to generate:")
        for i in slow:
            print("     "+str(i))

def test_atomic_2D():
    global outstructs
    global outstrings
    print("=== Testing generation of atomic 2D crystals. This may take some time. ===")
    from time import time
    from spglib import get_symmetry_dataset
    from pyxtal.crystal import get_layer
    from pyxtal.crystal import random_crystal_2D
    from pyxtal.crystal import cellsize
    from pyxtal.database.layergroup import Layergroup
    from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
    slow = []
    print("   Layergroup   | sg # Expected |Generated (SPG)|Generated (PMG)|Time Elapsed")
    skip = []#slow to generate
    for num in range(1, 81):
        if num not in skip:
            sg = Layergroup(num).sgnumber
            multiplicity = len(get_layer(num)[0]) / cellsize(sg) #multiplicity of the general position
            start = time()
            rand_crystal = random_crystal_2D(num, ['H'], [multiplicity], None, 4.0)
            end = time()
            timespent = np.around((end - start), decimals=2)
            t = str(timespent)
            if len(t) == 3:
                t += "0"
            t += " s"
            if timespent >= 1.0:
                t += " ~"
            if timespent >= 3.0:
                t += "~"
            if timespent >= 10.0:
                t += "~"
            if timespent >= 60.0:
                t += "~"
                slow.append(num)
            if rand_crystal.valid:
                ans1 = get_symmetry_dataset(rand_crystal.spg_struct, symprec=1e-1)
                if ans1 is None:
                    ans1 = "???"
                else:
                    ans1 = ans1['number']
                sga = SpacegroupAnalyzer(rand_crystal.struct)
                ans2 = None
                if sga is not None:
                    ans2 = sga.get_space_group_number()
                if ans2 is None:
                    ans2 = "???"

                #Compare expected and detected groups
                if ans1 != "???" and ans2 == "???":
                    t += " xxxxx"
                elif ans1 == "???":
                    if ans2 > sg: pass
                elif ans2 == "???":
                    if ans1 > sg: pass
                else:
                    if compare_wyckoffs(sg, ans1) or compare_wyckoffs(sg, ans2): pass
                    else: t += " xxxxx"

                print("\t"+str(num)+"\t|\t"+str(sg)+"\t|\t"+str(ans1)+"\t|\t"+str(ans2)+"\t|\t"+t)
                #output cif files for incorrect space groups
                if t[-1] == "x":
                    outstructs.append(rand_crystal.struct)
                    outstrings.append(str("2D_Atomic_"+str(num)+".poscar"))
            else:
                print("~~~~ Error: Could not generate layer group "+str(num)+" after "+t)
    if slow != []:
        print("~~~~ The following layer groups took more than 60 seconds to generate:")
        for i in slow:
            print("     "+str(i))

def test_molecular_2D():
    global outstructs
    global outstrings
    print("=== Testing generation of molecular 2D crystals. This may take some time. ===")
    from time import time
    from spglib import get_symmetry_dataset
    from pyxtal.crystal import get_layer
    from pyxtal.crystal import cellsize
    from pyxtal.molecular_crystal import molecular_crystal_2D
    from pyxtal.database.layergroup import Layergroup
    from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
    slow = []
    print("   Layergroup   | sg # Expected |Generated (SPG)|Generated (PMG)|Time Elapsed")
    skip = []#12, 64, 65, 80] #slow to generate
    for num in range(1, 81):
        if num not in skip:
            sg = Layergroup(num).sgnumber
            multiplicity = len(get_layer(num)[0]) / cellsize(sg) #multiplicity of the general position
            start = time()
            rand_crystal = molecular_crystal_2D(num, ['H2O'], [multiplicity], None, 4.0)
            end = time()
            timespent = np.around((end - start), decimals=2)
            t = str(timespent)
            if len(t) == 3:
                t += "0"
            t += " s"
            if timespent >= 1.0:
                t += " ~"
            if timespent >= 3.0:
                t += "~"
            if timespent >= 10.0:
                t += "~"
            if timespent >= 60.0:
                t += "~"
                slow.append(num)
            if rand_crystal.valid:
                ans1 = get_symmetry_dataset(rand_crystal.spg_struct, symprec=1e-1)
                if ans1 is None:
                    ans1 = "???"
                else:
                    ans1 = ans1['number']
                sga = SpacegroupAnalyzer(rand_crystal.struct)
                ans2 = None
                if sga is not None:
                    ans2 = sga.get_space_group_number()
                if ans2 is None:
                    ans2 = "???"

                #Compare expected and detected groups
                if ans1 != "???" and ans2 == "???":
                    t += " xxxxx"
                elif ans1 == "???":
                    if ans2 > sg: pass
                elif ans2 == "???":
                    if ans1 > sg: pass
                else:
                    if compare_wyckoffs(sg, ans1) or compare_wyckoffs(sg, ans2): pass
                    else: t += " xxxxx"

                print("\t"+str(num)+"\t|\t"+str(sg)+"\t|\t"+str(ans1)+"\t|\t"+str(ans2)+"\t|\t"+t)
                #output cif files for incorrect space groups
                if t[-1] == "x":
                    outstructs.append(rand_crystal.struct)
                    outstrings.append(str("2D_Molecular_"+str(num)+".poscar"))
            else:
                print("~~~~ Error: Could not generate layer group "+str(num)+" after "+t)
    if slow != []:
        print("~~~~ The following layer groups took more than 60 seconds to generate:")
        for i in slow:
            print("     "+str(i))

def test_atomic_1D():
    global outstructs
    global outstrings
    print("=== Testing generation of atomic 1D crystals. This may take some time. ===")
    from time import time
    from spglib import get_symmetry_dataset
    from pyxtal.crystal import get_rod
    from pyxtal.crystal import random_crystal_1D
    from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
    slow = []
    print("   Layergroup   | Gen sg. (SPG) | Gen. sg (PMG) |Time Elapsed")
    skip = []#slow to generate
    for num in range(1, 76):
        if num not in skip:
            multiplicity = len(get_rod(num)[0]) #multiplicity of the general position
            start = time()
            rand_crystal = random_crystal_1D(num, ['H'], [multiplicity], None, 4.0)
            end = time()
            timespent = np.around((end - start), decimals=2)
            t = str(timespent)
            if len(t) == 3:
                t += "0"
            t += " s"
            if timespent >= 1.0:
                t += " ~"
            if timespent >= 3.0:
                t += "~"
            if timespent >= 10.0:
                t += "~"
            if timespent >= 60.0:
                t += "~"
                slow.append(num)
            if rand_crystal.valid:
                try:
                    ans1 = get_symmetry_dataset(rand_crystal.spg_struct, symprec=1e-1)
                except:
                    ans1 = "???"
                if ans1 is None or ans1 == "???":
                    ans1 = "???"
                else:
                    ans1 = ans1['number']
                sga = SpacegroupAnalyzer(rand_crystal.struct)
                try:
                    ans2 = sga.get_space_group_number()
                except:
                    ans2 = "???"
                if ans2 is None:
                    ans2 = "???"
                if ans1 == "???" and ans2 == "???":
                    t += " xxxxx"
                print("\t"+str(num)+"\t|\t"+str(ans1)+"\t|\t"+str(ans2)+"\t|\t"+t)
                #output cif files for incorrect space groups
                if t[-1] == "x":
                    outstructs.append(rand_crystal.struct)
                    outstrings.append(str("1D_Atomic_"+str(num)+".poscar"))
            else:
                print("~~~~ Error: Could not generate layer group "+str(num)+" after "+t)
    if slow != []:
        print("~~~~ The following layer groups took more than 60 seconds to generate:")
        for i in slow:
            print("     "+str(i))

def test_molecular_1D():
    global outstructs
    global outstrings
    print("=== Testing generation of molecular 1D crystals. This may take some time. ===")
    from time import time
    from spglib import get_symmetry_dataset
    from pyxtal.crystal import get_rod
    from pyxtal.molecular_crystal import molecular_crystal_1D
    from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
    slow = []
    print("    Rod group   | Gen sg. (SPG) | Gen. sg (PMG) |Time Elapsed")
    skip = []#slow to generate
    for num in range(1, 76):
        if num not in skip:
            multiplicity = len(get_rod(num)[0]) #multiplicity of the general position
            start = time()
            rand_crystal = molecular_crystal_1D(num, ['H2O'], [multiplicity], None, 4.0)
            end = time()
            timespent = np.around((end - start), decimals=2)
            t = str(timespent)
            if len(t) == 3:
                t += "0"
            t += " s"
            if timespent >= 1.0:
                t += " ~"
            if timespent >= 3.0:
                t += "~"
            if timespent >= 10.0:
                t += "~"
            if timespent >= 60.0:
                t += "~"
                slow.append(num)
            if rand_crystal.valid:
                try:
                    ans1 = get_symmetry_dataset(rand_crystal.spg_struct, symprec=1e-1)
                except:
                    ans1 = "???"
                if ans1 is None or ans1 == "???":
                    ans1 = "???"
                else:
                    ans1 = ans1['number']
                sga = SpacegroupAnalyzer(rand_crystal.struct)
                try:
                    ans2 = sga.get_space_group_number()
                except:
                    ans2 = "???"
                if ans2 is None:
                    ans2 = "???"
                if ans1 == "???" and ans2 == "???":
                    t += " xxxxx"
                print("\t"+str(num)+"\t|\t"+str(ans1)+"\t|\t"+str(ans2)+"\t|\t"+t)
                #output cif files for incorrect space groups
                if t[-1] == "x":
                    outstructs.append(rand_crystal.struct)
                    outstrings.append(str("1D_Molecular_"+str(num)+".poscar"))
            else:
                print("~~~~ Error: Could not generate layer group "+str(num)+" after "+t)
    if slow != []:
        print("~~~~ The following layer groups took more than 60 seconds to generate:")
        for i in slow:
            print("     "+str(i))


def test_modules():
    print("====== Testing functionality for pyXtal version 0.1dev ======")

    global failed_package
    failed_package = False #Record if errors occur at any level

    reset()

    print("Importing sys...")
    try:
        import sys
        print("Success!")
    except Exception as e:
        fail(e)
        sys.exit(0)

    print("Importing numpy...")
    try:
        import numpy as np
        print("Success!")
    except Exception as e:
        fail(e)
        sys.exit(0)

    I = np.array([[1,0,0],[0,1,0],[0,0,1]])

    print("Importing pymatgen...")
    try:
        import pymatgen
        print("Success!")
    except Exception as e:
        fail(e)
        sys.exit(0)

    try:
        from pymatgen.core.operations import SymmOp
    except Exception as e:
        fail(e)
        sys.exit(0)

    print("Importing pandas...")
    try:
        import pandas
        print("Success!")
    except Exception as e:
        fail(e)
        sys.exit(0)

    print("Importing spglib...")
    try:
        import spglib
        print("Success!")
    except Exception as e:
        fail(e)
        sys.exit(0)

    print("Importing openbabel...")
    try:
        import ase
        print("Success!")
    except:
        print("Error: could not import openbabel. Try reinstalling the package.")

    print("Importing pyxtal...")
    try:
        import pyxtal
        print("Success!")
    except Exception as e:
        fail(e)
        sys.exit(0)

    print("=== Testing modules ===")

    #=====database.element=====
    print("pyxtal.database.element")
    reset()
    try:
        import pyxtal.database.element
    except Exception as e:
        fail(e)

    print("  class Element")
    try:
        from pyxtal.database.element import Element
    except Exception as e:
        fail(e)
    if passed():
        for i in range(1, 95):
            if passed():
                try:
                    ele = Element(i)
                except:
                    fail("Could not access Element # "+str(i))
                try:
                    y = ele.sf
                    y = ele.z
                    y = ele.short_name
                    y = ele.long_name
                    y = ele.valence
                    y = ele.valence_electrons
                    y = ele.covalent_radius
                    y = ele.vdw_radius
                    y = ele.get_all(0)
                except:
                    fail("Could not access attribute for element # "+str(i))
                try:
                    ele.all_z()
                    ele.all_short_names()
                    ele.all_long_names()
                    ele.all_valences()
                    ele.all_valence_electrons()
                    ele.all_covalent_radii()
                    ele.all_vdw_radii()
                except:
                    fail("Could not access class methods")

    check()

    #=====database.hall=====
    print("pyxtal.database.hall")
    reset()
    try:
        import pyxtal.database.hall
    except Exception as e:
        fail(e)

    print("  hall_from_hm")
    try:
        from pyxtal.database.hall import hall_from_hm
    except Exception as e:
        fail(e)

    if passed():
        for i in range(1, 230):
            if passed():
                try:
                    hall_from_hm(i)
                except:
                    fail("Could not access hm # "+str(i))

    check()

    #=====database.collection=====
    print("pyxtal.database.collection")
    reset()
    try:
        import pyxtal.database.collection
    except Exception as e:
        fail(e)

    print("  Collection")
    try:
        from pyxtal.database.collection import Collection
    except Exception as e:
        fail(e)

    if passed():
        for i in range(1, 230):
            if passed():
                try:
                    molecule_collection = Collection('molecules')
                except:
                    fail("Could not access hm # "+str(i))

    check()

    #=====database.layergroup=====
    print("pyxtal.database.layergroup")
    reset()
    try:
        import pyxtal.database.layergroup
    except Exception as e:
        fail(e)

    print("  class Layergroup")
    try:
        from pyxtal.database.layergroup import Layergroup
    except Exception as e:
        fail(e)

    if passed():
        for i in range(1, 81):
            if passed():
                try:
                    lgp = Layergroup(i)
                except:
                    fail("Could not access layer group # "+str(i))
                try:
                    lgp.input
                    lgp.lg
                    lgp.symbol
                    lgp.sgnumber
                    lgp.permutation
                except:
                    fail("Could not access attribute for layer group # "+str(i))

    check()

    #=====operations=====
    print("pyxtal.operations")
    reset()
    try:
        import pyxtal.operations
    except Exception as e:
        fail(e)

    print("  random_vector")
    try:
        from pyxtal.operations import random_vector
    except Exception as e:
        fail(e)

    if passed():
        try:
            for i in range(10):
                random_vector()
        except Exception as e:
            fail(e)

    check()

    print("  angle")
    try:
        from pyxtal.operations import angle
    except Exception as e:
        fail(e)

    if passed():
        try:
            for i in range(10):
                v1 = random_vector()
                v2 = random_vector()
                angle(v1, v2)
        except Exception as e:
            fail(e)

    check()

    print("  random_shear_matrix")
    try:
        from pyxtal.operations import random_shear_matrix
    except Exception as e:
        fail(e)

    if passed():
        try:
            for i in range(10):
                random_shear_matrix()
        except Exception as e:
            fail(e)

    check()

    print("  is_orthogonal")
    try:
        from pyxtal.operations import is_orthogonal
    except Exception as e:
        fail(e)

    if passed():
        try:
            a = is_orthogonal([[1,0,0],[0,1,0],[0,0,1]])
            b = is_orthogonal([[0,0,1],[1,0,0],[1,0,0]])
            if a is True and b is False:
                pass
            else:
                fail()
        except Exception as e:
            fail(e)

    check()

    print("  aa2matrix")
    try:
        from pyxtal.operations import aa2matrix
    except Exception as e:
        fail(e)

    if passed():
        try:
            for i in range(10):
                aa2matrix(1, 1, random=True)
        except Exception as e:
            fail(e)

    check()

    print("  matrix2aa")
    try:
        from pyxtal.operations import matrix2aa
    except Exception as e:
        fail(e)

    if passed():
        try:
            for i in range(10):
                m = aa2matrix(1, 1, random=True)
                aa = matrix2aa(m)
        except Exception as e:
            fail(e)

    check()

    print("  rotate_vector")
    try:
        from pyxtal.operations import rotate_vector
    except Exception as e:
        fail(e)

    if passed():
        try:
            for i in range(10):
                v1 = random_vector()
                v2 = random_vector()
                rotate_vector(v1, v2)
        except Exception as e:
            fail(e)

    check()

    print("  are_equal")
    try:
        from pyxtal.operations import are_equal
    except Exception as e:
        fail(e)

    if passed():
        try:
            op1 = SymmOp.from_xyz_string('x,y,z')
            op2 = SymmOp.from_xyz_string('x,y,z+1')
            a = are_equal(op1, op2, PBC=[3])
            b = are_equal(op1, op2, PBC=[1])
            if a is True and b is False:
                pass
            else:
                fail()
        except Exception as e:
            fail(e)

    check()


    print("  class OperationAnalyzer")
    try:
        from pyxtal.operations import OperationAnalyzer
    except Exception as e:
        fail(e)

    if passed():
        try:
            for i in range(10):
                m = aa2matrix(1,1,random=True)
                t = random_vector()
                op1 = SymmOp.from_rotation_and_translation(m, t)
                OperationAnalyzer(op1)
        except Exception as e:
            fail(e)

    check()

    print("  class orientation")
    try:
        from pyxtal.operations import orientation
    except Exception as e:
        fail(e)

    if passed():
        try:
            for i in range(10):
                v1 = random_vector()
                c1 = random_vector()
                o = orientation.from_constraint(v1, c1)
        except Exception as e:
            fail(e)

    check()

    #=====crystal=====
    print("pyxtal.crystal")
    reset()
    try:
        import pyxtal.crystal
    except Exception as e:
        fail(e)

    print("  get_wyckoffs (may take a moment)")
    try:
        from pyxtal.crystal import get_wyckoffs
    except Exception as e:
        fail(e)

    if passed():
        try:
            for i in [1, 2, 229, 230]:
                get_wyckoffs(i)
                get_wyckoffs(i, organized=True)
        except:
            fail(" Could not access Wyckoff positions for space group # "+str(i))

    check()

    print("  get_wyckoff_symmetry (may take a moment)")
    try:
        from pyxtal.crystal import get_wyckoff_symmetry
    except Exception as e:
        fail(e)

    if passed():
        try:
            for i in [1, 2, 229, 230]:
                get_wyckoff_symmetry(i)
                get_wyckoff_symmetry(i, molecular=True)
        except:
            fail("Could not access Wyckoff symmetry for space group # "+str(i))

    check()

    print("  get_wyckoffs_generators (may take a moment)")
    try:
        from pyxtal.crystal import get_wyckoff_generators
    except Exception as e:
        fail(e)

    if passed():
        try:
            for i in [1, 2, 229, 230]:
                get_wyckoff_generators(i)
        except:
            fail("Could not access Wyckoff generators for space group # "+str(i))

    check()

    print("  letter_from_index")
    try:
        from pyxtal.crystal import letter_from_index
    except Exception as e:
        fail(e)

    if passed():
        try:
            if letter_from_index(0, 47) == "A":
                pass
            else:
                fail()
        except Exception as e:
            fail(e)

    check()

    print("  index_from_letter")
    try:
        from pyxtal.crystal import index_from_letter
    except Exception as e:
        fail(e)

    if passed():
        try:
            if index_from_letter("A", 47) == 0:
                pass
            else:
                fail()
        except Exception as e:
            fail(e)

    check()

    print("  jk_from_i")
    try:
        from pyxtal.crystal import jk_from_i
    except Exception as e:
        fail(e)

    if passed():
        try:
            w = get_wyckoffs(2, organized=True)
            j, k = jk_from_i(1, w)
            if j == 1 and k == 0:
                pass
            else:
                print(j, k)
                fail()
        except Exception as e:
            fail(e)

    check()

    print("  i_from_jk")
    try:
        from pyxtal.crystal import i_from_jk
    except Exception as e:
        fail(e)

    if passed():
        try:
            w = get_wyckoffs(2, organized=True)
            j, k = jk_from_i(1, w)
            i = i_from_jk(j, k, w)
            if i == 1:
                pass
            else:
                print(j, k)
                fail()
        except Exception as e:
            fail(e)

    check()

    print("  ss_string_from_ops")
    try:
        from pyxtal.crystal import ss_string_from_ops
    except Exception as e:
        fail(e)

    if passed():
        try:
            strings = ['1','4 . .','2 3 .']
            for i, sg in enumerate([1, 75, 195]):
                ops = get_wyckoffs(sg)[0]
                ss_string_from_ops(ops, sg)
        except Exception as e:
            fail(e)

    check()

    print("  random_crystal")
    try:
        from pyxtal.crystal import random_crystal
    except Exception as e:
        fail(e)

    if passed():
        try:
            c = random_crystal(1, ['H'], [1], 10.0)
            if c.valid is True:
                pass
            else:
                fail()
        except Exception as e:
            fail(e)

    check()

    print("  random_crystal_2D")
    try:
        from pyxtal.crystal import random_crystal_2D
    except Exception as e:
        fail(e)

    if passed():
        try:
            c = random_crystal_2D(1, ['H'], [1], 1.0, 10.0)
            if c.valid is True:
                pass
            else:
                fail()
        except Exception as e:
            fail(e)

    check()

    #=====molecule=====
    print("pyxtal.molecule")
    reset()
    try:
        import pyxtal.molecule
    except Exception as e:
        fail(e)

    print("  ob_mol_from_string")
    try:
        from pyxtal.molecule import ob_mol_from_string
    except Exception as e:
        fail(e)

    if passed():
        try:
            h2o = molecule_collection['H2O']
            ch4 = molecule_collection['CH4']
        except Exception as e:
            fail(e)

    check()

    print("  get_inertia_tensor")
    try:
        from pyxtal.molecule import get_inertia_tensor
    except Exception as e:
        fail(e)

    if passed():
        try:
            get_inertia_tensor(h2o)
            get_inertia_tensor(ch4)
        except Exception as e:
            fail(e)

    check()

    print("  get_moment_of_inertia")
    try:
        from pyxtal.molecule import get_moment_of_inertia
    except Exception as e:
        fail(e)

    if passed():
        try:
            v = random_vector()
            get_moment_of_inertia(h2o, v)
            get_moment_of_inertia(ch4, v)
        except Exception as e:
            fail(e)

    check()

    print("  reoriented_molecule")
    try:
        from pyxtal.molecule import reoriented_molecule
    except Exception as e:
        fail(e)

    if passed():
        try:
            reoriented_molecule(h2o)
            reoriented_molecule(ch4)
        except Exception as e:
            fail(e)

    check()

    print("  orientation_in_wyckoff_position")
    try:
        from pyxtal.molecule import orientation_in_wyckoff_position
    except Exception as e:
        fail(e)

    if passed():
        try:
            w = get_wyckoffs(20)
            ws = get_wyckoff_symmetry(20, molecular=True)
            orientation_in_wyckoff_position(h2o, w, ws, 1)
            orientation_in_wyckoff_position(ch4, w, ws, 1)
        except Exception as e:
            fail(e)

    check()

    #=====molecular_crystal=====
    print("pyxtal.molecular_crystal")
    reset()
    try:
        import pyxtal.crystal
    except Exception as e:
        fail(e)

    print("  molecular_crystal")
    try:
        from pyxtal.molecular_crystal import molecular_crystal
    except Exception as e:
        fail(e)

    if passed():
        try:
            c = molecular_crystal(1, ['H2O'], [1], 10.0)
            if c.valid is True:
                pass
            else:
                fail()
        except Exception as e:
            fail(e)

    check()

    print("  molecular_crystal_2D")
    try:
        from pyxtal.molecular_crystal import molecular_crystal_2D
    except Exception as e:
        fail(e)

    if passed():
        try:
            c = molecular_crystal_2D(1, ['H2O'], [1], 1.0, 10.0)
            if c.valid is True:
                pass
            else:
                fail()
        except Exception as e:
            fail(e)

    check()

    end(condition=2)

from optparse import OptionParser
if __name__ == "__main__":
    import sys
    from time import time
    parser = OptionParser()
    parser.add_option("-m", "--module", dest="module", metavar='module', default='all', type=str,
            help="modules options: 'all', 'atomic', 'molecular', 'atomic_2D', 'molecular_2D', 'atomic_1D', 'molecular_1D' ")
    (options, args) = parser.parse_args()

    try:
        import numpy as np
    except Exception as e:
        fail(e)
        sys.exit(0)
    modules_lib = {
            'atomic': 'test_atomic()', 
            'molecular': 'test_molecular()',
            'atomic_2D': 'test_atomic_2D()',
            'molecular_2D': 'test_molecular_2D()',
            'atomic_1D': 'test_atomic_1D()', 
            'molecular_1D': 'test_molecular_1D()', 
            }
    if options.module == 'all':
        modules = modules_lib
    else:
        if options.module in modules_lib.keys():
            modules = [options.module]
        else:
            print('please choose the modules from the followings:')
            for module in modules_lib.keys():
                print(module)

    masterstart = time()

    test_modules()

    for module in modules:
        eval(modules_lib[module])

    masterend = time()
    mastertime = np.around((masterend-masterstart), decimals=2)

    print("TEST COMPLETE")
    print("Total time elapsed: "+str(mastertime)+" s")

    if outstructs != []:
        #from pymatgen.io.cif import CifWriter
        from os import mkdir
        from os.path import isdir
        outdir0 = "test_out_"
        i = 1
        while True:
            outdir = outdir0 + str(i)
            if not isdir(outdir):
                mkdir(outdir)
                break
            i += 1
            if i > 100:
                break
        print("Some generated space groups did not match the expected group.")
        print("POSCAR files for these groups will be output to the directory " + outdir + ":")
        for struct, string in zip(outstructs, outstrings):
            fpath = outdir + "/" + string
            struct.to(filename=fpath, fmt="poscar")
            #CifWriter(struct, symprec=0.1).write_file(filename = fpath)
            print("  "+string)
