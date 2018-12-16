import helper_scripts.setup_django

from core.models.MemberModels import Member


def fix_all_group_names():
    for member in Member.objects.all():
        group_name = member.groups.all()[0].name
        member.group = group_name
        member.save()


def map_group_to_groups():
    """Transfers all the data from the ForeignKey group to the ManyToMany field groups"""
    print("In map group to groups")
    for member in Member.objects.all():
        group_id = member.group_id
        group_name = Group.objects.get(pk=group_id)
        print(f"Group name: {group_name}")
        member.groups.set(Group.objects.filter(name=group_name))
        member.save()



if __name__ == "__main__":
    map_group_to_groups()
