import sys, os
from datetime import time
import kwargs as kwargs
from django.views.generic import View
from netmiko.cisco_base_connection import CiscoSSHConnection
from rest_framework import status, views, mixins, viewsets, permissions
from django.http import JsonResponse, HttpResponse
from netmiko import ConnectHandler
from netmiko.dlink.dlink_ds import DlinkDSTelnet, DlinkDSSSH
from netmiko.terminal_server.terminal_server import TerminalServerSSH





