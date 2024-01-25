import json

from django.views.decorators.csrf import get_token, csrf_exempt
from django.utils.crypto import constant_time_compare
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import UserModel, BankModel, ClientModel


def get_all_users(request):
    try:
        users = UserModel.objects.all()
        data = [{'id': user.id, 'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email} for
                user in users]
        return JsonResponse(data, safe=False)
    except UserModel.DoesNotExist:
        return JsonResponse({'error': 'No users found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_all_banks(request):
    try:
        banks = BankModel.objects.all()
        data = data = [{'id': bank.id, 'bank_name': bank.bank_name, 'routing_number': bank.routing_number, 'swift_bic': bank.swift_bic} for
                bank in banks]
        return JsonResponse(data, safe=False)
    except BankModel.DoesNotExist:
        return JsonResponse({'error': 'No banks found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_all_user_bank(request, user_id):
    try:
        id_banks = ClientModel.objects.filter(id_user=user_id).values_list('id_bank', flat=True)
        banks = BankModel.objects.filter(id__in=id_banks)
        data = data = [{'id': bank.id, 'bank_name': bank.bank_name, 'routing_number': bank.routing_number, 'swift_bic': bank.swift_bic} for
                bank in banks]
        return JsonResponse(data, safe=False)
    except BankModel.DoesNotExist:
        return JsonResponse({'error': 'No banks found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_POST
def add_user(request):
    try:
        data = json.loads(request.body)
        existing_user = UserModel.objects.filter(email=data.get('email')).first()
        if existing_user:
            return JsonResponse({'success': False, 'message': 'User with this email already exists'})

        new_user = UserModel.objects.create(
            password=data.get('password'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            email=data.get('email')
        )

        return JsonResponse({'success': True, 'message': 'User added successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

def get_csrf_token(request):
    if request.method == 'GET':
        csrf_token = get_token(request)
        return JsonResponse({'csrf_token': csrf_token})
    else:
        return JsonResponse({'error': 'Invalid method'}, status=405)
@csrf_exempt
def delete_user(request, user_id):
    try:
        ClientModel.objects.filter(id_user=user_id).delete()
        UserModel.objects.get(id=user_id).delete()
        return JsonResponse({'success': True, 'message': 'User deleted successfully'})
    except UserModel.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
@csrf_exempt
def delete_user_bank(request, user_id, bank_id):
    try:
        ClientModel.objects.filter(id_user=user_id, id_bank=bank_id).delete()
        return JsonResponse({'success': True, 'message': 'User deleted successfully'})
    except UserModel.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@csrf_exempt
@require_POST
def add_bank_for_user(request):
    try:
        data = json.loads(request.body)
        existing_bank = BankModel.objects.filter(bank_name=data.get('bank_name')).first()

        if existing_bank:
            user_id = data.get('user_id')

            if ClientModel.objects.filter(id_user=user_id, id_bank=existing_bank.id).exists():
                return JsonResponse({'success': False, 'message': 'User is already associated with this bank'})

            ClientModel.objects.create(
                id_user=user_id,
                id_bank=existing_bank.id
            )

            return JsonResponse({'success': True, 'message': 'User added successfully'})
        else:
            return JsonResponse({'success': False, 'message': 'Bank not found'})

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})