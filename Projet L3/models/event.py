# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import pytz
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import json

from odoo import models, fields, api, exceptions, _, SUPERUSER_ID

import base64
import io
import os
import logging
import requests

_logger = logging.getLogger(__name__)

try:
    import qrcode
except ImportError:
    _logger.debug('ImportError')


class EventQrCodeEvent(models.Model):
    _inherit = 'event.event'
