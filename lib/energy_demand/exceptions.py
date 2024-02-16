class UnexpectedNAError(Exception):
    """Unexpected NA error"""

    pass


def raise_exception_if_any_na(df):
    """Raise an exception if any NA is found in the dataframe"""
    from pdb import set_trace

    if df.isna().any().any():
        set_trace()
        raise UnexpectedNAError(f"Unexpected NA in dataframe")
