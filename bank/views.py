import json

from django.db.models import Q
from django.views.decorators.csrf import get_token, csrf_exempt
from django.utils.crypto import constant_time_compare
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import UserModel, BankModel, ClientModel


def get_all_users(request):
    try:
        users = UserModel.objects.all()
        data = [{'id': user.id, 'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email, 'password': user.password} for
                user in users]
        return JsonResponse(data, safe=False)
    except UserModel.DoesNotExist:
        return JsonResponse({'error': 'No users found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_all_banks(request):
    try:
        banks = BankModel.objects.all()
        data = [{'id': bank.id, 'bank_name': bank.bank_name, 'routing_number': bank.routing_number, 'swift_bic': bank.swift_bic} for
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
        data = [{'id': bank.id, 'bank_name': bank.bank_name, 'routing_number': bank.routing_number, 'swift_bic': bank.swift_bic} for
                bank in banks]
        return JsonResponse(data, safe=False)
    except BankModel.DoesNotExist:
        return JsonResponse({'error': 'No banks found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_all_bank_users(request, id_bank):
    try:
        id_users = ClientModel.objects.filter(id_bank=id_bank).values_list('id_user', flat=True)
        users = UserModel.objects.filter(id__in=id_users)
        data = [{'id': user.id, 'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email,
                 'password': user.password} for
                user in users]
        return JsonResponse(data, safe=False)
    except BankModel.DoesNotExist:
        return JsonResponse({'error': 'No users found'}, status=404)
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

@csrf_exempt
@require_POST
def add_bank(request):
    try:
        data = json.loads(request.body)
        existing_bank = BankModel.objects.filter(Q(bank_name__iexact=data.get('bank_name')) | Q(routing_number__iexact=data.get('routing_number')) | Q(swift_bic__iexact=data.get('swift_bic'))).first()
        if existing_bank:
            return JsonResponse({'success': False, 'message': 'Bank with this name, routing number, or SWIFT/BIC already exists'})

        new_bank = BankModel.objects.create(
            bank_name=data.get('bank_name'),
            routing_number=data.get('routing_number'),
            swift_bic=data.get('swift_bic'),
        )

        return JsonResponse({'success': True, 'message': 'Bank added successfully'})
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
def delete_bank(request, id_bank):
    try:
        user = ClientModel.objects.filter(id_bank=id_bank).values().first()
        if user:
            return JsonResponse({'success': False, 'message': 'Bank has user'})
        BankModel.objects.get(id=id_bank).delete()
        return JsonResponse({'success': True, 'message': 'Bank deleted successfully'})
    except BankModel.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Bank not found'}, status=404)
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
        existing_bank = BankModel.objects.filter(bank_name=data.get('bank_name')).values().first()
        if existing_bank:
            user_id = data.get('id_user')

            if ClientModel.objects.filter(id_user=user_id, id_bank=existing_bank.get('id')).exists():
                return JsonResponse({'success': False, 'message': 'User is already associated with this bank'})
            ClientModel.objects.create(
                id_user=user_id,
                id_bank=existing_bank.get('id')
            )

            return JsonResponse({'success': True, 'message': 'Bank added successfully'})
        else:
            return JsonResponse({'success': False, 'message': 'Bank not found'})

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@csrf_exempt
def update_user(request, user_id):
    try:
        data = json.loads(request.body)
        existing_user = UserModel.objects.exclude(id=user_id).filter(email=data.get('email')).values().first()

        if existing_user:
            return JsonResponse({'success': False, 'message': 'User with this email already exists'})
        user = UserModel.objects.get(id=user_id)
        user.first_name = data.get('first_name')
        user.last_name = data.get('last_name')
        user.email = data.get('email')
        user.password = data.get('password')
        user.save()

        return JsonResponse({'success': True, 'message': 'User updated successfully'})

    except UserModel.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@csrf_exempt
def update_bank(request, id_bank):
    try:
        data = json.loads(request.body)
        existing_bank = BankModel.objects.exclude(id=id_bank).filter(Q(bank_name__iexact=data.get('bank_name')) | Q(routing_number__iexact=data.get('routing_number')) | Q(swift_bic__iexact=data.get('swift_bic'))).values().first()

        if existing_bank:
            return JsonResponse({'success': False, 'message': 'Bank with this name, routing number, or SWIFT/BIC already exists'})
        bank = BankModel.objects.get(id=id_bank)
        bank.bank_name = data.get('bank_name')
        bank.routing_number = data.get('routing_number')
        bank.swift_bic = data.get('swift_bic')
        bank.save()

        return JsonResponse({'success': True, 'message': 'Bank updated successfully'})

    except UserModel.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Bank not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)