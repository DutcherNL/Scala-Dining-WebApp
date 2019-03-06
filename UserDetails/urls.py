from django.urls import path, include
from allauth.account.views import LoginView

from CreditManagement.views import TransactionAddView
from .views import RegisterView, DiningHistoryView
from .views_user_settings import SettingsView, Settings_Profile_View
from .views_association import CreditsOverview, TransactionsCsvView, MembersOverview, MembersEditView, \
    AssociationOverview

urlpatterns = [
    path('association/<slug:association_name>/', include([
        path('', AssociationOverview.as_view(), name='association_overview'),
        path('transactions/', CreditsOverview.as_view(), name='association_credits'),
        path('transactions/csv/', TransactionsCsvView.as_view(), name='association_transactions_csv'),
        path('transactions/add/', TransactionAddView.as_view(), name='transaction_add'),
        path('members/', MembersOverview.as_view(), name='association_members'),
        path('members/edit/', MembersEditView.as_view(), name='association_members_edit'),
    ])),

    path('statistics/', include([
        path('dining/', DiningHistoryView.as_view(), name='history_lists'),
        path('dining/<int:page>/', DiningHistoryView.as_view(), name='history_lists'),
    ])),


    path('settings/', include([
        path('', SettingsView.as_view(), name='settings_empty'),
        path('account/', Settings_Profile_View.as_view(), name='settings_account'),
    ])),
    path('settings/', include('allauth.urls')),

    # Override allauth login and sign up page with our registration page
    path('login/', LoginView.as_view(), name='login_view'),
    path('signup/', RegisterView.as_view(), name='account_signup'),
]
