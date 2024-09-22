from rest_framework import throttling
import datetime as dt

offset = dt.timedelta(hours=3)  # время смещения часового пояса
tz = dt.timezone(offset, name='MSC')  # часовая зона Москвы




class LunchBreakThrottle(throttling.BaseThrottle):
    """Запрет любых запросов к публикациям в обеденное время
    (с 13:00 до 14:00).
    """
    def allow_request(self, request, view):
        now = dt.datetime.now().hour
        if 13 <= now <= 14:  # если час с 13 до 14
            return False  # запретить обработку запросов
        return True  # во всех других случаях разрешить
