import os
import django
import sys
from time import sleep

def __setup_django(root_path, settings):

    os.chdir(root_path)

    # Django settings
    sys.path.append(root_path)
    os.environ['DJANGO_SETTINGS_MODULE'] = settings

    django.setup()

PROJECT_PATH = "/Users/etienne/texturizer/server/texturizerAPI/"
PROJECT_SETTING = "texturizerAPI.settings"

__setup_django(PROJECT_PATH, PROJECT_SETTING)

from api.models import Task
from api.config import baseImageDir, processedImageDir, homeDir

import json
import subprocess

def processTask(task):
    if task.taskType == 'texture' and task.status == 'new' and task.complete == '0':
        params = json.loads(task.params)

        inputFilename = params['inputFilename']
        inputFilePath = baseImageDir + inputFilename
        outputFilename = inputFilename

        command = f'cd ~/texturizer/floydhub/code/; cp {baseImageDir}{inputFilename} ./input.png; floyd run --gpu "python3 synthesize.py -s input.png --data-dir /vggweights/vggweights --output-dir /output --output-name /output/final/{outputFilename} --output-width 1024 --max-iter 50" --data edeguine/datasets/vggweights/1:vggweights'

        outname = f"{homeDir}texturizer/floydhub/logs/{inputFilename}.new.log"
        outerrname = f"{homeDir}texturizer/floydhub/logs/{inputFilename}.new.error.log"
        stdout = open(outname, 'w')
        stderr = open(outerrname, 'w')
        print(command)
        subprocess.call(command, shell=True, stdout=stdout, stderr=stderr)

        stdout.close()
        stderr.close()

        jobinfo = open(outname).readlines()[-1].rstrip('\n')
        jobinfo = jobinfo.strip(' ')
        _, _, jobName = jobinfo.split(' ')

        params = {'processedFilepath': f'/output/final/{outputFilename}', 
                  'outputFilename': outputFilename,
                  'jobName': jobName}

        t = Task(taskType = 'texture', status = 'check', params = json.dumps(params), complete = '0')
        t.save()

        task.complete = 1
        task.save()

    if task.taskType == 'texture' and task.status == 'check' and task.complete == '0':
        params = json.loads(task.params)

        outputFilename = params['outputFilename']
        jobName = params['jobName']

        command = f"cd {homeDir}texturizer/floydhub/code/; floyd status {jobName}"

        outname = f"{homeDir}texturizer/floydhub/logs/{outputFilename}.check.log"
        outerrname = f"{homeDir}texturizer/floydhub/logs/{outputFilename}.check.error.log"
        stdout = open(outname, 'a')
        stderr = open(outerrname, 'a')
        print(command)
        subprocess.call(command, shell=True, stdout=stdout, stderr=stderr)

        stdout.close()
        stderr.close()

        status = open(outname).read()
        if 'success' in status:
            print(f'Success for {jobName}')
            t = Task(taskType = 'texture', status = 'cpCheck', params = task.params, complete = '0')
            t.save()

            task.complete = '1'
            task.save()

    if task.taskType == 'texture' and task.status == 'cpCheck' and task.complete == '0':

        params = json.loads(task.params)

        processedFilepath = params['processedFilepath']
        outputFilename = params['outputFilename']
        jobName = params['jobName']

        command = f'cd {homeDir}texturizer/floydhub/code; floyd data clone {jobName}/output/final/; cp ./final/{outputFilename} {processedImageDir}{outputFilename}.processed.png'

        outname = f"{homeDir}texturizer/floydhub/logs/{outputFilename}.cpCheck.log"
        outerrname = f"{homeDir}texturizer/floydhub/logs/{outputFilename}.cpCheck.error.log"
        stdout = open(outname, 'a')
        stderr = open(outerrname, 'a')
        print(command)
        subprocess.call(command, shell=True, stdout=stdout, stderr=stderr)

        stdout.close()
        stderr.close()

        task.complete = '1'
        task.save()

def processTaskDummy(task):
    if task.taskType== "texture" and task.status == "new" and task.complete == "0":
        params = json.loads(task.params)

        inputFilename = params['inputFilename']
        outputFilename = inputFilename
        inputFilePath = baseImageDir + inputFilename

        command = f'cp {inputFilePath} {processedImageDir}{outputFilename}.processed.png'
        print(command)
        subprocess.call(command, shell=True, stdout=None, stderr=None)

        task.complete = '1'
        task.save()

def main():
    while True:
        tasks = Task.objects.filter(complete = '0')

        for task in tasks:
            processTask(task)
        sleep(10)


if __name__ == "__main__":
    main()
