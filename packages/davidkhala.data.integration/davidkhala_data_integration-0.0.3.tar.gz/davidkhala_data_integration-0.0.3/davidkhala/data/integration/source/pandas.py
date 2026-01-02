from pyarrow import Table
from pandas import DataFrame


def toArrow(df: DataFrame) -> Table:
    return Table.from_pandas(df)
