from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import uvicorn

app = FastAPI(title="Student Application Testing System")

# In-memory storage
students = {}
tests = {}
test_results = {}

# Models
class Student(BaseModel):
    id: int = Field(..., description="Unique identifier for the student")
    name: str = Field(..., min_length=2, max_length=50, description="Student's full name")
    email: str = Field(..., description="Student's email address")
    tests_taken: List[int] = []

class Test(BaseModel):
    id: int = Field(..., description="Unique identifier for the test")
    name: str = Field(..., min_length=2, max_length=100, description="Name of the test")
    max_score: int = Field(..., description="Maximum possible score")

class TestResult(BaseModel):
    student_id: int = Field(..., description="ID of the student taking the test")
    test_id: int = Field(..., description="ID of the test taken")
    score: int = Field(..., description="Score obtained in the test")

class ResponseMessage(BaseModel):
    message: str

# API Endpoints
@app.post("/students/", response_model=ResponseMessage)
async def create_student(student: Student):
    if student.id in students:
        raise HTTPException(status_code=400, detail="Student ID already exists")
    students[student.id] = student
    return {"message": "Student created successfully"}

@app.get("/students/{student_id}/", response_model=Student)
async def get_student(student_id: int):
    if student_id not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    return students[student_id]

@app.get("/students/", response_model=List[Student])
async def get_all_students():
    return list(students.values())

@app.post("/tests/", response_model=ResponseMessage)
async def create_test(test: Test):
    if test.id in tests:
        raise HTTPException(status_code=400, detail="Test ID already exists")
    tests[test.id] = test
    return {"message": "Test created successfully"}

@app.get("/tests/{test_id}/", response_model=Test)
async def get_test(test_id: int):
    if test_id not in tests:
        raise HTTPException(status_code=404, detail="Test not found")
    return tests[test_id]

@app.get("/tests/", response_model=List[Test])
async def get_all_tests():
    return list(tests.values())

@app.post("/results/", response_model=ResponseMessage)
async def submit_test_result(result: TestResult):
    if result.student_id not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    if result.test_id not in tests:
        raise HTTPException(status_code=404, detail="Test not found")
    if result.score > tests[result.test_id].max_score:
        raise HTTPException(status_code=400, detail="Score exceeds maximum allowed")
    test_results[(result.student_id, result.test_id)] = result
    students[result.student_id].tests_taken.append(result.test_id)
    return {"message": "Test result submitted successfully"}

@app.get("/results/student/{student_id}/", response_model=List[TestResult])
async def get_student_results(student_id: int):
    if student_id not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    return [result for (sid, tid), result in test_results.items() if sid == student_id]

@app.get("/results/test/{test_id}/", response_model=List[TestResult])
async def get_test_results(test_id: int):
    if test_id not in tests:
        raise HTTPException(status_code=404, detail="Test not found")
    return [result for (sid, tid), result in test_results.items() if tid == test_id]

@app.get("/results/test/{test_id}/average", response_model=float)
async def get_test_average(test_id: int):
    if test_id not in tests:
        raise HTTPException(status_code=404, detail="Test not found")
    results = [result.score for (sid, tid), result in test_results.items() if tid == test_id]
    if not results:
        raise HTTPException(status_code=404, detail="No results found for this test")
    return sum(results) / len(results)

@app.get("/results/test/{test_id}/highest", response_model=int)
async def get_test_highest(test_id: int):
    if test_id not in tests:
        raise HTTPException(status_code=404, detail="Test not found")
    results = [result.score for (sid, tid), result in test_results.items() if tid == test_id]
    if not results:
        raise HTTPException(status_code=404, detail="No results found for this test")
    return max(results)

@app.delete("/students/{student_id}/", response_model=ResponseMessage)
async def delete_student(student_id: int):
    if student_id not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    del students[student_id]
    # Remove associated test results
    test_results_to_delete = [(sid, tid) for (sid, tid) in test_results.keys() if sid == student_id]
    for key in test_results_to_delete:
        del test_results[key]
    return {"message": "Student deleted successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)