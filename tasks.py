import sys
from helper_scripts import setup_django
from core.tasks import expire_members, update_listserv


tasks = {
    'expire_member': expire_members,
    'update_listserv': update_listserv
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
