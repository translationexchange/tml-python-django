#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'xepa4ep'

from django.core.management.base import BaseCommand, CommandError
import tml.commands as tml_commands

class Command(BaseCommand):

    help = (
         u'Small utility that works with tml cache'
    )

    def add_arguments(self, parser):
        parser.add_argument('--download',
            action='store_true',
            dest='download',
            default=False,
            help='Download current release')
        parser.add_argument('--cache-dir', action='store', dest='cache_dir', default=None, type=str, help='Current working directory for cache files')
        parser.add_argument('--warmup',
            action='store_true',
            dest='warmup',
            default=False,
            help='Cache warmup')

    def handle(self, *a, **options):
        if options['download']:
            return tml_commands.download_release(options.pop('cache_dir', None))
        elif options['warmup']:
            return tml_commands.warmup_cache()
        raise CommandError("`download` should be set to start downloading")
