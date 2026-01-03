from typing import Dict, List
from xml.etree import ElementTree as ET

from .base import Translator
from .html_translator import HtmlToJsonTranslator, HTMLTranslator
from .json_translator import JSONImageInfoTranslator, JSONTranslator

"""
変換元は、複数のXMLをマージしたxml(e.g. document.xml)でなければならない
text-blocks, document-sections, images などのグループごとに
translator_config に namespace, doctype, xsl, translator class を定義する。

"""

translator_config = {
    "text-blocks": [
        ### A163 日本語特許出願関連
        {
            ### 願書 テキストブロック SSG用
            "namespace": "http://www.jpo.go.jp",
            "doctype": "pat-app-doc",
            "xsl": "text-blocks/pat-appd.xsl",
            "extra_args": {
                "force_list": ["blocks"],
            },
            "translator": JSONTranslator,
        },
        {
            ### 明細書 テキストブロック SSG用
            "namespace": "",
            "doctype": "application-body",
            "xsl": "text-blocks/application-body.xsl",
            "extra_args": {
                "force_list": ["blocks"],
            },
            "translator": JSONTranslator,
        },
        ### A163 外国語書面出願
        {
            ### 明細書 テキストブロック SSG用
            "namespace": "http://www.jpo.go.jp",
            "doctype": "foreign-language-body",
            "xsl": "text-blocks/foreign-language-body.xsl",
            "extra_args": {
                "force_list": ["blocks"],
            },
            "translator": JSONTranslator,
        },
    ],
    "document-sections": [
        ### A163 日本語特許出願関連
        {
            ### 願書のフルテキスト. 検索用
            "namespace": "http://www.jpo.go.jp",
            "doctype": "pat-app-doc",
            "xsl": "html/pat-appd.xsl",
            "extra_args": {
                "json_key": "ApplicationFullText",
            },
            "translator": HtmlToJsonTranslator,
        },
        {
            ### 願書の特定項目テキスト. 検索用
            "namespace": "http://www.jpo.go.jp",
            "doctype": "pat-app-doc",
            "xsl": "xml/pat-appd.xsl",
            "extra_args": {
                "force_list": ["Inventors", "Applicants", "Agents"],
            },
            "translator": JSONTranslator,
        },
        {
            ### 書誌情報の各項目のテキスト. 検索用
            "namespace": "",
            "doctype": "procedure-params",
            "xsl": "xml/bibliographic.xsl",
            "extra_args": {"force_list": None},
            "translator": JSONTranslator,
        },
        {
            ### 明細書の各項目のテキスト. 検索用
            "namespace": "",
            "doctype": "application-body",
            "xsl": "xml/application-body.xsl",
            "extra_args": {"force_list": None},
            "translator": JSONTranslator,
        },
    ],
    "images": [
        {
            ### 画像情報
            "namespace": "",
            "doctype": "images",
            "xsl": "xml/images.xsl",
            "extra_args": {
                "force_list": [],
            },
            "translator": JSONImageInfoTranslator,
        },
    ],
    # "html": [
    # {
    #    ### 願書のhtml
    #    "namespace": "http://www.jpo.go.jp",
    #    "doctype": "pat-app-doc",
    #    "xsl": "html/pat-appd.xsl",
    #    "translator": HTMLTranslator,
    # },
    # {
    #    ### 明細書のhtml
    #    "namespace": "",
    #    "doctype": "application-body",
    #    "xsl": "html/application-body.xsl",
    #    "translator": HTMLTranslator,
    # },
    # ]
}


def get_translators(src_xml_path: str) -> Dict[str, List[Translator]]:
    result = {}
    src_xml_string = open(src_xml_path, "r").read()
    root = ET.fromstring(src_xml_string)

    ### translator_config を、group(key) と config(value) に分解して走査
    for group, configs in translator_config.items():

        ### translator_config の各 config を走査
        for config in configs:

            ### namespace, doctype に合致する要素があれば Translator を生成
            if config["namespace"]:
                search_tag = f"{{{config['namespace']}}}{config['doctype']}"
            else:
                search_tag = config["doctype"]
            if root.find(search_tag) is not None:

                ### translator class の取得
                translator_cls = config["translator"]
                args = {
                    "xsl_path": config["xsl"],
                    "xml_string": src_xml_string,
                }

                if "extra_args" in config:
                    args = {**args, **config["extra_args"]}

                ### Translator インスタンスの生成
                translator = translator_cls(**args)

                ### group ごとに分類して格納
                if group not in result:
                    result[group] = []
                result[group].append(translator)

    return result
