import datetime

from django.contrib.auth.models import User
from nose.tools import eq_
from test_utils import TestCase

import fudge

from remo.reports.models import OVERDUE_DAY, Report
from remo.base.utils import go_back_n_months


class ModelTest(TestCase):
    """Tests related to Reports Models."""
    fixtures = ['demo_users.json']

    def setUp(self):
        """Setup tests."""
        self.user = User.objects.get(username="rep")
        self.month_year = datetime.date(year=2012, month=1, day=10)
        self.report = Report(user=self.user, month=self.month_year)
        self.report.save()

    def test_mentor_set_for_new_report(self):
        """Test that report mentor field stays the same when user
        changes mentor.

        """
        eq_(self.report.mentor, self.user.userprofile.mentor)

        # Change user mentor and re-save the report. Report should
        # point to the first mentor.
        old_mentor = self.user.userprofile.mentor
        self.user.userprofile.mentor = User.objects.get(username="counselor")
        self.user.save()

        self.report.save()
        eq_(self.report.mentor, old_mentor)

    def test_overdue_true(self):
        """Test overdue report (first test)."""
        eq_(self.report.overdue, True)

    @fudge.patch('datetime.date.today')
    def test_overdue_true_2(self, fake_requests_obj):
        """Test overdue report (second test)."""
        today = datetime.datetime.today()

        # act like it's OVERDUE_DAY + 1
        fake_date = datetime.datetime(year=today.year, month=today.month,
                                      day=OVERDUE_DAY+1)
        (fake_requests_obj.expects_call().returns(fake_date))

        month_year = go_back_n_months(today)
        report = Report.objects.create(user=self.user, month=month_year)
        eq_(report.overdue, True)

    def test_overdue_false(self):
        """Test not overdue report (first test)."""
        # Change report created_on, so report is not overdue
        month_year = datetime.date(year=2020, month=1, day=10)
        report = Report.objects.create(user=self.user, month=month_year)
        eq_(report.overdue, False)

    @fudge.patch('datetime.date.today')
    def test_overdue_false_2(self, fake_requests_obj):
        """Test not overdue report (first test)."""
        # marginal case
        today = datetime.datetime.today()

        # act like it's OVERDUE_DAY
        fake_date = datetime.datetime(year=today.year, month=today.month,
                                      day=OVERDUE_DAY)
        (fake_requests_obj.expects_call().returns(fake_date))

        month_year = go_back_n_months(today)
        report = Report.objects.create(user=self.user, month=month_year)
        eq_(report.overdue, False)

    def test_set_month_day(self):
        """Test that reports month always points to first day of the month."""
        eq_(self.report.month.day, 1)
