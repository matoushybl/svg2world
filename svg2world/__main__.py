import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List, Optional
import math
import pathlib
import argparse

SCALE = 0.2 # distance in meters for svg "pixel"
WALL_HEIGHT = 0.2 # wall height in meters
WALL_THICKNESS = 0.004 # wall thickness in meters

@dataclass(frozen=True)
class Point:
    x: float
    y: float

@dataclass
class Line:
    start: Point
    stop: Point

@dataclass
class SvgMaze:
    origin: Point
    lines: List[Line]

@dataclass(frozen=True)
class GzWall:
    center: Point
    angle: float # in rads
    len: float

@dataclass
class GzMaze:
    walls: List[GzWall]

def parse_svg(file: pathlib.Path) -> SvgMaze: 
    with open(file) as svg_file:
        xml_root = ET.fromstring(svg_file.read())
        origin = None
        lines = []
        for child in xml_root:
            tag_no_ns = child.tag.rsplit('}')[1]
            if tag_no_ns == "ellipse":
                items = dict(child.items())
                origin = Point(float(items["cx"]), float(items["cy"]))
            elif tag_no_ns == "path":
                items = dict(child.items())
                commands = items["d"]
                split_commands = commands.split(" ")

                cmd_iter = iter(split_commands)
                line_origin: Optional[Point] = None
                while True:
                    try:
                        cmd = next(cmd_iter)
                        param = next(cmd_iter)
                        match cmd:
                            case "M":
                                coords = param.split(",")
                                line_origin = Point(float(coords[0]), float(coords[1]))
                            case "m":
                                raise RuntimeError("m command not supported")
                            case "H": 
                                if line_origin is None:
                                    raise RuntimeError("attempted to manipulate path when origin was not defined")
                                x = float(param)
                                end_point = Point(x, line_origin.y)
                                lines.append(Line(line_origin, end_point))
                                line_origin = end_point
                            case "h":
                                if line_origin is None:
                                    raise RuntimeError("attempted to manipulate path when origin was not defined")
                                dx = float(param)
                                end_point = Point(line_origin.x + dx, line_origin.y)
                                lines.append(Line(line_origin, end_point))
                                line_origin = end_point
                            case "V": 
                                if line_origin is None:
                                    raise RuntimeError("attempted to manipulate path when origin was not defined")
                                y = float(param)
                                end_point = Point(line_origin.x, y)
                                lines.append(Line(line_origin, end_point))
                                line_origin = end_point
                            case "v": 
                                if line_origin is None:
                                    raise RuntimeError("attempted to manipulate path when origin was not defined")
                                dy = float(param)
                                end_point = Point(line_origin.x, line_origin.y + dy)
                                lines.append(Line(line_origin, end_point))
                                line_origin = end_point
                            case _:
                                print(cmd)
                                raise RuntimeError(f"unexpected command {cmd}")
                    except StopIteration as e:
                        print(e)
                        break
        if origin is None:
            raise RuntimeError("origin undefined")
        return SvgMaze(origin, lines)

def rotate(pt: Point) -> Point:
    return Point(-pt.y, -pt.x)

def transform_coords(svg: SvgMaze) -> SvgMaze:
    origin = rotate(svg.origin)
    lines = []

    for line in svg.lines:
        lines.append(Line(rotate(line.start), rotate(line.stop)))

    return SvgMaze(origin, lines)


def transform(svg: SvgMaze) -> GzMaze:
    vector = Point(0 - svg.origin.x,0 - svg.origin.y)
    lines = svg.lines.copy()

    for line in lines:
        line.start = Point(line.start.x + vector.x, line.start.y + vector.y)
        line.stop = Point(line.stop.x + vector.x, line.stop.y + vector.y)

    walls = []
    for line in lines:
        angle = 0.0
        if line.stop.x == line.start.x:
            angle = math.pi / 2
        else:
            angle = math.asin((line.stop.y - line.start.y) / (line.stop.x - line.start.x))
        walls.append(
            GzWall(
                center=Point((line.start.x + line.stop.x) / 2 * SCALE, (line.start.y + line.stop.y) / 2 * SCALE), 
                angle=angle,
                len=(math.sqrt((line.stop.x - line.start.x)**2 + (line.stop.y - line.start.y)**2)) * SCALE
            )
        )

    return GzMaze(walls)

def gen_world(maze: GzMaze) -> str:
    file = f"""<?xml version="1.0"?>
<sdf xmlns:xacro="http://www.ros.org/wiki/xacro" version="1.9">
    <xacro:include filename="physics.sdf.xacro"/>
    <xacro:include filename="ground_plane.sdf.xacro"/>
    <xacro:include filename="light.sdf.xacro"/>
    <xacro:include filename="wall.sdf.xacro"/>
    <world name="maze">
        <xacro:physics />
        <xacro:ground_plane />
        <model name="maze">
            <static>true</static>
    """

    for i, wall in enumerate(maze.walls):
        file += f"""
                <xacro:wall 
                    x="{wall.center.x}" 
                    y="{wall.center.y}" 
                    thickness="{WALL_THICKNESS}" 
                    height="{WALL_HEIGHT}" 
                    length="{wall.len}" 
                    yaw="{wall.angle}" 
                    name="wall_{i}" />
        """

    file += f"""
        </model>
        <xacro:light />
    </world>
</sdf>"""

    return file


parser = argparse.ArgumentParser(description="Converts svg maze to gazebo world.")
parser.add_argument("filename", type=str, help="Path to the input SVG")

args = parser.parse_args()

svg_path = pathlib.Path(args.filename)
sdf_path = svg_path.with_suffix(".xacro.sdf")

svg_maze = parse_svg(svg_path)
coord_tf_maze = transform_coords(svg_maze)
maze = transform(coord_tf_maze)
sdf = gen_world(maze)
with open(sdf_path, "w+") as out:
    out.write(sdf)

print("Conversion successful.")
print(f"Maze world was written to {sdf_path}.")
print("Run xacro to generate the raw world file.")
