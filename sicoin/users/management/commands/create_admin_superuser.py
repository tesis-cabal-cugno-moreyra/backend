from django.core.management.base import BaseCommand, CommandError
from sicoin.users import models


class Command(BaseCommand):
    help = 'Adds Admin profile to the first user registered as superuser'

    def handle(self, *args, **options):
        users = models.User.objects.all().order_by('date_joined')

        if not len(users):
            raise CommandError('No users loaded')

        first_user = users[0]

        if not first_user.is_superuser:
            raise CommandError('First user is not superuser')

        if not first_user.is_active:
            self.stdout.write(self.style.WARNING('First user "%s" was not active' % first_user))
            first_user.is_active = True

        first_user.save()
        existent_admin_profile = models.AdminProfile.objects.filter(user=first_user)

        if len(existent_admin_profile):
            raise CommandError('First user has already an Admin profile')

        models.AdminProfile.objects.create(user=first_user)

        self.stdout.write(self.style.SUCCESS('Successfully created admin profile for user "%s"' % first_user))
