from .vitex_api import get_exchange_orders, get_rollback_transaction
from django.shortcuts import redirect, render
from app.models import Claim, VitexAccount
from .utils import orders_processor, VARS
from django.http import JsonResponse
from django.views import generic
from app.forms import EIOUForm
from .models import ClaimFile
import datetime


class HomeView(generic.TemplateView):
    template_name = "home.html"


class EIOUClaimConfirmationView(generic.TemplateView):
    template_name = "eiou_confirm_form.html"
    model = Claim

    def get(self, request, *args, **kwargs):
        if 'active_claim' in request.session:
            claim_id = request.session['active_claim']
            claim = Claim.objects.get(id=claim_id)
            context = self.get_context_data(claim=claim)
            print(context['claim'])
            response = render(request, self.template_name, context)
            if 'vitex_data' in request.session:
                del request.session['vitex_data']
            del request.session['active_claim']
            return response
        else:
            return redirect('home')


class EIOUClaimView(generic.TemplateView):
    fields = ['telegram', 'vitex_address', 'details']
    template_name = "eiou_claim_app.html"
    success_url = "eiou_claim_confirmed"
    form_class = EIOUForm
    model = Claim

    def post(self, request, *args, **kwargs):
        claim_id = request.session['active_claim'] or None
        if claim_id:
            claim = Claim.objects.get(id=claim_id)

            for field in self.fields:
                value = request.POST.get(field) or None
                if field == 'telegram':
                    if str(value).startswith('@'):
                        value = str(value[1:])
                setattr(claim, field, value)

            if 'vitex_data' in request.session:
                vitex_data = request.session['vitex_data']
                claim.estimations = vitex_data

            claim.status = claim.STATUS.submitted
            claim.save()
            print('Yay!')
            return redirect(self.success_url)
        else:
            return render(request, self.template_name)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        """Start new claim or continue already started one"""

        # Check if there is already started claim saved in session,
        # if yes continue started one, if no start new
        if 'active_claim' not in request.session:
            claim = Claim.objects.create()
            # TODO: remove this from session after successful submission
            request.session['active_claim'] = str(claim.id)
        else:
            claim, created = Claim.objects.get_or_create(id=request.session['active_claim'])

        context = self.get_context_data(claim_id=claim.id)
        response = render(request, self.template_name, context)

        # Check for cookie, we will save number of sent claims there (anti-flood)
        if not request.COOKIES.get('eiou_claim_visits'):
            response.set_cookie('eiou_claim_visits', '1')
            print(request.COOKIES)
        else:
            visits = int(request.COOKIES.get('eiou_claim_visits'))
            print(visits)
            response.set_cookie('eiou_claim_visits', visits + 1)
        return response


def vitex_details_handler(request):
    request.session['vitex_data'] = {}
    if request.method == 'GET' and request.is_ajax():
        response = {
            'icon': '<i class="fs-5 fas fa-ban"></i>',
            'msg': 'No address',
            'data': {}
            }

        address = request.GET.get('address').strip()

        if not address:
            response['msg'] = ''
            response['icon'] = '<i class="fs-5 text-muted fas fa-ban"></i>'
            return JsonResponse(response)

        if address.startswith('vite') and len(address) == 55:
            account = VitexAccount.objects.filter(address=address)

            if account:
                print('-----------------------------------------------')
                print(str(datetime.datetime.now()))
                print(address)

                try:
                    epic_002_tx = get_rollback_transaction(viteAddress=address)
                    orders = get_exchange_orders(viteAddress=address, limit=10000,
                                                 status=None, filterTime=
                                                 [VARS['event_timestamp'], VARS['end_date']],
                                                 side=None, symbol=VARS['trading_pair'])
                except ValueError as er:
                    print(er)
                    response['msg'] = 'Invalid address format'
                    response['icon'] = '<i class="fs-5 text-danger fas fa-ban"></i>'
                    return JsonResponse(response)

                try:
                    if epic_002_tx:
                        difference = account[0].total - epic_002_tx
                    else:
                        difference = account[0].total
                    print("Difference: {:.8f} EPIC".format(float(difference)))

                    if 1 > difference > -1:
                        difference = None
                except:
                    response['msg'] = 'Connection problems (usually too many transactions),' \
                                      ' please continue your claim'
                    response['icon'] = '<i class="fs-5 text-danger fas fa-ban"></i>'
                    print('-----------------------------------------------')
                    return JsonResponse(response)
            else:
                request.session['vitex_data'] = {}
                response['msg'] = 'Address is not holding any EPIC-001'
                response['icon'] = '<i class="fs-5 text-danger fas fa-ban"></i>'
                return JsonResponse(response)

            if difference and len(orders) > 0:
                orders = orders_processor(orders)
                balance_diff = difference - orders['balance']
                balance_diff_value = balance_diff * VARS['eiou_multiplier']
                total_claim_value = sum([orders['balance_usd'], balance_diff_value])

                if balance_diff < 0:
                    print('balance_diff_value lower than trading itself - hm')

                request.session['vitex_data'] = {
                    'trading_claim_value': int(orders['balance_usd']),
                    'balance_diff_value': int(balance_diff_value),
                    'total_claim_value': int(total_claim_value)
                    }

            elif difference and not orders:
                request.session['vitex_data'] = {
                    'trading_claim_value': None,
                    'balance_diff_value': int(difference),
                    'total_claim_value': int(difference)
                    }

            response['msg'] = 'Address correct'
            response['icon'] = '<i class="fs-5 text-success fas fa-check"></i>'
            print('-----------------------------------------------')
            return JsonResponse(response)

        else:
            response['msg'] = 'Invalid address format'
            response['icon'] = '<i class="fs-5 text-danger fas fa-ban"></i>'
            return JsonResponse(response)


def upload(request):
    def generate_file_name(file, claim_id):
        """Add date to name files"""
        return f"{claim_id}_{str(file)}"

    if request.method == 'POST':
        if request.is_ajax():
            claim_id = request.session['active_claim']
            file = request.FILES.get('file')
            new, created = ClaimFile.objects. \
                get_or_create(name=generate_file_name(file, claim_id))
            new.file = file
            new.save()
            active_claim = Claim.objects.get(id=claim_id)
            active_claim.files.add(new)
            active_claim.save()
            print(file, 'successfully uploaded')
            response_data = {
                'url': new.file.url,
                'status': 'success'
                }
            return JsonResponse(response_data)
