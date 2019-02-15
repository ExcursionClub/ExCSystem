import sys
from helper_scripts import setup_django
from core.tasks import expire_members, update_listserv
from helper_scripts.build_permissions import build_all as build_all_perms


def populate_database():
    import helper_scripts.populate_database


def reset_database():
    import helper_scripts.restart_database


tasks = {
    'expire_member': expire_members,
    'update_listserv': update_listserv,
    'build_permissions': build_all_perms,
    'populate_database': populate_database,
    'reset_database': reset_database,

}


def run(task_name):
    task_name = task_name.lower()
    if task_name in tasks.keys():
        return tasks[task_name]()
    else:
        raise KeyError("Unknown task name!")


if __name__ == "__main__":
    task_to_run = sys.argv[1]
    run(task_to_run)
