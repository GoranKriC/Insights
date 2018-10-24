#-------------------------------------------------------------------------------
# Copyright 2017 Cognizant Technology Solutions
# 
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License.  You may obtain a copy
# of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# License for the specific language governing permissions and limitations under
# the License.
#-------------------------------------------------------------------------------
from com.cognizant.devops.platformagents.core.BaseAgent import BaseAgent
from datetime import datetime as dateTime2
from dateutil import parser
import datetime
import json

class QtestAgent(BaseAgent):
    def process(self):
        baseUrl = self.config.get("baseUrl", None)
        username = self.config.get("username", None)
        password = self.config.get("password", None)
        startFrom = self.config.get("startFrom", '')
        startFrom = parser.parse(startFrom, ignoretz=True)
        headers_token = {'accept': "application/json",'content-type': "application/x-www-form-urlencoded",'authorization': "Basic T25lRGV2T3BzSW5TaWdodHM6"}
        payload = "grant_type=password&username="+str(username)+"&password="+str(password)
        trackingDetails = self.tracking.get("token",None)
        if trackingDetails is None:
            tokenResponse = self.getResponse(baseUrl+"/oauth/token", 'POST', None, None, payload, None, headers_token)
            token=tokenResponse.get("access_token", None)
            trackingDetails = {}
            self.tracking["token"] = token
        else:
            token=trackingDetails
        headers = {"accept": "application/json","Authorization": "bearer "+str(token)+""}
        projectsList = self.getResponse(baseUrl+"/api/v3/projects?assigned=false", 'GET', None, None, None, None, headers)
        if len(projectsList) > 0:
            for projects in projectsList:
                projectLinks = self.config.get("dynamicTemplate", {}).get("extensions", None)
                projectName = projects.get("name", None)
                projectId = projects.get("id", None)
                projectLastUpdateDate = self.tracking.get(str(projectId), {}).get("lastupdated", None)
                if projectLastUpdateDate is not None:
                    startFrom = parser.parse(projectLastUpdateDate, ignoretz=True)
                if len(projectLinks) > 0:
                    linkUpdateTracking = []
                    projectMaxUpdateDate = None
                    for links in projectLinks:
                        data = []
                        link_type = links.get("type", None)
                        if link_type != "self":
                            link = baseUrl + "/api/v3/projects/" + str(projectId) + "/" + str(link_type)
                            pagination = links.get("pagination", False)
                            if pagination:
                                page_num = 1
                                page_size = 25
                                link = baseUrl + "/api/v3/projects/" + str(projectId) + "/" + str(link_type) + "?page=" + str(page_num) + "&size=" + str(page_size) + "&expandProps=false&expandSteps=false"
                            nextPageResponse = True
                            linkResponse = self.getResponse(link, 'GET', None, None, None, None, headers)
                            while nextPageResponse:
                                if len(linkResponse) > 0:
                                    linkTypeUpdateTracking = {link_type: True}
                                    linkUpdateTracking.append(linkTypeUpdateTracking)
                                    try:
                                        for res in linkResponse:
                                            lastUpdated = res.get('last_modified_date', None)
                                            if lastUpdated > projectMaxUpdateDate:
                                                projectMaxUpdateDate = lastUpdated
                                            if lastUpdated is not None:
                                                lastUpdated = parser.parse(lastUpdated, ignoretz=True)
                                            if lastUpdated is not None and lastUpdated > startFrom:
                                                responseTemplate = links.get("responseTemplate", None)
                                                if responseTemplate:
                                                    injectData= {}
                                                    injectData['projectName'] = projectName
                                                    injectData['projectId'] = projectId
                                                    injectData['type'] = link_type
                                                    data += self.parseResponse(responseTemplate, res, injectData)
                                    except Exception as ex:
                                        nextPageResponse = False
                                        break
                                        logging.error(ex)
                                else:
                                    nextPageResponse = False
                                if pagination:
                                    page_num = page_num + 1
                                    link = baseUrl + "/api/v3/projects/" + str(projectId) + "/" + str(link_type) + "?page=" + str(page_num) + "&size=" + str(page_size) + "&expandProps=false&expandSteps=false"
                                    linkResponse = self.getResponse(link, 'GET', None, None, None, None, headers)
                                else:
                                    nextPageResponse = False
                        metadata = links.get("metadata", None)
                        if len(data) > 0:
                            self.publishToolsData(data, metadata)
                    trackingDetails = {"lastupdated": projectMaxUpdateDate, "linkUpdateTracking": linkUpdateTracking}
                    self.tracking[str(projectId)] = trackingDetails
                    self.updateTrackingJson(self.tracking)
                enableTraceMatrixReport = self.config.get("enableTraceMatrixReport", False)
                dataTraceMatrix = []
                if enableTraceMatrixReport:
                    #metaDataTraceMatrix = {"labels" : ["QTEST_REQUIREMENT"],"dataUpdateSupported" : True,"uniqueKey" : ["projectId", "ID"]}
                    metaDataTraceMatrix = self.config.get("dynamicTemplate", {}).get("traceMatrixReportMetadata", None)
                    page_size = 25
                    page_num = 1
                    link = baseUrl + "/api/v3/projects/" + str(projectId) + "/requirements/trace-matrix-report" + "?page=" + str(page_num) + "&size=" + str(page_size)
                    traceMatrixReport = self.getResponse(link, 'GET', None, None, None, None, headers)
                    nextPageResponse = True
                    while nextPageResponse:
                        if len(traceMatrixReport) > 0:
                            traceMatrixReport = traceMatrixReport[0].get("requirements", None)
                            for matrix in traceMatrixReport:
                                injectData= {}
                                if 'testcases' in matrix:
                                    injectData['projectName'] = projectName
                                    injectData['projectId'] = projectId
                                    injectData['testcases'] = matrix.get('testcases', None)
                                    injectData['linkedTestcaseCount'] = matrix.get('linked-testcases', None)
                                    injectData['ID'] = matrix.get('id', None)
                                    dataTraceMatrix.append(injectData)
                        else:
                            nextPageResponse = False
                        page_num = page_num + 1
                        link = baseUrl + "/api/v3/projects/" + str(projectId) + "/requirements/trace-matrix-report" + "?page=" + str(page_num) + "&size=" + str(page_size)
                        traceMatrixReport = self.getResponse(link, 'GET', None, None, None, None, headers)
                    if len(dataTraceMatrix) > 0:
                        self.publishToolsData(dataTraceMatrix, metaDataTraceMatrix)
    '''
                            self.numbers_to_months(link_type, link)
    def numbers_to_months(self, link_type, link):
        switch_link = { 
            "releases": self.get_releases, 
            "test-cycles": self.get_cycles, 
            "test-suites": self.get_suites, 
            "test-runs": self.get_runs,
            "test-cases": self.get_cases
                        }
        func = switch_link.get(link_type, lambda: "Unknown Process")
        func(link)
    def get_releases(self, link):
        print link
    def get_cycles(self, link):
        print link
    def get_suites(self, link):
        print link
    def get_runs(self, link):
        print link
    def get_cases(self, link):
        print link
    '''
                
if __name__ == "__main__":
    QtestAgent()       
