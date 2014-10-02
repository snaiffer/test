"""
from django.template.loader import get_template
from django.template import Context
"""
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader, RequestContext
from django.template import Template, Context

import branch

def treemind(request, offset=0):
  try:
    offset = int(offset)
  except ValueError:
    raise Http404()
  dt = datetime.datetime.now() + datetime.timedelta(hours=offset)
  #html =  "<html><body>In %s hour(s), it will be %s.</body></html>" % (offset, dt)
  html = "<html><body>" + branch.test() + "</body></html>"
  return HttpResponse(html)

def custom_proc(request):
  "A context processor that provides 'app', 'user' and 'ip_address'."
  return {
    'name': 'My app',
    'user': request.user,
    'ip_address': request.META['REMOTE_ADDR']
  }

def test(request):
  t = loader.get_template('test.html')
  c = RequestContext(request, processors=[custom_proc])
  return HttpResponse(t.render(c))

def hello(request):
  return HttpResponse("Hello world")

import datetime
def current_datetime(request):
  now = datetime.datetime.now()
  return render(request, 'current_datetime.html', {'current_date': now})
  """
  t = get_template('current_datetime.html')
  html = t.render(Context({'current_date': now}))
  return HttpResponse(html)
  """

def hours_ahead(request, offset):
  try:
    offset = int(offset)
  except ValueError:
    raise Http404()
  dt = datetime.datetime.now() + datetime.timedelta(hours=offset)
  html = "<html><body>In %s hour(s), it will be %s.</body></html>" % (offset, dt)
  return HttpResponse(html)

def display_meta(request):
  values = request.META.items()
  values.append( ('get_full_path', request.get_full_path()) )
  values.sort()
  return render(request, 'display_meta.html', {'values': values})
