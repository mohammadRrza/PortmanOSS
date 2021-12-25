import datetime
import json
import os
import sys
import paramiko
from django.db import connection
from django.http import JsonResponse
from pathlib import Path


class GetDslamPortParams():
    def __init__(self):
        pass

    def run_command(self):
        query = 'SELECT * from "16M_report"'
        cursor = connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            print(row)


