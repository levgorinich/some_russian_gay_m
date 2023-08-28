from math import sqrt
from typing import Any

import pygame

from Sprites import Hexagon
class HexesGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.hexes_dict =Grid()


    def add(self, *hexes, **kwargs):
        for hex in hexes:
            super().add(hex, **kwargs)  # Add sprite to the standard Group
            cube_pos = hex.offset_to_cube_coords(hex.grid_pos)
            self.hexes_dict[hex] = [hex.grid_pos, cube_pos]  # Add sprite to the lookup dictionary



class KeyAlreadyExistsError(Exception):
    pass
class Grid(dict):
    # """An extension of a basic dictionary with a fast, consistent lookup by value implementation."""
    def __init__(self):
        super().__init__()
        self.key_to_value = {}
        self.value_to_keys = {}

    def __setitem__(self, value: Any, keys: list[Any])  -> None:
        for key in keys:
            if key not in self.key_to_value.keys():
                # print(key, value)
                self.key_to_value[key] = value
                if value in self.value_to_keys:
                    self.value_to_keys[value].append(key)
                else:
                    self.value_to_keys[value] = [key]
            else:
                raise KeyAlreadyExistsError(f"Key '{key}' already exists in the dictionary.")

    def __getitem__(self, key):
        return self.key_to_value.get(key)
    def __len__(self):
        return len(self.key_to_value)
    def __iter__(self):
        return iter(self.key_to_value)

    def get_keys(self, value):
        return self.value_to_keys.get(value, set())






