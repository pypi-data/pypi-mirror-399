"""
ER diagram generation component using in4viz library.
"""

from in4viz import ERDiagram, Table as In4vizTable, Column as In4vizColumn, LineType, Cardinality
from dbgear.models.schema import SchemaManager
from dbgear.models.table import Table
from dbgear.models.column import Column


def collect_related_tables(
    all_tables: dict[str, Table],
    start_table_name: str,
    direction: str,
    level: int,
    visited: set[str] | None = None
) -> set[str]:
    """
    Recursively collect related tables.

    Args:
        all_tables: Dictionary of all tables in the schema
        start_table_name: Name of the starting table
        direction: 'refs' (tables referencing this) or 'fks' (tables referenced by this)
        level: How many levels deep to search
        visited: Set of already visited table names

    Returns:
        Set of table names including the start table
    """
    if visited is None:
        visited = set()

    if level < 0 or start_table_name in visited:
        return visited

    visited.add(start_table_name)

    if level == 0:
        return visited

    start_table = all_tables.get(start_table_name)
    if not start_table:
        return visited

    if direction == 'fks':
        # Collect tables that this table references (via foreign keys)
        for relation in start_table.relations:
            target_table_name = relation.target.table_name
            if target_table_name in all_tables:
                collect_related_tables(
                    all_tables, target_table_name, direction, level - 1, visited
                )

    elif direction == 'refs':
        # Collect tables that reference this table
        for table_name, table in all_tables.items():
            if table_name in visited:
                continue
            for relation in table.relations:
                if relation.target.table_name == start_table_name:
                    collect_related_tables(
                        all_tables, table_name, direction, level - 1, visited
                    )
                    break

    return visited


def dbgear_to_in4viz_column(column: Column) -> In4vizColumn:
    """
    Convert DBGear Column to in4viz Column.

    Args:
        column: DBGear Column object

    Returns:
        in4viz Column object
    """
    # Get column type display string
    col_type = column.column_type
    type_str = col_type.base_type if col_type else "UNKNOWN"

    if col_type and col_type.length:
        type_str += f"({col_type.length}"
        if col_type.precision:
            type_str += f",{col_type.precision}"
        type_str += ")"

    return In4vizColumn(
        name=column.column_name,
        logical_name=column.display_name or column.column_name,
        type=type_str,
        primary_key=(column.primary_key is not None),
        nullable=column.nullable,
        foreign_key=False,  # Will be set when processing relations
        index=False  # Will be set when processing indexes
    )


def dbgear_to_in4viz_table(table: Table, table_name: str) -> In4vizTable:
    """
    Convert DBGear Table to in4viz Table.

    Args:
        table: DBGear Table object
        table_name: Name of the table

    Returns:
        in4viz Table object
    """
    columns = [dbgear_to_in4viz_column(col) for col in table.columns]

    # Mark foreign key columns
    for relation in table.relations:
        for bind in relation.bind_columns:
            for col in columns:
                if col.name == bind.source_column:
                    col.foreign_key = True

    # Mark indexed columns
    for index in table.indexes:
        for index_col in index.columns:
            for col in columns:
                if col.name == index_col:
                    col.index = True

    return In4vizTable(
        name=table_name,
        logical_name=table.display_name or table_name,
        columns=columns
    )


def generate_er_diagram_svg(
    schema_manager: SchemaManager,
    schema_name: str,
    center_table: str,
    ref_level: int = 1,
    fk_level: int = 1
) -> str:
    """
    Generate ER diagram SVG centered on a specific table.

    Args:
        schema_manager: SchemaManager instance
        schema_name: Name of the schema
        center_table: Name of the table to center the diagram on
        ref_level: How many levels of referencing tables to include (default: 1)
        fk_level: How many levels of referenced tables to include (default: 1)

    Returns:
        SVG string of the ER diagram

    Raises:
        ValueError: If schema or table not found
        Exception: Any errors from in4viz library
    """
    # Get all tables in the schema
    schemas = schema_manager.schemas
    schema = schemas.get(schema_name)
    if not schema:
        raise ValueError(f"Schema '{schema_name}' not found")

    all_tables = {table.table_name: table for table in schema.tables}

    if center_table not in all_tables:
        raise ValueError(f"Table '{center_table}' not found in schema '{schema_name}'")

    # Collect related tables
    tables_to_include = {center_table}

    # Add tables that reference the center table (refs direction)
    if ref_level > 0:
        ref_tables = collect_related_tables(
            all_tables, center_table, 'refs', ref_level, set()
        )
        tables_to_include.update(ref_tables)

    # Add tables that the center table references (fks direction)
    if fk_level > 0:
        fk_tables = collect_related_tables(
            all_tables, center_table, 'fks', fk_level, set()
        )
        tables_to_include.update(fk_tables)

    # Create ER diagram
    diagram = ERDiagram()

    # Add tables to diagram
    in4viz_tables = {}
    for table_name in tables_to_include:
        table = all_tables[table_name]
        in4viz_table = dbgear_to_in4viz_table(table, table_name)
        diagram.add_table(in4viz_table)
        in4viz_tables[table_name] = in4viz_table

    # Add edges (relationships)
    for table_name in tables_to_include:
        table = all_tables[table_name]
        for relation in table.relations:
            target_name = relation.target.table_name
            if target_name in tables_to_include:
                # Convert cardinality from DBGear format to in4viz format
                # DBGear uses: '1', '0..1', '0..*', '1..*'
                # in4viz Cardinality(source, target)
                cardinality = Cardinality(
                    relation.cardinarity_source,
                    relation.cardinarity_target
                )

                diagram.add_edge(
                    table_name,
                    target_name,
                    LineType.STRAIGHT,
                    cardinality
                )

    # Generate and return SVG
    return diagram.render()
