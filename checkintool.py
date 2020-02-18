import arrow
import requests

ETOWN_HOST = ""
member_id = 11467998
STUDY_PLAN_CHECK_IN_HELPER_URL = "http://{}.englishtown.com/services/ecplatform/_tools/StudyPlanHelper.aspx?".format(
    ETOWN_HOST)

WCF_REFRESH_GROUP_URL = 'http://' + ETOWN_HOST + "/services/ecplatform/StudyPlanService.svc"

HttpStatusCode = 200

http = requests.Session()

now = arrow.now()


def check_http_status_code(response, status):
    try:

        if response.status_code == status:

            return True

        else:
            return False

    except:
        raise ("get a bad response!")


class CheckinHelperApi():
    def toggle_checkin_status(self, member_id, dates, expected_http_status_code=HttpStatusCode):
        '''It will change the date in dates list from unchecked in to checked in and checked-in to unchecked in'''
        check_in_dates = '|'.join(dates)

        url = STUDY_PLAN_CHECK_IN_HELPER_URL + 'studentId={0}&cmd=checkin&dates={1}'.format(member_id, check_in_dates)
        response = http.get(url)
        check_http_status_code(response, expected_http_status_code)
        return response

    def load_checkin_dates(self, member_id, expected_http_status_code=HttpStatusCode):
        url = STUDY_PLAN_CHECK_IN_HELPER_URL + 'studentId={0}&cmd=loadcheckincalendar'.format(member_id)
        response = http.get(url)
        check_http_status_code(response, expected_http_status_code)
        return response.json()

    def refresh_group(self, member_id, expected_http_status_code=HttpStatusCode):
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': '"http://tempuri.org/IStudyPlanService/RefreshStudyPlanGroup"'
        }
        data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body><RefreshStudyPlanGroup xmlns="http://tempuri.org/"><studentId>{}</studentId></RefreshStudyPlanGroup></s:Body></s:Envelope>'.format(
            member_id)
        response = http.post(url=WCF_REFRESH_GROUP_URL, headers=headers, data=data)

        check_http_status_code(response, expected_http_status_code)

    def load_user_checkin_status(self):
        checkin_dates = self.load_checkin_dates(member_id)
        return checkin_dates

    def toggle_user_checkin_status(self, checkin_dates):
        """

        :param checkin_dates: the format is: YYYYMMDD, use it like [check_in_dates]
        :return:
        """
        self.toggle_checkin_status(member_id, checkin_dates)

    def toggle_checkin_days_before_today(self, days_to_toggle, today):
        now = arrow.now()
        date_range = sorted([now.shift(days=-e).format('YYYYMMDD') for e in range(today, days_to_toggle)])

        self.toggle_user_checkin_status(date_range)

    def clear_checkin_data(self):
        date_list = self.load_user_checkin_status()

        # Undo check-in for those already checked-in days
        if date_list:
            checkin_dates = list(map(lambda x: x.split('T')[0].replace('-', ''), date_list))
            self.toggle_user_checkin_status(checkin_dates)


key_new = [7, 21, 35, 60, 100]
badge_type = [8, 7, 6, 26, 27]  # 8, 7, 6 , 26,27stand for bronze, sliver, gold, diamond, rare

sql = "insert into  Oboe.dbo.StudyPlanEventHistory values ({},{},'NULL','{}','{}','{}')"

ck = CheckinHelperApi()


def below_bronze_badge(days, today):
    ck.toggle_checkin_days_before_today(days, today)

    if days >= key_new[0]:
        badgedate = now.shift(days=-(days - key_new[0])).format('YYYY-MM-DD')
        print("please add bronze badge like\n" + sql.format(member_id, badge_type[0], badgedate, badgedate, badgedate))


def above_bronze_badge(days, today):
    below_bronze_badge(days, days - key_new[0])

    ck.toggle_checkin_days_before_today(days - key_new[0], today)

    if days >= key_new[1]:
        badgedate = now.shift(days=-(days - key_new[1])).format('YYYY-MM-DD')
        print("please add sliver badge like\n" + sql.format(member_id, badge_type[1], badgedate, badgedate, badgedate))


def above_sliver_badge(days, today):
    above_bronze_badge(days, days - key_new[1])
    ck.toggle_checkin_days_before_today(days - key_new[1], today)

    if days >= key_new[2]:
        badgedate = now.shift(days=-(days - key_new[2])).format('YYYY-MM-DD')
        print("please add gold badge like\n" + sql.format(member_id, badge_type[2], badgedate, badgedate, badgedate))


def above_gold_badge(days, today):
    above_sliver_badge(days, days - key_new[2])
    ck.toggle_checkin_days_before_today(days - key_new[2], today)

    if days >= key_new[3]:
        badgedate = now.shift(days=-(days - key_new[3])).format('YYYY-MM-DD')
        print("please add dimond badge like\n" + sql.format(member_id, badge_type[3], badgedate, badgedate, badgedate))


def above_diamond_badge(days, today):
    above_gold_badge(days, days - key_new[3])
    ck.toggle_checkin_days_before_today(days - key_new[3], today)

    if days >= key_new[4]:
        badgedate = now.shift(days=-(days - key_new[4])).format('YYYY-MM-DD')
        print("please add rare badge like\n" + sql.format(member_id, badge_type[4], badgedate, badgedate, badgedate))


def above_rare_badge(days, today):
    above_diamond_badge(days, days - key_new[4])
    ck.toggle_checkin_days_before_today(days - key_new[4], today)


if __name__ == "__main__":

    start = input("Do you want checkin today?")
    days = int(input("input your checkin time"))

    if start == 'y':
        today = 0
    else:
        today = 1

    ck.clear_checkin_data()

    # 8, 7, 6 stand for bronze, sliver, gold

    if days > key_new[4]:
        above_rare_badge(days, today)

    if days > key_new[3] and days <= key_new[4]:
        above_diamond_badge(days, today)

    if days > key_new[2] and days <= key_new[3]:
        above_gold_badge(days, today)

    if days > key_new[1] and days <= key_new[2]:
        above_sliver_badge(days, today)

    if days > key_new[0] and days <= key_new[1]:
        above_bronze_badge(days, today)

    if days <= key_new[0]:
        below_bronze_badge(days, today)
