"""
"""
# Validators
def validator_action_trigger(request):
    if 'action' in request and 'trigger' in request:
        return True
    return False

def validator_action(request):
    if 'type' in request['action'] and 'url' in request['action'] and 'kind' in request['action']:
        return True
    return False

def validator_trigger(request):
    if 'date' in request['trigger'] or 'interval' in request['trigger'] or 'cron' in request['trigger']:
        return True
    return False