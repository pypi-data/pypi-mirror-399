# 安装: pip install pdfannots
# 命令: pdfannots --no-group -f md -o notes.md 文档.pdf

import sys
from pathlib import Path
import shutil
import fitz
import pprint

base_level = 1


def is_cmd_installed(cmd: str):
    return True if shutil.which(cmd) else False


def get_unique_path(path: Path):
    """
    如果文件已存在，则在文件名后添加 (n)
    例如: test.md -> test (1).md -> test (2).md
    """
    # path = Path(path)
    if not path.exists():
        return path

    name = path.stem  # 文件名（不含后缀）
    suffix = path.suffix  # 后缀（如 .md）
    parent = path.parent  # 父目录

    counter = 1
    while True:
        # 生成新的候选路径
        new_path = parent / f"{name} ({counter}){suffix}"
        if not new_path.exists():
            return new_path
        counter += 1


# --------------------------------
# 提取高亮文字
# --------------------------------
def extract_highlight_text(page: fitz.Page, annot: fitz.Annot):
    text = ""
    if not annot.vertices:
        return text

    for i in range(0, len(annot.vertices), 4):
        quad = fitz.Quad(annot.vertices[i : i + 4])
        rect = quad.rect
        text += page.get_text("text", clip=rect)

    return text.strip()


def get_page_tocs(tocs: list, page_idx: int) -> list[dict]:
    """_summary_

    Args:
        tocs (list): _description_
        page_idx (int): _description_

    Returns:
        list: [{"position": int, "text": str}]
    """
    # print("base_level", base_level)
    # for toc in tocs:
    #     if toc[3]["page"] == page_idx:
    #         print("-----toc-----")
    #         pprint.pprint(toc)

    # "text": f"{'#' * level} 📘 {chapter}"
    # return [{"xref": toc[3]["xref"], "text": f"{'#' * (base_level + toc[0])} 📘 {toc[1]}\n\n"} for toc in tocs if toc[3]["page"] == page_idx]
    return [{"position": toc[3]["to"].y, "text": f"{'#' * (base_level + toc[0])} 📘 {toc[1]}\n\n"} for toc in tocs if toc[3]["page"] == page_idx]


def get_page_annots(page: fitz.Page) -> list[dict]:
    """_summary_

    Args:
        page (fitz.Page): _description_

    Returns:
        list[dict]: [{"position": int, "text": str}]
    """
    annots = page.annots()

    if not annots:
        return []

    res = []
    for annot in annots:
        text: str = ""
        annot_type = annot.type[1]
        comment: str = annot.info.get("content", "").strip()
        # print("-----annot-----")
        # pprint.pprint(annot.rect)

        # 高亮 / 下划线 / 删除线
        if annot_type in ("Highlight", "Underline", "StrikeOut"):
            highlight_text = extract_highlight_text(page, annot)
            if not highlight_text:
                continue

            highlight_text = highlight_text.replace("\n", "")
            text += f"> {highlight_text}\n\n"

            if comment:
                text += f"💬 **注释**：\n{comment}\n\n"

        # 纯文本注释
        elif annot_type == "Text":
            text += f"💬 **注释**：\n{comment}\n\n"
        elif annot_type == "FreeText":
            text += f"💬 **悬浮文本框**：\n{comment}\n\n"

        # res.append({"xref": annot.xref, "text": text})
        res.append({"position": annot.rect.y1, "text": text})
    return res


def extract_notes(pdf: Path, md: Path):
    doc: fitz.Document = fitz.open(pdf)
    # outline level, title, page number, link destination
    # [2, '9.6.私有变量', 9, {'kind': 1, 'page': 8, 'to': Point(41.2, 299.57), 'xref': 3662, 'zoom': 0.0}]
    tocs = doc.get_toc(False)
    with open(md, "w", encoding="utf-8") as f:
        for page_idx in range(doc.page_count):
            page: fitz.Page = doc[page_idx]
            tocs_of_page = get_page_tocs(tocs, page_idx)
            annots_of_page = get_page_annots(page)
            combined = tocs_of_page + annots_of_page
            for item in sorted(combined, key=lambda d: d["position"]):
                f.write(item["text"])
                # pprint.pprint(item)


def export_pdf_notes_to_markdown(file_path: Path):
    """_summary_

    Args:
        file_path (Path): _description_
        base_level (int, optional): 章节前添加几个 # . Defaults to 1.

    Raises:
        Exception: 非 pdf 文件
        Exception: 文件不存在
    """
    if not file_path.suffix.lower().endswith(".pdf"):
        raise Exception(f"非 pdf 文件：{file_path}")
    if not file_path.exists():
        raise Exception(f"文件不存在：{file_path}")

    pdf: Path = Path(file_path)
    md: Path = pdf.with_suffix(".md")
    if md.exists():
        is_replace: bool = input(f"{md} 已存在，是否替换(y/n)：") == "y"
        if not is_replace:
            md = get_unique_path(md)

    extract_notes(pdf, md)


def main():
    files: list[str] = []
    stop: bool = False

    if len(sys.argv) > 1:
        files = sys.argv[1:]
    else:
        stop = True
        print("没有文件")

    try:
        global base_level
        user_input = int(input("章节基于几个 # (默认为1)："))
        base_level = user_input if user_input >= 0 else 1
    except Exception:
        pass

    for file in files:
        try:
            export_pdf_notes_to_markdown(Path(file))
        except Exception as e:
            stop = True
            print(e)
        # export_pdf_notes_to_markdown(Path(file))

    if stop:
        input()


if __name__ == "__main__":
    main()
