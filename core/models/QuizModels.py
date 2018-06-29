from django.db import models


class Answer(models.Model):

    answer_text = models.CharField(max_length=100)
    answer_text.description = "The full answer text to be displayed to the user"

    answer_phrase = models.CharField(max_length=10)
    answer_phrase.description = "Short one word summary of the answer to be used by the system"

    def __str__(self):
        return "{phrase}: {text}".format(phrase=self.answer_phrase, text=self.answer_text)

    def as_choice(self):
        """Return a tuple, as one choice tuple for the choices attribute for a char field"""
        return tuple([self.answer_phrase, self.answer_text])


class Question(models.Model):

    usages = (("membership", "membership quiz questions"),
              ("staffhood", "stafhood quiz questions"),
              ("special", "special questions for special purposes"),
              ("other", "yeah, not sure. something else"))
    usage = models.CharField(max_length=20, choices=usages)

    question_text = models.CharField(max_length=100)
    answers = models.ManyToManyField(to=Answer, null=True)
    correct_answer = models.OneToOneField(to=Answer, on_delete=models.CASCADE, related_name='+')

    def __str__(self):
        return self.question_text

    def is_correct(self, selected_answer_phrase):
        return selected_answer_phrase == self.correct_answer.answer_phrase


