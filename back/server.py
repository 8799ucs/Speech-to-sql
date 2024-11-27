from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import pipeline
import google.generativeai as genai
import re
import sqlite3 
import duckdb
from pymongo import MongoClient
from bson import ObjectId
import random
import string
import json

app = Flask(__name__)
CORS(app)

sql_generator = pipeline("text2text-generation", model="SwastikM/bart-large-nl2sql")
DATABASE_FILE = 'databases.json'

@app.route('/generate', methods=['POST'])
def generate_random_word(length=6):
    """Generate a random word of given length."""
    name=request.json['username']
    print(name)
    with open(DATABASE_FILE, 'r') as file:
        database = json.load(file)
    word=''.join(random.choices(string.ascii_lowercase, k=length))
    print(word)
    database[name] = word
    with open(DATABASE_FILE, 'w') as file:
        json.dump(database, file, indent=4)
    return {"message": "Word added successfully", "name": name, "word": word}


@app.route('/process_text', methods=['POST'])
def preprocess_text():
    text_input = request.json['text']
    database = request.json['database']
    username=request.json['user']
    print(database)
    print(username)
    with open(DATABASE_FILE, 'r') as file:
        dblist = json.load(file)
    dbname=dblist[username]
    print(dbname)
    genai.configure(api_key='AIzaSyDaCsJGuR5nBmKQf1Pp_aRSGwu1x9N_yKM')

    # LLM-Based Understanding
    prompt = f"Convert this into SQL query : {text_input} give me only query wihtout 'sql'"
    model = genai.GenerativeModel()
    response = model.generate_content(prompt)
    llm_query = response.text.strip()

    # Rule-Based Refinement
    # Handle DDL (Data Definition Language)
    if "CREATE TABLE" in llm_query:
        # Extract table name and column definitions from llm_query (more complex parsing needed)
        sql_query = llm_query  # Replace with actual parsing logic

    elif "ALTER TABLE" in llm_query:
        match = re.search(r"(ALTER TABLE (\w+) (.*))", llm_query, re.IGNORECASE)
        if match:
            table_name = match.groups(1)
            operation = match.groups(2)
            if "RENAME COLUMN" in operation:
                # Extract old and new column names
                sql_query = f"ALTER TABLE {table_name} RENAME COLUMN {table_name} TO {table_name};"
            else:
                # Handle other ALTER TABLE operations (e.g., ADD COLUMN, DROP COLUMN)
                sql_query = llm_query  # Replace with specific parsing logic
        else:
            sql_query = llm_query  # Handle other ALTER TABLE cases
        # Handle DML (Data Manipulation Language) - Basic example for INSERT
    elif "INSERT INTO" in llm_query:
        # Extract table name and values from llm_query (more complex parsing needed)
        sql_query = llm_query  # Replace with actual parsing logic
    # Handle DQL (Data Query Language) - Basic example for SELECT
    elif "SELECT" in llm_query:
        # Extract table name, columns, and conditions from llm_query (more complex parsing needed)
        sql_query = llm_query  # Replace with actual parsing logic
    else:
        # Handle other cases or fallback to LLM-generated query
        sql_query = llm_query

    if(database.lower()=="sqlite"):
        results = execute_sqlite_query(llm_query,dbname)
    elif(database.lower()=="mongodb"):
        results=execute_mongo_query(llm_query,dbname)
        return results
    elif(database.lower()=="duckdb"):
        results=execute_duckdb_query(llm_query,dbname)


    return jsonify(results)


def execute_sqlite_query(query,dbname):
    datab=dbname+".db"
    conn = sqlite3.connect(datab)
    cursor = conn.cursor()
    cursor.execute(query)
    if cursor.description is not None:
        column_names = [desc[0] for desc in cursor.description]
    else:
        column_names="columns" 

    results = cursor.fetchall()
    conn.commit()
    conn.close()
    print(results)
    return column_names, results

# Connect to MongoDB
def connect_to_mongo(db_name, collection_name):
    client = MongoClient("mongodb+srv://Shameem:Sha123@cluster0.ubezwan.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")  # Adjust with your MongoDB URI
    db = client[db_name]
    collection = db[collection_name]
    return collection

