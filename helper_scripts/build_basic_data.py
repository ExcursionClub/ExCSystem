"""Populate the database with the universal information: permissions, departments, certifications, etc"""
from helper_scripts import setup_django

import os
import random

from core.models.CertificationModels import Certification
from core.models.DepartmentModels import Department
from core.models.FileModels import AlreadyUploadedImage
from core.models.QuizModels import Answer, Question
from django.contrib.sites.models import Site
from django.db.utils import IntegrityError

from uwccsystem import settings


def build_all():

    build_funcs = [
        build_site,
        build_permissions,
        build_quiz_questions,
        build_certifications,
        build_departments,
        build_images
    ]
    for func in build_funcs:
        try:
            func()
        except IntegrityError as ex:
            print(f'  Skipping Error: {ex}')
            pass


def build_images():
    print("Uploading gear images...")

    sub_types = ["Fake SubType", "SubType I made up", "More Type", "Something"]

    # Build the default common shaka image
    try:
        img = AlreadyUploadedImage.objects.create(image_type="gear", picture=settings.DEFAULT_IMG)
        img.save()
    except IntegrityError:
        print(f'Shaka Image already exists')


def build_site():
    """Re-name the Site in the sites framework to match actual data"""
    site = Site.objects.all()[0]
    site.domain = settings.SITE_DOMAIN
    site.name = settings.SITE_NAME
    site.save()


def build_permissions():
    """Run the script to build the group and permission structure"""
    from helper_scripts import build_permissions

    build_permissions.build_all()


def save_question(
    question_name=None,
    question_text=None,
    choices=None,
    correct_answer_index=0,
    error_message="You're Wrong!",
):
    # Make and save all of the answers
    answers = []
    for answer in choices:
        ans = Answer(answer_phrase=answer[0], answer_text=answer[1])
        ans.save()
        answers.append(ans)

    # make the question and relate all the answers
    try:
        question = Question.objects.create(
            usage="membership",
            name=question_name,
            question_text=question_text,
            correct_answer=answers[correct_answer_index],
            error_message=error_message,
        )
        question.answers.add(*answers)
        question.save()
    except IntegrityError as ex:
        print(f'Question {question_name} already exists. Skipping!')
        pass


def build_quiz_questions():
    # Write default quiz questions
    save_question(
        question_name="Punishment",
        question_text="What is the punishment for breaking a club rule?",
        choices=(
            ("wallow", "Wallow in you own incompetence"),
            ("arrest", "We have you arrested"),
            ("membership", "Forfeit your membership"),
            ("lashes", "10 lashes before the mast"),
        ),
        correct_answer_index=2,
        error_message="If you break a rule you lose your membership!",
    )
    save_question(
        question_name="gear",
        question_text="How many of each item type can you check out?",
        choices=(
            ("None", "Trick question, we don't check out gear"),
            ("1", "One of each type of gear"),
            ("2", "Two of each type of gear"),
            ("unlimited", "as many as you'd like"),
        ),
        correct_answer_index=1,
        error_message="You can only check out one of each type of item!",
    )
    save_question(
        question_name="broken",
        question_text="What do you do when a piece of gear breaks?",
        choices=(
            ("hide", "Hide it and hope no one notices"),
            ("run", "Run away, Simba! Run away and NEVER return!"),
            ("fine", "Pay a $10 fine for broken gear"),
            ("tell", "Shit happens. Just let us know so we can fix it"),
        ),
        correct_answer_index=3,
        error_message="Just tell us it's broken so we can make sure it stays in good shape.",
    )
    save_question(
        question_name="staffers",
        question_text="Who are our staffers?",
        choices=(
            ("volunteers", "Student volunteers who do this for fun"),
            ("pros", "Well-paid professionals"),
            ("blokes", "Random blokes we found on the street"),
            ("fake", "Fake news. There are no staffers"),
        ),
        correct_answer_index=0,
        error_message="All our staffers are volunteers!",
    )


def build_certifications():
    kayak_cert = Certification(
        title="Kayaking",
        requirements="1) Be able to swim, dammit\n"
        "2) Have received the safety talk, know about wind and current dangers\n"
        "3) Be able to take the kayak out into the surf safely\n"
        "4) Be able to get off of, flip, and get back into a kayak out in deep water\n"
        "5) Be able to bring the kayak back in to shore safely\n",
    )
    kayak_cert.save()


def build_departments():
    departments = [
        "Camping",
        "Backpacking",
        "Rock Climbing",
        "Mountaineering"
    ]

    for dept in departments:
        name = dept
        details = "All the gear related to {}".format(name)
        department = Department(name=name, description=details)
        department.save()
    print("")
    print("Made departments")


if __name__ == "__main__":
    build_all()
