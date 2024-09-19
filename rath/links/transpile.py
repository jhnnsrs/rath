from asyncio.log import logger
from typing import Any, Callable, Dict, Optional
from graphql import (
    ListTypeNode,
    NamedTypeNode,
    NonNullTypeNode,
    OperationDefinitionNode,
    TypeNode,
)
from pydantic import BaseModel, ConfigDict, Field
from rath.links.parsing import ParsingLink
from rath.operation import Operation


class TranspileHandler(BaseModel):
    """A Transpilation Handler

    A TranspileHandler is a function that takes any Any and returns a
    GraphQLType. It is used to implement custom type resolution.

    The default TranspileHandler is the identity function, which returns the
    type passed to it.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    graphql_type: str
    name: str
    predicate: Callable[[Any], bool] = Field(exclude=True)
    parser: Callable[[Any], Any] = Field(exclude=True)
class ListTranspileHandler(BaseModel):
    """A List Transpile Handler

    Similar to a TranspileHandler, but takes act on GraphqQLList Type of that type
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    graphql_type: str
    name: str
    predicate: Callable[[Any, int], bool] = Field(exclude=True)
    parser: Callable[[Any, int], Any] = Field(exclude=True)


class TranspilationError(Exception):
    """A transpilation Exception"""


class TranspilationHandlerException(TranspilationError):
    """A transpilation Exception happening within a TranspileHandler"""


class TranspileRegistry(BaseModel):
    """A Registry to hold TranspileHandlers"""

    list_handlers: Dict[str, Dict[str, ListTranspileHandler]] = Field(
        default_factory=dict
    )
    item_handlers: Dict[str, Dict[str, TranspileHandler]] = Field(default_factory=dict)

    def register_item(
        self,
        graphql_type: str,
        predicate: Callable[[Any], bool],
        name: Optional[str] = None,
    ) -> Callable:
        """A Decorator for registering a TranspileHandler

        If acting on a List of this type, the handle_list parameter should be set to True.

        Example:
            ```python
            registry = TranspileRegistry()

            @registry.register_item("ID", lambda x: isinstance(x, BaseModel))
            def transpile_id_to_id(x):
                return str(x.id)
            ```


        Args:
            graphql_type (str): The graphql Type to act upon
            predicate (Callable[[Any], bool]): A predicate Function
            name (_type_, optional): A name for this hanlder. Defaults to the function name.
        """

        def decorator(func: Callable) -> Callable:
            """The decorator function

            Args:
                func (_type_): The function to use as a handler

            Returns:
                Callable: The function
            """

            x = name or func.__name__

            self.item_handlers.setdefault(graphql_type, {})[x] = TranspileHandler(
                predicate=predicate, parser=func, name=x, graphql_type=graphql_type
            )
            return func

        return decorator

    def register_list(
        self,
        graphql_type: str,
        predicate: Callable[[Any, int], bool],
        name: Optional[str] = None,
    ) -> Callable:
        """A Decorator for registering a TranspileHandler

        If acting on a List of this type, the handle_list parameter should be set to True.

        Example:
            ```python
            registry = TranspileRegistry()

            @registry.register_list("InputVector", lambda x, listdepth: isinstance(x, np.ndarray))
            def transpile_numpy_array_to_vectors(x, listdepth):
                assert listdepth == 1, "Only one level of nesting is supported"
                return [InputVector(x) for x in x]
            ```
        Args:
            graphql_type (str): The graphql Type to act upon
            predicate (Callable[[Any], bool]): A predicate Function
            handle_list (bool, optional): Should we act on lists of this type. Defaults to False.
            name (_type_, optional): A name for this hanlder. Defaults to the function name.
        """  # noqa: E501

        def decorator(func: Callable) -> Callable:
            """The decorator function

            Args:
                func (_type_): The function to use as a handler

            Returns:
                Callable: The function
            """

            x = name or func.__name__

            self.list_handlers.setdefault(graphql_type, {})[x] = ListTranspileHandler(
                predicate=predicate, parser=func, name=x, graphql_type=graphql_type
            )

            return func

        return decorator


