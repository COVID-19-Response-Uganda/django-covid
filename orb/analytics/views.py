
import datetime
import json
import tablib

from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render,render_to_response
from django.template import RequestContext
from django.utils import timezone
from django.utils.translation import ugettext as _

from orb.analytics.models import UserLocationVisualization
from orb.models import Resource, SearchTracker, ResourceTracker, Tag, TagOwner

# Create your views here.


def home_view(request):
    if not request.user.is_staff:
        return HttpResponse(status=401,content="Not Authorized") 
    start_date = timezone.now() - datetime.timedelta(days=31)
    end_date = timezone.now()
    pending_crt_resources = Resource.objects.filter(status=Resource.PENDING_CRT)
    pending_mep_resources = Resource.objects.filter(status=Resource.PENDING_MRT)
    popular_searches = SearchTracker.objects.filter(access_date__gte=start_date).values('query').annotate(total_hits=Count('id')).order_by('-total_hits')[:10]
    popular_resources = ResourceTracker.objects.filter(access_date__gte=start_date).values('resource','resource__slug','resource__title').annotate(total_hits=Count('id')).order_by('-total_hits')[:10]
    organisations = Tag.objects.filter(category__slug='organisation',resourcetag__isnull=False).annotate(total_resources=Count('resourcetag__id')).order_by('name')
    
    snor = timezone.now() - datetime.timedelta(days=90)
    searches_no_results = SearchTracker.objects.filter(access_date__gte=snor, no_results=0).values('query').annotate(total_hits=Count('id')).order_by('-total_hits')[:10]
    
    recent_activity = []
    no_days = (end_date-start_date).days + 1
    for i in range(0,no_days,+1):
        temp = start_date + datetime.timedelta(days=i)
        day = temp.strftime("%d")
        month = temp.strftime("%m")
        year = temp.strftime("%Y")
        r_trackers = ResourceTracker.objects.filter(access_date__day=day,access_date__month=month,access_date__year=year)
        s_trackers = SearchTracker.objects.filter(access_date__day=day,access_date__month=month,access_date__year=year)
        count_activity = {'resource':0, 'resource_file':0, 'resource_url':0, 'search':0, 'total':0}
        for r in r_trackers:
            count_activity['total']+=1
            if r.resource_file:
                count_activity['resource_file']+=1
            elif r.resource_url:
                count_activity['resource_url']+=1
            else:
                count_activity['resource']+=1
        for s in s_trackers:
            count_activity['total']+=1
            count_activity['search']+=1
            
        recent_activity.append([temp.strftime("%d %b %y"),count_activity])
        
    return render_to_response('orb/analytics/home.html',
                              {'pending_crt_resources': pending_crt_resources,
                               'pending_mep_resources': pending_mep_resources,
                               'popular_searches': popular_searches,
                               'popular_resources': popular_resources,
                               'organisations': organisations,
                               'recent_activity': recent_activity,
                               'searches_no_results': searches_no_results},
                              context_instance=RequestContext(request))
    
def map_view(request):
    if not request.user.is_staff:
        return HttpResponse(status=401,content="Not Authorized") 
    return render_to_response('orb/analytics/map.html',
                              {},
                              context_instance=RequestContext(request))


def tag_view(request,id):
    if not is_tag_owner(request, id):
        return HttpResponse(status=401,content="Not Authorized")
    
    tag = Tag.objects.get(pk=id) 
    
    start_date = timezone.now() - datetime.timedelta(days=31)
    end_date = timezone.now()
    
    # Activity Graph
    recent_activity = []
    no_days = (end_date-start_date).days + 1
    for i in range(0,no_days,+1):
        temp = start_date + datetime.timedelta(days=i)
        day = temp.strftime("%d")
        month = temp.strftime("%m")
        year = temp.strftime("%Y")
        r_trackers = ResourceTracker.objects.filter(access_date__day=day,access_date__month=month,access_date__year=year, resource__resourcetag__tag=tag,resource__status=Resource.APPROVED)
        count_activity = {'resource':0, 'resource_file':0, 'resource_url':0, 'total':0}
        for r in r_trackers:
            count_activity['total']+=1
            if r.resource_file:
                count_activity['resource_file']+=1
            elif r.resource_url:
                count_activity['resource_url']+=1
            else:
                count_activity['resource']+=1
            
        recent_activity.append([temp.strftime("%d %b %y"),count_activity])
    
    
    # Activity detail
    trackers = ResourceTracker.objects.filter(access_date__gte=start_date,resource__resourcetag__tag=tag,resource__status=Resource.APPROVED).order_by('-access_date')
    
    paginator = Paginator(trackers, 20)
    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    
    try:
        trackers = paginator.page(page)
    except (EmptyPage, InvalidPage):
        trackers = paginator.page(paginator.num_pages)
    
    # get the monthly trackers
    export = ResourceTracker.objects.filter(resource__resourcetag__tag=tag,resource__status=Resource.APPROVED).datetimes('access_date','month','DESC')
    
    return render_to_response('orb/analytics/tag.html',
                              { 'tag': tag,
                               'recent_activity': recent_activity,
                               'page': trackers,
                               'export': export },
                              context_instance=RequestContext(request))


def tag_download(request,id, year, month):
    if not is_tag_owner(request, id):
        return HttpResponse(status=401,content="Not Authorized")
    
    tag = Tag.objects.get(pk=id)
     
    headers = ('Date', 'Resource', 'Resource File/URL', 'IP Address', 'User Agent', 'Country', 'Lat', 'Lng', 'Location')
    data = []
    data = tablib.Dataset(*data, headers=headers)
    trackers = ResourceTracker.objects.filter(resource__resourcetag__tag=tag,resource__status=Resource.APPROVED,access_date__month=month, access_date__year=year).order_by('access_date')
    for t in trackers:
        if t.resource_file:
            object = t.resource_file.filename
        elif t.resource_url:
            object = t.resource_url.url
        else:
            object = ''
            
        if t.get_location():
            lat = t.get_location().lat
            lng = t.get_location().lng
            location = t.get_location().region 
            country = t.get_location().country_name
        else:
            lat = ''
            lng = ''
            location = ''
            country = ''
        data.append((t.access_date.strftime('%Y-%m-%d %H:%M:%S'), t.resource.title, object,t.ip, t.user_agent, country ,lat, lng, location ))
        
            
    response = HttpResponse(data.xls, content_type='application/vnd.ms-excel;charset=utf-8')
    response['Content-Disposition'] = "attachment; filename=export.xls"

    return response

# Helper functions
def is_tag_owner(request,id):
    if not request.user.is_authenticated:
        return False
    
    if request.user.is_staff:
        return True
    
    try:
        TagOwner.objects.get(tag__pk=id,user__id=request.user.id)
        return True
    except TagOwner.DoesNotExist:
        return False