# dbconnect.py
import sqlite3
import os
import pandas as pd

from commonfuncs import remove_sql_comments, logmessage

root = os.path.dirname(__file__)
DB_FILENAME = os.environ.get("DB_FILENAME","questionbank.db")
DB_FOLDER = os.environ.get("DB_FOLDER","data/database")
DB_SCHEMAFILE = os.environ.get("DB_SCHEMAFILE","dbschema.sql")
dbFolder = os.path.join(root, DB_FOLDER)
os.makedirs(dbFolder, exist_ok=True)


def makeQuery(
    s1,
    output="oneValue",
    noprint=False,
):
    """
    output choices:
    oneValue : ex: select count(*) from table1 (output will be only one value)
    df: ex: select * from users (output will be a table)
    list: json array, like df.to_dict(orient='records')
    column: first column in output as a list. ex: select username from users
    oneJson: First row, as dict
    """
    if not isinstance(s1, str):
        logmessage("query needs to be a string")
        return False
    if ";" in s1:
        logmessage("; not allowed")
        return False

    if not noprint:
        # keeping auth check and some other queries out
        skipPrint = ["where token=", ".STArea()", "STGeomFromText"]
        if not any([(x in s1) for x in skipPrint]):
            logmessage(f"Query: {' '.join(s1.split())}")
        else:
            logmessage(f"Query: {' '.join(s1.split())[:20]}")

    global dbFolder, DB_FILENAME
    # Make SQLite connection in read-only mode
    conn = sqlite3.connect(f"file:{os.path.join(dbFolder, DB_FILENAME)}?mode=ro", uri=True)
    df1 = pd.read_sql_query(s1, conn)
    conn.close()

    result = None  # default return value
    if not len(df1):
        if output in ("df","list","column"):
            return []
        else:
            return None
    
    if output == "df":
        return df1
    elif output == "oneValue":
            result = df1.values[0][0]
            return result
    elif output in ("list", "oneJson"):
        result = df1.to_dict(orient="records")
        if output == "list":
            return result
        else:
            return result[0]
    elif output == "column":
        result = df1.iloc[:, 0].tolist()  # .iloc[:,0] -> first column
        return result
    else:
        return df1


def execSQL(s1, noprint=False):
    # if not noprint: print(' '.join(s1.split())[:200])
    if not noprint:
        logmessage(" ".join(s1.split()))
    
    global dbFolder, DB_FILENAME
    conn = sqlite3.connect(os.path.join(dbFolder, DB_FILENAME ))
    cursor = conn.cursor()
    try:
        cursor.execute(s1)
        conn.commit()
        affected = cursor.rowcount
    except Exception as e:
        logmessage("DB error")
        logmessage(e)
        affected = None
    finally:    
        conn.close()

    return affected

def initiate():
    global dbFolder, DB_FILENAME, DB_SCHEMAFILE
    if not os.path.isfile(os.path.join(dbFolder, DB_FILENAME )):
        logmessage(f"Creating {DB_FILENAME}")
        with open(os.path.join(root, DB_SCHEMAFILE), 'r') as f:
            sql = f.read()
        
        clean_sql = remove_sql_comments(sql)
        statements = clean_sql.split(';')
        for statement in statements:
            execSQL(statement)

    else:
        logmessage(f"Found {DB_FILENAME}")

# startup: initiate if db not found
initiate()
