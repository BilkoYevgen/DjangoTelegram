from django.db import models


class TgUser(models.Model):
    user_id = models.BigIntegerField(primary_key=True)
    user_username = models.CharField(max_length=50, null=True)
    user_first_name = models.CharField(max_length=50, null=True)
    user_last_name = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.user_username, self.user_first_name, self.user_last_name


class Phone(models.Model):
    user = models.ForeignKey(TgUser, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=50)
    phone_name = models.CharField(max_length=50, default="Empty")

    def __str__(self):
        return self.phone_number


class Task(models.Model):
    user = models.ForeignKey(TgUser, on_delete=models.CASCADE)
    task = models.TextField()
    photo = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)

    def __str__(self):
        return self.task
