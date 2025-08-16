import weaviate
import textwrap
from sentence_transformers import SentenceTransformer


WEAVIATE_COLLECTION = 'DBSchema'
embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
num_entries = 15

embedder = SentenceTransformer(embedding_model_name)


def get_schema_context(client: weaviate.Client, user_query: str, top_k=num_entries) -> str:

    query_vec = embedder.encode([user_query])[0].tolist()
    results = client.collections.get(WEAVIATE_COLLECTION).query.near_vector(
        near_vector=query_vec,
        limit=top_k
    )
    if not results.objects:
        return ""

    context_parts = []
    for obj in results.objects:
        tbl = obj.properties["tableName"]
        schema = obj.properties["schemaText"]
        context_parts.append(f"### {tbl}\n{schema}")
    return "\n\n".join(context_parts)


def build_sql_prompt(user_query: str, schema_context: str) -> str:
    return textwrap.dedent(
        f"""
        You are a Text-to-SQL assistant. Output ONLY SQL for the given schema. Use PostgreSQL dialect. No explanations. Enclose the answer between ```sql and ```"

        Use the provided database schema context to write the correct SQL query.
        Note that the payment table consists of multiple partitions, but you should access them via the main table name 'payment'.
        Do not use the individual partition names like 'payment_p2022_05' in the SQL.
        Also make sure that all the column names that you are using actually exist in the database.

        Database schema context:
        {schema_context}

        Natural language request:
        {user_query}

        SQL Query:
        """
    ).strip()