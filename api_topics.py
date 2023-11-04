# api_topics.py

from fastapi import HTTPException, Header
from pydantic import BaseModel

import dbconnect
from questionbank_launch import app
import commonfuncs as cf


###########################
# FUNCTIONS


###########################
# APIs

@app.get("/api/topics/list", tags=["topics"])
def fetchTopics():

    s1 = "select * from topics"
    df1 = dbconnect.makeQuery(s1, output="df")

    if not len(df1):
        return {"message": "no topics in DB", "data": []}
    
    returnD = {
        "message": "success"
    }
    returnD["data"] = df1.to_dict(orient="records")

    returnD["subject_id_list"] = df1[["subject_id","subject_name"]].drop_duplicates().to_dict(orient='records')    
    returnD["topic_id_list"] = df1[["topic_id","topic_name"]].drop_duplicates().to_dict(orient='records')
    returnD["subtopic_id_list"] = df1[["subtopic_id","subtopic_name"]].drop_duplicates().to_dict(orient='records')
    return returnD


##########

class add_topic_payload(BaseModel):
    subject: str
    topic: str
    subtopic: str
    
@app.post("/api/topics/add", tags=["topics"])
def addTopic(r: add_topic_payload, x_access_token: str = Header(...) ):
    # check if subject and topic are existing *_id values. else create their slugs.
    cf.logmessage("addTopic POST api call")

    new_subject = False
    new_topic = False

    # fetch everything
    s1 = "select * from topics"
    df1 = dbconnect.makeQuery(s1, output="df")

    # check if subject existing
    df2 = df1[df1['subject_id']== r.subject].copy()
    if len(df2):
        subject_id = r.subject
        subject_name = df2['subject_name'].values[0]

    else:
        # new subject
        new_subject = True
        subject_name = r.subject
        existing_subject_ids = df1.drop_duplicates('subject_id').copy()['subject_id'].tolist()
        subject_id = cf.create_unique_slug(subject_name, existing_subject_ids)

    
    # check if topic existing
    df3 = df1[df1['topic_id'] == r.topic].copy()
    if len(df3):
        topic_id = r.topic
        topic_name = df2['topic_name'].values[0]
    else:
        # new topic
        new_topic = True
        topic_name = r.topic
        existing_topic_ids = df1.drop_duplicates('topic_id').copy()['topic_id'].tolist()
        topic_id = cf.create_unique_slug(topic_name, existing_topic_ids)
    
    
    # check if subtopic name is existing
    if not new_topic and not new_subject:
        df4 = df1.query(f'subject_id == "{subject_id}" and topic_id == "{topic_id}"').copy()
        if r.subtopic in df4['subtopic_name'].tolist():
            raise HTTPException(status_code=400, detail="Repeating subtopic name in the same group")
    
    subtopic_name = r.subtopic
    existing_subtopic_ids = df1['subtopic_id'].tolist()
    subtopic_id = cf.create_unique_slug(subtopic_name, existing_subtopic_ids)

    i1 = f"""insert into topics (subject_name, subject_id, topic_name, topic_id, subtopic_name, subtopic_id)
    values (
    '{subject_name}','{subject_id}', 
    '{topic_name}','{topic_id}', 
    '{subtopic_name}','{subtopic_id}'
    )
    """
    i1Count = dbconnect.execSQL(i1)

    if not i1Count:
        raise HTTPException(status_code=500, detail="Error, Could not add in DB")

    returnD = {"subtopic_added": True, "subtopic_id": subtopic_id, "new_subject": new_subject, "new_topic": new_topic}
    return returnD
    
    
###############

@app.get("/api/topics/dropdown", tags=["topics"])
def fetchDropdown(
    parent_category: str = None,
    value: str = None,
):
    cf.logmessage("fetchDropdown GET api call")
    s1 = "select distinct subject_id, subject_name from topics"
    
    if parent_category:
        if not value:
            raise HTTPException(status_code=400, detail="Missing value")

        if parent_category == "subject_id":
            s1 = f"select distinct topic_id, topic_name from topics where subject_id = '{value}'"
        else:
            s1 = f"select distinct subtopic_id, subtopic_name from topics where topic_id = '{value}'"

    df1 = dbconnect.makeQuery(s1, output="df")

    if not len(df1):
        return {"message": "no topics for this", "data": []}
    
    returnD = {
        "message": "success"
    }
    returnD["data"] = df1.to_dict(orient="records")
    return returnD



class edit_topic_payload(BaseModel):
    col: str
    # idcol: str
    newVal: str
    oldVal: str

@app.put("/api/topics/edit", tags=["topics"])
def edit_topic(r: edit_topic_payload, x_access_token: str = Header(...)):
    cf.logmessage("edit_topic PUT api call")
    # to do : validations

    u1 = f"""update topics
    set {r.col} = '{r.newVal}'
    where {r.col} = '{r.oldVal}'
    """
    u1Count = dbconnect.execSQL(u1)

    returnD = {"updated_rows": u1Count}
    return returnD



@app.delete("/api/topics/delete", tags=["topics"])
def delete_topic(subtopic_id: str, x_access_token: str = Header(...)):
    cf.logmessage("delete_topic DELETE api call")

    s1 = f"select count(*) from questionbank where subtopic_id = '{subtopic_id}'"
    c1 = dbconnect.makeQuery(s1, output="oneValue")

    if c1:
        raise HTTPException(status_code=400, detail="There are existing questions under this subtopic. Delete them first.")
        return
    
    d1 = f"delete from topics where subtopic_id = '{subtopic_id}'"
    d1Count = dbconnect.execSQL(d1)
    if not d1Count:
        raise HTTPException(status_code=500, detail="Could not delete subtopic_id from DB")
        return
    
    return {"deleted": True, "count": d1Count}
