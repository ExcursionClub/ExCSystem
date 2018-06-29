from django.db import models


class Answer(models.Model):

    answer_text = models.CharField(max_length=100)
    answer_text.description = "The full answer text to be displayed to the user"

    answer_phrase = models.CharField(max_length=10)
    answer_phrase.description = "Short one word summary of the answer to be used by the system"


class Question(models.Model):

    usages = (("membership", "membership quiz questions"),
              ("staffhood", "stafhood quiz questions"),
              ("special", "special questions for special purposes"),
              ("other", "yeah, not sure. something else"))
    usage = models.CharField(max_length=20, choices=usages)

    question_text = models.CharField(max_length=100)
    answers = models.ManyToManyField(to=Answer)
    correct_answer = models.OneToOneField(to=Answer, on_delete=models.CASCADE)


