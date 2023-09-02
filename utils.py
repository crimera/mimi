from datetime import timedelta


def time(seconds):
            tdelta = timedelta(seconds=seconds)
            hours, rem = divmod(tdelta.seconds, 3600)
            minutes, seconds = divmod(rem, 60)
            return "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)
