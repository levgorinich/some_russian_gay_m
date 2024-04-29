import json
from collections import deque, defaultdict

import pygame

from math import *

from game_content.Groups import HexesGroup
from game_content.Sprites import Hexagon, HexagonMountain, HexagonSea, HexagonLand, Town, HexagonEmpty, \
    OffsetCoordinates
from game_content.sprites_factory import HexesFactory


class Map:

    def __init__(self, file_to_load_from, rows=10, columns=10, new=False):

        self.rows = int(rows)
        self.columns = int(columns)
        self.file_to_load_from = file_to_load_from
        self.hexes_factory = HexesFactory()
        self.new = new
        self.hex_width = 30 * sqrt(3)
        self.buildings = []
        # self.hexes   = self.create_tiles()

        if self.new:
            self.hexes = self.create_empty_map()
        else:
            self.hexes = self.load_from_json(self.file_to_load_from)
        self.find_neighbours()
        # self.create_mines()

        # self.spawner = Spawner(self)

    def create_graph(self):
        queue = deque()
        graph = defaultdict(list)
        visited = [[False for _ in range(self.columns)] for _ in range(self.rows)]
        previous = [[None for _ in range(self.columns)] for _ in range(self.rows)]
        for hex in self.hexes:
            if hex.building_on_hex and not visited[hex.grid_pos[0]][hex.grid_pos[1]]:
                visited[hex.grid_pos[0]][hex.grid_pos[1]] = True
                queue.append(hex)

                while queue:
                    cur_hex = queue.popleft()
                    if cur_hex.building_on_hex:
                        prev_hex = self.hexes[previous[cur_hex.grid_pos[0]][cur_hex.grid_pos[1]]]
                        count = 0
                        if prev_hex:
                            while not prev_hex.building_on_hex:
                                count += 1
                                prev_hex = self.hexes[previous[prev_hex.grid_pos[0]][prev_hex.grid_pos[1]]]
                            graph[prev_hex.building_on_hex].append((cur_hex.building_on_hex, count))
                            graph[cur_hex.building_on_hex].append((prev_hex.building_on_hex, count))

                    for neighbour in cur_hex.neighbours:
                        if neighbour.is_road_on_hex() and not visited[neighbour.grid_pos[0]][neighbour.grid_pos[1]]:
                            visited[neighbour.grid_pos[0]][neighbour.grid_pos[1]] = True
                            previous[neighbour.grid_pos[0]][neighbour.grid_pos[1]] = cur_hex.grid_pos
                            queue.append(neighbour)

        print(graph)
        return graph
    def calculate(self):
        self.graph = self.create_graph()
        i = 1
        while i < 100:
            print(i)
            i+=1
            for city, neighbours in self.graph.items():
                neighbours = [neighbour[0] for neighbour in neighbours]
                for neighbour in neighbours:
                    if city.population < neighbour.population:
                        city.population += 1
                        neighbour.population -= 1


    def load_from_json(self, name: str) -> HexesGroup:
        hexes = HexesGroup()
        print("this is file in load from json", name)
        with open("./model_saves/" + name, "r") as f:
            map_json= json.load(f)
            meta_json =map_json["meta_info"]
            self.rows = int(meta_json["rows"])
            self.columns = int(meta_json["columns"])
            hexes_json = map_json["map"]
        for grid_pos, hex_params in hexes_json.items():
            grid_pos = OffsetCoordinates(*list(map(int, grid_pos[1:-1].split(","))))

            hex_created = self.create_hex(hex_params, grid_pos)
            hex_created.draw()
            hexes.add(hex_created)
            if hex_created.building_on_hex:
                self.buildings.append(hex_created)
        return hexes

    def save_to_json(self, ):

        map_dict = {}
        for hex in self.hexes:
            grid_pos, d = hex.save_to_json()
            map_dict[grid_pos] = d
        final_dict = {"meta_info":{"rows":self.rows, "columns" :self.columns}, "map": map_dict}
        with open("./model_saves/" + self.file_to_load_from, "w") as f:
            json.dump(final_dict, f, sort_keys=True, indent=4)

    def create_hex(self, type: str, grid_pos: OffsetCoordinates) -> Hexagon:
        hex_created = self.hexes_factory.create_hex(type, grid_pos)
        return hex_created

    def set_hex(self, hexagon):
        self.hexes[hexagon.grid_pos] = hexagon

    def change_hex(self, hex_type: str, grid_pos: OffsetCoordinates) -> None:
        old_hex = self.hexes[grid_pos]
        hex_created = self.hexes_factory.replace_hex(hex_type, grid_pos, old_hex)

        self.hexes[grid_pos] = hex_created

    def find_neighbours(self, ):
        for hex in self.hexes:
            coords = hex.offset_to_cube_coords(hex.grid_pos)
            hex.neighbours = list(
                filter(None, [self.hexes[tuple(coords + direction)] for direction in hex.directions.values()]))

    def get_hex_by_coord(self, grid_pos: OffsetCoordinates):
        if grid_pos.column in range(0, self.columns + 1) and grid_pos.row in range(0, self.rows + 1):
            return self.hexes[grid_pos]
        return False

    def get_cube_coords(self, hex):
        return self.hexes.get_hex_cube_coords(hex)

    def calculate_distance(self, hex1, hex2):

        cube_coords1 = self.get_cube_coords(hex1)
        cube_coords2 = self.get_cube_coords(hex2)

        return int((abs(cube_coords1[0] - cube_coords2[0]) + abs(cube_coords1[1] - cube_coords2[1]) + abs(
            cube_coords1[2] - cube_coords2[2])) // 2)


    def create_empty_map(self):
        hexes = HexesGroup()
        for i in range(self.rows):
            for j in range(self.columns):
                hexes.add(self.hexes_factory.create_hex("HexagonEmpty", OffsetCoordinates(i, j)))
        return hexes

    def check_coord_validity(self, cords: OffsetCoordinates):
        return 0 <= cords.row < self.rows and 0 <= cords.column < self.columns

    def coordinate_range(self, hex, distance):
        hexes = []
        distance = int(distance)
        qs, rs, ss = map(int, self.get_cube_coords(hex))
        for q in range(qs - distance, qs + distance + 1):

            for r in range(rs - distance, rs + distance + 1):
                for s in range(ss - distance, ss + distance + 1):

                    if q + r + s == 0 and q >= 0 and q < self.columns and r > -self.rows and s <= 0:

                        hex = self.hexes[(q, r, s)]
                        if hex:
                            hexes.append(hex)
        return hexes

    def visualize_parameters(self, parameter: str ):
        for building in self.buildings:
            building.building_on_hex.change_visualization_parameter(parameter)
            building.draw()
    def draw_buildings(self):
        for building in self.buildings:
            building.draw()




    def __str__(self) -> str:
        return f"map with {self.rows} rows and {self.columns} columns"

