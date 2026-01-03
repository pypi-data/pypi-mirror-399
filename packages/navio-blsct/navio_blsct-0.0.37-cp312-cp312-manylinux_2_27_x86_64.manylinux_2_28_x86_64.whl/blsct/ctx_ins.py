from . import blsct
from .ctx_in import CTxIn
from typing import Any;

# holds a reference fo std::vector<CTxIn>
class CTxIns:
  def __init__(self, obj: Any):
    self.obj = obj

  def at(self, i: int) -> CTxIn:
    obj = blsct.get_ctx_in_at(self.obj, i)    
    return CTxIn.from_obj(obj)

  def size(self) -> int:
    return blsct.get_ctx_ins_size(self.obj)
  
  def __getitem__(self, i: int) -> CTxIn:
    if i < 0:
      i += self.size()
    if not (0 <= i < self.size()):
      raise IndexError(f"Index {i} is out of range; the size is {self.size()}")
    return self.at(i)

