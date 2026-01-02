from django.core.management import BaseCommand

from varanus.server.tasks import maintenance


class Command(BaseCommand):
    help = "Manually runs the maintenance task."

    def add_arguments(self, parser):
        parser.add_argument(
            "-q",
            "--queue",
            action="store_true",
            help="Queues the task instead of running it directly",
        )

    def handle(self, *args, **options):
        if options["queue"]:
            maintenance.enqueue()
        else:
            maintenance.call()