def recurse_transpile(
    key: str,
    var: TypeNode,
    value: Any,
    registry: TranspileRegistry,
    in_list: int = 0,
    strict: bool = False,
) -> Any:
    """Recurse Transpile a variable according to a registry and
    its definition

    Args:
        key (str): The key of the variable
        var (VariableNode): The variable definition node correspoin to this variable
        value (Any): The to transpile valued
        registry (TranspileRegistry): The transpile registry to use
        in_list (bool, optional): Recursive Parameter. That will be set to the list depth.
                                 Defaults to False.
        strict (bool, optional): Should we error on predicate errors. Defaults to False.

    Raises:
        TranspilationError: _description_

    Returns:
        Any: The transpiled value or the original value if no handler matched
    """

    if isinstance(var, NonNullTypeNode):
        return recurse_transpile(
            key, var.type, value, registry, in_list=in_list, strict=strict
        )
    if isinstance(var, ListTypeNode):
        return recurse_transpile(
            key, var.type, value, registry, in_list=in_list + 1, strict=strict
        )
    if isinstance(var, NamedTypeNode):
        try:
            if in_list > 0:
                if var.name.value in registry.list_handlers:
                    for k, handler in registry.list_handlers[var.name.value].items():
                        try:
                            predicate = handler.predicate(value, in_list)
                        except Exception as e:
                            if strict:
                                raise TranspilationHandlerException(
                                    f"Handler {handler} predicate failed"
                                ) from e
                            logger.warning(
                                f"Handler {handler} failed on predicating {value}."
                                "Please check your predicate for edge cases"
                            )
                            continue

                        if predicate:
                            parsed_value = handler.parser(value, in_list)
                            assert (
                                parsed_value is not None
                            ), f"Handler {handler} failed on parsing {value} Please check your parser for edge cases"
                            return parsed_value

                return value

            else:
                if var.name.value in registry.item_handlers:
                    type_handlers = registry.item_handlers[var.name.value]

                    for key, item_handler in type_handlers.items():
                        try:
                            predicate = item_handler.predicate(value)
                        except Exception as e:
                            if strict:
                                raise Exception(f"Handler {handler} failed with {e}")
                            logger.warning(
                                f"Handler {handler} failed on predicating {value}. Please check your predicate for edge cases"
                            )
                            continue
                        if predicate:
                            parsed_value = [
                                item_handler.parser(value) for value in value
                            ]
                            assert (
                                parsed_value is not None
                            ), f"Handler {handler} failed on parsing {value}. Please check your parser for edge cases"
                            return parsed_value

                else:
                    return value

        except Exception as e:
            raise TranspilationError(
                f"Transpilation for variable {key} on graphql type `{var.name.value}` ! Original value: {repr(value)}"
            ) from e


def transpile(
    op: OperationDefinitionNode,
    variables: Dict[str, Any],
    registry: TranspileRegistry,
    strict: bool = False,
) -> Dict[str, Any]:
    """Transpile

    Transpiles a operations variabels to a dictionary of variables, with
    json serializable values according to a transpile registry.

    Args:
        op (OperationDefinitionNode): The operation definition node,
        registry (TranspileRegistry): The registry
        strict (bool, optional): Should we fail if a handler predicate fails. Defaults
        to False.

    Returns:
        Dict: The transpiled variables
    """
    variable_nodes = {
        var_node.variable.name.value: var_node.type
        for var_node in op.variable_definitions
        if var_node.variable.name.value in variables
    }

    transpiled_variables = {
        key: recurse_transpile(key, variable, variables[key], registry, strict=strict)
        for key, variable in variable_nodes.items()
        if isinstance(variable, TypeNode)
    }

    return transpiled_variables


class TranspileLink(ParsingLink):
    """Transpile Link

    Transpile Link is a link that transpiles variables according to a transpile registry.


    Attributes:
        registry (TranspileRegistry): The transpile registry to use
        strict (bool): Should we fail if a handler predicate fails. Defaults to False.

    """

    registry: TranspileRegistry
    strict: bool = False

    async def aparse(self, operation: Operation) -> Operation:
        """Parse an operation

        This method will transpile the variables dict, according to the registry.


        Parameters
        ----------
        operation : Operation
            The operation to transpile

        Returns
        -------
        Operation
            The transpiled operation
        """
        operation.variables = transpile(
            operation.node, operation.variables, self.registry, self.strict
        )
        return operation
