class MongoRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'kernel_app':
            if model.__name__ != 'User':
                return 'mongodb'
        return None
    
    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'kernel_app':
            if model.__name__ != 'User':
                return 'mongodb'
        return None
    
    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'kernel_app' and obj2._meta.app_label == 'kernel_app':
            return True
        return None
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'kernel_app':
            if model_name == 'user':
                return db == 'default'
            return db == 'mongodb'
        elif db == 'mongodb':
            return False
        return None