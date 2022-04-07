import sys
import os
from struct import pack, unpack

# defaults
def_dim = [10, 10, 16]
def_siz = [0.1775, 0.1775, 0.242]
def_inp = "dummy_ascii_141"
def_out = def_inp+".vxl"
# colors for coloring output (works on linux)
CRED    = '\033[91m'
CGREEN  = '\33[32m'
CBLUE   = '\33[34m'
CEND    = '\033[0m'
CVIOLET = '\33[35m'
############################

def sizewrap(byte):
    s = len(byte)
    return pack('i', s) + byte + pack('i', s)

def input_handler(length):
    print("Please input filename with ascii voxel data (i.e 0 0 0 0 3 0 0 2 0 0 15 0 0...)")
    print(f"{CBLUE}{def_inp} for default{CEND}")
    fn = input() or def_inp
    if not os.path.isfile(fn):
        print(CRED + "ERROR: input file with name\"" + fn + "\"does not exist", CEND)
        sys.exit(0)

    data = []
    with open(fn) as f:
        for line in f:
            data.extend(line.split())
    if len(data) != length:
        print(CRED + "ERROR: size of data inconsistent with dimensions input previously")
        print("ascii data size =", len(data), "but sizes x*y*z =", length, CEND)
        sys.exit(0)
    print(CGREEN + "Success read data from file", fn, CEND)
    data = [int(i) for i in data]
    KREG = [0 for i in range(1000)]
    IREG = []
    NO = 0
    MO = 0
    organ_map = dict()
    for num in data:
        if num > 0:
            MO = max(MO, num)
            if num not in IREG:
                NO += 1
                IREG.append(num)
                KREG[num-1] = NO
                organ_map[NO] = num 

    print("Max organ number", MO)
    print("Number of organs", NO)
    print("Please input filename for prints organ map (from old numbers to new)")
    print(CBLUE + "prints on screen for default", CEND)
    col_width = max(len(str(key)) for key in organ_map.keys()) + 2
    fn = input()
    if fn:
        with open(fn, "w+") as f:
            f.write("new".ljust(col_width) + " old\n")
            for k,v in sorted(organ_map.items()):
                f.write(str(k).ljust(col_width) + " " + str(v) + "\n")
    else:
        print(CVIOLET + "new".ljust(col_width), "old", CEND)
        for k,v in sorted(organ_map.items()):
            print(str(k).ljust(col_width),v)
    
    return (data, KREG, MO, NO)

def dim_handler():
    print("Hello, please input voxel model dimensions separate by space ' ' in order x->y->z")
    print(f"{CBLUE}{def_dim} for default{CEND}")
    dims = input().split() or def_dim
    dims = [int(i) for i in dims]
    if len(dims) !=3:
        print(CRED + "ERROR: incorrect dimensions number (must be 3), you got ", len(dims), CEND)
        sys.exit(0)
    for n in dims:
        if n<= 0:
            print(CRED + "ERROR: input incorrect dimensions: ", dims, CEND)
            sys.exit(0)
    print(CGREEN + "Success input dimensions: ", dims, CEND)
    return tuple(dims)

def size_handler():
    print("Please input voxel sizes separate by space ' ' in order x->y->z")
    print(f"{CBLUE}{def_siz} for default{CEND}")
    sizes = input().split() or def_siz
    sizes = [float(i) for i in sizes]
    if len(sizes) !=3:
        print(CRED + "ERROR: incorrect sizes number (must be 3), you got ", len(sizes),CEND)
        sys.exit(0)
    for n in sizes:
        if n<= 0:
            print(CRED + "ERROR: input incorrect sizes: ", sizes, CEND)
            sys.exit(0)
    print(CGREEN + "Success input sizes: ", sizes, CEND)
    return tuple(sizes)

def output_handler():
    print("Please input output filename (.vxl file for fluka)")
    print(f"{CBLUE}{def_out} for default{CEND}")
    fn = input() or def_out
    with open(fn, "wb") as f:
        # write title
        title = pack('80s', fn.encode())
        print(title)
        title = sizewrap(Title)
        print(title)
        f.write(Title)
        ints = pack('5i', NX, NY, NZ, NO, MO)
        ints = sizewrap(ints)
        f.write(ints)
        dbles = pack('3d', DX, DY, DZ)
        dbles = sizewrap(dbles)
        f.write(dbles)
        array = pack(str(NX*NY*NZ)+"h", *data)
        array = sizewrap(array)
        f.write(array)
        kreg = pack(str(len(KREG[:MO]))+"h", *KREG[:MO])
        print("kreg: ", KREG[:MO])
        #kreg = pack("3h", *[1,2,3])
        kreg = sizewrap(kreg)
        f.write(kreg)


if __name__ == "__main__":
    NX, NY, NZ   = dim_handler()
    DX, DY, DZ   = size_handler()
    data, KREG, MO, NO = input_handler(NX*NY*NZ)
    
    print("Please input output filename (.vxl file for fluka)")
    print(f"{CBLUE}{def_out} for default{CEND}")
    fn = input() or def_out
    with open(fn, "wb") as f:
        title = pack('80s', fn.encode())
        title = sizewrap(title)
        f.write(title)
        ints = pack('5i', NX, NY, NZ, NO, MO)
        ints = sizewrap(ints)
        f.write(ints)
        dbles = pack('3d', DX, DY, DZ)
        dbles = sizewrap(dbles)
        f.write(dbles)
        array = pack(str(NX*NY*NZ)+"h", *data)
        array = sizewrap(array)
        f.write(array)
        kreg = pack(str(len(KREG[:MO]))+"h", *KREG[:MO])
        kreg = sizewrap(kreg)
        f.write(kreg)
    print(CGREEN + "Success write to file", fn, CEND)

