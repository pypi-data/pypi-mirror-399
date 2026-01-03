"""The 'worktoy' package provides a collection of utilities leveraging
advanced python features including custom metaclasses and the descriptor
protocol. The readme file included provides detailed documentation on the
included features. The modules provided depend on each other in
implementation, but can be used independently.

The package consists of thr following modules:
- utilities: A set of general-purpose utility functions and classes.
- waitaminute: Tools for managing execution flow and timing.
- core: Core functionalities and base classes for the package.
- desc: Descriptor protocol utilities.
- dispatch: Function and method dispatching used by overload system.
- mcls: Custom metaclass implementations.
- keenum: Enumeration utilities.
- ezdata: Dataclass implementation.
- work_io: Input/output utilities for file and directory management.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from . import utilities
from . import waitaminute
from . import core
from . import desc
from . import dispatch
from . import mcls
from . import keenum
from . import ezdata
from . import work_io

__all__ = [
  'utilities',
  'waitaminute',
  'core',
  'desc',
  'dispatch',
  'mcls',
  'keenum',
  'ezdata',
  'work_io',
]
