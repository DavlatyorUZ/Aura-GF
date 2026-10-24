"""Literal, user-configured application commands without language-specific rules."""
import json
import re
import unicodedata


def _normalise(text):
    return ' '.join(unicodedata.normalize('NFKC', text).casefold().split()).strip(' .!?')


def match_application_command(text, templates, assistant_names=()):
    """Return a bounded application name only for a complete configured template."""
    if not isinstance(text, str) or len(text) > 512 or not isinstance(templates, list):
        return None
    query = _normalise(text)
    for name in sorted((name for name in assistant_names if isinstance(name, str)), key=len, reverse=True):
        prefix = _normalise(name)
        if prefix and (query.startswith(prefix + ' ') or query.startswith(prefix + ', ')):
            query = query[len(prefix):].lstrip(', ')
            break
    valid = [_normalise(item) for item in templates[:32] if isinstance(item, str)
           and len(item) <= 200 and item.count('{application}') == 1]
    for template in sorted(valid, key=len, reverse=True):
        pattern = re.escape(template).replace(re.escape('{application}'), r'(?P<application>.{1,160}?)')
        match = re.fullmatch(pattern, query)
        if match:
            name = match.group('application').strip()
            if name:
                return name
    return None


def application_command_reply(result, requested_name, responses):
    """Render configured acknowledgements only from the actual launch outcome."""
    try:
        data = json.loads(result.reply_text or '{}')
    except (ValueError, TypeError):
        data = {}
    if not isinstance(data, dict):
        data = {}
    status = ('launch_requested' if result.success and data.get('status') == 'launch_requested'
              else data.get('error', 'error'))
    status = status if isinstance(status, str) else 'error'
    template = responses.get(status, responses['error'])
    application = data.get('application', requested_name)
    if not isinstance(application, str):
        application = requested_name
    return template.replace('{application}', application)
