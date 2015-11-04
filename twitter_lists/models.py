from django.db import models

# Create your models here.

class ListMemberRec(models.Model):
    list_id = models.BigIntegerField()
    member_id = models.BigIntegerField()

    class Meta:
        db_table = 'list_member_rec'
        unique_together = (('list_id', 'member_id'),)


class ListRec(models.Model):
    list_id = models.BigIntegerField(primary_key=True)
    list_description = models.TextField(blank=True, null=True)
    list_name = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'list_rec'


