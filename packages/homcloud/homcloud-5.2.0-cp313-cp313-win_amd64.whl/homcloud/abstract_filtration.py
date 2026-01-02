import re
import math

from homcloud.pdgm_format import PDGMWriter, BoundaryMapChunk
import homcloud.phat_ext as phat
from homcloud.argparse_common import parse_bool


class AbstractFiltration:
    def __init__(self, boundary_map, dim, levels, symbols, save_boundary_map):
        self.boundary_map = boundary_map
        self.dim = dim
        self.index_to_level = levels
        self.index_to_symbol = symbols
        self.save_boundary_map = save_boundary_map

    def build_phat_matrix(self):
        matrix = phat.Matrix(len(self.boundary_map), "none")
        for n, single in enumerate(self.boundary_map):
            dim = single[0]
            boundary = []
            for idx, coef in zip(single[1], single[2]):
                if coef % 2 != 0:
                    boundary.append(idx)
            matrix.set_dim_col(n, dim, sorted(boundary))

        return matrix

    def compute_pdgm(self, f, algorithm=None, output_suppl_info=True, parallels=None):
        matrix = self.build_phat_matrix()
        matrix.reduce(algorithm)

        writer = PDGMWriter(f, "abstract", self.dim)
        writer.save_pairs(matrix.birth_death_pairs(), self.index_to_level, output_suppl_info)
        if output_suppl_info:
            writer.append_simple_chunk("index_to_level", self.index_to_level)
            writer.append_simple_chunk("index_to_symbol", self.index_to_symbol)

        if self.save_boundary_map:
            writer.append_chunk(BoundaryMapChunk("abstract", self.boundary_map))

        writer.write()


class ParseError(RuntimeError):
    pass


class AbstractFiltrationLoader:
    def __init__(self, io):
        self.io = io
        self.autoid = False
        self.autosymbol = True
        self.nextid = 0
        self.lasttime = -math.inf
        self.boundary_information = []

    @staticmethod
    def load_from(f, save_boundary_map):
        loader = AbstractFiltrationLoader(f)
        loader.load()
        return loader.filtration(save_boundary_map)

    def load(self):
        for line in self.io:
            line = line.strip()
            if line == "" or self.iscomment(line):
                continue
            if self.is_optionline(line):
                self.parse_option(line)
                continue
            self.boundary_information.append(self.parse_line(line))
            self.nextid += 1

    def filtration(self, save_boundary_map):
        symbols = []
        levels = []
        boundary_map = []
        dims = []
        for id, symbol, dim, time, indices, coefs in self.boundary_information:
            symbols.append(symbol)
            levels.append(time)
            dims.append(dim)
            boundary_map.append([dim, indices, coefs])

        return AbstractFiltration(boundary_map, max(dims), levels, symbols, save_boundary_map)

    OPTIONS = [re.compile(r"autoid\s*:"), re.compile(r"autosymbol\s*:")]

    def is_optionline(self, line):
        return any(option.match(line) for option in self.OPTIONS)

    def parse_option(self, line):
        if self.boundary_information:
            raise ParseError("Options must be above boundary information")
        command, _, args = line.lower().partition(":")
        args = args.strip()
        if command == "autoid":
            self.autoid = parse_bool(args)
        if command == "autosymbol":
            self.autosymbol = parse_bool(args)

    @staticmethod
    def iscomment(line):
        return line.startswith("#")

    def parse_line(self, line):
        def check_id(id):
            if id != self.nextid:
                raise ParseError("id must be incremental integers from 0")

        def check_symbol(symbol):
            if not re.match(r"[a-zA-Z0-9_]+\Z", symbol):
                raise ParseError("Invalid cell symbol {}".format(symbol))

        def check_time(time):
            if time < self.lasttime:
                raise ParseError("time must be monotone")
            self.lasttime = time

        if line.count("=") != 1:
            raise ParseError('"=" symbol is required')

        leftstr, rightstr = line.split("=")

        indices, coefs = self.parse_boundary(rightstr)

        left = re.split(r"\s+", leftstr.strip())
        id = self.nextid if self.autoid else int(left.pop(0), 10)
        check_id(id)
        symbol = str(id) if self.autosymbol else left.pop(0)
        check_symbol(symbol)
        dim = int(left.pop(0), 10)
        time = float(left.pop(0))
        check_time(time)
        if left:
            raise ParseError('Too much elements in a line: "{}"'.format(line))

        return id, symbol, dim, time, indices, coefs

    def parse_boundary(self, s):
        def parse_numbers(string):
            if string:
                return [int(n, 10) for n in re.split(r"\s+", string.strip())]
            else:
                return []

        if s.count(":") != 1:
            raise ParseError('":" symbol is required')
        indices_str, coef_str = re.split(r":", s.strip())
        return parse_numbers(indices_str), parse_numbers(coef_str)
