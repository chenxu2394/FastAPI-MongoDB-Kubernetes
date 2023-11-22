 
from fastapi import FastAPI, HTTPException
from mongoengine import (
    connect,
    disconnect,
    Document,
    StringField,
    ReferenceField,
    ListField,
    IntField
)
import json
from pydantic import BaseModel
from typing import Optional, List
from bson import ObjectId

app = FastAPI()


@app.on_event("startup")
def startup_db_client():
    # Set the correct parameters to connect to the database
    connect(db="fast-api-database", host="mongo", port=27017)


@app.on_event("shutdown")
def shutdown_db_client():
    # Set the correct parameters to disconnect from the database
    disconnect("fast-api-database")


# Helper functions to convert MongeEngine documents to json

def course_to_json(course):
    course = json.loads(course.to_json())
    course["students"] = list(map(lambda dbref: str(dbref["$oid"]), course["students"]))
    course["id"] = str(course["_id"]["$oid"])
    course.pop("_id")
    return course


def student_to_json(student):
    student = json.loads(student.to_json())
    student["id"] = str(student["_id"]["$oid"])
    student.pop("_id")
    return student

# Schema

class Student(Document):
    # Implement the Student schema according to the instructions
    name = StringField(required=True)
    student_number = IntField()

class Course(Document):
    # Implement the Course schema according to the instructions
    name = StringField(required=True)
    description = StringField()
    tags = ListField(StringField())
    students = ListField(ReferenceField("Student", reverse_delete_rule=4))    

# Input Validators

class CourseData(BaseModel):
    name: str
    description: Optional[str] = None
    tags: Optional[list[str]] = None
    students: Optional[list[str]] = None


class StudentData(BaseModel):
    name: str
    student_number: Optional[int] = None


# Student routes
# Complete the Student routes similarly as per the instructions provided in A+
@app.get('/students')
def get_students():
    # pylint: disable=no-member
    students = Student.objects()
    return json.loads(students.to_json())

@app.post("/students", status_code=201)
def create_student(student_data: StudentData):
    student = Student(**student_data.dict()).save()
    # pylint: disable=no-member
    return {"message": "Student successfully created", "id": str(student.id)}

@app.get("/students/{student_id}", status_code=200)
def read_student(student_id: str):
    # pylint: disable=no-member
    student = Student.objects(id=ObjectId(student_id)).first()
    if student:
        return student_to_json(student)
    raise HTTPException(status_code=404, detail="Student not found")

@app.put("/students/{student_id}", status_code=200)
def update_student(student_id: str, student_data: StudentData):
    # pylint: disable=no-member
    student = Student.objects(id=ObjectId(student_id)).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    student.update(**student_data.dict(exclude_unset=True))
    return {"message": "Student successfully updated"}

@app.delete("/students/{student_id}", status_code=200)
def delete_student(student_id: str):
    # pylint: disable=no-member
    result = Student.objects(id=ObjectId(student_id)).delete()
    if result:
        return {"message": "Student successfully deleted"}
    raise HTTPException(status_code=404, detail="Student not found")


# Course routes
# Complete the Course routes similarly as per the instructions provided in A+

@app.post("/courses", status_code=201)
def create_course(course_data: CourseData):
    course = Course(**course_data.dict()).save()
    # pylint: disable=no-member
    return {"message": "Course successfully created", "id": str(course.id)}

@app.get("/courses", status_code=200)
def read_courses(tag: Optional[str] = None, studentName: Optional[str] = None):
    # pylint: disable=no-member
    query = {}
    if tag:
        query["tags__in"] = [tag]

    if studentName:
        # Get the IDs of students with the given name
        student_ids = [str(student.id) for student in Student.objects(name=studentName)]
        if student_ids:
            query["students__in"] = student_ids

    courses = Course.objects(**query)
    return [course_to_json(course) for course in courses]

@app.get("/courses/{course_id}", status_code=200)
def read_course(course_id: str):
    # pylint: disable=no-member
    course = Course.objects(id=ObjectId(course_id)).first()
    if course:
        return course_to_json(course)
    raise HTTPException(status_code=404, detail="Course not found")

@app.put("/courses/{course_id}", status_code=200)
def update_course(course_id: str, course_data: CourseData):
    # pylint: disable=no-member
    try:
        course = Course.objects.get(id=ObjectId(course_id))
    except Course.DoesNotExist:
        raise HTTPException(status_code=404, detail="Course not found")

    # If 'students' is provided, process it
    if course_data.students is not None:
        # Convert student string IDs to ObjectIds
        student_ids = [ObjectId(student_id) for student_id in course_data.students]

        # Verify that each student exists
        for student_id in student_ids:
            # pylint: disable=no-member
            if not Student.objects(id=student_id):
                raise HTTPException(status_code=400, detail=f"Student with ID {student_id} does not exist")

        course_data.students = student_ids

    # Update course details
    update_data = course_data.dict(exclude_unset=True)
    course.update(**update_data)
    return {"message": "Course successfully updated"}

@app.delete("/courses/{course_id}", status_code=200)
def delete_course(course_id: str):
    # pylint: disable=no-member
    result = Course.objects(id=ObjectId(course_id)).delete()
    if result:
        return {"message": "Course successfully deleted"}
    raise HTTPException(status_code=404, detail="Course not found")

