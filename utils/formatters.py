def format_results(columns, rows, max_rows=100):
    """Format SQL query results into a readable table"""
    if not rows:
        return "No results found."
    
    if len(rows) > max_rows:
        rows = rows[:max_rows]
        truncated = True
    else:
        truncated = False
    
    # Create header
    header = "| " + " | ".join(str(col) for col in columns) + " |"
    separator = "|" + "|".join(["---"] * len(columns)) + "|"
    
    # Create rows
    formatted_rows = []
    for row in rows:
        formatted_row = "| " + " | ".join(str(cell) for cell in row) + " |"
        formatted_rows.append(formatted_row)
    
    # Combine everything
    result = "\n".join([header, separator] + formatted_rows)
    
    if truncated:
        result += f"\n\n(Showing first {max_rows} rows out of {len(rows)})"
    
    return result

def format_schema_info(table_info):
    """Format database schema information"""
    return f"Database Schema:\n{table_info}"