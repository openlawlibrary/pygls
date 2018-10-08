##########################################################################
# Copyright (c) Open Law Library. All rights reserved.                   #
# See ThirdPartyNotices.txt in the project root for license information. #
##########################################################################


class CommandAlreadyRegisteredError(Exception):
    pass


class FeatureAlreadyRegisteredError(Exception):
    pass


class ThreadDecoratorError(Exception):
    pass


class ValidationError(Exception):

    def __init__(self, errors=None):
        self.errors = errors or []

    def __repr__(self):
        opt_errs = '\n-'.join([e for e in self.errors])
        return 'Missing options: {}'.format(opt_errs)
