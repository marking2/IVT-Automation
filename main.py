import user_handler
import jira_handler
from Ibox import Ibox

if __name__ == "__main__":
    args = user_handler.parse_args()
    ibox_serial = args.ibox
    user = user_handler.get_user_info(user=args.user, password=args.password)
    jira = jira_handler.init_jira(user)
    taivt = jira_handler.get_taivt(jira, ibox_serial)
    ibox = Ibox(ibox_serial, user["name"], jira)
    description = args.description

    component = user_handler.get_component(args, ibox)
    try:
        print(str(component))
    except ValueError as ve:
        print(ve)
    if not component.serial:
        component.serial = "Please provide old S/N"
    logs_path = ""
    if not args.noLogs and "sa" not in args.component:
        logs_path = component.collect_logs(ibox)
    if "sa" in args.component:
        description += "\n" + component.smartctl

    resolution = jira_handler.get_resolution(args.resolution)

    issue = jira_handler.create_jira_issue(
        ibox,
        component,
        user,
        jira,
        logs_path,
        description,
        args.rejection,
        resolution)
