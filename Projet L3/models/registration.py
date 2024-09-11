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


class EventQrCodeEventRegistration(models.Model):
    _inherit = 'event.registration'

    code = fields.Char(
        string='Code',
        compute='_get_code',
        store=True
    )
    qr_code = fields.Binary(
        string='QR Code', attachment=True,
        compute='create_qr'
    )

    ticket_file = fields.Binary(
        string='Ticket PDF'
    )

    @api.depends('partner_id', 'event_id', 'name', 'event_ticket_id', 'email', 'write_date', 'date_open', 'visitor_id')
    def _get_code(self):
        for rec in self:
            rec.code = f"REG{int(datetime.utcnow().timestamp())}{rec.event_id.id}{int(rec.date_open.timestamp())}"

    @api.depends('code')
    def create_qr(self):
        _logger.info('*** create_qr ***')
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        _logger.info(self)
        for rec in self:
            if rec.code:
                qr.add_data(json.dumps({
                    'code': rec.code,
                }))
                qr.make(fit=True)
                img = qr.make_image()
                buffer = io.BytesIO()
                x = img.save(buffer, format='PNG')
                data = buffer.getvalue()
                qrcode_img = base64.b64encode(data)
                rec.qr_code = qrcode_img
            else:
                rec.qr_code = False

    @api.model
    def check_registration(self, vals):
        _logger.info('*** check_registration ***')
        registration_id = self.sudo().search([
            ('code', '=', vals['code']),
            ('event_id', '=', int(vals['event_id'])),
        ])

        _logger.info(registration_id)
        _logger.info(registration_id.state)

        if len(registration_id) > 0:
            state = registration_id.state
            if registration_id.state == 'open':
                registration_id.sudo().write({
                    'state': 'done'
                })
            return state
        else:
            return False
