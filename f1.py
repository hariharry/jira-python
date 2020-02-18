from jira import JIRA
import unicodedata
import sys
import os
import re
from datetime import datetime
now = datetime.now()
stime=now.strftime("%Y-%m-%d %H:%M:%S")

user=sys.argv[1]
apikey=sys.argv[2]
issue_key = sys.argv[3]
juser = sys.argv[4]
rw = sys.argv[5]
instance = sys.argv[6]
email = sys.argv[7]
server = 'https://manojsrao.atlassian.net'
options = {
'server': server
}

jira = JIRA(options, basic_auth=(user,apikey))
issue = jira.issue(issue_key)
assigne=issue.fields.assignee.displayName
assign=unicodedata.normalize('NFKD', assigne).encode('ascii','ignore')
status=issue.fields.status
issuetype=issue.fields.issuetype
print(issuetype)
print(status)
s1=[]
s1=issue.fields.labels

with open('mail_list.txt', 'r') as emails:
    mail=emails.read()
    if re.search(email,mail):
        print("found")
        os.putenv('name',juser)
        os.system('bash')
    else:
       for i in s1:
         if i=="ssh":
             if str(issue.fields.issuetype) == 'S1':
                print('Jira ticket {} current assignee is {}'.format(issue_key,assign))
                if assign==juser:
                    print("Jira ticket assignee and username is matching")
                    f = open("SSH_Access.log", "a")
                    sys.stdout = f
                    os.putenv('name',juser)
                    os.system('bash')
                    if rw=='RO':
                        print('{} Read Only access have given for {} in {} server '.format(stime,juser,instance))
                        os.system("aws s3 cp s3://bigbasketsshaccess/%s  /var/lib/jenkins/workspace/ssh-access/%s "% (juser,juser))
                    else:
                        print('{} Admin access have given for {} in {} server '.format(stime,juser,instance))
                        os.system("aws s3 cp s3://bigbasketsshaccess/%s  /var/lib/jenkins/workspace/ssh-access/%s "% (juser,juser))
                        f.close()

