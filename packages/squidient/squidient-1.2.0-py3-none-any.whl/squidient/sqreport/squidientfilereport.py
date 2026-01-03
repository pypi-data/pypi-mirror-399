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
import re

try:
    from utils.compare import *
except:
    from ..utils.compare import *
import sys

from typing import Optional, Sequence

class SquidientFileReport:

    def __init__(self, case):
        self._case = case
        self._file = case + ".json"
        self._json = None
        self._test = {}
        self._status = False
        self._error = "execution"
        self._cwd = os.getcwd()
        self._base_dir = "base/1p"

    def run(self):
        self.open_json()
        self.set()
        self.validate_files()
        self.save_json()
        print(self.files_report_console())

    def open_json(self):
        self._json = open_json(self._file)

    def set(self):
        json = self._json
        test = {}
        test["name"] = json["name"]
        test["files"] = []
        test["hostname"] = "unknown"
        test["env"] = {}
        self._test = test

    def validate_files(self):
        for file in self._json["comparisons"]:
            test = {}
            f = file["file"]
            test["file"] = f
            test["status"] = True
            test["error"] = "OK"
            test["maxAbs"] = 0
            test["maxRel"] = 0
            test["maxPower"] = 0
            test["differences"] = 0
            test["total"] = 0
            test["method"] = file["method"]
            if "rows" in file:
                rows = file["rows"]
            else:
                rows = None
            if "cols" in file:
                cols = file["cols"]
            else:
                cols = None
            if "tolerance" in file:
                test["tolerance"] = file["tolerance"]
            else:
                test["tolerance"] = 0
            if not self.present_file(self._base_dir + "/" + f):
                test["status"] = False
                test["error"] = "missing base"
            elif not self.present_file(f):
                test["status"] = False
                test["error"] = "missing test file"
            else:
                try:
                    res = self.compare(f, self._base_dir + "/" + f, test["method"], test["tolerance"], rows, cols)
                except Exception as e:
                    test["status"] = False
                    test["error"] = "comparison"
                    print(e)
                else:
                    test["maxAbs"] = res["maxAbs"]
                    test["maxRel"] = res["maxRel"]
                    test["maxPower"] = res["maxPower"]
                    test["differences"] = res["differences"]
                    test["total"] = res["total"]
                    test["status"] = res["status"]
                    test["error"] = res["error"]
            self.update_error(test["status"], test["error"])
            self._test["files"].append(test)
        self._test["status"] = self._status
        self._test["error"] = self._error

    def files_report_console(self):
        title = f'{self._test.get("name", "?")}'

        headers = [
            "file", "method", "tolerance",
            "maxAbs", "maxRel", "maxPower",
            "differences", "total", "error", "status"
        ]

        rows = []
        for f in self._test.get("files", []) or []:
            status_val = f.get("status", "")
            if isinstance(status_val, bool):
                status_val = "OK" if status_val else "FAIL"

            rows.append([
                str(f.get("file", "")),
                str(f.get("method", "")),
                f'{f.get("tolerance", "")}',
                f'{f.get("maxAbs", "")}',
                f'{f.get("maxRel", "")}',
                f'{f.get("maxPower", "")}',
                f'{f.get("differences", "")}',
                f'{f.get("total", "")}',
                str(f.get("error", "")),
                str(status_val),
            ])

        # Compute column widths
        widths = []
        for i, h in enumerate(headers):
            col_values = [h] + [r[i] for r in rows]
            widths.append(max(len(v) for v in col_values))

        def sep():
            return "+-" + "-+-".join("-" * w for w in widths) + "-+"

        def fmt(row):
            return "| " + " | ".join(row[i].ljust(widths[i]) for i in range(len(headers))) + " |"

        lines = []
        lines.append(title)
        lines.append("=" * len(title))
        lines.append(sep())
        lines.append(fmt(headers))
        lines.append(sep())
        for r in rows:
            lines.append(fmt(r))
        lines.append(sep())

        return "\n".join(lines)

    def update_error(self, status, error):
        #New status is True, no need to update
        if status:
            return
        old_status = self._status
        #Updating status if new status is not True
        self._status = False
        #If old status is True, take error
        if old_status:
            self._error = error
            return
        #If old status is False, determine which error is the most important
        #Tolerance has the lowest priority
        #New error is tolerance, old one is not
        if "tolerance" in error and "tolerance" not in self._error:
            return
        #New error is not tolerance, new one is or is not
        if "tolerance" in self._error:
            self._error = error
            return
        #If new error is different, mixed, else, keep the same error
        if self._error != error:
            self._error = "mixed"
        return

    def save_json(self):
        save_json(self._test, "report.json")

    def present_file(self, file):
        return os.path.isfile(file)

    def compare(self, base, test, method, tolerance, rows=None, cols=None):
        c = Compare(base, test, method, tolerance, rows, cols)
        return c.compare()

def main(argv: Optional[Sequence[str]] = None) -> int:
    if argv is None:
        if len(sys.argv) < 2 :
            print("Usage: sqreport [case]")
            exit(1)
    report = SquidientFileReport(sys.argv[1])
    report.run()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: sqreport [case]")
        exit(1)
    report = SquidientFileReport(sys.argv[1])
    report.run()
