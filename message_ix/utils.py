import warnings

from message_ix.util import make_df

__all__ = ["make_df"]

warnings.warn(
    "Using or importing make_df() from 'message_ix.utils' instead of from 'message_ix' "
    "or is deprecated since message_ix 3.2, and in 5.0 it will stop working",
    DeprecationWarning,
)
