import os
from pathlib import Path


def read_question_context(output_directory: os.PathLike, question: str):
    with open(os.path.join(output_directory, question, "context.txt")) as file:
        context = file.read()
    return context


def read_submission_images(output_directory: os.PathLike, question: str) -> list[Path]:
    submission_image_paths = [
        Path(output_directory, question, i, "submission.png")
        for i in os.listdir(os.path.join(output_directory, question))
        if i != "context.txt"
    ]
    submission_image_paths.sort()
    return submission_image_paths


def read_solution_images(output_directory: os.PathLike, question: str) -> list[Path]:
    solution_image_paths = [
        Path(output_directory, question, i, "solution.png")
        for i in os.listdir(os.path.join(output_directory, question))
        if i != "context.txt"
    ]
    solution_image_paths.sort()
    return solution_image_paths
