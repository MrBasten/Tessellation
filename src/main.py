from pathlib import Path
from argparse import ArgumentParser

import utils
from logger import get_logger


def main(args, path, out_path, model_name):
    _logger = get_logger(__name__, 'INFO')
    _logger.info('Start!')

    input_obj = utils.load_trimesh_obj(f"{path}\{model_name}.stl")
    _logger.info("input_obj Done")

    union_mesh = utils.union_itself(args, input_obj)
    _logger.info("union_itself Done")

    manifold_mesh = utils.manifold(args, union_mesh)
    _logger.info("manifold Done")

    assembling_mesh = utils.assembling(args, manifold_mesh)
    _logger.info("assembling Done")

    pyacvd_mesh = utils.pyacvd_process(args, assembling_mesh, subdivide=3, cluster=20000)
    _logger.info("pyacvd_process Done")

    utils.smoothing(pyacvd_mesh, out_path)
    _logger.info("smoothing Done")
    
    _logger.info("All Done")


if __name__ == "__main__":
    parser = ArgumentParser(description="Case for mesh_tessellation")
    parser.add_argument(
        "-f",
        "--folder",
        action="store_true",
        help="Use the argument if you want to create folders with intermediate results"
    )
    parser.add_argument(    
        "-d",
        "--depth",
        action="store",
        help="Use the argument if you want change argument for manifold function"

    )
    args = parser.parse_args()
    print(args)
    main(
        args,
        path=Path('../input').resolve(),
        out_path=Path('../output').resolve(),
        model_name = 'correct_rocket'
    )
