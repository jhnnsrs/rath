from turms.types.object import GraphQLObject
from turms.types.object import GraphQLObject
from pydantic.fields import Field
from typing import Optional, List, Dict, Union, Literal
from enum import Enum
from turms.types.object import GraphQLInputObject
from turms.types.object import GraphQLObject
from rath.turms.operation import GraphQLQuery
from rath.turms.operation import GraphQLMutation
from rath.turms.operation import GraphQLSubscription


class OmeroFileType(str, Enum):
    """An enumeration."""

    TIFF = "TIFF"
    "Tiff"
    JPEG = "JPEG"
    "Jpeg"
    MSR = "MSR"
    "MSR File"
    CZI = "CZI"
    "Zeiss Microscopy File"
    UNKNOWN = "UNKNOWN"
    "Unwknon File Format"


class RepresentationVariety(str, Enum):
    """An enumeration."""

    MASK = "MASK"
    "Mask (Value represent Labels)"
    VOXEL = "VOXEL"
    "Voxel (Value represent Intensity)"
    UNKNOWN = "UNKNOWN"
    "Unknown"


class RepresentationVarietyInput(str, Enum):
    """Variety expresses the Type of Representation we are dealing with"""

    MASK = "MASK"
    "Mask (Value represent Labels)"
    VOXEL = "VOXEL"
    "Voxel (Value represent Intensity)"
    UNKNOWN = "UNKNOWN"
    "Unknown"


class OmeroRepresentationInput(GraphQLInputObject):
    None
    planes: Optional[List[Optional["PlaneInput"]]]
    channels: Optional[List[Optional["ChannelInput"]]]
    physicalSize: Optional["PhysicalSizeInput"]
    scale: Optional[List[Optional[float]]]


class PlaneInput(GraphQLInputObject):
    None
    zIndex: Optional[int]
    yIndex: Optional[int]
    xIndex: Optional[int]
    cIndex: Optional[int]
    tIndex: Optional[int]
    exposureTime: Optional[float]
    deltaT: Optional[float]


class ChannelInput(GraphQLInputObject):
    None
    name: Optional[str]
    emmissionWavelength: Optional[float]
    excitationWavelength: Optional[float]
    acquisitionMode: Optional[str]
    color: Optional[str]


class PhysicalSizeInput(GraphQLInputObject):
    None
    x: Optional[int]
    y: Optional[int]
    z: Optional[int]
    t: Optional[int]
    c: Optional[int]


OmeroRepresentationInput.update_forward_refs()


class RepresentationFragmentSample(GraphQLObject):
    """Samples are storage containers for representations. A Sample is to be understood analogous to a Biological Sample. It existed in Time (the time of acquisiton and experimental procedure),
    was measured in space (x,y,z) and in different modalities (c). Sample therefore provide a datacontainer where each Representation of
    the data shares the same dimensions. Every transaction to our image data is still part of the original acuqistion, so also filtered images are refering back to the sample
    """

    typename: Optional[Literal["Sample"]] = Field(alias="__typename")
    name: str


class RepresentationFragment(GraphQLObject):
    typename: Optional[Literal["Representation"]] = Field(alias="__typename")
    sample: Optional[RepresentationFragmentSample]
    "The Sample this representation belongs to"
    type: Optional[str]
    "The Representation can have varying types, consult your API"
    id: str
    store: Optional[str]
    variety: RepresentationVariety
    "The Representation can have varying types, consult your API"
    name: Optional[str]
    "Cleartext name"


class From_xarrayMutation(GraphQLMutation):
    fromXArray: Optional[RepresentationFragment]

    class Meta:
        domain = "mikro"
        document = "fragment Representation on Representation {\n  sample {\n    name\n  }\n  type\n  id\n  store\n  variety\n  name\n}\n\nmutation from_xarray($xarray: XArray!, $name: String, $origins: [ID], $tags: [String], $sample: ID, $omero: OmeroRepresentationInput) {\n  fromXArray(\n    xarray: $xarray\n    name: $name\n    origins: $origins\n    tags: $tags\n    sample: $sample\n    omero: $omero\n  ) {\n    ...Representation\n  }\n}"


class Get_random_repQuery(GraphQLQuery):
    randomRepresentation: Optional[RepresentationFragment]

    class Meta:
        domain = "mikro"
        document = "fragment Representation on Representation {\n  sample {\n    name\n  }\n  type\n  id\n  store\n  variety\n  name\n}\n\nquery get_random_rep {\n  randomRepresentation {\n    ...Representation\n  }\n}"


async def afrom_xarray(
    xarray: str,
    name: str = None,
    origins: List[str] = None,
    tags: List[str] = None,
    sample: str = None,
    omero: OmeroRepresentationInput = None,
) -> RepresentationFragment:
    """from_xarray

    Creates a Representation

    Arguments:
        xarray (XArray): XArray
        name (String, Optional): String
        origins (List[ID], Optional): ID
        tags (List[String], Optional): String
        sample (ID, Optional): ID
        omero (OmeroRepresentationInput, Optional): OmeroRepresentationInput

    Returns:
        RepresentationFragment: The returned Mutation"""
    return (
        await From_xarrayMutation.aexecute(
            {
                "xarray": xarray,
                "name": name,
                "origins": origins,
                "tags": tags,
                "sample": sample,
                "omero": omero,
            }
        )
    ).fromXArray


def from_xarray(
    xarray: str,
    name: str = None,
    origins: List[str] = None,
    tags: List[str] = None,
    sample: str = None,
    omero: OmeroRepresentationInput = None,
) -> RepresentationFragment:
    """from_xarray

    Creates a Representation

    Arguments:
        xarray (XArray): XArray
        name (String, Optional): String
        origins (List[ID], Optional): ID
        tags (List[String], Optional): String
        sample (ID, Optional): ID
        omero (OmeroRepresentationInput, Optional): OmeroRepresentationInput

    Returns:
        RepresentationFragment: The returned Mutation"""
    return From_xarrayMutation.execute(
        {
            "xarray": xarray,
            "name": name,
            "origins": origins,
            "tags": tags,
            "sample": sample,
            "omero": omero,
        }
    ).fromXArray


async def aget_random_rep() -> RepresentationFragment:
    """get_random_rep

    Get a single representation by ID

    Arguments:

    Returns:
        RepresentationFragment: The returned Mutation"""
    return (await Get_random_repQuery.aexecute({})).randomRepresentation


def get_random_rep() -> RepresentationFragment:
    """get_random_rep

    Get a single representation by ID

    Arguments:

    Returns:
        RepresentationFragment: The returned Mutation"""
    return Get_random_repQuery.execute({}).randomRepresentation
