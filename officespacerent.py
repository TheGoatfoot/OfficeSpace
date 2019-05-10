import time
import calendar


class Rent:
    context = None

    def __init__(self, context):
        self.context = context

    def start_rent(self, rent_id, admin_id):
        result = self.context.application_database.get_rent(rent_id)
        if result is None:
            return False
        if result[3] == 1 or result[2] < 0 or result[8] == 1:
            return False
        self.context.application_database.activate_rent(rent_id)
        self.context.application_database.insert_client_rent_history(rent_id, admin_id)
        return True

    def stop_rent(self, rent_id, admin_id):
        result = self.context.application_database.get_rent(rent_id)
        if result is None:
            return False
        if result[3] == 0:
            return False
        value_subtractor = calendar.timegm(time.gmtime()) - self.datetime_to_epoch(result[4])
        value = result[2] - value_subtractor
        self.context.application_database.deactivate_rent(rent_id)
        self.context.application_database.stamp_client_rent_history(rent_id, admin_id, value_subtractor)
        self.context.application_database.update_rent_value(rent_id, value)
        return True

    def void_rent(self, rent_id, admin_id):
        result = self.context.application_database.get_rent(rent_id)
        if result is None:
            return False
        if result[8] == 1:
            return False
        if result[3] == 1:
            value_subtractor = calendar.timegm(time.gmtime()) - self.datetime_to_epoch(result[4])
            value = result[2] - value_subtractor
            self.context.application_database.deactivate_rent(rent_id)
            self.context.application_database.stamp_client_rent_history(rent_id, admin_id, value_subtractor)
            self.context.application_database.update_rent_value(rent_id, value)
        self.context.application_database.void_rent(rent_id, admin_id)
        return True

    def datetime_to_epoch(self, datetime):
        mysql_time_struct = time.strptime(datetime, '%Y-%m-%d %H:%M:%S')
        mysql_time_epoch = calendar.timegm(mysql_time_struct)
        return mysql_time_epoch
