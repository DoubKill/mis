

class AppRouter(object):
    def db_for_read(self, model, **hints):
        if hasattr(model, '_database'):
            return model._database
        return 'default'

    def db_for_write(self, model, **hints):
        if hasattr(model, '_database'):
            return model._database
        return 'default'
