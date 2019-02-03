import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from CreditManagement.models import AbstractTransaction
from .models import UserMembership, Association, User


class AssociationBoardMixin:
    """Gathers association data and verifies that the user is a board member."""
    association = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['association'] = self.association
        return context

    def dispatch(self, request, *args, **kwargs):
        """Gets association and checks if user is board member."""
        self.association = get_object_or_404(Association, slug=kwargs['association_name'])
        if not request.user.groups.filter(id=self.association.id):
            raise PermissionDenied("You are not on the board of this association")
        return super().dispatch(request, *args, **kwargs)


class CreditsOverview(LoginRequiredMixin, AssociationBoardMixin, ListView):
    template_name = "accounts/association_overview.html"
    paginate_by = 50

    def get_queryset(self):
        return AbstractTransaction.get_all_transactions(association=self.association)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['balance'] = AbstractTransaction.get_association_balance(self.association)
        return context


class MembersOverview(LoginRequiredMixin, AssociationBoardMixin, ListView):
    template_name = "accounts/association_members.html"
    paginate_by = 50

    def get_queryset(self):
        return User.objects.filter(
            Q(usermembership__association=self.association) & Q(usermembership__is_verified=True))


def _alter_state(verified, id):
    """
    Alter the state of the given usermembership
    :param verified: yes/no(!) if it should be verified or not.
    :param id: The id of the usermembershipobject
    """
    membership = UserMembership.objects.get(id=id)
    if verified == "yes":
        if membership.is_verified:
            return
        membership.is_verified = True
        membership.verified_on = datetime.datetime.now().date()
        membership.save()
    elif verified == "no":
        if not membership.is_verified and membership.verified_on is not None:
            return
        membership.is_verified = False
        membership.verified_on = datetime.datetime.now().date()
        membership.save()


class MembersEditView(LoginRequiredMixin, AssociationBoardMixin, ListView):
    template_name = "accounts/association_members_edit.html"
    paginate_by = 50

    def get_queryset(self):
        return UserMembership.objects.filter(Q(association=self.association)).order_by('is_verified', 'verified_on',
                                                                                       'created_on')

    def post(self, request, *args, **kwargs):
        # Todo: there is no check on ID, i.e. any passed ID will work. I suggest switching to FormSets.
        for i in request.POST:
            # Seek if any of the validate buttons is pressed and change that state.
            if "validate" in i:
                string = i.split("-")
                verified = string[1]
                id = string[2]
                _alter_state(verified, id)
        return HttpResponseRedirect(request.path_info)