# Function to convert a simple SQL SELECT query to a MongoDB query
def convert_sql_to_mongo(sql_query):
    sql_query = sql_query.strip().lower()
    
    # Extract components of the SQL query
    if sql_query.startswith("select"):
        if sql_query.endswith(';'):
            sql_query = sql_query[:-1]
        parts = sql_query.split("from")
        fields_part = parts[0].replace("select", "").strip()
        fields = {field.strip(): 1 for field in fields_part.split(",")} if fields_part != "*" else {}
        

        table_part = parts[1].strip()
        table_name = table_part.split("where")[0].strip() if "where" in table_part else table_part
        
        # Handle WHERE clause
        where_clause = {}
        if "where" in table_part:
            conditions = table_part.split("where")[1].strip()
            for condition in conditions.split("and"):
                field, value = condition.split("=")
                where_clause[field.strip()] = value.strip().strip("'\"")  # Remove quotes

        client = MongoClient("mongodb+srv://Shameem:Sha123@cluster0.ubezwan.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        db = client["vivitsu"]
        collection = db[table_name]
        results = collection.find(where_clause, fields)
        return list(results)
    elif sql_query.startswith("CREATE TABLE"):
        parts = sql_query.split()
        collection_name = parts[2]

        # Create a MongoDB client (replace with your connection string)
        client = MongoClient("mongodb+srv://Shameem:Sha123@cluster0.ubezwan.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        db = client["vivitsu"]
        collection = db[collection_name]

        # Create an index on the 'id' field for efficient querying
        collection.create_index("id")

        return f"Created MongoDB collection: {collection_name}"
    elif sql_query.startswith("INSERT INTO"):
        parts = sql_query.split()
        collection_name = parts[2]

        try:
            field_names_str = parts[3].strip('()')
            values_str = parts[-1].strip('();')

            field_names = [field.strip() for field in field_names_str.split(',') if field.strip()]
            values = [value.strip() for value in values_str.split(',') if value.strip()]
            print(field_names)
            print(values)

            # Check for mismatch
            if len(field_names) != len(values):
                raise ValueError("Number of field names and values mismatch")

            # Create a dictionary to represent the MongoDB document
            document = {}
            for field, value in zip(field_names, values):
                document[field] = value
                

            # Insert the document into the MongoDB collection
            client = MongoClient("mongodb+srv://Shameem:Sha123@cluster0.ubezwan.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
            db = client["vivitsu"]
            collection = db[collection_name]
            result = collection.insert_one(document)

            print("Inserted document ID:", result.inserted_id)
            return results
        except ValueError as e:
            print(f"Error: {e}")
            print("Please ensure the SQL query has the correct number of fields and values.")
            return f"Error processing SQL query: {sql_query}"

        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return f"Error processing SQL query: {sql_query}"
        
    elif sql_query.startswith("drop table"):
        # Handle DROP TABLE
        table_name = sql_query.split()[2]
        return table_name, None, None
    elif sql_query.startswith("alter table"):
        # Basic ALTER TABLE handling (more complex scenarios may require additional parsing)
        parts = sql_query.split()
        table_name = parts[2]
        action = parts[3]
        field = parts[4]
        if action == "add":
            field_type = parts[5]
            return table_name, {field: field_type}, None
        elif action == "drop":
            return table_name, {field: None}, None
    else:
        raise ValueError("Unsupported SQL query type")

def convert_objectid_to_str(document):
    """Recursively convert ObjectId fields to strings in a document."""
    if isinstance(document, list):
        return [convert_objectid_to_str(item) for item in document]
    elif isinstance(document, dict):
        return {
            key: convert_objectid_to_str(value)
            for key, value in document.items()
        }
    elif isinstance(document, ObjectId):
        return str(document)
    else:
        return document
    
# Main function
def execute_mongo_query(sql_query):
    
    # Convert SQL to MongoDB
    try:
        results = convert_sql_to_mongo(sql_query)
        if isinstance(results, list):
            data = [convert_objectid_to_str(result) for result in results]
        else:
            data = {"message": "No results found or unsupported query"}
        # Display results
        print("Query Results:")
        for result in results:
            print(result)
    except ValueError as e:
        print(f"Error: {e}")
    return data

def execute_duckdb_query(query):
    conn = duckdb.connect('shameem.duckdb')
    result = conn.execute(query).fetchall()
    column_names = [desc[0] for desc in conn.description]
    conn.commit()
    conn.close()
    return column_names, result

if __name__ == '__main__':
    app.run(debug=True)
