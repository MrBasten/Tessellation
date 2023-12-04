"""Набор утилит для работы модуля тесселляции.
"""
import os
import sys
import subprocess
import shutil
from typing import Union
from argparse import Namespace

import trimesh
import pycork
import numpy as np
import pyacvd
from pyvista import helpers


def trimesh_repair(mesh: trimesh.base.Trimesh) -> None:
    """Several trimesh repair fixes for obj model.

    Args:
        mesh (trimesh.base.Trimesh): Input mesh object.
    """
    trimesh.repair.fix_normals(mesh)
    trimesh.repair.fill_holes(mesh)
    trimesh.repair.broken_faces(mesh)


def load_trimesh_obj(path: Union[str, os.PathLike]) -> trimesh.Trimesh:
    """Загрузка модели в сцену как единого меша.
    Лучше всего такой способ загрузки работет с CFMesh.

    Args:
        path (Union[str, os.PathLike]): Путь до исходного меша, который может быть разбит на несколько моделей.

    Raises:
        Exception: В случаи, если расширение объекта или его форма описания не понята trimesh.

    Returns:
        trimesh.Trimesh: Меш как один объект.
    """
    obj = trimesh.load(path)
    if type(obj) == trimesh.base.Trimesh:
        return obj
    elif type(obj) == trimesh.scene.scene.Scene:
        yourList = obj.geometry.items()
        vertice_list = [mesh.vertices for _, mesh in yourList]
        faces_list = [mesh.faces for _, mesh in yourList]
        faces_offset = np.cumsum([v.shape[0] for v in vertice_list])
        faces_offset = np.insert(faces_offset, 0, 0)[:-1]

        vertices = np.vstack(vertice_list)
        faces = np.vstack(
            [face + offset for face, offset in zip(faces_list, faces_offset)]
        )

        merged__meshes = trimesh.Trimesh(vertices, faces)
        return merged__meshes
    else:
        raise Exception("Unknown type of extension!")


def union_itself(args: Namespace, mesh: trimesh.base.Trimesh) -> list[trimesh.base.Trimesh]:
    """Работа с пересечением и, в случае если в сцене находится два отдельных объекта, сохранение их в отдельные файлы.

    Args:
        mesh (trimesh.base.Trimesh): Путь до исходного меша, который может быть разбит на несколько моделей.

    Returns:
        list[trimesh.base.Trimesh]: Массив Trimesh объектов.
    """
    if args.folder:
        if not os.path.exists("../union_itself"):
            os.mkdir("../union_itself")
    else:
        if os.path.exists("../union_itself"):
            shutil.rmtree("../union_itself")

    mesh_list = []
    connected_groups_np_array = mesh.split(only_watertight=False)

    if len(connected_groups_np_array) > 2:
        union_mesh = trimesh.boolean.union(connected_groups_np_array, engine='blender')
        connected_groups = union_mesh.split(only_watertight=False)

    if args.folder: 
        for k in range(len(connected_groups)):
            trimesh.exchange.export.export_mesh(
                connected_groups[k], f"..\\union_itself\\union_itself_{k}.obj", "obj"
            )

    mesh_list = connected_groups.tolist()
    return mesh_list


def manifold(args: Namespace, mesh_list: list[trimesh.base.Trimesh]) -> list[trimesh.base.Trimesh]:
    """Тесселяция сетки.

    Args:
        mesh_list (list[trimesh.base.Trimesh]): Массив с trimesh объектами.

    Kwargs:
        depth (int): Детализация выходной триангулированной сетки.

    Returns:
        list[trimesh.base.Trimesh]: Массив с trimesh объектами.
    """
    if not os.path.exists("obj_before_manifold"):
        os.mkdir("obj_before_manifold")
    if not os.path.exists("../obj_after_manifold"):
        os.mkdir("../obj_after_manifold")

    if args.depth is None:
        args.depth = 4

    for i in range(len(mesh_list)):
        trimesh.exchange.export.export_mesh(
            mesh_list[i], f"obj_before_manifold/mesh_before_manifold{i}.obj", "obj"
        )

    list_obj = os.listdir("obj_before_manifold")
    enum_list_obj = list(enumerate(list_obj))
    for k, elem in enum_list_obj:
        subprocess.run(
            f"manifold.exe --input obj_before_manifold/{elem} --output ../obj_after_manifold/mesh_after_manifold{k}.obj --depth {args.depth}",
            shell=True,
        )

    list_obj_2 = os.listdir("../obj_after_manifold")
    manifold_obj = []
    for i in range(len(list_obj_2)):
        op = trimesh.load(f"../obj_after_manifold/mesh_after_manifold{i}.obj")
        manifold_obj.append(op)

    shutil.rmtree("obj_before_manifold")

    if not args.folder:
        shutil.rmtree("../obj_after_manifold")

    return manifold_obj


