import typing

T = typing.TypeVar('T')
C = typing.TypeVar('C')


class TableField:
    property_name: str
    header_name: str
    formatter: typing.Optional[typing.Callable[[T], str]]
    picker: typing.Optional[typing.Callable[[C], typing.Any]]

    def __init__(
            self, property_name: str,
            header_name: typing.Optional[str] = None,
            formatter: typing.Optional[typing.Callable[[T], str]] = None,
            picker: typing.Optional[typing.Callable[[C], typing.Any]] = None,
    ):
        self.property_name = property_name
        self.header_name = header_name if header_name is not None else property_name.upper()
        self.formatter = formatter
        self.picker = picker


class ShowMixin(object):
    # class property
    table_fields: typing.List[TableField] = []
    wide_table_extra_fields: typing.List[TableField] = []

    @classmethod
    def table_title(cls, wide: bool = False) -> typing.List[str]:
        fields = cls.table_fields.copy()
        if wide and len(cls.wide_table_extra_fields) > 0:
            fields.extend(cls.wide_table_extra_fields)

        return [field.header_name for field in fields]

    def table_row(self, wide: bool = False) -> typing.List:
        result = self.convert(self.table_fields)
        if wide:
            extra = self.convert(self.wide_table_extra_fields)
            result.extend(extra)
        return result

    def convert(self, fields: typing.List[TableField]) -> typing.List:
        result = []
        for field in fields:
            if field.picker is not None:
                value = field.picker(self)
            elif hasattr(self, field.property_name):
                value = getattr(self, field.property_name)
            else:
                result.append('None')
                continue

            if field.formatter is None:
                result.append(value)
            else:
                result.append(field.formatter(value))
        return result
