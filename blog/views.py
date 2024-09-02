""" blog.views file """

from django.shortcuts import render, redirect
from django.views import View
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from .models import Post
from .forms import PostForm

class PostList(View):
    """ Index page for blog section """
    def get(self, request):
        posts = Post.objects.all().order_by("-created_date")
        return render(request, "blog/post_list.html", {"posts": posts})
    
@method_decorator(login_required, name='dispatch')
class AddPost(View):
    # permissions need. authentication, blogger_permission -> post model permission
    def get(self, request):
        form = PostForm()
        return render(request, 'blog/add_post.html', {'form': form})

    def post(self, request):
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('blog:post_list')
        # else