def assembling(args: Namespace, mesh_list: list[trimesh.base.Trimesh]) -> trimesh.base.Trimesh:
    """Включение Trimesh объектов из массива в единую сцену с сохранением положения.

    Args:
        mesh_list (list[trimesh.base.Trimesh]): Массив с trimesh объектами.

    Returns:
        trimesh.base.Trimesh: Меш как один объект.
    """
    scene = trimesh.scene.scene.Scene()
    for i in range(len(mesh_list)):
        trimesh_repair(mesh_list[i])
        scene.add_geometry(mesh_list[i])
    final_object = scene.dump(concatenate=True)
    if args.folder:
        if not os.path.exists("../assembling"):
            os.mkdir("../assembling")

        trimesh.exchange.export.export_mesh(
            final_object, "../assembling/assemling.obj", "obj"
        )
    else:
        if os.path.exists("../assembling"):
            shutil.rmtree("../assembling")
    return final_object


def pyacvd_process(
    args: Namespace, 
    mesh: trimesh.base.Trimesh, 
    subdivide: int = 3, 
    cluster: int = 20000
) -> trimesh.base.Trimesh:
    """Триангуляция.

    Args:
        mesh_list (list[trimesh.base.Trimesh]): Массив с trimesh объектами.

    Kwargs:
        subdivide (int): Параметр линейного разбиения сетки.
        cluster (int): Количество точек скопления.

    Returns:
        trimesh.base.Trimesh: Меш как один объект.
    """
    rocket = helpers.wrap(mesh)
    clus = pyacvd.Clustering(rocket)
    clus.subdivide(subdivide)
    clus.cluster(cluster)
    remesh = clus.create_mesh()
    faces_as_array = remesh.faces.reshape((remesh.n_faces, 4))[:, 1:]
    tmesh = trimesh.Trimesh(remesh.points, faces_as_array)

    if args.folder:
        if not os.path.exists("../pyacvd"):
            os.mkdir("../pyacvd")
        trimesh.exchange.export.export_mesh(tmesh, "../pyacvd/pyacvd.obj", "obj")

    else:
        if os.path.exists("../pyacvd"):
            shutil.rmtree("../pyacvd")
    return tmesh


def smoothing(
    mesh: trimesh.base.Trimesh, 
    out_path: Union[str, os.PathLike], 
    number_proc_times: int = 8
) -> trimesh.base.Trimesh:
    """Сглаживание с помощью filter humphrey. 
    Статья Improved Laplacian Smoothing of Noisy Surface Meshes:( http://joerg-vollmer.de/downloads/Improved_Laplacian_Smoothing_of_Noisy_Surface_Meshes.pdf )

    Args:
        mesh_list (list[trimesh.base.Trimesh]): Массив с trimesh объектами.

    Kwargs:
        number_proc_times (int): Количество итераций сглаживания.

    Returns:
        trimesh.base.Trimesh: Меш как один объект.
    """
    for _ in range(number_proc_times):
        trimesh_repair(mesh)
        smoothing_mesh = trimesh.smoothing.filter_humphrey(mesh)
        trimesh.exchange.export.export_mesh(
            smoothing_mesh, f"{out_path}/final_mesh.obj", "obj"
        )
