from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    # 1) Prefer the public module if/when Polars exposes it (polars.typing)
    try:
        from polars.typing import PolarsDataType
    except Exception:
        # 2) For now, fall back to the private module (polars._typing)
        #    This avoids importing the deprecated polars.type_aliases.
        try:
            from polars._typing import PolarsDataType

        except Exception:
            # 3) Last resort: define the alias
            from polars.type_aliases import PolarsDataType as _PolarsDataType
            import polars as pl

            PolarsDataType = _PolarsDataType | pl.DataType
else:
    # At runtime we don't need the type alias; keep a lightweight placeholder.
    PolarsDataType = Any


__all__ = ['PolarsDataType']
