from pyarrow import Table, BufferOutputStream



def bytesFrom(table: Table) -> bytes:
    from pyarrow.parquet import write_table
    buffer = BufferOutputStream()
    write_table(table, buffer)
    return buffer.getvalue().to_pybytes()
