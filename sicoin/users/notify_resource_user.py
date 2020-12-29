from sicoin.users.models import ResourceProfile


def notify_resource_user_activation(resource: ResourceProfile):
    title = 'Usuario activado!'
    body = f'Tu usuario, para el dominio {resource.domain.domain_name} ha sido activado.'
    resource.device.send_message(title=title, body=body)


def notify_resource_user_deactivation(resource: ResourceProfile):
    title = 'Usuario desactivado!'
    body = f'Tu usuario, para el dominio {resource.domain.domain_name} ha sido desactivado.'
    resource.device.send_message(title=title, body=body)
