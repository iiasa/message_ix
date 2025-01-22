"""Analyse MPS-format files."""

# Written by Marek Makowski, ECE Program of IIASA, in March 2023.

import math
from collections import Counter

import numpy as np
import pandas as pd


class LPdiag:
    """Process the MPS-format input file and provide its basic diagnostics.

    The diagnostics currently include:

    - handling formal errors of the MPS file
    - basic statistics of the matrix coefficients.
    """

    def __init__(self):
        self.fname = "undefined"  # MPS file name, to be defined by read_mps() call
        self.pname = "undefined"  # problem name
        self.id_rhs = False  # True, if rhs_id defined
        self.id_range = False  # True, if range_id defined
        self.id_bnd = False  # True, if bnd_id defined
        self.rhs_id = ""  # id of rhs elements
        self.range_id = ""  # id of ranges elements (might differ from rhs_id)
        self.bnd_id = ""  # id of bounds elements
        self.infty = "none"  # marker for infinity value
        self.n_lines = 0  # number of processed lines of the MPS file
        self.n_rhs = 0  # number of defined RHS
        self.n_ranges = 0  # number of defined ranges
        self.n_bounds = 0  # number of defined bounds
        # if not os.path.exists(self.rep_dir):
        #     os.makedirs(self.rep_dir, mode=0o755)

        # dictionaries for searchable names and its indices
        # (searching very-long lists is prohibitively slow)
        self.row_name = {}  # key: row-name, item: its seq_id
        self.seq_row = {}  # key: row sequence, item: [row-name, lo_bnd, up_bond, type]
        self.col_name = {}  # key: col-name, item: its seq_id
        self.seq_col = {}  # key: col-sequence, item: [col-name, lo_bnd, up_bond]
        # tmp space for reading COLUMN section of the MPS
        self.mat_row = []  # row seq_no of the matrix coef.
        self.mat_col = []  # col seq_no the matrix coef.
        self.mat_val = []  # matrix coeff.
        self.col_curr = ""  # current column (initialized to an illegal empty name)
        self.gf_seq = (
            -1
        )  # sequence_no of the goal function (objective) row: equal = -1, if undefined
        # representation of the LP matrix:
        self.mat = pd.DataFrame(columns=["row", "col", "val"])  # LP matrix
        # cols attributes:
        # self.cols = pd.DataFrame(columns=['seq_id', 'name', 'lo_bnd', 'up_bnd'])
        # rows attributes:
        # self.rows = pd.DataFrame(
        #   columns=['seq_id', 'name', 'type', 'lo_bnd', 'up_bnd']
        # )

    def read_mps(self, fname):
        """Process the MPS file."""
        print(f"\nReading MPS-format file {fname}.")
        self.fname = fname
        sections = [
            "NAME",
            "ROWS",
            "COLUMNS",
            "RHS",
            "RANGES",
            "BOUNDS",
            "SOS",
            "ENDATA",
        ]

        # lists are OK only for small and medium problems
        # row_names = []     # names of rows
        # row_types = []     # types of rows
        # col_names = []     # names of columns

        # wrk vars
        n_section = 0  # seq_no of the currently processed MPS-file section
        next_sect = 0  # seq_no of the next (to be processed) MPS-file section
        # last_sect = -1  # last processed section

        # process the MPS file
        with open(self.fname, "r") as reader:
            for n_line, line in enumerate(reader):
                line = line.rstrip("\n")
                # print(f'line {line}')
                if line[0] == "*" or len(line) == 0:  # skip commented and empty lines
                    continue
                words = line.split()
                if line[0] == " ":  # continue reading the current MPS section
                    # columns/matrix (first here because most frequently used)
                    if n_section == 2:
                        self.add_coeff(words, n_line)  # add column and its coefficients
                    elif n_section == 1:  # rows
                        self.add_row(words, n_line)  # add row and its type
                    elif n_section == 3:  # rhs
                        self.add_rhs(words, n_line)  # process RHS
                    elif n_section == 4:  # ranges
                        self.add_range(words, n_line)  # process range
                    elif n_section == 5:  # bounds
                        self.add_bnd(words, n_line)  # process bound
                    elif n_section == 6:  # SOS section
                        pass  # SOS section not processed
                    # elif n_section == 7:  # end data
                    #     raise RunTimeError(
                    #         "Unexpected execution flow; needs to be explored."
                    #     )
                    else:
                        print(f"MPS record {n_line}, section id {n_section}.")
                        raise RuntimeError(
                            f"MPS line '{line}' (line {n_line}) misplaced,"
                            f" processing section {sections[n_section]}."
                        )
                else:  # found a new section
                    if n_section == 0:  # problem-name processed with the section header
                        pass
                    elif n_section <= 5:
                        # print(f'\tData of section {sections[n_section]} processed.')
                        pass
                    elif n_section == 6:  # SOS
                        print(f"WARNING: Section {sections[n_section]} not processed.")
                    else:
                        raise RuntimeError(
                            f"Should not come here, n_section = {n_section}."
                        )

                    # process the head of new section
                    print(f"Next section found: {line} (line {n_line}).")
                    self.n_lines = n_line
                    # last_sect = n_section
                    n_section = self.next_sec(next_sect, words, sections)
                    next_sect = n_section + 1
                    # print(f'{n_section = }, {next_sect = }')
            # end of MPS reading

        # check, if the last required section ('ENDATA') was defined
        assert n_section == 7, (
            f'The "ENDATA" section is not declared; last section_id = {n_section}.'
        )

        self.mps_sum()  # summarize the processed MPS content

    def next_sec(self, n_exp, words, sections):
        # required/optional MPS sections
        req_sect = [True, True, True, False, False, False, False, True]
        n_line = self.n_lines
        n_words = len(words)
        if req_sect[n_exp]:  # required section must be in the sequence
            # assert (
            #     words[0] == sections[next_sect]
            # ), f"expect section {sections[next_sect]} found: {line}."
            if words[0] == sections[n_exp]:  # required section found
                if n_exp == 0:  # store the problem name
                    assert n_words > 1, (
                        f"problem name undefined: line {n_line} has {n_words} words."
                    )
                    # print(f"\tProblem name line {words[1:]}.")
                    if n_words == 2:
                        self.pname = words[1]  # store the problem name
                    else:
                        self.pname = words[1:]  # store the problem name
                    print(f"\tProblem name: {self.pname}.")
                return n_exp  # n_sections equals to the expected: n_exp
            else:
                print(f"section {words} found.")
                raise NameError(
                    f"Required MPS section {sections[n_exp]} undefined or misplaced."
                )
        else:  # the found section does not follow the last processed section
            try:
                n_section = sections.index(words[0])
            except ValueError as e:
                raise ValueError(f"Unknown section: {words} (line {n_line}).") from e
            if n_section < n_exp:
                raise AttributeError(
                    f"Section {words[0]} (line {n_line}) is misplaced or duplicated."
                )
            return n_section

    def mps_sum(self):
        # check, if there was at least one N row
        # (the first N row assumed to be the objective):
        assert self.gf_seq != -1, "objective (goal function) row is undefined."

        # create a df with the matrix coefficients
        self.mat = pd.DataFrame(
            {"row": self.mat_row, "col": self.mat_col, "val": self.mat_val}
        )
        self.mat["abs_val"] = abs(
            self.mat["val"]
        )  # add column with absolute values of coeff.
        self.mat["log"] = np.log10(self.mat["abs_val"]).astype(
            int
        )  # add col with int(log10(coeffs))
        # print(f'matrix after initialization:\n {self.mat}')

        # Finish the MPS processing with the summary of its attributes
        dens = f"{float(len(self.mat)) / (len(self.row_name) * len(self.col_name)):.2e}"
        print(
            f"\nFinished processing {self.n_lines} lines of the MPS file: {self.fname}."
        )
        print(
            f"LP has: {len(self.row_name)} rows, {len(self.col_name)} cols,"
            f" {len(self.mat)} non-zeros, matrix density = {dens}."
        )
        print(
            f"Numbers of redefined: RHS = {self.n_rhs}, ranges = {self.n_ranges},"
            f" bounds = {self.n_bounds}."
        )

        # todo: add info on dense rows and cols

        # info on the GF row, RHS, ranges, bounds
        df = self.mat.loc[self.mat["row"] == self.gf_seq][
            "val"
        ]  # df with values of the GF coefficients.
        print(
            f'\nThe GF (objective) row named "{self.seq_row.get(self.gf_seq)[0]}" has'
            f" {len(df)} elements."
        )
        print(f"Distribution of the GF (objective) values:\n{df.describe()}")

    def add_row(self, words: list[str], n_line: int):
        """Process current line of the ROWS section.

        While processing the ROWS section the row attributes are initialized to the
        default (for the corresponding row type) values. The attributes are updated for
        optionally defined values in the (also optional) RHS and RANGES sections. The
        interpretation of the MPS-format (in particular of values in the RANGES section)
        follows the original MPS standard, see e.g., "Advanced Linear Programming," by
        Bruce A. Murtagh. or the standard summary at
        https://lpsolve.sourceforge.net/5.5/mps-format.htm .

        Parameters
        ----------
        words : str
            Words of the current line.
        n_line : int
            Sequence number of the current MPS line.
        """

        row_types = ["N", "E", "G", "L"]  # types of rows
        n_words = len(words)
        assert n_words == 2, (
            f"row declaration (line {n_line}) has {n_words} words instead of 2."
        )
        row_type = words[0]
        row_name = words[1]
        row_seq = len(self.row_name)
        assert row_type in row_types, f"unknown row type {row_type} (line {n_line})."
        assert row_name not in self.row_name, (
            f"duplicated row name: {row_name} (line {n_line})."
        )
        if row_type == "N" and self.gf_seq == -1:
            self.gf_seq = row_seq
            print(
                f"\tRow {row_name} (row_seq = {row_seq}) is the objective"
                " (goal function) row."
            )
        self.row_name.update({row_name: row_seq})  # add to dict of row_names
        # store row_{seq, name, type} and the default
        # (to be changed in rhs/ranges) [lo_bnd, upp_bnd]
        self.row_att(row_seq, row_name, row_type, "rows")

    def add_coeff(self, words: list[str], n_line: int):
        """Process current line of the COLUMNS section.

        The section defines both column names and values of the matrix coefficients.
        One line can have either one or two matrix elements.

        Parameters
        ----------
        words : str
            Words of the current line.
        n_line : int
            Sequence number of the current MPS line.
        """

        n_words = len(words)
        # print(
        #     f"processing line no {n_line}, n_words {n_words}:"
        #     f" {line}"
        # )
        assert n_words in [
            3,
            5,
        ], f"matrix element (line {n_line}) has {n_words} words."
        col_name = words[0]
        if col_name != self.col_curr:  # new column
            assert col_name not in self.col_name, (
                f"duplicated column name: {col_name} (line {n_line})"
            )
            col_seq = len(self.col_name)
            self.col_name.update({col_name: col_seq})
            self.seq_col.update({col_seq: [col_name, 0.0, self.infty]})
            self.col_curr = col_name
        else:
            col_seq = self.col_name.get(col_name)
        row_name = words[1]
        row_seq = self.row_name.get(row_name)
        assert row_seq is not None, f"unknown row name {row_name} (line {n_line})."
        try:
            val = float(words[2])
        except ValueError as e:
            raise ValueError(
                f"string {words[2]} (line {n_line}) is not a number."
            ) from e
        # add the matrix element to the lists of: seq_row, seq_col, val
        # the lists will be converted to self.mat df after all elements
        # will be read
        self.mat_row.append(row_seq)
        self.mat_col.append(col_seq)
        self.mat_val.append(val)
        # print(f' matrix element ({row_seq}, {col_seq}) = {val}')
        # the next two commands take far too long for large matrices;
        # thus tmp-store in three lists
        # df2 = pd.DataFrame(
        #     {"row": row_seq, "col": col_seq, "val": val},
        #     index=list(range(1)),
        # )
        # self.mat = pd.concat(
        #     [self.mat, df2],
        #     axis=0,
        #     ignore_index=True
        # )

        # proccess the second matrix element in the same MPS row, if defined
        if n_words > 3:
            assert n_words == 5, (
                f"line {n_line}) has {n_words} words, five words needed for defining "
                "second element in the same MPS line."
            )
            row_name = words[3]
            row_seq = self.row_name.get(row_name)
            assert row_seq is not None, f"unknown row name {row_name} (line {n_line})."
            try:
                val = float(words[4])
            except ValueError as e:
                raise ValueError(
                    f"string {words[4]} (line {n_line}) is not a number."
                ) from e
            self.mat_row.append(row_seq)
            self.mat_col.append(col_seq)
            self.mat_val.append(val)

    def add_rhs(self, words: list[str], n_line: int):
        """Process current line of the RHS section.

        The section defines both column names and values of the matrix coefficients.
        One line can have either one or two matrix elements.

        Parameters
        ----------
        words : str
            Words of the current line.
        n_line : int
            Sequence number of the current MPS line.
        """

        n_words = len(words)

        # first RHS record implies RHS/ranges id (might be empty)
        if self.n_rhs == 0:
            # print(f"first rhs line: {n_line}: '{words}'")
            if n_words in [3, 5]:  # RHS name/id defined
                self.id_rhs = True
                self.rhs_id = words[0]
                print(f"\tId of RHS: {self.rhs_id}")
            else:
                self.id_rhs = False
                self.rhs_id = ""
                print("\tId of RHS: (empty)")

        if self.id_rhs:
            n_req_wrd = [3, 5]  # number of required words in a line (either 3 or 5)
            pos_name = 1  # first row-name in words[pos_name]
        else:
            n_req_wrd = [2, 4]
            pos_name = 0  # first row-name in words[pos_name]

        assert n_words in n_req_wrd, (
            f"rhs line {n_line} has {n_words} words, expected {n_req_wrd}."
        )
        if self.id_rhs:  # check id of the RHS entry, if it was defined
            assert words[0] == self.rhs_id, (
                f"RHS id {words[0]}, line {n_line} differ from expected: {self.rhs_id}."
            )
        row_name = words[pos_name]
        row_seq = self.row_name.get(row_name)
        assert row_seq is not None, f"unknown RHS row-name {row_name} (line {n_line})."
        try:
            val = float(words[pos_name + 1])
        except ValueError as e:
            raise ValueError(
                f"RHS value {words[pos_name + 1]} (line {n_line}) is not a number."
            ) from e
        attr = self.seq_row.get(row_seq)  # [row_name, lo_bnd, up_bnd, row_type]
        row_type = attr[3]
        self.row_att(row_seq, row_name, row_type, "rhs", val)
        self.n_rhs += 1
        if n_words == n_req_wrd[1]:  # second pair of rhs defined
            row_name = words[pos_name + 2]
            row_seq = self.row_name.get(row_name)
            assert row_seq is not None, (
                f"unknown RHS row-name {row_name} (line {n_line})."
            )
            try:
                val = float(words[pos_name + 3])
            except ValueError as e:
                raise ValueError(
                    f"RHS value {words[pos_name + 3]} (line {n_line}) is not a number."
                ) from e
            attr = self.seq_row.get(row_seq)  # [row_name, lo_bnd, up_bnd, row_type]
            row_type = attr[3]
            self.row_att(row_seq, row_name, row_type, "rhs", val)
            self.n_rhs += 1

    def add_range(self, words: str, n_line: int):
        """Process current line of the RANGES section.

        The section defines both column names and values of the matrix coefficients.
        One line can have either one or two matrix elements.

        Parameters
        ----------
        words : str
            Words of the current line.
        n_line : int
            Sequence number of the current MPS line.
        """

        n_words = len(words)

        # first ranges record implies ranges id (might be empty)
        if self.n_ranges == 0:
            if n_words in [3, 5]:
                self.id_range = True
                self.range_id = words[0]
                print(f"\tId of ranges: {self.range_id}")
            else:
                self.id_range = False
                self.range_id = ""
                print("\tId of ranges: (empty)")

        if self.id_range:
            n_req_wrd = [3, 5]  # number of required words in a line (either 3 or 5)
            pos_name = 1  # first row-name in words[pos_name]
        else:
            n_req_wrd = [2, 4]
            pos_name = 0  # first row-name in words[pos_name]

        assert n_words in n_req_wrd, (
            f"ranges line {n_line} has {n_words} words, expected {n_req_wrd}."
        )
        if self.id_range:  # check id of the ranges' entry, if it was defined
            assert words[0] == self.range_id, (
                f"Ranges id {words[0]}, line {n_line} differ from"
                f" expected: {self.range_id}."
            )
        row_name = words[pos_name]
        row_seq = self.row_name.get(row_name)
        assert row_seq is not None, (
            f"unknown range row-name {row_name} (line {n_line})."
        )
        try:
            val = float(words[pos_name + 1])
        except ValueError as e:
            raise ValueError(
                f"Range value {words[pos_name + 1]} (line {n_line}) is not a number."
            ) from e
        attr = self.seq_row.get(row_seq)  # [row_name, lo_bnd, up_bnd, row_type]
        row_type = attr[3]
        self.row_att(row_seq, row_name, row_type, "ranges", val)
        self.n_ranges += 1
        if n_words == n_req_wrd[1]:  # second pair of ranges defined
            row_name = words[pos_name + 2]
            row_seq = self.row_name.get(row_name)
            assert row_seq is not None, (
                f"unknown ranges row-name {row_name} (line {n_line})."
            )
            try:
                val = float(words[pos_name + 3])
            except ValueError as e:
                raise ValueError(
                    f"Range value {words[pos_name + 3]} (line {n_line}) is not a "
                    "number."
                ) from e
            attr = self.seq_row.get(row_seq)  # [row_name, lo_bnd, up_bnd, row_type]
            row_type = attr[3]
            self.row_att(row_seq, row_name, row_type, "ranges", val)
            self.n_ranges += 1

    def add_bnd(self, words: list[str], n_line: int):
        """Process current line of the BOUNDS section.

        The section defines both column names and values of the matrix coefficients.
        One line can have either one or two matrix elements.

        Parameters
        ----------
        words : str
            Words of the current line.
        n_line : int
            Sequence number of the current MPS line.
        """

        # items of the below dictionaries indicate bounds to be modified:
        # 1 - low, 2 - upper, 3 - both
        bnd_type1 = {"LO": 1, "UP": 2, "FX": 3}  # types of bounds requiring value
        bnd_type2 = {"MI": 1, "PL": 2, "FR": 3}  # types of bounds not requiring value
        bnd_type3 = {
            "BV": 0,
            "LI": 0,
            "UI": 0,
            "SC": 0,
        }  # types of bounds legal for int-type vars, not processed yet

        n_words = len(words)

        # first Bounds record implies bounds id (might be empty)
        if self.n_bounds == 0:
            # print(f"first BOUNDS line: {n_line}: '{words}'")
            if n_words == 4 or (n_words == 3 and words[0] in ["FR", "MI", "PL"]):
                self.id_bnd = True
                self.bnd_id = words[1]
                print(f"\tId of BOUNDS: {self.bnd_id}")
            else:
                self.id_bnd = False
                self.bnd_id = ""
                print("\tId of BOUNDS: (empty)")

        # number of required words in a line (with/without) required value:
        if self.id_bnd:
            n_req_wrd = [4, 3]
            pos_name = 2  # col-name in words[pos_name]
        else:
            n_req_wrd = [3, 2]
            pos_name = 1  # col-name in words[pos_name]

        assert n_words in n_req_wrd, (
            f"bounds line {n_line} has {n_words} words, expected: {n_req_wrd}."
        )
        if self.id_bnd:  # check id of the BOUNDS line, if it was defined
            assert words[1] == self.bnd_id, (
                f"BOUNDS id {words[1]}, line {n_line} differ from "
                f"expected id: {self.bnd_id}."
            )
        col_name = words[pos_name]
        col_seq = self.col_name.get(col_name)
        assert col_seq is not None, (
            f"unknown BOUNDS col-name {col_name} (line {n_line})."
        )
        attr = self.seq_col.get(col_seq)  # [col_name, lo_bnd, up_bnd]

        typ = words[0]
        if typ in bnd_type1:  # bound-types that require a value
            try:
                val = float(words[pos_name + 1])
            except ValueError as e:
                raise ValueError(
                    f"BOUND value {words[pos_name + 1]} (line {n_line}) is not a "
                    "number."
                ) from e
            at_pos = bnd_type1.get(typ)
            if at_pos == 3:  # set both bounds
                attr[1] = attr[2] = val
            else:
                attr[at_pos] = val
        elif typ in bnd_type2:  # value not needed;
            # therefore it is neither checked nor processed
            at_pos = bnd_type2.get(typ)
            if at_pos == 3:  # set both bounds
                attr[1] = attr[2] = self.infty
            else:
                attr[at_pos] = self.infty
        elif typ in bnd_type3:
            raise TypeError(
                f"Bound type {typ} of integer var. (line {n_line}) not processed yet."
            )
        else:
            raise TypeError(f"Unknown bound type {typ} (line {n_line}).")
        self.seq_col.update({col_seq: attr})  # store the updated col-attributes
        self.n_bounds += 1

    def row_att(
        self,
        row_seq: int,
        row_name: str,
        row_type: str,
        sec_name: str,
        val: float = 0.0,
    ):
        """Process values defined in ROWS, RHS and RANGES sections

        The corresponding row attributes are stored or updated.

        While processing the ROWS section the row attributes are initialized to the
        default (for the corresponding row type) values. The attributes are updated for
        optionally defined values in the (also optional) RHS and RANGES sections. The
        interpretation of the MPS-format (in particular of values in the RANGES section)
        follows the original MPS standard, see e.g., "Advanced Linear Programming," by
        Bruce A. Murtagh. or the standard summary at
        https://lpsolve.sourceforge.net/5.5/mps-format.htm .

        Parameters
        ----------
        row_seq : int
            Position of row in dictionaries and the matrix df.
        row_name : str
            Row name (defined in the ROWS section).
        row_type : str
            Row type (defined in the ROWS section).
        sec_name : str
            Identifies the MPS section: either 'rows' (for initialization) or 'rhs' or
            'ranges' (for updates).
        val: float
            Value of the row attribute defining either lo_bnd or up_bnd of the row
            (the type checked while processing the MPS section).
        """

        type2bnd = {
            "E": [0.0, 0.0],
            "G": [0.0, self.infty],
            "L": [self.infty, 0.0],
            "N": [self.infty, self.infty],
        }
        assert row_seq == self.row_name.get(row_name), (
            f"{row_seq=} should be equal to: {self.row_name.get(row_name)}."
        )
        assert row_type in type2bnd, f"undefined row type {row_type=} for {row_name=}."
        if sec_name == "rows":  # initialize row attributes (used in ROW section)
            low_upp = type2bnd[row_type]
            self.seq_row.update({row_seq: [row_name, low_upp[0], low_upp[1], row_type]})
            # print(
            #     f"attributes of row {row_name} initialized in section {sec_name} to"
            #     f"{self.seq_row.get(row_seq)}."
            # )
        elif sec_name in [
            "rhs",
            "ranges",
        ]:  # update row attributes (used in RHS and ranges sections)
            if row_type == "N":
                print(f"{sec_name} value {val} ignored for neutral row {row_name}.")
                return
            attr = self.seq_row.get(row_seq)  # [row_name, lo_bnd, up_bnd, row_type]
            if sec_name == "rhs":  # process the RHS value
                if row_type == "G":  # update lo_bnd
                    attr[1] = val
                elif row_type == "L":  # update up_bnd
                    attr[2] = val
                elif row_type == "E":  # update both bounds
                    attr[1] = attr[2] = val
            else:  # process the ranges value
                if row_type == "G":  # update up_bnd
                    attr[2] = attr[1] + abs(val)
                elif row_type == "L":  # update lo_bnd
                    attr[1] = attr[2] - abs(val)
                elif row_type == "E":  # update both bounds
                    if val > 0:
                        attr[2] = attr[1] + val
                    else:
                        attr[1] = attr[2] - abs(val)
            self.seq_row.update({row_seq: attr})
            # print(
            #     f"attributes of row {row_name} updated in section {sec_name} to"
            #     f" {attr}."
            # )
        else:  # update row attributes (used in RHS and ranges sections)
            raise SyntaxError(f"row_att() should not be called for {sec_name=}.")

    def print_statistics(self, lo_tail: int = -7, up_tail: int = 6):
        """Basic statistics of the matrix coefficients.

        Focus on distributions of magnitudes of non-zero coefficients represented by
        values of int(log10(abs(coeff))). Additionally, tails (low and upp) of the
        distributions are reported.

        Parameters
        ----------
        lo_tail: int
            Magnitude order of the low-tail (-7 denotes values < 10^(-6)).
        up_tail: int
            Magnitude order of the upper-tail (6 denotes values >= 10^6).
        """

        # print(f'\nDistribution of non-zero values:\n{self.mat["val"].describe()}')
        print(
            f"\nDistribution of abs(non-zero) values:\n{self.mat['abs_val'].describe()}"
        )
        print(
            f"\nDistribution of int(log10(abs(values))):\n{self.mat['log'].describe()}"
        )
        min_logv = self.mat["log"].min()
        max_logv = self.mat["log"].max()

        # count numbers of coeffs for each order of magnitude of their value
        distribution_magnitude_counter = Counter(self.mat["log"])
        distribution_magnitudes = dict(
            sorted(distribution_magnitude_counter.items())
        )  # counter (sorted by occurances) --> dict sorted by magnitudes
        print(
            "\nDistribution of int(log10(abs(values))) sorted by magnitudes of values:"
        )
        print(
            f"range = [{min_logv}, {max_logv}] (magnitudes with zero-occurrences"
            " skipped)."
        )
        for magn in distribution_magnitudes:
            print(f"{magn:3d}: {distribution_magnitudes[magn]:7d}")

        if lo_tail > up_tail:
            print(f"Overlapping distribution tails ({lo_tail}, {up_tail}) reset to 0.")
            lo_tail = up_tail = 0

        # low-tail of the distribution
        if lo_tail < min_logv:
            print(
                f"\nNo log10(values) in the requested low-tail (<= {lo_tail}) of the"
                " distribution."
            )
        else:
            print(
                "\nDistribution of log10(values) in the requested low-tail (<="
                f" {lo_tail}) of the distribution."
            )
            print(f"{self.mat.loc[self.mat['log'] <= lo_tail].describe()}")
            for val in [*range(min_logv, lo_tail + 1)]:
                print(
                    f"Number of log10(values) == {val}:"
                    f" {self.mat.loc[self.mat['log'] == val]['log'].count()}"
                )
        # up-tail of the distribution
        if max_logv < up_tail:
            print(
                f"\nNo log10(values) in the requested upper-tail (>= {up_tail}) of the"
                " distribution."
            )
        else:
            print(
                "\nDistribution of log10(values) in the requested upp-tail (>="
                f" {up_tail}) of the distribution."
            )
            print(f"{self.mat.loc[self.mat['log'] >= up_tail].describe()}")
            for val in [*range(up_tail, max_logv + 1)]:
                print(
                    f"Number of log10(values) == {val}:"
                    f" {self.mat.loc[self.mat['log'] == val]['log'].count()}"
                )

    def locate_outliers(self, small: bool = True, thresh: int = -7, max_rec: int = 500):
        """Locations of outliers, i.e., elements having small/large coefficient values.

        Locations of outliers (in the term of the matrix coefficient values). The
        provided ranges of values in the corresponding row/col indicate potential of the
        simple scaling.

        Parameters
        ----------
        small : bool
            True/False for threshold of either small or large coefficients
        thresh : int
            Magnitude of the threshold (in: int(log10(abs(coeff))), i.e. -7 denotes
            values < 10^(-6)).
        max_rec : int
            Maximum number of processed coefficients.
        """

        if small:  # sub-matrix composed of only small-value outliers
            df = self.mat.loc[self.mat["log"] <= thresh]
            print(
                f"\nRow-wise locations of {df['log'].count()} outliers (coeff. with"
                f" values of log10(values) <= {thresh})."
            )
        else:  # large-value outliers
            df = self.mat.loc[self.mat["log"] >= thresh]
            print(
                f"\nRow-wise locations of {df['log'].count()} outliers (coeff. with"
                f" values of log10(values) >= {thresh})."
            )
        df1 = df.sort_values(
            "row"
        )  # sort the df with outliers ascending seq_id of rows
        df1.reset_index()
        col_out = []  # col_seq of outliers' cols
        for n_rows, (_, row) in enumerate(df1.iterrows()):
            assert n_rows < max_rec, (
                "To process all requested coeffs modify the safety limit assertion."
            )
            row_seq, row_name = self.get_entity_info(
                row, True
            )  # row seq_id and name of the current coeff.
            col_seq, col_name = self.get_entity_info(
                row, False
            )  # col seq_id and name of the current coeff.
            if col_seq not in col_out:
                col_out.append(col_seq)
            else:
                print(f"{col_seq = } already in another outlier row.")
            print(
                f"Coeff. ({row_seq}, {col_seq}): val = {row['val']:.4e}, log(val) ="
                f" {row['log']:n}"
            )
            df_row_out = df1.loc[df1["row"] == row_seq]  # df with only outlier elements
            df_row_all = self.mat.loc[
                self.mat["row"] == row_seq
            ]  # df with all elements
            # print(f'matrix elements in the same row:\n{df_row}')
            print(
                f"\tRow {row_name} {self.get_entity_range(row_seq, True)} has"
                f" {df_row_out['log'].count()} outlier-coeff. of magnitudes in"
                f" [{df_row_out['log'].min()}, {df_row_out['log'].max()}]"
            )
            print(
                f"\tRow {row_name} {self.get_entity_range(row_seq, True)} has"
                f" {df_row_all['log'].count()} (all)-coeff. of magnitudes in"
                f" [{df_row_all['log'].min()}, {df_row_all['log'].max()}]"
            )
            # a column may include more than 1 outlier;
            # therefore columns with outliers reported below:
            # df with outliers in the same col:
            # df_col = df1.loc[df1['col'] == col_seq]
            # print(
            #     f"\tCol {col_name} {self.get_entity_range(col_seq, False)} has "
            #     f"{df_col["log"].count()} outlier coeff. of magnitudes in "
            #     f"[{df_col["log"].min()}, {df_col["log"].max()}]"
            # )
        print(
            "\nColumn-wise locations of outlier coefficients in"
            f" {len(col_out)} columns:"
        )
        col_out.sort()
        for col_seq in col_out:
            col_name = self.seq_col.get(col_seq)[0]
            df_col = self.mat.loc[
                self.mat["col"] == col_seq
            ]  # df with elements in the same col
            print(
                f"\tCol {col_name} {self.get_entity_range(col_seq, False)} has"
                f" {df_col['log'].count()} coeff. of magnitudes in"
                f" [{df_col['log'].min()}, {df_col['log'].max()}]"
            )

    def get_entity_info(
        self, mat_row: pd.Series, by_row: bool = True
    ) -> tuple[int, str]:
        """Return info on the entity (row or col) defining the given matrix coefficient.

        Each row of the dataFrame contains the definition (composed of the row_seq,
        col_seq, value, log(value)) of one matrix coefficient. The function returns
        seq_id and name of either row or col of the currently considered coeff.

        Parameters
        ----------
        mat_row : pandas.Series
            Record of the df with the data of currently processed element.
        by_row : bool
            True/False for returning the seq_id and name of the corresponding row/col.
        """

        if by_row:
            # if seq_row {} not stored, then:
            # names = [k for k, idx in self.row_name.items() if idx == ent_seq]
            ent_seq = int(mat_row["row"])
            name = self.seq_row.get(ent_seq)[0]
        else:
            ent_seq = int(mat_row["col"])
            name = self.seq_col.get(ent_seq)[0]
        return ent_seq, name

    def get_entity_range(self, seq_id: int, by_row: bool = True) -> str:
        """Return formatted ranges of feasible values of either a row or a column.

        The returned values of ranges are either 'none' (for plus/minus infinity) or
        int(log10(abs(val))) for other values. Small values, defined as
        abs(value) < 1e-10, are represented by 0.

        Parameters
        ----------
        seq_id : int
            Sequence number of either row or col.
        by_row : bool
            True/False for returning the seq_id and name of the corresponding row/col.
        """

        if by_row:
            attr = self.seq_row.get(seq_id)  # [row_name, lo_bnd, up_bnd, row_type]
            pass
        else:
            attr = self.seq_col.get(seq_id)  # [col_name, lo_bnd, up_bnd]
            pass
        s = []  # strings representing lo/up-bounds
        for pos in [0, 1]:
            val = attr[pos + 1]  # 0-th element is the name
            if val == self.infty:  # used for both infinites (positive and negative)
                s.append(self.infty)
            else:
                if isinstance(val, int):
                    val = float(val)
                if abs(val) < 1e-10:
                    s.append("0")  # same string for int and float zeros
                else:
                    val = int(math.log10(abs(val)))
                    s.append(f"{val}")  # small integer value, no formatting needed
        ret = "[" + s[0] + ", " + s[1] + "]"
        return ret  # the range is formatted as: '[lo_bnd, up_bnd]'

    def plot_hist(self):
        """Plot histograms.

        .. note:: Not implemented.
        """
        raise NotImplementedError
