import json
import sys
from pathlib import Path
from typing import List

from .translation.base import Translator
from .translation.factory import get_translators


def translate_to_json(src_xml_path: str, dst_dir: str, image_size_tag: str = "middle"):
    translators = get_translators(src_xml_path)
    for group, translator_list in translators.items():
        dst_path = Path(dst_dir) / (group + ".json")
        if group == "document-sections":
            data = merge_document_sections(translator_list, image_size_tag)
        elif group == "text-blocks":
            data = merge_text_blocks(translator_list)
        else:
            data = merge_others(translator_list)
        with open(dst_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def merge_text_blocks(translators: List[Translator]):
    result = []
    for translator in translators:
        blocks = translator.translate("", params={})
        result.extend(blocks["root"]["blocks"])
    return {"blocks": result}


def merge_document_sections(
    translators: List[Translator], image_size_tag: str = "middle"
):
    result = {}
    for translator in translators:
        section = translator.translate("", params={"image_size_tag": image_size_tag})
        result = {**result, **section["root"]}
    return result


def merge_others(translators: List[Translator]):
    result = {}
    for translator in translators:
        data = translator.translate("", params={})
        result = {**result, **data}
    return result
