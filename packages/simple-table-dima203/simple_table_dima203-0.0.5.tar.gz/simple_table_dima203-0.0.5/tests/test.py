from src.simple_table_dima203 import Table, SINGLE_BORDER


class TestTable:
    def test_table_print(self) -> None:
        table = Table(keys=["name", "age"], style=SINGLE_BORDER)
        table.none_format = '-'
        table.min_table_width = 20
        table.max_table_width = 30
        table.max_width["age"] = 4
        table.min_width["age"] = 4
        table.align["name"] = "<"
        table.add_row(["Alex gfjdkljgkdjklfgld", 22])
        print(table)
        table.add_column("id", alias="tabel", default=0, align="<")
        table.min_width["id"] = 5
        table.add_row(["User", 13, 2])
        table.add_delimiter()
        table.add_row(["Average", 17.5, ""])
        print(table)
