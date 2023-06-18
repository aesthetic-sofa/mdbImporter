from pathlib import Path
from parsing.mdbParser import MDB
import glob

mdbFiles = glob.glob(str(Path(Path(__file__).parent, "__testfiles__/*.mdb")))

for f in mdbFiles:
    print(MDB(f))