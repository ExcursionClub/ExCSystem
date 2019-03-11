from django.db import models


class Answer(models.Model):

    answer_text = models.CharField(max_length=100)
    answer_text.description = "The full answer text to be displayed to the user"

    answer_phrase = models.CharField(max_length=10)
    answer_phrase.description = (
        "Short one word summary of the answer to be used by the system"
    )

    def __str__(self):
        return f"{self.answer_phrase}: {self.answer_text}"

    def as_choice(self):
        """Return a tuple, as one choice tuple for the choices attribute for a char field"""
        return tuple([self.answer_phrase, self.answer_text])


class Question(models.Model):

    usages = (
        ("membership", "membership quiz questions"),
        ("staffhood", "stafhood quiz questions"),
        ("special", "special questions for special purposes"),
        ("other", "yeah, not sure. something else"),
    )
    usage = models.CharField(max_length=20, choices=usages)

    name = models.CharField(max_length=20, unique=True)
    question_text = models.CharField(max_length=100)
    answers = models.ManyToManyField(to=Answer)
    correct_answer = models.OneToOneField(
        to=Answer, on_delete=models.CASCADE, related_name="+"
    )
    error_message = models.CharField(max_length=100)

    def __str__(self):
        return self.question_text

    def get_choices(self):
        """Get all the answer options as a list of tuples for the choices attribute of a form or model field"""
        choices = []
        for ans in self.answers.all():
            choices.append(ans.as_choice())
        return choices

    def is_correct(self, selected_answer_phrase):
        return selected_answer_phrase == self.correct_answer.answer_phrase
