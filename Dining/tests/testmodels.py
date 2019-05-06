from datetime import datetime, date, timezone, time
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from Dining.models import DiningEntryUser, DiningEntryExternal
from Dining.models import DiningList, DiningEntry
from UserDetails.models import User, Association


class DiningListTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        pass

    def test_is_open(self):
        association = Association.objects.create()
        list = DiningList.objects.create(date=date(2015, 1, 1), association=association,
                                         sign_up_deadline=datetime(2015, 1, 1, 17, 00, tzinfo=timezone.utc))

        with patch.object(timezone, 'now', return_value=datetime(2015, 1, 1, 16, 59, tzinfo=timezone.utc)) as mock_now:
            self.assertTrue(list.is_open())
        with patch.object(timezone, 'now', return_value=datetime(2015, 1, 1, 17, 00, tzinfo=timezone.utc)) as mock_now:
            self.assertFalse(list.is_open())
        with patch.object(timezone, 'now', return_value=datetime(2015, 1, 1, 17, 1, tzinfo=timezone.utc)) as mock_now:
            self.assertFalse(list.is_open())


class DiningListCleanTestCase(TestCase):
    def setUp(self):
        self.dining_list = DiningList(date=date(2123, 1, 2), sign_up_deadline=datetime(2100, 2, 2),
                                      association=Association.objects.create())

    def test_serve_time_valid(self):
        self.dining_list.serve_time = time(18,00)
        self.dining_list.full_clean() # Shouldn't raise

    def test_serve_time_too_late(self):
        self.dining_list.serve_time = time(23,30)
        self.assertRaises(ValidationError, self.dining_list.full_clean)

    def test_serve_time_too_early(self):
        self.dining_list.serve_time = time(11,00)
        self.assertRaises(ValidationError, self.dining_list.full_clean)


class DiningEntryTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('piet')
        cls.association = Association.objects.create(slug='assoc')
        cls.dining_list = DiningList.objects.create(date=date(2123, 2, 1), association=cls.association,
                                                    claimed_by=cls.user)

    def test_get_internal_true(self):
        entry = DiningEntryUser(dining_list=self.dining_list, user=self.user)
        entry.save()
        self.assertEqual(entry, entry.get_internal())  # Direct call
        self.assertEqual(entry, DiningEntry.objects.get(pk=entry.pk).get_internal())  # Indirect call
        self.assertEqual(entry, DiningEntryUser.objects.get(pk=entry.pk).get_internal())  # Indirect call 2

    def test_get_internal_false(self):
        entry = DiningEntryExternal.objects.create(dining_list=self.dining_list, user=self.user, name='Jan')
        self.assertIsNone(entry.get_internal())  # Direct call
        self.assertIsNone(DiningEntry.objects.get(pk=entry.pk).get_internal())  # Indirect call
