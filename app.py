import random


from datasets import load_dataset
from flask import Flask, render_template, url_for, redirect, request, current_app
app = Flask(__name__)

dataset = (
    load_dataset("hotpot_qa", "distractor")["train"]
    .filter(lambda x: x["answer"] not in {"yes", "no"} and x["level"] not in {"easy", "medium"})
)

correct_lessons = []
incorrect_lessons = []

def highlight_random_words(words, color, N=20):
    # In "real setting", these would be highlights from feature importance methods like LIME
    word_idxs = random.sample(range(len(words)), N)
    context = [
        '<span style="background-color:{0}">{1}</span>'.format(color, word) if i in word_idxs else word 
        for i, word in enumerate(words)
    ]
    return " ".join(context)

@app.route('/')
def index():
    option = random.choice(dataset)
    current_app.answer = option["answer"]
    context = "\n".join(" ".join(e) for e in option["context"]["sentences"])
    return render_template(
        "testing.html", context=context, question=option["question"], 
        correct_lessons=correct_lessons, incorrect_lessons=incorrect_lessons
    )

@app.route("/", methods=["POST"])
def index_post():
  return redirect(url_for("teaching"))

@app.route('/teaching')
def teaching():
    # In "real setting", these would be contrasting examples
    option1 = random.choice(dataset)
    option2 = random.choice(dataset)
    context1 = "\n".join(" ".join(e) for e in option1["context"]["sentences"])
    context2 = "\n".join(" ".join(e) for e in option2["context"]["sentences"])

    highlighted_context1 = highlight_random_words(context1.split(), "#FF0000")
    highlighted_context2 = highlight_random_words(context2.split(), "#008000")

    model_correct =  random.random() > 0.5
    model_correct_str = '<span style="background-color:#008000">Correct</span>' if model_correct \
        else  '<span style="background-color:#FF0000">Incorrect</span>'
    current_app.model_correct = model_correct

    return render_template(
        "teaching.html", model_correct=model_correct_str, context1=highlighted_context1, 
        question1=option1["question"], context2=highlighted_context2, question2=option2["question"]
    )
 
@app.route("/teaching", methods=["POST"])
def teaching_post():
    lesson = request.form["lesson"]
    if current_app.model_correct:
        correct_lessons.append(lesson)
    else:
        incorrect_lessons.append(lesson)
    return redirect(url_for("index"))
