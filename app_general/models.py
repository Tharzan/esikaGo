from django.db import models
from blog.models import Blog
from my_user.models import MyUser
import uuid
import os
from core.models import BaseImage


class PostProduit(models.Model):
 
    name_service = models.CharField(max_length=255)
    devise = models.CharField(max_length=10,default='$')
    description = models.CharField(max_length=255, null=True,blank=True)
    price = models.FloatField()
    user = models.ForeignKey(MyUser,on_delete=models.CASCADE,null=True,blank=True) 
   
    blog = models.ForeignKey(Blog,on_delete=models.CASCADE,null=True,blank=True)

    image = models.ImageField(upload_to=BaseImage.upload_to_unique_uuid, null=True)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = 'app_general/article_post_images' 
    

class Reabilitation(models.Model):
    user = models.ForeignKey(MyUser,on_delete=models.CASCADE,null=True,blank=True, related_name='reabilitations') 
   
    blog = models.ForeignKey(Blog,on_delete=models.CASCADE,null=True,blank=True, related_name="reabilitations")
    date = models.DateField()
    planifier_depuis = models.DateField(blank=True,auto_now_add=True)
    description = models.CharField(null=True,blank=True,max_length=500)
    budget = models.FloatField()
    devise = models.CharField(max_length=50,default='$')
       
    

# Create your models here.
