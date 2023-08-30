# api_topics.py

from fastapi import HTTPException
from pydantic import BaseModel
from typing import List

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
    
    return returnD


##########

class add_topic_payload(BaseModel):
    # category: str
    # parent_id: str
    subtopic_name: str
    topic_id: str = None
    topic_name: str = None
    subject_id: str = None
    subject_name: str = None

@app.post("/api/topics/add", tags=["topics"])
def addTopic(r: add_topic_payload ):
    if r.topic_id:
        # check if the topic exists
        s1 = f"select subject_id, subject_name, topic_name from topics where topic_id = '{r.topic_id}'"
        subjectRow = dbconnect.makeQuery(s1, output="oneJson")

        if not subjectRow:
            raise HTTPException(status_code=400, detail="Invalid topic_id")

        print(f"subjectRow: {subjectRow}")
        
        # create slug
        s2 = f"""select subtopic_id from topics
        where topic_id = '{r.topic_id}'
        """
        existing_slugs = dbconnect.makeQuery(s2, output="column")
        print(f"existing_slugs: {existing_slugs}")
        subtopic_id = cf.create_unique_slug(r.subtopic_name, existing_slugs)


        i1 = f"""insert into topics (subject_id, subject_name, topic_id, topic_name, 
        subtopic_id, subtopic_name) values (
        '{subjectRow['subject_id']}', '{subjectRow['subject_name']}', 
        '{r.topic_id}', '{subjectRow['topic_name']}', 
        '{subtopic_id}', '{r.subtopic_name}')
        """
        i1Count = dbconnect.execSQL(i1)

        returnD = {"message": "created subtopic", "subtopic_id": subtopic_id}
        return returnD

    elif r.subject_id:
        # to do: flow in case we're creating topic and subtopic both
        return {"message": "WIP"}
    
    elif r.subject_name:
        # to do: flow in case we're creating subject, topic and subtopic
        return {"message": "WIP"}
    
    else:
        raise HTTPException(status_code=400, detail="Valid topic_id needed")
        
    
