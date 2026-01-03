import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pymupdf
import PyPDF2
from ollama import Image
from PIL import Image as PILImage


def render_prompt_template(
    prompt_content: str,
    submission: Path,
    has_submission_image: bool = False,
    has_solution_image: bool = False,
    solution: Optional[Path] = None,
    test_output: Optional[Path] = None,
    question: Optional[str] = None,
    marking_instructions: Optional[str] = None,
    **kwargs,
) -> str:
    """Render a prompt template by replacing placeholders with actual values.

    Args:
        prompt_content (str): The prompt template with placeholders
        submission (Path): Path to the student's submission file
        solution (Path, optional): Path to the instructor's solution file
        test_output (Path, optional): Path to the student's test output or error trace file
        question (str, optional): The question string to use
        prompt_content (str): The prompt template with placeholders like {file_contents}
        has_submission_image (bool): Whether a submission image is present
        has_solution_image (bool): Whether a solution image is present
        marking_instructions (str, optional): Marking instructions to replace {marking_instructions} placeholder
        **kwargs: Additional key-value pairs for placeholder replacement

    Returns:
        str: The rendered prompt with placeholders replaced
    """
    template_data = kwargs.copy()

    template_data['file_references'] = gather_file_references(submission, solution, test_output)
    if question is not None:
        template_data['file_contents'] = _get_question_contents([submission, solution], question)
    else:
        template_data['file_contents'] = gather_xml_file_contents(submission, solution, test_output)

    # Handle marking instructions placeholder
    if marking_instructions is not None:
        template_data['marking_instructions'] = marking_instructions
    elif '{marking_instructions}' in prompt_content:
        template_data['marking_instructions'] = ''

    # Handle image placeholders with context-aware replacement
    if '{submission_image}' in prompt_content and 'submission_image' not in template_data:
        if has_submission_image and has_solution_image:
            template_data['submission_image'] = 'The first attached image is the student\'s submission.'
        elif has_submission_image:
            template_data['submission_image'] = 'The attached image is the student\'s submission.'
        else:
            template_data['submission_image'] = '[Submission Image Attached]'

    if '{solution_image}' in prompt_content and 'solution_image' not in template_data:
        if has_submission_image and has_solution_image:
            template_data['solution_image'] = 'The second attached image is the expected solution.'
        elif has_solution_image:
            template_data['solution_image'] = 'The attached image is the expected solution.'
        else:
            template_data['solution_image'] = '[Solution Image Attached]'

    return prompt_content.format(**template_data)


def gather_file_references(
    submission: Optional[Path] = None, solution: Optional[Path] = None, test_output: Optional[Path] = None
) -> str:
    """Generate file reference descriptions for prompt templates.

    Args:
        submission (Path, optional): Student's submission file path
        solution (Path, optional): Instructor's solution file path
        test_output (Path, optional): Student's test output file path

    Returns:
        str: Descriptions like "The instructor's solution file..."
    """
    references: List[str] = []
    if submission:
        references.append(f"The student's submission file is {submission.name}.")
    if solution:
        references.append(f"The instructor's solution file is {solution.name}.")
    if test_output:
        references.append(f"The student's test output file is {test_output.name}.")
    return "\n".join(references)


def gather_xml_file_contents(
    submission: Optional[Path] = None, solution: Optional[Path] = None, test_output: Optional[Path] = None
) -> str:
    """Generate file contents with XML tags for prompt templates.

    Args:
        submission (Path, optional): Student's submission file path
        solution (Path, optional): Instructor's solution file path
        test_output (Path, optional): Student's test output file path

    Returns:
        str: File contents formatted with XML tags and line numbers
    """
    file_contents = ""

    if submission:
        file_contents += _format_file_with_xml_tag(submission, "submission")

    if solution:
        file_contents += _format_file_with_xml_tag(solution, "solution")

    if test_output:
        file_contents += _format_file_with_xml_tag(test_output, "test_output")

    return file_contents


def _format_file_with_xml_tag(file_path: Path, tag_name: str) -> str:
    """Format a single file with XML tags and line numbers.

    Args:
        file_path (Path): Path to the file to format
        tag_name (str): The XML tag name (submission, solution, test_output)

    Returns:
        str: Formatted file content with XML tags
    """
    if not file_path:
        return ""

    filename = os.path.basename(file_path)

    try:
        # Handle PDF files separately
        if filename.lower().endswith('.pdf'):
            text_content = extract_pdf_text(file_path)
            return f"<{tag_name} filename=\"{filename}\">\n{text_content}\n</{tag_name}>\n\n"
        else:
            # Handle regular text files
            with open(file_path, "r", encoding="utf-8") as file:
                lines = file.readlines()
            return _wrap_lines_with_xml(lines, tag_name, filename)

    except Exception as e:
        print(f"Error reading file {filename}: {e}")
        return ""


