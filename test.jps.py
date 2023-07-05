#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

map_test = [[0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0]]

g_dir = [[1, 0], [0, 1], [0, -1], [-1, 0], [1, 1], [1, -1], [-1, 1], [-1, -1]]


class Node:
    def __init__(self, parent, pos, g, h):
        self.parent = parent
        self.pos = pos
        self.g = g
        self.h = h
        self.f = g + h

    def get_direction(self):
        return self.parent and [
            self.pos[0] != self.parent.pos[0] and (self.pos[0] - self.parent.pos[0]) // abs(
                self.pos[0] - self.parent.pos[0]) or 0,
            self.pos[1] != self.parent.pos[1] and (self.pos[1] - self.parent.pos[1]) // abs(
                self.pos[1] - self.parent.pos[1]) or 0] or [0, 0]


class JPS:
    def __init__(self, width, height):
        self.s_pos = None
        self.e_pos = None

        self.width = width
        self.height = height
        self.open = []
        self.close = []
        self.path = []

    def prune_neighbours(self, c):
        nbs = []
        if c.parent:
            dir = c.get_direction()
            if self.is_pass(c.pos[0] + dir[0], c.pos[1] + dir[1]):
                nbs.append([c.pos[0] + dir[0], c.pos[1] + dir[1]])
            if dir[0] != 0 and dir[1] != 0:
                if self.is_pass(c.pos[0], c.pos[1] + dir[1]):
                    nbs.append([c.pos[0], c.pos[1] + dir[1]])
                if self.is_pass(c.pos[0] + dir[0], c.pos[1]):
                    nbs.append([c.pos[0] + dir[0], c.pos[1]])
                if not self.is_pass(c.pos[0] - dir[0], c.pos[1]) and self.is_pass(c.pos[0], c.pos[1] + dir[1]):
                    nbs.append([c.pos[0] - dir[0], c.pos[1] + dir[1]])
                if not self.is_pass(c.pos[0] + dir[0], c.pos[1]) and self.is_pass(c.pos[0] + dir[0], c.pos[1] - dir[1]):
                    nbs.append([c.pos[0] + dir[0], c.pos[1] - dir[1]])
            else:
                if dir[0] == 0:
                    if self.is_pass(c.pos[0] + 1, c.pos[1]):
                        nbs.append([c.pos[0] + 1, c.pos[1]])
                    if self.is_pass(c.pos[0] - 1, c.pos[1]):
                        nbs.append([c.pos[0] - 1, c.pos[1]])
                    if not self.is_pass(c.pos[0] - 1, c.pos[1]) and self.is_pass(c.pos[0], c.pos[1] + 1):
                        nbs.append([c.pos[0] - 1, c.pos[1] + 1])
                    if not self.is_pass(c.pos[0] - 1, c.pos[1]) and self.is_pass(c.pos[0], c.pos[1] - 1):
                        nbs.append([c.pos[0] - 1, c.pos[1] - 1])
                else:
                    if self.is_pass(c.pos[0], c.pos[1] + 1):
                        nbs.append([c.pos[0], c.pos[1] + 1])
                    if self.is_pass(c.pos[0], c.pos[1] - 1):
                        nbs.append([c.pos[0], c.pos[1] - 1])
                    if not self.is_pass(c.pos[0], c.pos[1] - 1) and self.is_pass(c.pos[0] + 1, c.pos[1]):
                        nbs.append([c.pos[0] + 1, c.pos[1] - 1])
                    if not self.is_pass(c.pos[0], c.pos[1] - 1) and self.is_pass(c.pos[0] - 1, c.pos[1]):
                        nbs.append([c.pos[0] - 1, c.pos[1] - 1])
        else:
            for d in g_dir:
                if self.is_pass(c.pos[0] + d[0], c.pos[1] + d[1]):
                    nbs.append([c.pos[0] + d[0], c.pos[1] + d[1]])
        return nbs

    def is_pass(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height and map_test[y][x] == 0

    def get_distance(self, pos):
        return abs(pos[0] - self.e_pos[0]) + abs(pos[1] - self.e_pos[1])

    def get_successors(self, c):
        nbs = self.find_neighbours(c)
        succs = []
        for n in nbs:
            jump_node = self.jump(n[0], n[1], c.pos[0], c.pos[1])
            if jump_node:
                succs.append(jump_node)
        return succs

    def find_neighbours(self, c):
        nbs = []
        for d in g_dir:
            x = c.pos[0] + d[0]
            y = c.pos[1] + d[1]
            if self.is_pass(x, y):
                nbs.append([x, y])
        return nbs

    def jump(self, x, y, px, py):
        dx = x - px
        dy = y - py
        if not self.is_pass(x, y):
            return None
        if [x, y] == self.e_pos:
            return Node(None, [x, y], 0, 0)
        if dx != 0 and dy != 0:
            if (self.is_pass(x - dx, y + dy) and not self.is_pass(x - dx, y)) or (
                    self.is_pass(x + dx, y - dy) and not self.is_pass(x, y - dy)):
                return Node(None, [x, y], 1, self.get_distance([x, y]))
        else:
            if dx != 0:
                if (self.is_pass(x + dx, y + 1) and not self.is_pass(x, y + 1)) or (
                        self.is_pass(x + dx, y - 1) and not self.is_pass(x, y - 1)):
                    return Node(None, [x, y], 1, self.get_distance([x, y]))
            else:
                if (self.is_pass(x + 1, y + dy) and not self.is_pass(x + 1, y)) or (
                        self.is_pass(x - 1, y + dy) and not self.is_pass(x - 1, y)):
                    return Node(None, [x, y], 1, self.get_distance([x, y]))
        if dx != 0 and dy != 0:
            jx = self.jump(x + dx, y, x, y)
            jy = self.jump(x, y + dy, x, y)
            if jx or jy:
                return Node(None, [x, y], 1, self.get_distance([x, y]))
        if self.is_pass(x + dx, y) or self.is_pass(x, y + dy):
            return self.jump(x + dx, y + dy, x, y)
        return None

    def search(self, s_pos, e_pos):
        self.s_pos = s_pos
        self.e_pos = e_pos
        start = Node(None, self.s_pos, 0, self.get_distance(self.s_pos))
        self.open.append(start)
        while len(self.open) > 0:
            c = self.open.pop(0)
            self.close.append(c)
            if c.pos == self.e_pos:
                self.path = []
                while c:
                    self.path.append(c.pos)
                    c = c.parent
                self.path.reverse()
                return self.path
            succs = self.get_successors(c)
            for s in succs:
                if s in self.close:
                    continue
                new_g = c.g + self.get_distance(s.pos)
                i = self.in_open(s)
                if i != -1:
                    if new_g < self.open[i].g:
                        self.open[i].g = new_g
                        self.open[i].f = new_g + self.open[i].h
                        self.open[i].parent = c
                else:
                    s.g = new_g
                    s.h = self.get_distance(s.pos)
                    s.f = s.g + s.h
                    s.parent = c
                    self.open.append(s)
            self.open.sort(key=lambda x: x.f)
        return []

    def in_open(self, node):
        for i in range(len(self.open)):
            if node.pos == self.open[i].pos:
                return i
        return -1


def main():
    jps = JPS(len(map_test[0]), len(map_test))
    start_pos = [0, 0]
    end_pos = [6, 6]
    path = jps.search(start_pos, end_pos)
    if path:
        print("Path found:")
        for pos in path:
            print(pos)
    else:
        print("No path found.")


if __name__ == '__main__':
    main()
