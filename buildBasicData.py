"""Populate the database with the universal information: permissions, departments, certifications, etc"""

import setupDjango

from django.contrib.sites.models import Site

from ExCSystem import settings
from core.models.CertificationModels import Certification
from core.models.DepartmentModels import Department
from core.models.MemberModels import Staffer
from core.models.QuizModels import Question, Answer


def build_all():
    build_site()
    build_permissions()
    build_quiz_questions()
    build_certifications()
    build_departments()


def build_site():
    """Remane the Site in the sites framework to match actual data"""
    site = Site.objects.all()[0]
    site.domain = settings.SITE_DOMAIN
    site.name = settings.SITE_NAME
    site.save()

def build_permissions():
    """Run the script to build the group and permission structure"""
    import buildPermissions
    buildPermissions.build_all()


def save_question(question_name=None, question_text=None, choices=None, correct_answer_index=0, error_message="You're Wrong!"):

    # Make and save all of the answers
    answers = []
    for answer in choices:
        ans = Answer(answer_phrase=answer[0], answer_text=answer[1])
        ans.save()
        answers.append(ans)

    # make the question and relate all the answers
    question = Question.objects.create(
        usage="membership",
        name=question_name,
        question_text=question_text,
        correct_answer=answers[correct_answer_index],
        error_message=error_message
    )
    question.answers.add(*answers)
    question.save()


def build_quiz_questions():
    # Write default quiz questions
    save_question(
        question_name="Punishment",
        question_text="What is the punishment for breaking a club rule?",
        choices=(
            ("wallow", "Wallow in you own incompetence"),
            ("arrest", "We have you arrested"),
            ("membership", "Forfeit your membership"),
            ("lashes", "10 lashes before the mast")
        ),
        correct_answer_index=2,
        error_message="If you break a rule you lose your membership!"
    )
    save_question(
        question_name="gear",
        question_text="How many of each item type can you check out?",
        choices=(
            ("None", "Trick question, we don't check out gear"),
            ("1", "One of each type of gear"),
            ("2", "Two of each type of gear"),
            ("unlimited", "as many as you'd like")

        ),
        correct_answer_index=1,
        error_message="You can only check out one of each type of item!"
    )
    save_question(
        question_name="certification",
        question_text="How do you get certified for kayaks and SUPS?",
        choices=(
            ("class", "Take a $500 class"),
            ("trip", "Go on a trip with a staffer"),
            ("date", "Bang a bunch of staffers"),
            ("nudie", "Run naked around the block")
        ),
        correct_answer_index=1,
        error_message="To get certified just go on a trip with a staffer."
    )
    save_question(
        question_name="broken",
        question_text="What do you do when a piece of gear breaks?",
        choices=(
            ("hide", "Hide it and hope no one notices"),
            ("run", "Run away, Simba! Run away and NEVER return!"),
            ("fine", "Pay a $10 fine for broken gear"),
            ("tell", "Shit happens. Just let us know so we can fix it")
        ),
        correct_answer_index=3,
        error_message="Just tell us it's broken so we can make sure it stays in good shape."
    )
    save_question(
        question_name="staffers",
        question_text="Who are our staffers?",
        choices=(
            ("volunteers", "Student volunteers who do this for fun"),
            ("pros", "Well-paid professionals"),
            ("blokes", "Random blokes we found on the street"),
            ("fake", "Fake news. There are no staffers")
        ),
        correct_answer_index=0,
        error_message="All our staffers are volunteers!"
    )


def build_certifications():
    # Add certifications
    kayak_cert = Certification(
        title='Kayaking',
        requirements='1) Be able to swim, dammit\n'
        '2) Have received the safety talk, know about wind and current dangers\n'
        '3) Be able to take the kayak out into the surf safely\n'
        '4) Be able to get off of, flip, and get back into a kayak out in deep water\n'
        '5) Be able to bring the kayak back in to shore safely\n'
    )
    kayak_cert.save()

    sup_cert = Certification(
        title='Stand Up Paddleboarding',
        requirements='1) Be able to swim, dammit\n'
        '2) Have received the safety talk, know about wind and current dangers\n'
        '3) Be able to take the SUP out into the surf safely\n'
        '4) Be able to get off of, flip, and get back onto the SUP out in deep water\n'
        '5) Be able to bring the SUP back in to shore safely\n'
    )
    sup_cert.save()


def build_departments():
    # Add departments
    departments = [
        'Camping', 'Backpacking', 'Rock Climbing', 'Skiing/Snowboarding', 'Kayaking', 'Paddleboarding',
        'Surfing', 'Wetsuits', 'Mountaineering', 'Archery', 'Paintballing', 'Free Diving', 'Off-Road'
    ]
    all_staffers = Staffer.objects.all()
    for dept in departments:
        name = dept
        details = 'All the gear related to {}'.format(name)
        department = Department(name=name, description=details)
        department.save()
    print('')
    print('Made departments')


if __name__ == "__main__":
    build_all()