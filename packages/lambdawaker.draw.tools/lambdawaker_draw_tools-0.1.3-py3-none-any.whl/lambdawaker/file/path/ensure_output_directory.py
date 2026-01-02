import os


def ensure_output_directory(output_path):
    if output_path is not None:
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)


