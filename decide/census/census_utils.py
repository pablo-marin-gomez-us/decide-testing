from django.contrib.auth.models import User
from .models import Census

def get_user_atributes():
    user = User.objects.all().values()[0]
    atributes_list = []

    counter = 0
    for atribute in user.keys():
        if not atribute == 'id' and not atribute == 'password':
            atributes_list.append((counter, atribute))
            counter += 1

    return atributes_list

def get_csvtext_and_voters(form_values, census):
    atributes_list = get_user_atributes()
    selected_atributes = []
    voters = []
    
    # Header
    census_text = 'ID,'
    for index in form_values:
        census_text += str(atributes_list[int(index)][1])
        selected_atributes.append(str(atributes_list[int(index)][1]))
        if not form_values[-1] == index:
            census_text += ','
        else:
            census_text += '/'

    # CSV values
    for c in census:
        voter = User.objects.filter(id=c['voter_id']).values()[0]
        voters.append(voter)
        census_text += str(c['voter_id']) + ','
        for atr in selected_atributes:
            census_text += str(voter[atr])
            if not selected_atributes[-1] == atr:
                census_text += ','
            else:
                census_text += '/'

    return (census_text, voters)

