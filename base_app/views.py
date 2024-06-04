from django_xhtml2pdf.utils import generate_pdf
from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView
from .models import Question, Answer, Stage, Result, Certificate
import json
from django.http import JsonResponse
import os
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders
from django.db.models import Sum

from django.core.files import File
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont


class IndexView(ListView):
    template_name = "index.html"
    model = Stage
    context_object_name = "stages"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['results'] = list(Result.objects.filter(
            user=self.request.user).values('stage').distinct())
        try:
            context['results'] = context['results'][-1]['stage']+1
        except:
            context['results'] = 1
        stage_count = Stage.objects.all().count()
        if stage_count+1 == context['results']:
            context['diplom'] = 'diplom'

        else:
            context['diplom'] = 'yoq'
        context['stages'] = Stage.objects.all()
        return context


class TestDetailView(ListView):
    template_name = "test_detail.html"
    model = Question
    context_object_name = "questions"

    def get_queryset(self):
        queryset = Question.objects.filter(stage__id=self.kwargs.get('pk'))
        return queryset


def TestCheckerView(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        stage = data['stage']
        answers = data['answers']
        correct_answers_list = list(Answer.objects.filter(
            question__stage=stage, is_correct=True).values('question', 'text'))
        correct_ans_count = 0
        for user_ans, true_ans in zip(answers, correct_answers_list):
            if user_ans['answer'] == true_ans['text']:
                correct_ans_count += 1

        stage = Stage.objects.filter(id=stage)[0]
        Result.objects.create(
            user=request.user, stage=stage, score=correct_ans_count)
        last_stage = Stage.objects.last()

        if last_stage.id > stage.id:
            next_stage = stage.id+1
        else:
            next_stage = 0
        return JsonResponse({'correct_ans_count': correct_ans_count, 'next_stage': next_stage})


def render_pdf_view(request):
    # Load the base image
    img = Image.open('diplom.jpg')
    draw = ImageDraw.Draw(img)

    # Define the font and size
    font_path = 'FreeMono.ttf'
    font_size = 65
    font = ImageFont.truetype(font_path, font_size)

    # Define the text and position
    text = "Qodirov Rasulbek"
    position = (350, 450)
    color = (5, 37, 98) # Red color

    # Draw the text onto the image
    draw.text(position, text, font=font, fill=color)

    # Save the edited image to a temporary location
    temp_image_path = 'temp_certificate.png'
    img.save(temp_image_path)

    # Open the saved image as a Django File object
    with open(temp_image_path, 'rb') as f:
        django_file = File(f)

        # Create a new Certificate object and save the image to the ImageField
        cert = Certificate.objects.create(user=request.user)
        cert.img.save('certificate.png', django_file, save=True)

    # Clean up the temporary file
    os.remove(temp_image_path)

    cert = Certificate.objects.filter(user=request.user).last()

    return render(request, 'user_printer.html', {"cert": cert})
