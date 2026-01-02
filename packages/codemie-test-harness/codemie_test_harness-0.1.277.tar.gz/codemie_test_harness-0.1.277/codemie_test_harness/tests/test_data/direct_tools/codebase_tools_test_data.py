import pytest

from codemie_test_harness.tests.enums.tools import Toolkit, CodeBaseTool

sonar_tools_test_data = [
    pytest.param(
        Toolkit.CODEBASE_TOOLS,
        CodeBaseTool.SONAR,
        {
            "relative_url": "/api/issues/search",
            "params": '{"types":"CODE_SMELL","ps":"1"}',
        },
        """
            {
              "total" : 71,
              "p" : 1,
              "ps" : 1,
              "paging" : {
                "pageIndex" : 1,
                "pageSize" : 1,
                "total" : 71
              },
              "effortTotal" : 482,
              "issues" : [ {
                "key" : "89db8998-115c-4fbe-96bd-510e1e6f9f26",
                "rule" : "python:S5713",
                "severity" : "MINOR",
                "component" : "codemie:src/codemie/rest_api/routers/index.py",
                "project" : "codemie",
                "line" : 1171,
                "hash" : "10ad4a4551083c0ddbcb5863814db038",
                "textRange" : {
                  "startLine" : 1171,
                  "endLine" : 1171,
                  "startOffset" : 16,
                  "endOffset" : 36
                },
                "flows" : [ {
                  "locations" : [ {
                    "component" : "codemie:src/codemie/rest_api/routers/index.py",
                    "textRange" : {
                      "startLine" : 1171,
                      "endLine" : 1171,
                      "startOffset" : 38,
                      "endOffset" : 48
                    },
                    "msg" : "Parent class.",
                    "msgFormattings" : [ ]
                  } ]
                } ],
                "status" : "OPEN",
                "message" : "Remove this redundant Exception class; it derives from another which is already caught.",
                "effort" : "1min",
                "debt" : "1min",
                "author" : "",
                "tags" : [ "error-handling", "bad-practice", "unused" ],
                "creationDate" : "2025-12-12T08:50:22+0000",
                "updateDate" : "2025-12-12T08:50:22+0000",
                "type" : "CODE_SMELL",
                "scope" : "MAIN",
                "quickFixAvailable" : false,
                "messageFormattings" : [ ],
                "codeVariants" : [ ],
                "cleanCodeAttribute" : "LOGICAL",
                "cleanCodeAttributeCategory" : "INTENTIONAL",
                "impacts" : [ {
                  "softwareQuality" : "MAINTAINABILITY",
                  "severity" : "LOW"
                } ],
                "issueStatus" : "OPEN",
                "prioritizedRule" : false
              } ],
              "components" : [ {
                "key" : "codemie:src/codemie/rest_api/routers/index.py",
                "enabled" : true,
                "qualifier" : "FIL",
                "name" : "index.py",
                "longName" : "src/codemie/rest_api/routers/index.py",
                "path" : "src/codemie/rest_api/routers/index.py"
              }, {
                "key" : "codemie",
                "enabled" : true,
                "qualifier" : "TRK",
                "name" : "codemie",
                "longName" : "codemie"
              } ],
              "facets" : [ ]
            }
        """,
        marks=pytest.mark.sonar,
        id=CodeBaseTool.SONAR,
    ),
    pytest.param(
        Toolkit.CODEBASE_TOOLS,
        CodeBaseTool.SONAR_CLOUD,
        {
            "relative_url": "/api/issues/search",
            "params": '{"types":"CODE_SMELL","ps":"1"}',
        },
        """
            {
              "total" : 15,
              "p" : 1,
              "ps" : 1,
              "paging" : {
                "pageIndex" : 1,
                "pageSize" : 1,
                "total" : 15
              },
              "effortTotal" : 127,
              "debtTotal" : 127,
              "issues" : [ {
                "key" : "AZTWg867SN_Wuz1X4Py2",
                "rule" : "kubernetes:S6892",
                "severity" : "MAJOR",
                "component" : "alezander86_python38g:deploy-templates/templates/deployment.yaml",
                "project" : "alezander86_python38g",
                "line" : 34,
                "hash" : "723c0daa435bdafaa7aa13d3ae06ca5e",
                "textRange" : {
                  "startLine" : 34,
                  "endLine" : 34,
                  "startOffset" : 19,
                  "endOffset" : 30
                },
                "flows" : [ ],
                "status" : "OPEN",
                "message" : "Specify a CPU request for this container.",
                "effort" : "5min",
                "debt" : "5min",
                "author" : "codebase@edp.local",
                "tags" : [ ],
                "creationDate" : "2024-11-07T13:14:43+0000",
                "updateDate" : "2025-02-05T14:28:27+0000",
                "type" : "CODE_SMELL",
                "organization" : "alezander86",
                "cleanCodeAttribute" : "COMPLETE",
                "cleanCodeAttributeCategory" : "INTENTIONAL",
                "impacts" : [ {
                  "softwareQuality" : "MAINTAINABILITY",
                  "severity" : "MEDIUM"
                }, {
                  "softwareQuality" : "RELIABILITY",
                  "severity" : "MEDIUM"
                } ],
                "issueStatus" : "OPEN",
                "projectName" : "python38g"
              } ],
              "components" : [ {
                "organization" : "alezander86",
                "key" : "alezander86_python38g:deploy-templates/templates/deployment.yaml",
                "uuid" : "AZTWg8uJSN_Wuz1X4Pye",
                "enabled" : true,
                "qualifier" : "FIL",
                "name" : "deployment.yaml",
                "longName" : "deploy-templates/templates/deployment.yaml",
                "path" : "deploy-templates/templates/deployment.yaml"
              }, {
                "organization" : "alezander86",
                "key" : "alezander86_python38g",
                "uuid" : "AZTWgJZiF0LopzvlIH8p",
                "enabled" : true,
                "qualifier" : "TRK",
                "name" : "python38g",
                "longName" : "python38g"
              } ],
              "organizations" : [ {
                "key" : "alezander86",
                "name" : "Taruraiev Oleksandr"
              } ],
              "facets" : [ ]
            }
        """,
        marks=pytest.mark.sonar,
        id=CodeBaseTool.SONAR_CLOUD,
    ),
]
