from collections import defaultdict
import gettext
from django.shortcuts import render
from rest_framework.views import APIView

from base.backends import ConfiguredEmailBackend
from payroll.models.tax_models import TaxBracket
from payroll.threadings.mail import MailSendThread
from payroll.views.views import payslip_pdf
from . serializers import AllowanceSerializer, ContractSerializer, DeductionSerializer, LoanAccountSerializer, PayslipSerializer, ReimbursementSerializer, TaxBracketSerializer
from base_api.methods import groupby_queryset
from payroll.filters import AllowanceFilter, ContractFilter, DeductionFilter, PayslipFilter
from payroll.models.models import Allowance, Contract, Deduction, LoanAccount, Payslip, Reimbursement
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator


class PayslipView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.has_perm("payroll.view_payslip"):
            payslips = Payslip.objects.all()
        else:
            payslips = Payslip.objects.filter(
                employee_id__employee_user_id=request.user
            )

        payslip_filter_queryset = PayslipFilter(request.GET, payslips).qs
        # groupby workflow
        field_name = request.GET.get("groupby_field", None)
        if field_name:
            url = request.build_absolute_uri()
            return groupby_queryset(request, url, field_name, payslip_filter_queryset)
        pagination = PageNumberPagination()
        page = pagination.paginate_queryset(payslip_filter_queryset, request)
        serializer = PayslipSerializer(page, many=True)
        return pagination.get_paginated_response(serializer.data)


class PayslipDownloadView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        if request.user.has_perm("payroll.view_payslip"):
            return payslip_pdf(request, id)

        if Payslip.objects.filter(id=id, employee_id=request.user.employee_get):
            return payslip_pdf(request, id)
        else:
            raise Response({"error":"You don't have permission"})

class PayslipSendMailView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(permission_required("payroll.add_payslip", raise_exception=True))
    def post(self, request):
        email_backend = ConfiguredEmailBackend()
        if not getattr(
            email_backend, "dynamic_username_with_display_name", None
        ) or not len(email_backend.dynamic_username_with_display_name):
            return Response({"error": "Email server is not configured"}, status=400)

        payslip_ids = request.data.get("id", [])
        payslips = Payslip.objects.filter(id__in=payslip_ids)
        result_dict = defaultdict(
            lambda: {"employee_id": None, "instances": [], "count": 0}
        )

        for payslip in payslips:
            employee_id = payslip.employee_id
            result_dict[employee_id]["employee_id"] = employee_id
            result_dict[employee_id]["instances"].append(payslip)
            result_dict[employee_id]["count"] += 1
        mail_thread = MailSendThread(
            request, result_dict=result_dict, ids=payslip_ids)
        mail_thread.start()
        return Response({"status": "success"}, status=200)


