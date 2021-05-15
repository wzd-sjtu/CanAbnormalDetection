from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
import os
from . import generalModels as gm

global_data = []


def instantiate_glabal_data(file):
    """Read from dataset and instantiate global_data with SingleData"""
    global_data.clear()
    raw_lines = file.readlines()
    raw_lines.pop(0)
    for line in raw_lines:
        items = line.decode('utf-8').strip().split(',')
        hex_to_dec = int(items[2], 16)
        dec_to_bin = bin(hex_to_dec)[2:]
        sd = gm.SingleData(items[1], items[3], items[2], dec_to_bin)
        global_data.append(sd)


def home(request):
    return render(request, 'home.html')


def parse(request):
    file = request.FILES.get('myfile')
    items = []
    if file:
        instantiate_glabal_data(file)
        return render(request, 'parse/parse.html', {'parse': global_data})
    else:
        return render(request, 'parse/parse.html')


def _parse_sequence(request):
    return render(request, 'parse/sequence.html', {'parse': global_data})


def _parse_datafield(request):
    return render(request, 'parse/datafield.html', {'parse': global_data})


def detect(request):
    file = request.FILES.get('myfile')
    items = []
    if file:
        instantiate_glabal_data(file)
        return render(request, 'detect/detect.html', {'detect': global_data})
    else:
        return render(request, 'detect/detect.html')


def _detect_sequence(request):
    return render(request, 'detect/sequence.html', {'detect': global_data})


def _detect_datafield(request):
    return render(request, 'detect/datafield.html', {'detect': global_data})


def _detect_sequenceRelationship(request):
    return render(request, 'detect/seq_relate.html', {'detect': global_data})


def _detect_datafieldRalationship(request):
    return render(request, 'detect/df_relate.html', {'detect': global_data})


def construct(request):
    return render(request, 'construct/construct.html')


def work(request):
    return render(request, 'work.html')


def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')


def rules(request):
    file = request.FILES.get('myfile')
    raw_lines = file.readlines()
    lines = []
    for line in raw_lines:
        lines.append(line.decode('utf-8').strip())
    return render(request, 'rules.html', {'file': lines[:10]})


def uniqueid(request):
    return render(request, 'uniqueid.html')
