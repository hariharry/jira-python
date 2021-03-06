
import pandas as pd
import unicodedata
import time
import sys
import os
import re                   #regex
from jira import JIRA
from datetime import datetime
from pandas import ExcelWriter
from pandas import ExcelFile


#date and time
now = datetime.now()
stime=now.strftime("%Y-%m-%d %H:%M:%S")
publickey = ''
jiramailID= ''
ticketType= ''
#parametes for python script
user=sys.argv[1]
apikey=sys.argv[2]
jenkinsuser=sys.argv[3]
rw = sys.argv[4]
instance = sys.argv[5]
JiraTicketId =sys.argv[6]
f = open("logs/SSH_Access.log", "a")
sys.stdout = f
print("{} Execution Begins".format(stime))
#-----------------------------striping @example.com---------------------
def stripMail(word):

   string = word.replace('@example.com',"")
   return string

#---------------fetching public key -------------------------------------
def ExcelRead():
    try:
        #mentioned excel should have only read permision in jenkin server
        df = pd.read_excel('publickeyssh.xlsx', sheet_name='public-ssh-keys-final')
        mailID = df['Email address']

        pkey = df['Public SSH Key']
        for i in range(0,len(mailID)-1):

            if mailID[i]==jenkinsuser:
                publickey=pkey[i]
                print("{} reading public key function".format(stime))
                return publickey
    except:
        import traceback
        print(traceback.format_exc())




#Priority list for Shift employees

os.system("aws s3 cp s3://sshaccess/publickeyssh.xlsx  /var/lib/jenkins/workspace/TestJiraSSHAccess/publickeyssh.xlsx ")
os.system("aws s3 cp s3://sshaccess/PriorityMailList.txt  /var/lib/jenkins/workspace/TestJiraSSHAccess/PriorityMailList.txt ")
if JiraTicketId == "no":
    with open('PriorityMailList.txt', 'r') as emails:
        mail=emails.read()
        if re.search(jenkinsuser,mail):
            print("{} found".format(stime))
            pubkey=ExcelRead()
            linuxusername=stripMail(jenkinsuser)
            os.system("/var/lib/jenkins/workspace/TestJiraSSHAccess/useradd.sh %s admin '\"%s\"' fe '%s' 1"% (linuxusername,pubkey,instance))
            time.sleep(30)
            print("{} Build user {} is in priority list and given access for {}".format(stime,jenkinsuser,instance))
        else :
            print("{} Build user {} is not in priority list".format(stime,jenkinsuser))
            print("Please provide valid JiraTicketId")
    exit(0)



#If build user is not in priority list
else:
    #jira url
    server = 'https://example.atlassian.net'
    options = { 'server': server }

    jira = JIRA(options, basic_auth=(user,apikey))  #Jira Api authentication
    try:
        issue = jira.issue(JiraTicketId) #Fetch Ticket from ticket ID
        getassignee = issue.fields.assignee.displayName       #Fetching assignee from ticket
        assign = unicodedata.normalize('NFKD', getassignee).encode('ascii','ignore')
        status = issue.fields.status
        ticketType = issue.fields.issuetype

        #Fetching Severity field by name
        allfields = jira.fields()
        nameMap = {jira.field['name']:jira.field['id'] for jira.field in allfields}
        getvalue = getattr(issue.fields, nameMap["Severity"])
    except:
        print("{} Ticket ID is wrong or you don't have permission to see it.".format(stime))
    #---------------fetching email of assignee ----------
    def ExceljiraRead():
        try:
            #mentioned excel should have only read permision in jenkin server
            df = pd.read_excel('publickeyssh.xlsx', sheet_name='public-ssh-keys-final')
            jiraDisplayName = df['Employee Name']
            jmailID = df['Email address']
            for i in range(0,len(jmailID)-1):

                if jiraDisplayName[i]==assign:
                    jiramailid=jmailID[i]
                    return jiramailid
        except:
            import traceback
            print(traceback.format_exc())


    #Checking the issue type,severity and status of the ticket
    if((str(ticketType))=="Bug" and (str(getvalue))=="S1" and (str(status))=="Open in Engineering"):
                    jiramailID=str(ExceljiraRead())
                    pubkey=str(ExcelRead())
                    if jiramailID==jenkinsuser:
                        print("{} Jira ticket assignee and username is matching".format(stime))
                        if rw=='RO':
                            print('{} Read Only access have given for {} in {} server for ticket {}  '.format(stime,jenkinsuser,instance,JiraTicketId))
                            linuxusername=stripMail(jiramailID)
                            os.system("/var/lib/jenkins/workspace/TestJiraSSHAccess/useradd.sh %s admin '\"%s\"' fe '%s' 1"% (linuxusername,pubkey,instance))
                        else:
                            print('{} Admin access have given for {} in {} server for ticket {} '.format(stime,jenkinsuser,instance,JiraTicketId))
                            linuxusername=stripMail(jiramailID)
                            os.system("/var/lib/jenkins/workspace/TestJiraSSHAccess/useradd.sh %s read '\"%s\"' fe '%s' 2"% (linuxusername,pubkey,instance))
                       f.close()
    else:
        print('{} Something went wrong please contact administrator'.format(stime))
        print("Possible cases :\n\t issuetype not bug \n\t severity is not S1 \n\t ticket status might be changed \n\t Given mail id is wrong")
f.close()
time.sleep(20)
os.system("rm -rf /var/lib/jenkins/workspace/TestJiraSSHAccess/publickeyssh.xlsx /var/lib/jenkins/workspace/TestJiraSSHAccess/PriorityMailList.txt")
