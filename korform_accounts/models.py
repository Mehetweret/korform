from django.db import models
from django.utils.functional import cached_property
from django.contrib.auth.models import AbstractUser

class Profile(models.Model):
    def __unicode__(self):
      usernames = [u.get_full_name() for u in self.users.all()]
      if len(usernames) == 0:
        return u"Orphaned Profile"
      return u"Profile for {0}".format(u', '.join(usernames))

class User(AbstractUser):
    profile = models.ForeignKey(Profile, related_name='users', on_delete=models.PROTECT, null=True, help_text=u"Multiple users may be associated with a single profile. These users will have access to the same data, but with different logins.")
    
    @cached_property
    def shared_users(self):
        return self.get_shared_users()
    
    def get_full_name(self):
        return u"{0} {1}".format(self.first_name, self.last_name) if self.first_name else \
            self.email
    
    def get_shared_users(self):
        return self.profile.users.exclude(id=self.id)

def create_user_profile(instance, created, raw, **kwargs):
    if raw:
        return
    
    if not instance.profile_id:
        instance.profile = Profile.objects.create()
        instance.save()

def delete_orphaned_profile(instance, **kwargs):
    if instance.profile.users.count() == 0:
        instance.profile.delete()

models.signals.post_save.connect(create_user_profile, sender=User, dispatch_uid='create_user_profile')
models.signals.post_delete.connect(delete_orphaned_profile, sender=User, dispatch_uid='delete_orphaned_profile')