def _wrap_lines_with_xml(lines: List[str], tag_name: str, filename: str) -> str:
    """Wrap lines with XML tags and add line numbers.

    Args:
        lines (List[str]): List of lines to format
        tag_name (str): The XML tag name (submission, solution, test_output)
        filename (str): The filename to include in the XML tag

    Returns:
        str: Formatted content with XML tags and line numbers
    """
    content = f"<{tag_name} filename=\"{filename}\">\n"

    for i, line in enumerate(lines, start=1):
        stripped_line = line.rstrip("\n")
        if stripped_line.strip():
            content += f"(Line {i}) {stripped_line}\n"
        else:
            content += f"(Line {i}) {line}"

    content += f"</{tag_name}>\n\n"
    return content


def extract_pdf_text(pdf_path: Path | str) -> str:
    """Extract text content from a PDF file.

    Args:
        pdf_path (str): Path to the PDF file

    Returns:
        str: Extracted text content from the PDF
    """
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""

            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"

            return text.strip()
    except Exception as e:
        print(f"Error extracting text from PDF {pdf_path}: {e}")
        return f"[Error: Could not extract text from PDF {os.path.basename(pdf_path)}]"


def gather_image_context(output_directory: str, question: str) -> str:
    """Gather question context for image prompts.

    Args:
        output_directory (str): Directory containing extracted images
        question (str): Question identifier

    Returns:
        str: Question context content
    """
    try:
        from ..helpers.image_reader import read_question_context

        return read_question_context(output_directory, question)
    except Exception as e:
        print(f"Error reading question context: {e}")
        return ""


def gather_image_size(output_directory: str, question: str) -> str:
    """Gather image size information for prompts.

    Args:
        output_directory (str): Directory containing extracted images
        question (str): Question identifier

    Returns:
        str: Image size in format "width by height"
    """
    try:
        from ..helpers.image_reader import read_submission_images

        submission_image_paths = read_submission_images(output_directory, question)
        if submission_image_paths:
            image = PILImage.open(submission_image_paths[0])
            return f"{image.width} by {image.height}"
    except Exception as e:
        print(f"Error reading image size: {e}")
    return "unknown"


def gather_images(output_directory: str, question: str, include_images: list[str]) -> list[Image]:
    """Gather images for attachment to message.

    Args:
        output_directory (str): Directory containing extracted images
        question (str): Question identifier
        include_images (list[str]): List of image types to include ("submission", "solution")

    Returns:
        list[Image]: List of Image objects for message attachment
    """
    images = []

    try:
        from ..helpers.image_reader import read_solution_images, read_submission_images

        if "submission" in include_images:
            submission_paths = read_submission_images(output_directory, question)
            if submission_paths:
                images.append(Image(value=submission_paths[0]))

        if "solution" in include_images:
            solution_paths = read_solution_images(output_directory, question)
            if solution_paths:
                images.append(Image(value=solution_paths[0]))

    except Exception as e:
        print(f"Error gathering images: {e}")

    return images


def _get_question_contents(assignment_files: List[Optional[Path]], question: str) -> str:
    """
    Retrieve contents of files specifically for a targeted question heading.

    Args:
        assignment_files (List[Optional[Path]]): List of Path or None objects to parse.
            Expected order: [submission, solution]
        question (str): Question identifier

    Returns:
        str: Combined content of the introduction and the specified task from matching files.

    Raises:
        SystemExit: If no matching task is found in the provided files.
    """
    file_contents = ""
    task_found = False

    semantic_tags = ["submission", "solution"]

    for index, file_path in enumerate(assignment_files):
        if not file_path or "error_output" in file_path.name or file_path.name == ".DS_Store":
            continue

        task_content = ""
        if file_path.suffix == '.txt':
            intro_content, found = extract_question_from_txt(file_path, question)
        elif file_path.suffix == ".pdf":
            intro_content, found = extract_question_from_pdf(file_path, question)
        else:
            continue

        if found:
            task_found = True

        tag_name = semantic_tags[index] if index < len(semantic_tags) else "file"
        file_contents += f"<{tag_name} filename=\"{file_path.name}\">\n"
        file_contents += intro_content + "\n\n" if intro_content else ""
        file_contents += task_content + "\n\n"
        file_contents += f"</{tag_name}>\n\n"

    if not task_found:
        print(f"Task '{question}' not found in any assignment file.")
        sys.exit(1)

    return file_contents.strip()


