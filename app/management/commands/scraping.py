from .ConcertHallArakawa import get_data_ConsertHallArakawa
from .ParkStudioTakenotsuka import get_data_p_arkStudioTakenotsuka
from .BBstationNippori import get_data_BBstationNippori
from django.core.management.base import BaseCommand
import traceback


class Command(BaseCommand):
    def handle(self, *args, **options):
        errors = []
        day = 0
        # try:
        #   get_data_p_arkStudioTakenotsuka(day)
        # except Exception as e:
        #   print(traceback.format_exc())
        #   errors.append(e)
        #   errors.append(traceback.format_exc())
        try:
          print('コンサートホール荒川, day=' + str(day))

          get_data_ConsertHallArakawa(day)
        except Exception as e:
          errors.append(e)
          errors.append(traceback.format_exc())
        # try:
        #   get_data_BBstationNippori(day)
        # except Exception as e :
        #   errors.append(e)
        #   errors.append(traceback.format_exc())

        if errors:
          print(errors)
