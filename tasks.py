import sys
from helper_scripts import setup_django
from core.tasks import expire_members, update_listserv, expire_gear, email_overdue_gear
from helper_scripts.build_permissions import build_all as build_all_perms
from helper_scripts.listserv_interface import get_email_file
from helper_scripts.fix_member_group import fix_all_group_names


def populate_database():
    import helper_scripts.populate_database


def reset_database():
    import helper_scripts.restart_database


tasks = {
    "expire_members": expire_members,
    "expire_gear": expire_gear,
    "email_overdue_gear": email_overdue_gear,
    "update_listserv": update_listserv,
    "get_email_file": get_email_file,
    "build_permissions": build_all_perms,
    "populate_database": populate_database,
    "reset_database": reset_database,
    "fix_group": fix_all_group_names,
}


def run_task(task_name):
    task_name = task_name.lower()
    if task_name in tasks.keys():
        func = tasks[task_name]
        return func()
    else:
        raise KeyError("Unknown task name!")


if __name__ == "__main__":
    task_to_run = sys.argv[1]
    value = run_task(task_to_run)
    print(value)