def normalize_text(x: str) -> str:
    """Normalize text for consistent matching (rough R parity)."""
    x = re.sub(r"[\r\n\t]", " ", x)
    x = re.sub(r"[‘’´`]", "'", x)
    x = re.sub(r"[“”]", '"', x)
    x = re.sub(r"[–—]", "-", x)
    x = re.sub(r"\s+", " ", x)
    return x.strip().lower()


def flatten_toc(pdf_path: Path) -> List[Dict[str, Any]]:
    """
    Convert PyMuPDF TOC (outline) to a flat list of dicts:
    {title, page, level}
    """
    doc = pymupdf.open(pdf_path)
    toc_rows = doc.get_toc(simple=False)
    doc.close()

    flat = []
    for row in toc_rows:
        level, title, page = row[0], row[1], row[2]
        flat.append({"title": title, "page": page if page is not None else None, "level": level})
    return flat


def get_next_heading_title(flat_toc: List[Dict[str, Any]], heading: str) -> Optional[str]:
    """
    Given a flattened TOC and a heading title, return the title of the next
    heading that is at the same or higher level (not a subheading).
    """
    norm_heading = normalize_text(heading)
    titles_norm = [normalize_text(d["title"]) for d in flat_toc]
    matches = [i for i, t in enumerate(titles_norm) if t == norm_heading]
    if not matches:
        return None

    match_idx = matches[-1]
    start_level = flat_toc[match_idx]["level"]

    if match_idx >= len(flat_toc) - 1:
        return None

    for i in range(match_idx + 1, len(flat_toc)):
        if flat_toc[i]["level"] <= start_level:
            return flat_toc[i]["title"]
    return None


def extract_question_from_pdf(pdf_path: Path, heading: str) -> tuple[str, bool]:
    """
    Extract the text block under a given heading (matched by exact normalized title)
    up to the next heading at the same or higher level.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"[Error: Submission file {os.path.basename(pdf_path)} not found]")

    # Load and flatten TOC
    toc = flatten_toc(pdf_path)

    titles_norm = [normalize_text(d["title"]) for d in toc]
    norm_heading = normalize_text(heading)

    if norm_heading not in titles_norm:
        print(f"[ERROR] Heading '{norm_heading}' not found in TOC")
        return "", False

    next_heading_title = get_next_heading_title(toc, heading)

    # Read full text (as continuous lines)
    full_text = extract_pdf_text(pdf_path)
    lines = full_text.split("\n")

    norm_lines = [normalize_text(l.strip()) for l in lines]

    # Locate start of heading within text
    start_indices = [i for i, t in enumerate(norm_lines) if t == norm_heading]

    if not start_indices:
        raise ValueError(f"[ERROR] Start indices for heading '{heading}' not found.")

    start_line = start_indices[0]
    end_line = len(lines) - 1

    # If we know the next heading, find its first occurrence after start_line
    if next_heading_title:
        nh = normalize_text(next_heading_title)
        next_idx = [i for i, t in enumerate(norm_lines) if t == nh and i > start_line]
        if next_idx:
            end_line = next_idx[0] - 1

    if start_line > end_line or start_line < 0:
        raise ValueError(f"Invalid line bounds: start={start_line}, end={end_line}")

    extracted = lines[start_line : end_line + 1]

    return "\n".join([l.strip() for l in extracted]), True


def extract_question_from_txt(submission_path: Path, question: str) -> tuple[str, bool]:
    """
    Given a Markdown file, return the block from the heading 'question'
    up to (but not including) the next heading of the same or higher level.
    """
    _MD_HEADER_RE = re.compile(r"^(#{1,6})\s+(.*)$")
    if not os.path.exists(submission_path):
        raise FileNotFoundError(f"[Error: Submission file {submission_path} not found]")

    with open(submission_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    def norm(x: str) -> str:
        return normalize_text(re.sub(r"\s+", " ", x.strip()))

    header_lines = []
    for idx, line in enumerate(lines):
        m = _MD_HEADER_RE.match(line)
        if m:
            level = len(m.group(1))
            text = norm(m.group(2))
            header_lines.append((idx, level, text))

    norm_question = norm(question)
    matches = [i for i, (_, _, txt) in enumerate(header_lines) if txt == norm_question]
    if not matches:
        return "", False

    start_tuple = header_lines[matches[0]]
    start_line, cur_level, _ = start_tuple

    # find next heading of same or higher level
    next_candidates = [ln for ln, lvl, _ in header_lines if ln > start_line and lvl <= cur_level]
    end_line = next_candidates[0] - 1 if next_candidates else len(lines) - 1

    block = "".join(lines[start_line : end_line + 1])
    return block, True
