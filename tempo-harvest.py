# Jira API Authentication Links
# https://confluence.atlassian.com/cloud/api-tokens-938839638.html
# https://developer.atlassian.com/cloud/jira/platform/jira-rest-api-basic-authentication/

import requests
from datetime import datetime


class HarvestInvoicer(object):
    def __init__(self):
        self.harvestLogs = []
        self.getHarvestStuff()  # Call first Function to getHarvestStuff then Return back here when done


    def getHarvestStuff(self):
        # Date parameters (yyyy-mm-dd) and harvest id
        fromDate = ''
        toDate = ''
        harvestProjId = ''
        tempoAccount = ''

        harvestappHeaders = {
            'Authorization': '',
            'Harvest-Account-ID': '', "Content-Type": "application/json"}
        tempoHeaders = {'Authorization': ''}
        jiraHeaders = {'Authorization': '',
                       'Content-Type': 'application/json'}
        responseData = requests.get("https://api.tempo.io/core/3/worklogs/account/"+tempoAccount+"?from=" + fromDate + "&to=" + toDate + "&limit=1000", headers=tempoHeaders).json()

        accountWorkLogs = responseData['results']
        issuesList = []

        for log in accountWorkLogs:
            issuesList.append(log['issue']['key'])
            issuesList = set(issuesList)
            issuesList = list(issuesList)

        for issue in issuesList:
            response = requests.get("https://somejira.atlassian.net/rest/api/2/issue/" + issue, headers=jiraHeaders)
            data = response.json()
            issueObject = {'issueId': issue, 'summary': data['fields']['summary']}
            self.harvestLogs.append(issueObject)

        for log in self.harvestLogs:
            totalTime = 0
            issueDate = datetime.strptime(fromDate, '%Y-%m-%d')
            response = requests.get(
                "https://api.tempo.io/core/3/worklogs/issue/" + log['issueId'] + "?from=" + fromDate + "&to=" + toDate,
                headers=tempoHeaders)
            data = response.json()

            for f in data['results']:
                totalTime += f['billableSeconds']
                datetime_object = datetime.strptime(f['startDate'], '%Y-%m-%d')
                if (datetime_object > issueDate):
                    issueDate = datetime_object

            log['hours'] = totalTime / float(3600)
            log['date'] = issueDate.strftime('%Y-%m-%d')

        for e in self.harvestLogs:
            notes = e['issueId'] + " - " + e['summary']
            r = requests.post("https://api.harvestapp.com/api/v2/time_entries",
                              json={'project_id': harvestProjId, 'task_id': ###, 'spent_date': e['date'],
                                    'hours': e['hours'], 'notes': notes}, headers=harvestappHeaders)
            print(e['issueId'], e['date'], notes)
            print(r.status_code, r.reason)


if __name__ == '__main__':
    invoicer = HarvestInvoicer()  ## Creates a new HarvestInvoicer Class and runs the __init__ method



