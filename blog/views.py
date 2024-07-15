from django.shortcuts import render
from django.views import View

from .models import Post

class PostList(View):
    def get(self, request):
        posts = Post.objects.all().order_by("created_date")
        context = {"posts": posts}
        return render(request, "blog/post_list.html", context=context)
    

