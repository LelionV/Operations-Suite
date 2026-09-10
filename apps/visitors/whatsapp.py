"""
WhatsApp notification sender.
Supports Twilio, Meta Cloud API, and a custom REST endpoint.
All calls are silent — never crash the main app.
"""
import json
import logging

logger = logging.getLogger(__name__)


def _get_config():
    try:
        from .models import WhatsAppConfig
        return WhatsAppConfig.objects.filter(is_active=True).first()
    except Exception:
        return None


def send_whatsapp(to_number: str, message: str) -> bool:
    """
    Send a WhatsApp message to `to_number` (E.164 format, e.g. +254712345678).
    Returns True on success, False on failure.
    """
    if not to_number or not to_number.strip():
        return False

    cfg = _get_config()
    if not cfg:
        logger.warning('WhatsApp: no active config found.')
        return False

    to_number = to_number.strip()
    if not to_number.startswith('+'):
        to_number = '+' + to_number

    try:
        if cfg.provider == 'twilio':
            return _send_twilio(cfg, to_number, message)
        elif cfg.provider == 'meta':
            return _send_meta(cfg, to_number, message)
        elif cfg.provider == 'custom':
            return _send_custom(cfg, to_number, message)
        else:
            logger.warning(f'WhatsApp: unknown provider {cfg.provider}')
            return False
    except Exception as e:
        logger.error(f'WhatsApp send error: {e}')
        return False


def _send_twilio(cfg, to_number, message):
    import urllib.request
    import urllib.parse
    import base64

    url = f'https://api.twilio.com/2010-04-01/Accounts/{cfg.account_sid}/Messages.json'
    data = urllib.parse.urlencode({
        'From':  f'whatsapp:{cfg.from_number}',
        'To':    f'whatsapp:{to_number}',
        'Body':  message,
    }).encode('utf-8')

    credentials = base64.b64encode(
        f'{cfg.account_sid}:{cfg.auth_token}'.encode()).decode()
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Authorization', f'Basic {credentials}')

    with urllib.request.urlopen(req, timeout=10) as resp:
        result = json.loads(resp.read())
        sid = result.get('sid', '')
        logger.info(f'WhatsApp Twilio sent SID={sid}')
        return bool(sid)


def _send_meta(cfg, to_number, message):
    import urllib.request

    # Strip leading + for Meta API
    clean_number = to_number.lstrip('+')
    payload = json.dumps({
        'messaging_product': 'whatsapp',
        'to': clean_number,
        'type': 'text',
        'text': {'body': message},
    }).encode('utf-8')

    url = f'https://graph.facebook.com/v18.0/{cfg.account_sid}/messages'
    req = urllib.request.Request(url, data=payload, method='POST')
    req.add_header('Authorization', f'Bearer {cfg.auth_token}')
    req.add_header('Content-Type', 'application/json')

    with urllib.request.urlopen(req, timeout=10) as resp:
        result = json.loads(resp.read())
        msg_id = result.get('messages', [{}])[0].get('id', '')
        logger.info(f'WhatsApp Meta sent id={msg_id}')
        return bool(msg_id)


def _send_custom(cfg, to_number, message):
    import urllib.request

    headers = {'Content-Type': 'application/json'}
    if cfg.api_key:
        headers['Authorization'] = f'Bearer {cfg.api_key}'
    if cfg.extra_headers:
        try:
            headers.update(json.loads(cfg.extra_headers))
        except Exception:
            pass

    payload = json.dumps({'to': to_number, 'message': message}).encode('utf-8')
    req = urllib.request.Request(cfg.api_url, data=payload, method='POST')
    for k, v in headers.items():
        req.add_header(k, v)

    with urllib.request.urlopen(req, timeout=10) as resp:
        logger.info(f'WhatsApp Custom: HTTP {resp.status}')
        return resp.status < 300
