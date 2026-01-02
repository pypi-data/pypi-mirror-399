import re
from fastapi import status, HTTPException, Request
from pydantic import Field
from typing import (
    Annotated,
    Callable,
    Generic,
    Literal,
    Mapping,
    Type,
    TypeVar,
    overload,
)
from ..enums import (
    ResourceOperationType,
    ResourceOperationTypeT,
    OptResourceOperationType,
    ResourceOperationUpdateType,
    OptResourceOperationUpdateType,
    ResourceOperationDataUpdateType,
    OptResourceOperationDataUpdateType,
    ResourceOperationStatusUpdateType,
    OptResourceOperationStatusUpdateType,
)
from .base import BaseOperationAction


class ResourceOperationAction(
    BaseOperationAction[ResourceOperationTypeT], Generic[ResourceOperationTypeT]
):
    pass


class CreateResourceOperationAction(
    ResourceOperationAction[Literal[ResourceOperationType.CREATE]]
):
    type: Literal[ResourceOperationType.CREATE] = ResourceOperationType.CREATE


CREATE_RESOURCE_OPERATION_ACTION = CreateResourceOperationAction()


class ReadResourceOperationAction(
    ResourceOperationAction[Literal[ResourceOperationType.READ]]
):
    type: Literal[ResourceOperationType.READ] = ResourceOperationType.READ


class UpdateResourceOperationAction(
    ResourceOperationAction[Literal[ResourceOperationType.UPDATE]]
):
    type: Literal[ResourceOperationType.UPDATE] = ResourceOperationType.UPDATE
    update_type: Annotated[
        OptResourceOperationUpdateType,
        Field(None, description="Update type (optional)"),
    ] = None
    data_update_type: Annotated[
        OptResourceOperationDataUpdateType,
        Field(None, description="Data update type (optional)"),
    ] = None
    status_update_type: Annotated[
        OptResourceOperationStatusUpdateType,
        Field(None, description="Status update type (optional)"),
    ] = None


class DeleteResourceOperationAction(
    ResourceOperationAction[Literal[ResourceOperationType.DELETE]]
):
    type: Literal[ResourceOperationType.DELETE] = ResourceOperationType.DELETE


ResourceOperationActions = (
    CreateResourceOperationAction,
    ReadResourceOperationAction,
    UpdateResourceOperationAction,
    DeleteResourceOperationAction,
)


AnyResourceOperationAction = (
    CreateResourceOperationAction
    | ReadResourceOperationAction
    | UpdateResourceOperationAction
    | DeleteResourceOperationAction
)


AnyResourceOperationActionT = TypeVar(
    "AnyResourceOperationActionT", bound=AnyResourceOperationAction
)


OptAnyResourceOperationAction = AnyResourceOperationAction | None


TYPE_ACTION_MODEL_MAP: Mapping[ResourceOperationType, Type] = {
    ResourceOperationType.CREATE: CreateResourceOperationAction,
    ResourceOperationType.READ: ReadResourceOperationAction,
    ResourceOperationType.UPDATE: UpdateResourceOperationAction,
    ResourceOperationType.DELETE: DeleteResourceOperationAction,
}


