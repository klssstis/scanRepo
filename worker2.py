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

os.chdir("/home/runner/work/PatchRNN-demo")

with open('/home/runner/work/scanRepo/scanRepo/repoList','r') as flist:
    for j in flist.readlines():
        userName = j.split(' ')[0]
        repoName = j.splitlines()[0].split(' ')[1]
        auth = Auth.Token(github_token)
        g = Github(auth=auth)
        repo = g.get_repo(userName+"/"+repoName)

        since = datetime.datetime.now() - datetime.timedelta(days=1)
        commits = repo.get_commits(since=since)

        index = 1

        os.system('rm -rf ./testdata/*')
        os.system('rm -rf ./results/*')
        os.system('rm -rf ./tmp/*')
        os.system('rm -rf ./logs/*')
        os.system('mkdir -p ./testdata/'+userName+'/'+repoName)
        for i in commits:
            os.system('cd ./testdata/'+userName+'/'+repoName+'&& wget https://github.com/'+userName+'/'+repoName+'/commit/'+i.commit.sha+'.patch -O '+i.commit.sha[:8]+'.patch')
            index+=1
            if index >10:
                break
        os.system('python3 demo.py')
        os.system('cat ./results/results.txt')
        if os.path.exists('./results/results.txt'):
            os.system('cp ./results/results.txt'+' /home/runner/work/scanRepo/scanRepo/result/rnn_'+datetime.date.today().strftime("%d%m%Y")+'_'+userName+'_'+repoName)
            with open('./results/results.txt','r') as file:
                for i in file.readlines():
                    if i.splitlines()[0].endswith(',1'):
                        bot_message = 'patchRNN\nhttps://github.com/'+userName+'/'+repoName+'/commit/'+i.split('/')[5].split('.')[0]
                        send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
                        response = requests.get(send_text)
        else:
            os.system('echo \"'+datetime.date.today().strftime("%d%m%Y")+'_'+userName+'_'+repoName+'\" >> /home/runner/work/scanRepo/scanRepo/result/rnn_tmp')
