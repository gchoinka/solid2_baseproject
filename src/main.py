import math  # noqa
import multiprocessing
import os
import shutil
import sys
from typing import Iterable, Tuple, Dict, List

from solid2 import cube, linear_extrude, polygon, cylinder, hull, scale, intersection
from solid2.core.object_base import OpenSCADObject
from pathlib import Path

unprintable_thickness = 0.01
preview_fix = 0.05


def cube_example() -> OpenSCADObject:
    return cube()


def stl_task_function(stl_task: Tuple[OpenSCADObject, str]) -> None:
    obj, filename = stl_task
    obj.save_as_stl(filename)


def main(output_scad_basename, output_stl_basename):
    output = [
        (cube_example(), "cube_example"),
    ]

    stl_task: List[Tuple[OpenSCADObject, str]] = []
    all_obj: OpenSCADObject = cube()
    obj_distance = 45
    next_pos = [obj_distance, obj_distance]

    for obj, filename_prefix in output:
        filename = output_scad_basename + filename_prefix + ".scad"
        stl_task.append((obj, output_scad_basename + filename_prefix + ".stl"))
        obj.save_as_scad(filename)
        all_obj += obj.left(next_pos[0]).fwd(next_pos[1])
        next_pos[0] += obj_distance
        next_pos[1] += obj_distance

    filename = output_scad_basename + f"{Path(__file__).stem}_all.scad"
    all_obj.save_as_scad(filename)
    stl_task.append((all_obj, output_scad_basename + f"{Path(__file__).stem}_all.stl"))
    if output_stl_basename is not None:
        with multiprocessing.Pool() as pool:
            pool.map(stl_task_function, stl_task)


if __name__ == "__main__":
    skip_stl: bool = True if len(sys.argv) > 1 and sys.argv[1] == "--fast" else False
    build_path: str = os.path.dirname(os.path.realpath(__file__))
    output_path: str = os.path.abspath(os.path.join(build_path, '..', 'build')) + os.path.sep
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    stl_output_path: str | None = output_path
    if shutil.which("openscad") is None or skip_stl:
        stl_output_path = None
    main(output_scad_basename=output_path, output_stl_basename=stl_output_path)
