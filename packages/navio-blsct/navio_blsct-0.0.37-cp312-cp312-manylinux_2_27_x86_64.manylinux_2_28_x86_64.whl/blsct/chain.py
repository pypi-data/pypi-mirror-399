from . import blsct
from enum import IntEnum

class Chain(IntEnum):
    Mainnet = 0
    Testnet = 1
    Signet  = 2
    Regtest = 3

def get_chain() -> Chain:
  """
  get the current chain

  >>> from blsct import Chain, get_chain
  >>> chain = get_chain()
  >>> chain
  Chain.Mainnet
  >>> int(chain)
  0
  >>> chain.name
  'Mainnet'
  """
  return Chain(blsct.get_blsct_chain())

def set_chain(chain: Chain) -> None:
  """
  set the current chain

  >>> from blsct import chain, set_chain
  >>> set_chain(Chain.Testnet)
  """
  blsct.set_blsct_chain(chain.value)
