import requests
import urllib
import time
import sys
import os
from github import Github
from github import Auth
import datetime

try:
    github_token = sys.argv[1]
    bot_token = sys.argv[2]
    bot_chatID = sys.argv[3]
except IndexError:
    print("not all parameters")
    os._exit(0)

aiFolder = '/home/runner/work/GraphSPD/'
with open('repoList','r') as flist:
    for j in flist.readlines():
        userName = j.split(' ')[0]
        repoName = j.splitlines()[0].split(' ')[1]
        auth = Auth.Token(github_token)
        g = Github(auth=auth)
        repo = g.get_repo(userName+"/"+repoName)

        since = datetime.datetime.now() - datetime.timedelta(days=100)
        commits = repo.get_commits(since=since)

        index = 1
        for i in commits:
            os.system('cd '+aiFolder+'raw_patch&&wget https://github.com/'+userName+'/'+repoName+'/commit/'+i.commit.sha[:8]+'.patch -O '+i.commit.sha[:8])
            os.system('cd '+aiFolder+'&&python3 get_ab_file.py '+userName+' '+repoName+' '+i.commit.sha[:8])
            index+=1
            if index >100:
                break
        os.system('cd '+aiFolder+'&&python3 gen_cpg.py')
        os.system('cd '+aiFolder+'&&python3 merge_cpg.py')
        os.system('cd '+aiFolder+'&&python3 test.py')

        os.system('cp '+aiFolder+'logs/test_results.txt'+' ./'+datetime.date.today().strftime("%d%m%Y")+'_'+userName+'_'+repoName)
        with open(aiFolder+'logs/test_results.txt','r') as file:
            for i in file.readlines():
                if i.splitlines()[0].endswith(',1'):
                    bot_message = 'https://github.com/nginx/nginx/commit/'+i.split('/')[2]
                    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
                    response = requests.get(send_text)
