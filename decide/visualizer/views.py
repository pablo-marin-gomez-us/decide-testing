import json
from django.views.generic import TemplateView
from django.conf import settings
from django.http import Http404

from base import mods


class VisualizerView(TemplateView):
    template_name = 'visualizer/visualizer.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vid = kwargs.get('voting_id', 0)

        try:
            r = mods.get('voting', params={'id': vid})
            context['voting'] = json.dumps(r[0])

            if r[0]['question']['multioption']:
                postpro = r[0]['postproc']
                position_votes = {}
                for i,votes in enumerate(postpro):
                    position_votes[i] = votes['votes']

                sorted_votes = dict(sorted(position_votes.items(), key=lambda item:item[1]))
                order = list(sorted_votes.values())

                for index,key in enumerate(sorted_votes.keys()):
                    order[key] = index+1
                context['order'] = order
                for index in range(0,len(r[0]['postproc'])):
                    r[0]['postproc'][index]['order'] = order[index]
                context['voting'] = json.dumps(r[0])

        except:
            raise Http404

        return context
