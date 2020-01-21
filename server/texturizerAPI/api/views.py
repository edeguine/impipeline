from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from api.config import baseImageDir, processedImageDir
from api.models import Image, Task, TUser
from backend import TaskProcessing

import json
import PIL.Image
import time

def createTextureTask(image, user):
    # Create a new texture processing task for a new image.

    params = {'inputFilename': image.filename}
    params = json.dumps(params)

    t = Task(taskType = 'texture', 
        params = params,
        status='new',
        user = user)
    t.save()

def findUser(username):
    # Find a TUser from username (Texturizer User = TUser) as opposed
    # to User which is the Django class for the authentication system.

    users = TUser.objects.filter(username = username)
    if len(users) == 0:
        return None
    else:
        return users[0]

def saveFile(obj, user):
    # Save an image to the DB and filesystem.

    im = Image(filename = "", user = user)
    im.save()
    imageName = str(im.id)
    fname = obj.name
    if fname[-3:] == 'png' or fname[-3:] == 'jpg':
        imageName += '.' + fname[-3:]
        print(f"Saving {imageName}")
        im.filename = imageName
        im.save()
        outfile = open(baseImageDir + imageName, 'wb')
        outfile.write(obj.read())
        return im
    else:
        return None

# Public (not logged-in)  methods

@csrf_exempt
def createUser(request):
    # Create a user, username, password and email need to be populated

    username = request.POST.get('username')
    password = request.POST.get('password')
    email = request.POST.get('email')

    user = findUser(username)

    if user != None:
        return HttpResponse("User already exists", status=409) # 409 is for Conflict

    if username != None and username != '' and password != None and password != '' and email != None and email != '':
        # TODO add password and email validation
        u = User.objects.create_user(username = username, password = password, email = email)
        tu = TUser(username = username, user = u)
        u.save()
        tu.save()
        return HttpResponse("Created user")
    else:
        return HttpResponse("Please specify a user, password and email", status=400) # 400 is for Bad Request

@csrf_exempt
def index(request):
    return HttpResponse('Welcome to the API')

@csrf_exempt
def loginPage(request):
    # Log a user in.

    username = request.POST.get('username')
    password = request.POST.get('password')

    user = authenticate(username = username, password = password)
    if user != None:
        login(request, user)
        return HttpResponse('User authenticated')
    else:
        return HttpResponseNotFound('No such username / password')


# Logged in methods

@csrf_exempt
@login_required
def deleteUser(request):
    username = request.user.username
    user = findUser(username)

    if user != None:
        user.delete()
        djangoUser = User.objects.filter(username = username)
        djangoUser.delete()
        return HttpResponse("User deleted")
    else:
        return HttpResponseNotFound("No such user")

@csrf_exempt
@login_required
def getPicture(request):
    # Get a picture previously uploaded, the 'id' field is the identifer coming
    # from getPictureList.

    username = request.user.username
    user = findUser(username)
    picId = request.POST.get('id')

    if user:
        pics = Image.objects.filter(user = user, id = picId)
        if len(pics) > 0:
            pic = pics[0]
            response = HttpResponse(content_type="image/png")
            image = PIL.Image.open(f"{baseImageDir}{pic.filename}")
            image.save(response, "PNG")
            return response
        else:
            return HttpResponseNotFound('No such picture')
    else:
        return HttpResponseNotFound('No such user')

@csrf_exempt
@login_required
def getPictureList(request):
    # Get the list of all pictures beloging to the user.

    username = request.user.username
    user = findUser(username)

    if user != None:
        pics = Image.objects.filter(user = user)
        res = {'pictures': [pic.id for pic in pics]}
        return JsonResponse(res)
    else:
        return HttpResponseNotFound('Please specify a user')


@csrf_exempt
@login_required
def getPictureProcessed(request):
    # Get a picture after it has been processed. The id is the same
    # as the id of the original picture.

    username = request.user.username
    user = findUser(username)
    picId = request.POST.get('id')


    if user:
        pics = Image.objects.filter(user = user, id = picId)
        if len(pics) > 0:
            pic = pics[0]
            response = HttpResponse(content_type="image/png")
            try:
                image = PIL.Image.open(f"{processedImageDir}{pic.filename}.processed.png")
                image.save(response, "PNG")
                return response
            except FileNotFoundError:
                return HttpResponseNotFound('Picture not processed yet')
        else:
            return HttpResponseNotFound('No such picture')
    else:
        return HttpResponseNotFound('No such user')

@csrf_exempt
@login_required
def protected(request):
    # Simple page to check if a user is logged in.

    return HttpResponse(f'Welcome {request.user.username}')


@csrf_exempt
@login_required
def logoutPage(request):
    # Log a user out

    logout(request)
    return HttpResponse("Logged out")

@csrf_exempt
@login_required
def testHelperProcessAllNewTasks(request):
    # Process all the new images immediately (no-op)
    # This method is used for testing the REST api without
    # the full backend logic in TaskProcessing.

    username = request.POST.get('username')
    user = findUser(username)
    tasks = Task.objects.filter(complete = '0')

    for task in tasks:
        TaskProcessing.processTaskDummy(task)

    return HttpResponse('Done')

@csrf_exempt
@login_required
def uploadPicture(request):
    # Upload the file witht the 'picture' identifier,
    # save to the FS and DB and  create new processing task.

    if 'picture' in request.FILES:
        obj = request.FILES['picture']
        username = request.user.username
        user = findUser(username)
        if user:
            im = saveFile(obj, user)
            if im:
                createTextureTask(im, user)
                return HttpResponse(str(im.id))
            else:
                return HttpResponse('Please upload a png or jpg file', status=400) # Bad request
        else:
            return HttpResponseNotFound('Please specify a user')
    else:
        return HttpResponse('Please upload a picture', status=400) # Bad request

