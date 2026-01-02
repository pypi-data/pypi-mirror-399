from agilix_api_fr8train.api import Api
import pendulum
import unittest


class TestActiveStudent(unittest.TestCase):
    def setUp(self):
        self.api = Api()
        self.student = "65636@txvirtual.org"
        self.teacher = "k.chaney@txvirtual.org"
        self._2_day_ago = pendulum.now(tz="UTC").subtract(days=2).to_iso8601_string()
        self._9_day_ago = pendulum.now(tz="UTC").subtract(days=9).to_iso8601_string()
        self.today = pendulum.now(tz="UTC").to_iso8601_string()
        self.crap_date = "1753-01-01T00:00:00.000Z"

        self.prod_test1_lld = "2025-12-15T20:39:02.937Z"
        self.prod_test1_esd = "2025-08-11T06:00:00Z"
        self.prod_test1_u = "79012@txvirtual.org"

    # FAILS BECAUSE IT'S A TEACHER
    def test_is_not_active_student(self):
        self.assertFalse(self.api.utils.is_active_student(self.teacher))

    # FAILS BECAUSE THEY HAVE NO LAST LOGIN DATE EVEN THOUGH THEY'RE A STUDENT
    def test_is_not_active_student_2(self):
        self.assertFalse(self.api.utils.is_active_student(self.student))

    # FAILS BECAUSE OF BULLSHIT LAST LOGIN DATE FROM IF THEY HAVEN'T LOGGED IN
    def test_no_last_login_date(self):
        self.assertFalse(self.api.utils.is_active_student(self.student, self.crap_date))

    # PASSES WITH NO LAST LOGIN DATE WITHIN FIRST WEEK OF SCHOOL (GOING OFF OF ENROLLMENT START DATE 2 DAYS AGO)
    def test_no_last_login_date_first_week_of_school(self):
        self.assertTrue(
            self.api.utils.is_active_student(
                username=self.student,
                enrollment_start_date=self._2_day_ago,
            )
        )

    # FAILS BECAUSE NO LAST LOGIN AND WE ARE PAST A WEEK OF SCHOOL
    def test_no_last_login_past_first_week_of_school(self):
        self.assertFalse(
            self.api.utils.is_active_student(
                username=self.student,
                enrollment_start_date=self._9_day_ago,
            )
        )

    # PASSES WITH CRAP LAST LOGIN DATE BUT ENROLLMENT START DATE IS WITHIN THE LAST TWO DAYS
    def test_crap_last_login_date_but_first_week_of_school(self):
        self.assertTrue(
            self.api.utils.is_active_student(
                username=self.student,
                last_login_date=self.crap_date,
                enrollment_start_date=self._2_day_ago,
            )
        )

    # FAILS WITH CRAP LAST LOGIN DATE AND ENROLLMENT START > 1 WEEK AGO
    def test_crap_last_login_date_longer_than_first_week_of_school(self):
        self.assertFalse(
            self.api.utils.is_active_student(
                username=self.student,
                last_login_date=self.crap_date,
                enrollment_start_date=self._9_day_ago,
            )
        )

    # DEFAULT NO LOGIN WITHIN THE PAST WEEK TEST
    def test_default_no_login_within_past_week(self):
        self.assertFalse(
            self.api.utils.is_active_student(self.student, self._9_day_ago)
        )

    # DEFAULT LOGIN WITHIN THE PAST WEEK TEST
    def test_default_login_within_past_week(self):
        self.assertTrue(self.api.utils.is_active_student(self.student, self._2_day_ago))

    # PROD TEST 1
    def test_prod_test1(self):
        self.assertTrue(
            self.api.utils.is_active_student(
                username=self.prod_test1_u,
                last_login_date=self.prod_test1_lld,
                enrollment_start_date=self.prod_test1_esd,
            )
        )


if __name__ == "__main__":
    unittest.main()
