from models import Task


def main():
    tasks = Tasks.objects.all() 

    for t in tasks:
        print(t.inputFilename)
