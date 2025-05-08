from rath.scalars import ID
from pydantic import BaseModel, Field


class IDModel(BaseModel):
    id: ID = Field(default_factory=ID)
    """The id field is a scalar that can be used to represent an ID"""
    
    

def test_id_serialization():
    """Test the ID serialization"""
    
    x = IDModel(id="123")
    assert x.id == "123"
    
    
def test_id_model_serialization():
    """Test the ID serialization of a BaseModel"""
    
    x = IDModel(id="123")
    
    iother_model = IDModel(id=x)
    assert iother_model.id == "123"