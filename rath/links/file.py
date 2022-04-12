from rath.links.base import ContinuationLink
from rath.operation import Operation
from rath.operation import Operation

import io
import aiohttp
from typing import AsyncGenerator


FILE_CLASSES = (
    io.IOBase,
    aiohttp.StreamReader,
    AsyncGenerator,
)
from typing import Any, Dict, Tuple, Type


def parse_variables(
    variables: Dict,
    file_classes: Tuple[Type[Any], ...] = FILE_CLASSES,
) -> Tuple[Dict, Dict]:
    files = {}

    def recurse_extract(path, obj):
        """
        recursively traverse obj, doing a deepcopy, but
        replacing any file-like objects with nulls and
        shunting the originals off to the side.
        """
        nonlocal files

        if isinstance(obj, list):
            nulled_obj = []
            for key, value in enumerate(obj):
                value = recurse_extract(f"{path}.{key}", value)
                nulled_obj.append(value)
            return nulled_obj
        elif isinstance(obj, dict):
            nulled_obj = {}
            for key, value in obj.items():
                value = recurse_extract(f"{path}.{key}", value)
                nulled_obj[key] = value
            return nulled_obj
        elif isinstance(obj, file_classes):
            # extract obj from its parent and put it into files instead.
            files[path] = obj
            return None

        else:
            # base case: pass through unchanged
            return obj

    nulled_variables = recurse_extract("variables", variables)

    return nulled_variables, files


class FileExtraction(ContinuationLink):
    async def aexecute(self, operation: Operation) -> Operation:
        operation.variables, operation.context.files = parse_variables(
            operation.variables
        )

        async for result in self.next.aexecute(operation):
            yield result
