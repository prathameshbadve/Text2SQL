import re
import sys
from pathlib import Path
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import numpy as np

import weaviate
import weaviate.classes as wvc
from weaviate.exceptions import WeaviateBaseError

def parse_db_schema_markdown(md_file_path: str) -> List[Dict]:

    """
    Parses a Markdown database schema file into a list of table metadata dictionaries.
    
    Args:
        md_file_path (str or Path): Path to the db_schema.md file.
    
    Returns:
        list[dict]: List of dictionaries with keys:
            - tableName (str)
            - schemaText (str)
            - columns (list of dict with Column, Type, Nullable, Default)
            - primaryKey (list of str)
            - foreignKeys (list of dict with columns and references)
    """

    # Read md file
    try:
        content = Path(md_file_path).read_text(encoding="utf-8")
    except FileNotFoundError:
        sys.exit(f"❌ ERROR: File not found: {md_file_path}")

    # Split by "## Table:" markers
    tables_raw = re.split(r"## Table: ", content)
    tables = []

    for table_raw in tables_raw[1:]:                                            # Skip first split part before the first table
        lines = table_raw.strip().splitlines()
        
        # First line is table name
        table_name = lines[0].strip()

        # Extract columns from the markdown table
        columns = []
        col_section = False
        for line in lines:
            if line.startswith("|--"):
                col_section = True
                continue
            if col_section:
                if line.strip() == "" or line.startswith("---"):
                    continue
                if not line.startswith("|"):
                    break                                                       # End of columns section
                parts = [p.strip() for p in line.strip("|").split("|")]
                if len(parts) == 4:
                    columns.append({
                        "column": parts[0],
                        "type": parts[1],
                        "nullable": parts[2],
                        "default": parts[3]
                    })

        # Extract Primary Key
        pk_match = re.search(r"\*\*Primary Key:\*\*\s*(.+)", table_raw)
        if pk_match:
            primary_key = [col.strip() for col in pk_match.group(1).split(",")]
        else:
            primary_key = []

        # Extract Foreign Keys
        foreign_keys = []
        fk_matches = re.findall(r"[-•]\s*\[(.+?)\]\s*→\s*(\w+)\((\w+)\)", table_raw)
        for fk_cols, ref_table, ref_col in fk_matches:
            cols = [c.strip() for c in fk_cols.split(",")]
            foreign_keys.append({
                "columns": cols,
                "ref_table": ref_table,
                "ref_columns": [ref_col]
            })

        # Create schema text summary (good for embeddings)
        schema_text_parts = [f"Table: {table_name}", "Columns:"]
        for col in columns:
            schema_text_parts.append(
                f"{col['column']} ({col['type']}, Nullable={col['nullable']}, Default={col['default']})"
            )
        if primary_key:
            schema_text_parts.append(f"Primary Key: {', '.join(primary_key)}")
        if foreign_keys:
            for fk in foreign_keys:
                schema_text_parts.append(
                    f"Foreign Key: {', '.join(fk['columns'])} → {fk['ref_table']}({', '.join(fk['ref_columns'])})"
                )
        schema_text = "\n".join(schema_text_parts)

        tables.append({
            "tableName": table_name,
            "schemaText": schema_text,
            "columns": columns,
            "primaryKey": primary_key,
            "foreignKeys": foreign_keys
        })

    print(f"✅ Parsed {len(tables)} tables from schema file.")
    return tables


def create_embeddings(table_entries: List[Dict], model_name='sentence-transformers/all-MiniLM-L6-v2') -> np.ndarray:

    """
    Generate embeddings for table metadata text using all-MiniLM-L6-v2 model.
    
    Args:
        table_entries (list of dict): List of table metadata dicts with 'schemaText' key.
    
    Returns:
        list of dict: Each dict contains 'tableName' and 'embedding' vector.
    """

    print(f"Loading embedding model = {model_name}")
    model = SentenceTransformer(model_name)

    schema_texts = [entry["schemaText"] for entry in table_entries]
    print(f"🔄 Generating embeddings for {len(schema_texts)} entries...")
    
    vectors = model.encode(schema_texts, show_progress_bar=True)
    print("✅ Embeddings generated.")
    
    return vectors


def setup_weaviate_collection(client: weaviate.Client, collection_name='DBSchema'):

    """
    Creates the Weaviate collection if not exists.
    """

    try:
        if collection_name in [c.name for c in client.collections.list_all()]:
            print(f"Collection '{collection_name}' already exists. Skipping creation.")
            return
        
        # Create new collection for our DB schema
        client.collections.create(
            name=collection_name,
            properties = [
                wvc.config.Property(name="tableName", data_type=wvc.config.DataType.TEXT),
                wvc.config.Property(name="schemaText", data_type=wvc.config.DataType.TEXT)
            ]
        )
        print(f'{collection_name} collection created successfully.')
        
    except WeaviateBaseError as e:
        sys.exit(f"❌ Failed to create collection in Weaviate: {e}")


def batch_insert_embeddings(client: weaviate.Client, collection_name: str, table_entries: List[Dict], embeddings: np.ndarray, batch_size=20):

    """
    Batch insert table metadata and vectors into Weaviate.
    """

    col = client.collections.get(collection_name)

    print(f"🔄 Inserting {len(table_entries)} objects in batches of {batch_size}...")
    for i in range(0, len(table_entries), batch_size):
        batch_items = table_entries[i:i+batch_size]
        batch_vectors = embeddings[i:i+batch_size]

        with col.batch.dynamic() as batch:
            for obj, vec in zip(batch_items, batch_vectors):
                try:
                    batch.add_object(
                        properties={
                            "tableName": obj["tableName"],
                            "schemaText": obj["schemaText"]
                        },
                        vector=vec.tolist()
                    )
                except Exception as e:
                    print(f"❌ Failed to insert {obj['tableName']}: {e}")

    print("✅ Batch insertion completed.")


def test_query(client: weaviate.Client, collection_name: str, query_text: str, limit=3):

    """Test a similarity search in Weaviate."""

    print(f"🔍 Testing query: '{query_text}'")
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    query_vec = model.encode(query_text).tolist()

    results = client.collections.get(collection_name).query.near_vector(
        near_vector=query_vec,
        limit=limit
    )

    print('-----')
    print(type(results))
    print('-----')

    for obj in results.objects:
        print(f"📌 {obj.properties['tableName']} -> {obj.properties['schemaText'][:80]}...")
