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

# csvtext -> Header1,Header2,Header3/value1,value2,value3/value1,value2,value3/
def get_csvtext_and_data(form_values, census):
    atributes_list = get_user_atributes()
    voters_data = []
    headers = []
    
    # Header
    census_text = 'id,'
    headers.append('id')
    for index in form_values:
        atribute = str(atributes_list[int(index)][1])
        headers.append(atribute)
        census_text += atribute
        if not form_values[-1] == index:
            census_text += ','
        else:
            census_text += '/'

    # CSV values
    for c in census:
        voter = User.objects.filter(id=c['voter_id']).values()[0]
        values_list = []
        for atr in headers:
            census_text += str(voter[atr])
            values_list.append(str(voter[atr]))
            if not headers[-1] == atr:
                census_text += ','
            else:
                census_text += '/'
        voters_data.append(values_list)

    return (census_text, headers, voters_data)


