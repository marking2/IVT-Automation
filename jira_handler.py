from Ibox import Ibox
from components.component import Component
from jira import JIRA, JIRAError

JIRA_DOMAIN = "https://jira.infinidat.com"

TELAD_REPLACEMENT = ["NODE"]
MT_REPLACEMENTS = ["SFP", "DIMM", "Node Components", "Local Drive"]
DRIVES = ["Enclosure Drive", "Local Drive", "SSD"]
RESOLUTIONS = [31, 21, 81]


def init_jira(user):
    options = {'server': JIRA_DOMAIN}
    return JIRA(options, basic_auth=(user["name"], user["password"]))


def create_jira_issue(ibox: Ibox,
                      component: Component,
                      user,
                      jira: JIRA,
                      file_logs: str,
                      description: str,
                      rc: str,
                      resolution: int):
    if component.get_model_parent() in MT_REPLACEMENTS and \
            component.__class__.__name__ != DRIVES[2]:
        issue = create_mt_issue(ibox,
                                component,
                                jira,
                                description)
    else:
        issue = create_ivts_issue(ibox,
                                  component,
                                  user,
                                  jira,
                                  description,
                                  rc)

    print("Issue Link: {}/browse/{}".format(JIRA_DOMAIN, issue.key))

    meta = jira.editmeta(issue)

    issue.update(fields={"customfield_11508": component.serial})

    if component.get_model_parent() in DRIVES:
        description += file_logs
    else:
        if file_logs:
            jira.add_attachment(issue=issue, attachment=file_logs)
    issue.update(description=description)
    # description = description + "\nRC: " + rc
    # if description:
    #     logs = open("component_logs.txt", "w")
    #     logs.write(description)
    #     jira.add_attachment(issue=issue, attachment=logs)

    taivt = get_taivt(jira, ibox.serial_number)
    if taivt:
        jira.create_issue_link(type='relates to', inwardIssue=taivt.key, outwardIssue=issue.key)
        comment = "On hold due to: {}".format(issue.key)
        transitions = jira.transitions(taivt)
        on_hold = False
        for transition in [(t['id'], t['name']) for t in transitions]:
            if '61' in transition[0] and not on_hold:  # Check if 'On Hold' transition available
                transition_of_issue(jira, taivt, 61, comment)
                print("TAIVT put on hold")
                on_hold = True
        if not on_hold:
            jira.add_comment(taivt, comment)

    ivts_list = get_ivts_incidents(ibox, jira, component.get_model_parent())
    if ivts_list:
        for ivts in ivts_list:
            jira.create_issue_link(type='relates to', inwardIssue=ivts.key, outwardIssue=issue.key)
            comment = "Replacing {} at {}".format(component.get_original_location(), issue.key)
            jira.add_comment(ivts, comment)

    if component.model:
        for allowed_value in meta["fields"]["customfield_11507"]["allowedValues"]:
            for child in allowed_value["children"]:
                if component.model in child["value"]:
                    if ("MZILT7T6HALA" and "007") in component.model:
                        issue.update(fields={"customfield_11507": {"value": component.get_model_parent(),
                                                                   "child": {"value": "SSD-11152 - SSD,SAMSUNG,"
                                                                                      "MZILT7T6HALA-00007,PM1643a,"
                                                                                      "7.68TB,W ADAPTOR"}}})
                    else:
                        issue.update(fields={"customfield_11507": {"value": component.get_model_parent(),
                                                                   "child": {"value": child["value"]}}})
                    print("Model Updated")
    else:
        issue.update(fields={"customfield_11507": {"value": component.get_model_parent()}})

    if component.get_model_parent() not in MT_REPLACEMENTS and \
            resolution in RESOLUTIONS:
        try:
            transition_of_issue(jira, issue, resolution, comment="")
        except JIRAError:
            print(JIRAError, "Transition failed")

    return issue


def create_ivts_issue(ibox: Ibox,
                      component: Component,
                      user,
                      jira: JIRA,
                      description: str,
                      rc: str):
    issue = jira.create_issue(project={"key": "IVTS"},
                              summary="IBOX{}: ".format(ibox.serial_number) + component.get_summary(),
                              description=description,
                              issuetype={"name": "Part Replacement"})
    issue.update(fields={"customfield_16713": component.get_original_location()})
    issue.update(fields={"customfield_16315": {"value": "TelAd"}})
    issue.update(assignee={'name': user["name"]})
    issue.update(fields={"customfield_12734": [str(ibox.serial_number)]})
    issue.update(fields={"customfield_15926": {"value": component.get_rc_parent()}})

    meta = jira.editmeta(issue)
    for allowed_value in meta["fields"]["customfield_15926"]["allowedValues"]:
        if component.get_rc_parent() in allowed_value["value"]:
            for child in allowed_value["children"]:
                if rc and rc in child["value"]:
                    try:
                        issue.update(fields={"customfield_15926": {"value": component.get_rc_parent(),
                                                                   "child": {"value": rc}}})
                        print("Rejection Criteria Updated")
                    except JIRAError as je:
                        print(je, "\nFailed to update rc child")
    return issue


def create_mt_issue(ibox: Ibox,
                    component: Component,
                    jira: JIRA,
                    description: str):
    taivt = jira.search_issues(f"""project = "TelAd IVT" AND summary ~ IBOX{str(ibox.serial_number)}""")
    mt_dict = {"project": "MT",
               "summary": "IBOX{}: ".format(ibox.serial_number) + component.get_summary(),
               "issuetype": {"name": "HW analysis"},
               "description": description,
               "customfield_11507": {"value": component.get_model_parent()},
               "customfield_14625": {"value": "Tel-Ad",
                                     "child": {"value": taivt[0].fields.environment}}}

    issue = jira.create_issue(mt_dict)
    issue.update(assignee={'name': "yevgenis"})
    return issue


def get_taivt(jira: JIRA, ibox_serial: str):
    taivt_issues = jira.search_issues(
        """project = TAIVT AND text ~ IBOX{} order by created DESC""".format(
            ibox_serial))  # Jira api limits search_issues to 50 results
    for issue in taivt_issues:
        if "IBOX{}".format(ibox_serial) in str(issue.fields.summary):
            return issue
    return None


def get_ivts_incidents(ibox: Ibox, jira: JIRA, component_model_parent: str):
    ivts_issues = jira.search_issues(
        f"""project = "IVT Support" AND issuetype = "IVT Incident" AND 
        (status = Open OR status = "In Progress") AND 
        summary ~ IBOX{ibox.serial_number} AND 
        summary !~ TEST AND 
        text ~ "{component_model_parent}" order by created DESC""")  # Jira api limits search_issues to 50 results
    if ivts_issues:
        return ivts_issues
    return None


def transition_of_issue(jira, issue, transition_number: int, comment: str) -> None:
    jira.transition_issue(issue, str(transition_number))
    if comment:
        jira.add_comment(issue.key, body=comment)


def get_resolution(resolution):
    if "RMA" in resolution:
        resolution = 31
    elif "FA" in resolution:
        resolution = 21
    elif "Internal Use" in resolution:
        resolution = 81
    else:
        resolution = 0
    return resolution
