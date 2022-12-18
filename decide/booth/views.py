import json
from django.views.generic import TemplateView
from django.conf import settings
from django.http import Http404
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth import logout
from django.shortcuts import redirect

from base import mods
from voting.models import Voting


# TODO: check permissions and census
class BoothView(TemplateView):
    template_name = 'booth/booth.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vid = kwargs.get('voting_id', 0)
        user = self.request.user

        try:
            r = mods.get('voting', params={'id': vid})
            # Casting numbers to string to manage in javascript with BigInt
            # and avoid problems with js and big number conversion
            for k, v in r[0]['pub_key'].items():
                r[0]['pub_key'][k] = str(v)

            context['voting'] = json.dumps(r[0])
        except:
            raise Http404

        context['KEYBITS'] = settings.KEYBITS

        if user.is_authenticated and not user.is_staff:
            password = User.objects.make_random_password()
            context['randomPassword'] = password
            user.set_password(password)
            user.save()

        return context

def list_votings(request):
  template = loader.get_template('booth/votings.html')
  votings = Voting.objects.all()
  context = {
    'votings': votings
  }
  return HttpResponse(template.render(context, request))

def social_logout(request):
  logout(request)
  return redirect(request.META['HTTP_REFERER'])

