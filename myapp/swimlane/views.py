import datetime as dt

from django.db import connections
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render

from models import Geo, Rdap, TextFile
from scripts.parse_ips import Interview
from scripts.utils import MyUtil


def home(request):
    return render(request, 'swimlane/home.html')


def upload(request):
    return render(request, 'swimlane/upload.html')


def handle_file_upload(request):
    curs = connections['default'].cursor()
    curs.execute('truncate table geo')
    curs.execute('truncate table rdap')
    text_file = request.FILES['file']
    my_util = MyUtil()
    ips = my_util.extract_ips(text_file)
    interview = Interview()
    interview.get_ip_data(ips)
    text_file = TextFile(file_name=text_file.name, ip_count=len(ips))
    text_file.save()
    return HttpResponse('done!')


def results(request):
    text_files = TextFile.objects.all()
    context = {'text_files': text_files}
    return render(request, 'swimlane/results.html', context)


def file_detail(request, file_id):
    geos = None
    if request.method == 'POST':
        query_dict = request.POST
        q = None
        if query_dict.get('country'):
            q = Q(country__in=query_dict.getlist('country'))
        if query_dict.get('name'):
            if q:
                q = q & Q(name__in=query_dict.getlist('name'))
            else:
                q = Q(name__in=query_dict.getlist('name'))
        rdap = Rdap.objects.filter(q)
        geos = Geo.objects.filter(ip__in=[x.ip for x in rdap])
        names = list(set([x.name for x in rdap if x.name]))
        countries = list(set([x.country for x in rdap if x.country]))
    else:
        geos = Geo.objects.all()
        curs = connections['default'].cursor()
        curs.execute('select distinct name from rdap')
        names = [x[0] for x in curs.fetchall() if x[0]]
        curs.execute('select distinct country from rdap')
        countries = [x[0].upper() for x in curs.fetchall() if x[0]]
    names.sort()
    countries.sort()

    context = {'geos': geos, 'names': names, 'countries': countries}
    return render(request, 'swimlane/detail.html', context)


def ip_detail(request, ip):
    geo = Geo.objects.filter(ip=ip)[0]
    rdap = Rdap.objects.filter(ip=ip)[0]
    context = {'geo': geo, 'rdap': rdap}
    return render(request, 'swimlane/ip_detail.html', context)
