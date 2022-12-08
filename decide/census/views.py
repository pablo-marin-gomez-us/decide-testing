from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.template import loader
from django.http import HttpResponse
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.status import (
        HTTP_201_CREATED as ST_201,
        HTTP_204_NO_CONTENT as ST_204,
        HTTP_400_BAD_REQUEST as ST_400,
        HTTP_401_UNAUTHORIZED as ST_401,
        HTTP_404_NOT_FOUND as ST_404,
        HTTP_409_CONFLICT as ST_409
)
from rest_framework.views import APIView
from base.perms import UserIsStaff
from .models import Census
from .forms import AtributosUser
from django.views.generic import TemplateView
import csv
import requests
from voting.models import Voting
from  django.contrib.admin.views.decorators import staff_member_required
from census import census_utils as Utils

class CensusCreate(generics.ListCreateAPIView):
    permission_classes = (UserIsStaff,)

    def create(self, request, *args, **kwargs):
        voting_id = request.data.get('voting_id')
        voters = request.data.get('voters')
        try:
            for voter in voters:
                census = Census(voting_id=voting_id, voter_id=voter)
                census.save()
        except IntegrityError:
            return Response('Error try to create census', status=ST_409)
        return Response('Census created', status=ST_201)

    def list(self, request, *args, **kwargs):
        voting_id = request.GET.get('voting_id')
        voters = Census.objects.filter(voting_id=voting_id).values_list('voter_id', flat=True)
        return Response({'voters': voters})

class CensusDetail(generics.RetrieveDestroyAPIView):

    def destroy(self, request, voting_id, *args, **kwargs):
        voters = request.data.get('voters')
        census = Census.objects.filter(voting_id=voting_id, voter_id__in=voters)
        census.delete()
        return Response('Voters deleted from census', status=ST_204)

    def retrieve(self, request, voting_id, *args, **kwargs):
        voter = request.GET.get('voter_id')
        try:
            Census.objects.get(voting_id=voting_id, voter_id=voter)
        except ObjectDoesNotExist:
            return Response('Invalid voter', status=ST_401)
        return Response('Valid voter')

class CensusView(APIView,TemplateView):
    template_name = 'census/census.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return (context)

    def post(self,request):
        HOST = 'http://localhost:8000'
        votation = request.data.get('votation', '')
        user = request.data.get('user', '')
        password = request.data.get('password', '')
        if not votation or not user or not password:
            return Response({'Any empty inputs?'}, status=ST_400)

        def decode_utf8(input_iterator):
            for line in input_iterator:
                yield line.decode('utf-8')

        def create_voters_csv(request):
            HOST = 'http://localhost:8000'
            reader = csv.DictReader(decode_utf8(request.FILES['file']))
            for row in reader:
                aux_list = list(row.values())
                username = aux_list[0]
                pwd = aux_list[1]
                token.update({'username': username, 'password': pwd})
                response = requests.post(HOST + '/authentication/register/', data=token)
                if response.status_code == 201:
                    voters_pk.append(response.json().get('user_pk'))
                else:
                    invalid_voters.append(username)
            return voters_pk,invalid_voters

        data = {'username': user, 'password': password}
        response = requests.post(HOST + '/authentication/login/', data=data)
        token = response.json()
        if not token.get('token') :
            return Response({'This user is incorrect, try again'}, status=ST_401)

        voters_pk = []
        invalid_voters = []
        voters_pk,invalid_voters = create_voters_csv(request)

        def add_census(voters_pk, voting_pk):
            data = {'username': user, 'password': password}
            response = requests.post(HOST + '/authentication/login/', data=data)
            token = response.json()

            data2 = {'voters': voters_pk, 'voting_id': voting_pk}
            auth = {'Authorization': 'Token ' + token.get('token')}
            response = requests.post(HOST + '/census/', json=data2, headers=auth)

        add_census(voters_pk, votation)
        return Response({'Votación poblada satisfactoriamente, '+ str(len(voters_pk))+ ' votantes añadidos' }, status=ST_201)
   
# @staff_member_required(login_url='/admin/login')
def export_census(request, voting_id):
    if not request.user.is_staff:
        template = loader.get_template('errors.html')
        context = {
            'message':"401 You don't have access to this page",
            'status_code':401,
        }
        return HttpResponse(template.render(context, request), status=401)

    if list(Voting.objects.filter(id=voting_id).values())== []:
        template = loader.get_template('errors.html')
        context = {
            'error_message':'404 Voting not found',
            'status_code':404,
        }
        return HttpResponse(template.render(context, request), status=404)

    template = loader.get_template('export_census.html')
    formulario = AtributosUser()
    voting = Voting.objects.filter(id=voting_id).values()[0]
    census_text = ''
    headers = []
    voters_data = []

    if request.method == 'POST':
        formulario = AtributosUser(request.POST)
        if formulario.is_valid():
            census = Census.objects.filter(voting_id=voting_id).values()
            data = Utils.get_csvtext_and_data(formulario.cleaned_data['user_atributes'], census)
            census_text = data[0]
            headers = data[1]
            voters_data = data[2]

    context = {
        'formulario':formulario,
        'voting':voting,
        'census_text':census_text,
        'voters_data':voters_data,
        'index':[i for i in range(0,len(voters_data))],
        'headers':headers,
        'header_index':[i for i in range(0,len(headers))],
    }

    return HttpResponse(template.render(context, request))
