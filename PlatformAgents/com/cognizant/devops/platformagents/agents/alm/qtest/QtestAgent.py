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

class QtestAgent(BaseAgent):
    def process(self):
        baseUrl = self.config.get("baseUrl", None)
        username = self.config.get("username", None)
        password = self.config.get("password", None)
        headers_token = {'accept': "application/json",'content-type': "application/x-www-form-urlencoded",'authorization': "Basic "}
        payload = "grant_type=password&username="+username+"&password="+password
        trackingDetails = self.tracking.get("token",None)
        if trackingDetails is None:
            tokenResponse = self.getResponse(baseUrl+"/oauth/token", 'POST', None, None, payload, None, headers_token)
            token=tokenResponse.get("access_token", None)
            trackingDetails = {}
            self.tracking["token"] = token
            self.updateTrackingJson(self.tracking)
        token = trackingDetails
        headers = {"accept": "application/json","Authorization": "bearer "+token}
        data = []
        projectsList = self.getResponse(baseUrl+"/api/v3/projects?assigned=false", 'GET', None, None, None, None, headers)
        if len(projectsList) > 0:
            for projects in projectsList:
                projectLinks = projects.get("links", None)
                projectName = projects.get("name", None)
                if len(projectLinks) > 0:
                    for links in projectLinks:
                        link_type = links.get("rel", None)
                        if link_type != "self":
                            link = links.get("href", None)
                            linkResponse = self.getResponse(link, 'GET', None, None, None, None, headers)
                            if len(linkResponse) > 0:
                                for res in linkResponse:
                                    responseTemplate = self.config.get("dynamicTemplate", {}).get("responseTemplate", {}).get(link_type, None)
                                    if responseTemplate:
                                        injectData= {}
                                        data += self.parseResponse(responseTemplate, res, injectData)
        if len(data) > 0:
            self.publishToolsData(data)
                                
                            
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
