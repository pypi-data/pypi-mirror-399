from . import blsct
from .ctx_out import CTxOut
from typing import Any;

# holds a reference fo std::vector<CTxOut>
class CTxOuts:
  def __init__(self, obj: Any):
    self.obj = obj

  def at(self, i: int) -> CTxOut:
    obj = blsct.get_ctx_out_at(self.obj, i)    
    return CTxOut.from_obj(obj)

  def size(self) -> int:
    return blsct.get_ctx_outs_size(self.obj)
  
  def __getitem__(self, i: int) -> CTxOut:
    if i < 0:
      i += self.size()
    if not (0 <= i < self.size()):
      raise IndexError(f"Index {i} is out of range; the size is {self.size()}")
    return self.at(i)


