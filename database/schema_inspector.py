from database.connection import db_connection
from sqlalchemy import text, inspect
from config.settings import settings

class SchemaInspector:
    def __init__(self):
        self.engine = db_connection.get_engine()
        
    def get_table_schema(self, table_name):
        """Get table schema for any table directly using SQL"""
        try:
            if settings.DATABASE_TYPE == 'mysql':
                schema_query = f"""
                SELECT 
                    COLUMN_NAME, 
                    DATA_TYPE, 
                    IS_NULLABLE, 
                    COLUMN_DEFAULT,
                    COLUMN_KEY,
                    EXTRA
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = '{table_name}' 
                AND TABLE_SCHEMA = DATABASE()
                ORDER BY ORDINAL_POSITION
                """
            else:
                schema_query = f"""
                SELECT 
                    column_name, 
                    data_type, 
                    is_nullable, 
                    column_default
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
                """
            with self.engine.connect() as conn:
                result = conn.execute(text(schema_query))
                columns = result.fetchall()  # Always fetch all results before next query
                result.close()  # Explicitly close result set (defensive for MySQL)
                # Format schema information
                schema_info = f"CREATE TABLE {table_name} (\n"
                for col in columns:
                    if settings.DATABASE_TYPE == 'mysql':
                        col_name, data_type, is_nullable, default_val, column_key, extra = col
                    else:
                        col_name, data_type, is_nullable, default_val = col
                        column_key, extra = '', ''
                    null_str = " NOT NULL" if is_nullable == 'NO' else ""
                    default_str = f" DEFAULT {default_val}" if default_val else ""
                    key_str = " PRIMARY KEY" if column_key == 'PRI' else ""
                    extra_str = f" {extra}" if extra else ""
                    schema_info += f"    {col_name} {data_type}{null_str}{default_str}{key_str}{extra_str},\n"
                schema_info = schema_info.rstrip(',\n') + "\n);"
                return schema_info
        except Exception as e:
            print(f"Error getting schema for {table_name}: {e}")
            return f"CREATE TABLE {table_name} (...);"