class ResourceOperationActionFactory:
    @overload
    @staticmethod
    def generate(
        type_: Literal[ResourceOperationType.CREATE],
        /,
    ) -> CreateResourceOperationAction: ...
    @overload
    @staticmethod
    def generate(
        type_: Literal[ResourceOperationType.READ],
        /,
    ) -> ReadResourceOperationAction: ...
    @overload
    @staticmethod
    def generate(
        type_: Literal[ResourceOperationType.UPDATE],
        *,
        update_type: OptResourceOperationUpdateType = ...,
        data_update_type: OptResourceOperationDataUpdateType = ...,
        status_update_type: OptResourceOperationStatusUpdateType = ...,
    ) -> UpdateResourceOperationAction: ...
    @overload
    @staticmethod
    def generate(
        type_: Literal[ResourceOperationType.DELETE],
        /,
    ) -> DeleteResourceOperationAction: ...
    @overload
    @staticmethod
    def generate(
        type_: ResourceOperationType,
        *,
        update_type: OptResourceOperationUpdateType = None,
        data_update_type: OptResourceOperationDataUpdateType = None,
        status_update_type: OptResourceOperationStatusUpdateType = None,
    ) -> AnyResourceOperationAction: ...
    @staticmethod
    def generate(
        type_: ResourceOperationType,
        *,
        update_type: OptResourceOperationUpdateType = None,
        data_update_type: OptResourceOperationDataUpdateType = None,
        status_update_type: OptResourceOperationStatusUpdateType = None,
    ) -> AnyResourceOperationAction:
        if type_ is ResourceOperationType.CREATE:
            return CreateResourceOperationAction()

        elif type_ is ResourceOperationType.READ:
            return ReadResourceOperationAction()

        elif type_ is ResourceOperationType.UPDATE:
            return UpdateResourceOperationAction(
                update_type=update_type,
                data_update_type=data_update_type,
                status_update_type=status_update_type,
            )

        elif type_ is ResourceOperationType.DELETE:
            return DeleteResourceOperationAction()

    @overload
    @staticmethod
    def extract(
        *,
        request: Request,
        from_state: bool = True,
        strict: Literal[False],
    ) -> AnyResourceOperationAction: ...
    @overload
    @staticmethod
    def extract(
        type_: Literal[ResourceOperationType.CREATE],
        *,
        request: Request,
        from_state: bool = True,
        strict: Literal[True],
    ) -> CreateResourceOperationAction: ...
    @overload
    @staticmethod
    def extract(
        type_: Literal[ResourceOperationType.READ],
        *,
        request: Request,
        from_state: bool = True,
        strict: Literal[True],
    ) -> ReadResourceOperationAction: ...
    @overload
    @staticmethod
    def extract(
        type_: Literal[ResourceOperationType.UPDATE],
        *,
        request: Request,
        from_state: bool = True,
        strict: Literal[True],
    ) -> UpdateResourceOperationAction: ...
    @overload
    @staticmethod
    def extract(
        type_: Literal[ResourceOperationType.DELETE],
        *,
        request: Request,
        from_state: bool = True,
        strict: Literal[True],
    ) -> DeleteResourceOperationAction: ...
    @overload
    @staticmethod
    def extract(
        type_: OptResourceOperationType = None,
        *,
        request: Request,
        from_state: bool = True,
        strict: bool = False,
    ) -> AnyResourceOperationAction: ...
    @staticmethod
    def extract(
        type_: OptResourceOperationType = None,
        *,
        request: Request,
        from_state: bool = True,
        strict: bool = False,
    ) -> AnyResourceOperationAction:
        if from_state:
            action = request.state.operation_action
            if not strict:
                if not isinstance(action, ResourceOperationActions):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid resource_operation_action in request's state: {action}",
                    )
                return action

            else:
                if type_ is None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Argument 'type_' must be given for strict extraction",
                    )
                model = TYPE_ACTION_MODEL_MAP[type_]
                if not isinstance(action, model):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Mismatched 'resource_operation_action' type, expected '{model.__name__}' but received '{type(action).__name__}'",
                    )
                return action

        else:
            action = None
            update_type = None
            data_update_type = None
            status_update_type = None

            if request.method == "POST":
                action = CreateResourceOperationAction()
            elif request.method == "GET":
                action = ReadResourceOperationAction()
            elif request.method in ["PATCH", "PUT"]:
                if request.method == "PUT":
                    update_type = ResourceOperationUpdateType.DATA
                    data_update_type = ResourceOperationDataUpdateType.FULL
                elif request.method == "PATCH":
                    status_pattern = re.search(
                        r"/status/(delete|restore|deactivate|activate)(?:/.*)?$",
                        request.url.path,
                    )
                    if status_pattern:
                        update_type = ResourceOperationUpdateType.STATUS
                        action = status_pattern.group(1)
                        try:
                            status_update_type = ResourceOperationStatusUpdateType(
                                action
                            )
                        except ValueError:
                            # This shouldn't happen since regex already validates, but keep for safety
                            pass
                    else:
                        update_type = ResourceOperationUpdateType.DATA
                        data_update_type = ResourceOperationDataUpdateType.PARTIAL
                action = UpdateResourceOperationAction(
                    update_type=update_type,
                    data_update_type=data_update_type,
                    status_update_type=status_update_type,
                )
            elif request.method == "DELETE":
                action = DeleteResourceOperationAction()

            if action is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unable to determine resource operation action",
                )

            if not strict:
                if not isinstance(action, ResourceOperationActions):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid resource_operation_action in request's state: {action}",
                    )
                return action

            else:
                if type_ is None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Argument 'type_' must be given for strict extraction",
                    )
                model = TYPE_ACTION_MODEL_MAP[type_]
                if not isinstance(action, model):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Mismatched 'resource_operation_action' type, expected '{model.__name__}' but received '{type(action).__name__}'",
                    )
                return action

    @overload
    @staticmethod
    def as_dependency(
        *,
        from_state: bool = True,
        strict: Literal[False],
    ) -> Callable[..., AnyResourceOperationAction]: ...
    @overload
    @staticmethod
    def as_dependency(
        type_: Literal[ResourceOperationType.CREATE],
        *,
        from_state: bool = True,
        strict: Literal[True],
    ) -> Callable[..., CreateResourceOperationAction]: ...
    @overload
    @staticmethod
    def as_dependency(
        type_: Literal[ResourceOperationType.READ],
        *,
        from_state: bool = True,
        strict: Literal[True],
    ) -> Callable[..., ReadResourceOperationAction]: ...
    @overload
    @staticmethod
    def as_dependency(
        type_: Literal[ResourceOperationType.UPDATE],
        *,
        from_state: bool = True,
        strict: Literal[True],
    ) -> Callable[..., UpdateResourceOperationAction]: ...
    @overload
    @staticmethod
    def as_dependency(
        type_: Literal[ResourceOperationType.DELETE],
        *,
        from_state: bool = True,
        strict: Literal[True],
    ) -> Callable[..., DeleteResourceOperationAction]: ...
    @staticmethod
    def as_dependency(
        type_: OptResourceOperationType = None,
        *,
        from_state: bool = True,
        strict: bool = False,
    ) -> Callable[..., AnyResourceOperationAction]:

        def dependency(request: Request) -> AnyResourceOperationAction:
            return ResourceOperationActionFactory.extract(
                type_, request=request, from_state=from_state, strict=strict
            )

        return dependency
