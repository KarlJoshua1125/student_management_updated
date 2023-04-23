from django.shortcuts import render, redirect
from django.apps import apps
from django.http import JsonResponse
import firebase_admin
from firebase_admin import credentials, db
from .forms import StudentForm


def connectDB():
    if not firebase_admin._apps:
        cred = credentials.Certificate("studentmanagement-admin-key.json")
        firebase_admin.initialize_app(cred, {
            "databaseURL": "https://studentmanagement-84271-default-rtdb.firebaseio.com/" #Your database URL
        })
    dbconn = db.reference("StudentsList")
    return dbconn


def index(request):
    students = []
    dbconn = connectDB()
    tblStudents = dbconn.get()
    for key, value in tblStudents.items():
        students.append({"id": int(value["ID"]), "name": value["Name"], "year": int(value["Year"]), "course": value["Course"], "key": key})
    return render(request, 'index.html', {'students':students})


def add_student(request):
    if request.is_ajax() and request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            id = int(form.cleaned_data.get("id")) 
            name = form.cleaned_data.get("name")
            year = int(form.cleaned_data.get("year"))  
            course = form.cleaned_data.get("course")

            dbconn = connectDB()
            dbconn.push({"ID": id, "Name": name, "Year": year, "Course": course})

            
            return JsonResponse({'status': 'success'})
        else:
           
            return JsonResponse({'status': 'errors', 'errors': form.errors})


def deletestudent(request, id):
    dbconn = connectDB()
    tblStudents = dbconn.get()
    for key, value in tblStudents.items():
        if(value["ID"] == id):
            deletekey = key
            break
    delitem = dbconn.child(deletekey)
    delitem.delete()
    return redirect('index')


def update_student(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
        id = int(request.POST.get('id'))
        name = request.POST.get('name')
        year = int(request.POST.get('year'))
        course = request.POST.get('course')
        key = request.POST.get('key')

        dbconn = connectDB()
        dbconn.child(key).update({"ID": id, "Name": name, "Year": year, "Course": course})

      
        return JsonResponse({'status': 'success'})
    else:
   
        return JsonResponse({'status': 'errors', 'errors': 'Unable to update student.'})
    
def search_students(request):
    query = request.GET.get('query', '')
    students = students.objects.filter(name__icontains=query)
    return render(request, 'index.html', {'students': students})
