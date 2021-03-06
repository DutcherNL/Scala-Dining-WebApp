from dal_select2.widgets import ModelSelect2
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Sum

from creditmanagement.models import PendingTransaction, UserCredit


class TransactionForm(forms.ModelForm):
    origin = forms.CharField(disabled=True)

    def __init__(self, *args, user=None, association=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Set the transaction source
        if user:
            self.instance.source_user = user
            self.fields['origin'].initial = user
        elif association:
            self.instance.source_association = association
            self.fields['origin'].initial = association
        else:
            raise ValueError("source is neither user nor association")

    class Meta:
        model = PendingTransaction
        fields = ['origin', 'amount', 'target_user', 'target_association']
        widgets = {
            'target_user': ModelSelect2(url='people_autocomplete', attrs={'data-minimum-input-length': '1'}),
        }


class AssociationTransactionForm(TransactionForm):

    def __init__(self, association, *args, **kwargs):
        super().__init__(*args, association=association, **kwargs)
        self.fields['target_user'].required = True

    class Meta(TransactionForm.Meta):
        fields = ['origin', 'amount', 'target_user', 'description']
        labels = {
            'target_user': 'User',
        }


class UserTransactionForm(TransactionForm):

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, user=user, **kwargs)
        self.fields['target_user'].required = False
        self.fields['target_association'].required = False

    class Meta(TransactionForm.Meta):
        fields = ['origin', 'amount', 'target_user', 'target_association', 'description']

    def clean(self):
        cleaned_data = super().clean()

        # Do not allow associations to make evaporating money transactons
        # (not restircted on database level, but it doesn't make sense to order it)
        if not cleaned_data.get('target_user') and not cleaned_data.get('target_association'):
            raise ValidationError("Select a target to transfer the money to.")

        return cleaned_data


class ClearOpenExpensesForm(forms.Form):
    """Creates pending transactions for all members of this associations who are negative."""

    def __init__(self, *args, association=None, **kwargs):
        assert association is not None
        self.association = association
        super(ClearOpenExpensesForm, self).__init__(*args, **kwargs)

    def get_applicable_user_credits(self):
        return UserCredit.objects.filter(
            user__usermembership__association=self.association,
            balance__lt=0,  # Use this to correct for any pending transactions
        )

    @property
    def negative_members_count(self):
        return self.get_applicable_user_credits().count()

    @property
    def negative_member_credit_total(self):
        balance_sum = self.get_applicable_user_credits().aggregate(Sum('balance'))['balance__sum']
        if balance_sum is None:
            balance_sum = 0
        # Remember the - value to correct for the negative outcomes
        return "{:.2f}".format(-balance_sum)

    def clean(self):
        if not self.association.has_min_exception:
            # This does not work for associations that have no minimum balance exception
            raise ValidationError(f"{self.association} has no miniumum exception")
        if self.negative_members_count == 0:
            raise ValidationError("There are no members with a negative balance to process")

        return super(ClearOpenExpensesForm, self).clean()

    def save(self):
        credits = self.get_applicable_user_credits()
        description = f"Process open costs to {self.association}"

        for credit in credits:
            PendingTransaction.objects.create(
                source_association=self.association,
                amount=-credit.balance,
                target_user=credit.user,
                description=description
            )