class ContractView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.has_perm("payroll.view_contract"):
            contracts = Contract.objects.all()
        else:
            contracts = Contract.objects.filter(
                employee_id=request.user.employee_get)
        filter_queryset = ContractFilter(request.GET, contracts).qs
        # groupby workflow
        field_name = request.GET.get("groupby_field", None)
        if field_name:
            url = request.build_absolute_uri()
            return groupby_queryset(request, url, field_name, filter_queryset)
        pagination = PageNumberPagination()
        page = pagination.paginate_queryset(filter_queryset, request)
        serializer = ContractSerializer(page, many=True)
        return pagination.get_paginated_response(serializer.data)

    @method_decorator(permission_required("payroll.add_contract", raise_exception=True))
    def post(self, request):
        serializer = ContractSerializer(request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    @method_decorator(permission_required("payroll.change_contract", raise_exception=True))
    def put(self, request, pk):
        contract = Contract.objects.get(id=pk)
        serializer = ContractSerializer(instance=contract, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    @method_decorator(permission_required("payroll.delete_contract", raise_exception=True))
    def delete(self, request, pk):
        contract = Contract.objects.get(id=pk)
        contract.delete()
        return Response({"status": "deleted"}, status=200)


class AllowanceView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(permission_required("payroll.view_allowance", raise_exception=True))
    def get(self, request):
        allowance = Allowance.objects.all()
        filter_queryset = AllowanceFilter(request.GET, allowance).qs
        pagination = PageNumberPagination()
        page = pagination.paginate_queryset(filter_queryset, request)
        serializer = AllowanceSerializer(page, many=True)
        return pagination.get_paginated_response(serializer.data)

    @method_decorator(permission_required("payroll.add_allowance", raise_exception=True))
    def post(self, request):
        serializer = AllowanceSerializer(request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    @method_decorator(permission_required("payroll.change_allowance", raise_exception=True))
    def put(self, request, pk):
        contract = Allowance.objects.get(id=pk)
        serializer = AllowanceSerializer(instance=contract, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    @method_decorator(permission_required("payroll.delete_allowance", raise_exception=True))
    def delete(self, request, pk):
        contract = Allowance.objects.get(id=pk)
        contract.delete()
        return Response({"status": "deleted"}, status=200)


class DeductionView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(permission_required("payroll.view_deduction", raise_exception=True))
    def get(self, request):
        allowance = Deduction.objects.all()
        filter_queryset = DeductionFilter(request.GET, allowance).qs
        pagination = PageNumberPagination()
        page = pagination.paginate_queryset(filter_queryset, request)
        serializer = DeductionSerializer(page, many=True)
        return pagination.get_paginated_response(serializer.data)

    @method_decorator(permission_required("payroll.add_deduction", raise_exception=True))
    def post(self, request):
        serializer = DeductionSerializer(request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    @method_decorator(permission_required("payroll.change_deduction", raise_exception=True))
    def put(self, request, pk):
        contract = Deduction.objects.get(id=pk)
        serializer = DeductionSerializer(instance=contract, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    @method_decorator(permission_required("payroll.delete_deduction", raise_exception=True))
    def delete(self, request, pk):
        contract = Deduction.objects.get(id=pk)
        contract.delete()
        return Response({"status": "deleted"}, status=200)


class LoanAccountView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(permission_required("payroll.add_loanaccount", raise_exception=True))
    def post(self, request):
        serializer = LoanAccountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    @method_decorator(permission_required("payroll.view_loanaccount", raise_exception=True))
    def get(self, request, pk=None):
        if pk:
            loan_account = LoanAccount.objects.get(id=pk)
            serializer = LoanAccountSerializer(instance=loan_account)
            return Response(serializer.data, status=200)
        loan_accounts = LoanAccount.objects.all()
        serializer = LoanAccountSerializer(loan_accounts, many=True)
        return Response(serializer.data, status=200)

    @method_decorator(permission_required("payroll.change_loanaccount", raise_exception=True))
    def put(self, request, pk):
        loan_account = LoanAccount.objects.get(id=pk)
        serializer = LoanAccountSerializer(loan_account, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    @method_decorator(permission_required("payroll.delete_loanaccount", raise_exception=True))
    def delete(self, request, pk):
        loan_account = LoanAccount.objects.get(id=pk)
        loan_account.delete()
        return Response(status=200)


class ReimbursementView(APIView):
    serializer_class = ReimbursementSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            reimbursement = Reimbursement.objects.get(id=pk)
            serializer = self.serializer_class(reimbursement)
            return Response(serializer.data, status=200)
        if request.user.has_perm("payroll.view_reimbursement"):
            reimbursements = Reimbursement.objects.all()
        else:
            reimbursements = Reimbursement.objects.filter(
                employee_id=request.user.employee_get)
        serializer = self.serializer_class(reimbursements, many=True)
        return Response(serializer.data, status=200)

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    @method_decorator(permission_required("payroll.change_reimbursement", raise_exception=True))
    def put(self, request, pk):
        reimbursement = Reimbursement.objects.get(id=pk)
        serializer = self.serializer_class(
            instance=reimbursement, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    @method_decorator(permission_required("payroll.delete_reimbursement", raise_exception=True))
    def delete(self, request, pk):
        reimbursement = Reimbursement.objects.get(id=pk)
        reimbursement.delete()
        return Response(status=200)


class ReimbusementApproveRejectView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        status = request.data.get('status', None)
        amount = request.data.get('amount', None)
        amount = eval(request.data.get('amount')
                      ) if request.data.get('amount') else 0
        amount = max(0, amount)
        reimbursement = Reimbursement.objects.filter(id=pk)
        if amount:
            reimbursement.update(amount=amount)
        reimbursement.update(status=status)
        return Response({"status": reimbursement.first().status}, status=200)


class TaxBracketView(APIView):

    def get(self, request, pk=None):
        if pk:
            tax_bracket = TaxBracket.objects.get(id=pk)
            serializer = TaxBracketSerializer(tax_bracket)
            return Response(serializer.data, status=200)
        tax_brackets = TaxBracket.objects.all()
        serializer = TaxBracketSerializer(instance=tax_brackets, many=True)
        return Response(serializer.data, status=200)

    def post(self, request):
        serializer = TaxBracketSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        tax_bracket = TaxBracket.objects.get(id=pk)
        serializer = TaxBracketSerializer(
            instance=tax_bracket, data=request.data, partial=True)
        if serializer.save():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        tax_bracket = TaxBracket.objects.get(id=pk)
        tax_bracket.delete()           
        return Response(status=200)
    
    