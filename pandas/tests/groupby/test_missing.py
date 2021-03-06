import numpy as np
import pytest

import pandas as pd
from pandas import DataFrame, Index, date_range
import pandas._testing as tm


@pytest.mark.parametrize("func", ["ffill", "bfill"])
def test_groupby_column_index_name_lost_fill_funcs(func):
    # GH: 29764 groupby loses index sometimes
    df = pd.DataFrame(
        [[1, 1.0, -1.0], [1, np.nan, np.nan], [1, 2.0, -2.0]],
        columns=pd.Index(["type", "a", "b"], name="idx"),
    )
    df_grouped = df.groupby(["type"])[["a", "b"]]
    result = getattr(df_grouped, func)().columns
    expected = pd.Index(["a", "b"], name="idx")
    tm.assert_index_equal(result, expected)


@pytest.mark.parametrize("func", ["ffill", "bfill"])
def test_groupby_fill_duplicate_column_names(func):
    # GH: 25610 ValueError with duplicate column names
    df1 = pd.DataFrame({"field1": [1, 3, 4], "field2": [1, 3, 4]})
    df2 = pd.DataFrame({"field1": [1, np.nan, 4]})
    df_grouped = pd.concat([df1, df2], axis=1).groupby(by=["field2"])
    expected = pd.DataFrame(
        [[1, 1.0], [3, np.nan], [4, 4.0]], columns=["field1", "field1"]
    )
    result = getattr(df_grouped, func)()
    tm.assert_frame_equal(result, expected)


def test_ffill_missing_arguments():
    # GH 14955
    df = pd.DataFrame({"a": [1, 2], "b": [1, 1]})
    with pytest.raises(ValueError, match="Must specify a fill"):
        df.groupby("b").fillna()


def test_fill_consistency():

    # GH9221
    # pass thru keyword arguments to the generated wrapper
    # are set if the passed kw is None (only)
    df = DataFrame(
        index=pd.MultiIndex.from_product(
            [["value1", "value2"], date_range("2014-01-01", "2014-01-06")]
        ),
        columns=Index(["1", "2"], name="id"),
    )
    df["1"] = [
        np.nan,
        1,
        np.nan,
        np.nan,
        11,
        np.nan,
        np.nan,
        2,
        np.nan,
        np.nan,
        22,
        np.nan,
    ]
    df["2"] = [
        np.nan,
        3,
        np.nan,
        np.nan,
        33,
        np.nan,
        np.nan,
        4,
        np.nan,
        np.nan,
        44,
        np.nan,
    ]

    expected = df.groupby(level=0, axis=0).fillna(method="ffill")
    result = df.T.groupby(level=0, axis=1).fillna(method="ffill").T
    tm.assert_frame_equal(result, expected)
