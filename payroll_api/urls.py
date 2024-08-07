from django.urls import path
from .views import *


urlpatterns = [
    path('contract/',ContractView.as_view(),),
    path('payslip/', PayslipView.as_view(), name='attendance-list'),
    path('payslip-download/<int:id>', PayslipDownloadView.as_view(), name='attendance-list'),
    path('payslip-send-mail/', PayslipSendMailView.as_view(), name=''),
    path('loan-account/', LoanAccountView.as_view(), name=''), 
    path('loan-account/<int:pk>', LoanAccountView.as_view(), name=''),
    path('reimbusement/', ReimbursementView.as_view(), name=''),
    path('reimbusement/<int:pk>', ReimbursementView.as_view(), name=''),
    path('reimbusement-approve-reject/<int:pk>', ReimbusementApproveRejectView.as_view(), name=''),
    path('tax-bracket/<int:pk>', TaxBracketView.as_view(), name=''),
    path('tax-bracket/', TaxBracketView.as_view(), name=''),
]
