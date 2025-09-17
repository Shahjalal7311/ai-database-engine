def format_results(columns, rows, max_rows=100):
    """Format SQL query results into a readable table or list"""
    if not columns or not rows:
        return "No results found."
    # Limit rows
    rows = rows[:max_rows]
    # If both 'title' and 'category'/'category_name' columns exist, format for user clarity
    col_names = [c.lower() for c in columns]
    # Try to find a title/name column
    title_col = None
    for t in ['title', 'name', 'article_title', 'article_name']:
        if t in col_names:
            title_col = t
            break
    # Try to find a category column
    category_col = None
    for c in ['name','category', 'category_name', 'category_title', 'categories', 'categoryid', 'category_id', 'cat_name', 'cat_title']:
        if c in col_names:
            category_col = c
            break
    if title_col and category_col:
        out = []
        for idx, row in enumerate(rows, 1):
            title = row[col_names.index(title_col)]
            category = row[col_names.index(category_col)]
            out.append(f"{idx}. Title: {title}\n   Category: {category}\n---")
        return "\n".join(out)
    # Otherwise, fallback to tabular output
    header = " | ".join(columns)
    lines = [header, "-" * len(header)]
    for row in rows:
        lines.append(" | ".join(str(cell) for cell in row))
    return "\n".join(lines)

def format_schema_info(table_info):
    """Format database schema information"""
    return f"Database Schema:\n{table_info}"