# -*- coding: utf-8 -*-
from typing import Any, Generator

try:
    import ujson as json
except ImportError:
    import json

from .base_formatter import Formatter
from ..node import Node, ErrorNode

class JSONFormatter(Formatter):
    def __init__(self):
        super().__init__()
        self.config.update({
            'compact': False,
            'indent': 4,
            'ensure_ascii': False,
        })

    def _format_key(self, node: Node) -> str:
        return node.get_key()

    def _format_props(self, node: Node) -> tuple[str, str]:
        return node.get_prop("title"), node.get_prop("type")

    def _format_attrs(self, node: Node) -> dict[str, Any]:
        return {self._attr_adjust_name(k): v for k, v in node.get_attrs().items()}

    def _format_value(self, node: Node) -> str:
        return node.get_value()

    def _format_header(self, key: str, props: tuple[str, str], attrs: dict[str, Any], value: str, indent: int, context: dict[str, Any]):
        context['parent'][key] = {
            "error": False,
            "name": props[0],
            "type": props[1],
            "attrs": attrs,
            "value": value,
        }

    def _format_error(self, key: str, props: tuple[str, str], attrs: dict[str, Any], value: str, indent: int, context: dict[str, Any]):
        context['parent'][key] = {
            "error": True,
            "name": props[0],
            "type": props[1],
            "attrs": attrs,
            "value": None,
        }

    def _format_node(self, node: Node, indent: int, context: dict[str, Any]):
        self._pre_node(node, context=context)
        parent_container = context['parent']

        key = self._format_key(node)
        props = self._format_props(node)
        attrs = self._format_attrs(node)
        value = self._format_value(node)
        if isinstance(node, ErrorNode):
            self._format_error(key, props, attrs, value, indent, context)
        else:
            self._format_header(key, props, attrs, value, indent, context)
        current = parent_container[key]

        if node.children.__len__() > 0:
            children_container = current.setdefault('children', {})
            for child_node in node.iter_children():
                context['parent'] = children_container
                self._format_node(child_node, indent + 1, context)

        # 在 post 钩子里让 parent 指向当前节点字典
        context['parent'] = current
        self._post_node(node, context)

        # 返回给上层时恢复为父容器，确保兄弟节点写入同一 children
        context['parent'] = parent_container

    def _render(self, node: Node) -> Generator[Any, Any, None]:
        json_root = {}
        context = {
            'root': json_root,
            'parent': json_root,
        }
        pre = self._pre_render(node, context)
        if pre:
            yield pre
        self._format_node(node, 0, context)
        yield json.dumps(context['root'][''], ensure_ascii=self.config['ensure_ascii'], indent=0 if self.config['compact'] else self.config['indent'])
        post = self._post_render(node, context)
        if post:
            yield post
