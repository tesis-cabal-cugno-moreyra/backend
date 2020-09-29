from enum import Enum


class ValidRoles(str, Enum):
    RESOURCE = 'Resource'
    SUPERVISOR = 'Supervisor'
    ADMINISTRATOR = 'Administrator'
