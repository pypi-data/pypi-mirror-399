#########################################################################
#                                                                       #
#  This file is part of squidient.                                      #
#                                                                       #
#  squidient is free software: you can redistribute it and/or modify    #
#  it under the terms of the GNU General Public License as published by #
#  the Free Software Foundation, either version 3 of the License, or    #
#  (at your option) any later version.                                  #
#                                                                       #
#  squidient is distributed in the hope that it will be useful,         #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of       #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the        # 
#  GNU General Public License for more details.                         #
#                                                                       #
#  You should have received a copy of the GNU General Public License    #
#  along with squidient. If not, see <https://www.gnu.org/licenses/>.   #
#                                                                       #
#########################################################################


from .squidientfilereport import *
try:
    from utils.compare import *
    from utils.comparewithdifftable import *
except:
    from ..utils.compare import *
    from ..utils.comparewithdifftable import *
import sys


class SquidientDetailedReport(SquidientFileReport):

    def __init__(self, case, test_file):
        super().__init__(case)
        self._test_file = test_file

    def run(self):
        self.open_json()
        self.set()
        self.validate_files()
        for file in self._json["comparisons"]:
            if file["file"] == self._test_file:
                tolerance = file["tolerance"]
                method = file["method"]
                if "rows" in file:
                    rows = file["rows"]
                else:
                    rows = None
                if "cols" in file:
                    cols = file["cols"]
                else:
                    cols = None
                base_path = self._base_dir + "/" + self._test_file
                if not self.present_file(base_path):
                    print(f"[ERROR] Base file missing: {base_path}")
                    exit(1)
                elif not self.present_file(self._file):
                    print(f"[ERROR] Test file missing: {self._test_file}")
                    exit(1)
                print(print_diff_table_for_file(base_path, self._test_file, method, tolerance, rows, cols))

def main(argv: Optional[Sequence[str]] = None) -> int:
    if argv is None:
        if len(sys.argv) < 3:
            print("Usage: sqdetails [case] [file]")
            exit(1)
    report = SquidientDetailedReport(sys.argv[1], sys.argv[2])
    report.run()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: sqdetails [case] [file]")
        exit(1)
    report = SquidientDetailedReport(sys.argv[1], sys.argv[2])
    report.run()
