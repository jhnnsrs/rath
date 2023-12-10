from rath.errors import NotComposedError
from rath.links.base import ContinuationLink
from rath.operation import GraphQLResult, Operation
from typing import AsyncIterator

import io
import aiohttp
from typing import AsyncGenerator
from pydantic import Field

from typing import Any, Dict, Tuple, Type, Union, List

FILE_CLASSES = (
    io.IOBase,
    aiohttp.StreamReader,
    AsyncGenerator,
)


ValidNestedTypes = Union[Dict[str, Any], List, Any]


def parse_nested_files(
    variables: Dict[str, Any],
    file_classes: Tuple[Type[Any], ...] = FILE_CLASSES,
) -> Tuple[Dict[str, Any], Dict]:
    """Parse nested files

    Parameters
    ----------
    variables : Dict
        The variables to parse
    file_classes : Tuple[Type[Any], ...], optional
        File-like classes to extract, by default FILE_CLASSES

    Returns
    -------
    Tuple[Dict, Dict]
        The parsed variables and the extracted files
    """

    files = {}

    def recurse_extract(path: str, obj: ValidNestedTypes) -> ValidNestedTypes:
        """
        recursively traverse obj, doing a deepcopy, but
        replacing any file-like objects with nulls and
        shunting the originals off to the side.
        """
        nonlocal files

        if isinstance(obj, list):
            nulled_list = []
            for index, value in enumerate(obj):
                value = recurse_extract(f"{path}.{str(index)}", value)
                nulled_list.append(value)
            return nulled_list
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

        elif hasattr(obj, "__file__"):
            # extract obj from its parent and put it into files instead.
            files[path] = obj.value
            return None

        else:
            # base case: pass through unchanged
            return obj

    nulled_variables = recurse_extract("variables", variables)
    assert isinstance(nulled_variables, dict), "variables must be a dict"

    return nulled_variables, files


class FileExtraction(ContinuationLink):
    """FileExtraction Link is a link that extracts file-like objects from the variables dict.
    It traverses the variables dict, and extracts any (nested) file-like objects to the context.files dict.

    These can then be used by the FileUploadLink to upload the files to a remote server.
    or used through the multipart/form-data encoding in the terminating link (if supported).
    """

    file_classes: Tuple[Type[Any], ...] = Field(default=FILE_CLASSES)

    async def aexecute(self, operation: Operation) -> AsyncIterator[GraphQLResult]:
        """Extracts files from the variables dict

        Extracts any file-like objects from the variables dict and puts them into the context.files dict.
        The variables dict is then updated to replace the file-like objects with nulls.
        """
        if not self.next:
            raise NotComposedError(
                "FileExtractionLink must be composed with another link"
            )

        operation.variables, operation.context.files = parse_nested_files(
            operation.variables, file_classes=self.file_classes
        )

        async for result in self.next.aexecute(operation):
            yield result
