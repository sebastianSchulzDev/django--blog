from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail


def post_list(request):
    object_list = Post.published.all()
    paginator = Paginator(object_list,3)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request,
                  'my_blog/post/list.html',
                  {'page': page,
                      'posts': posts})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                                   status='published',
                                   publish__year=year,
                                   publish__month=month,
                                   publish__day=day)
    # Lista aktywnych komentarzy dla danego posta
    comments = post.comments.filter(active=True)
    if request.method == 'POST':
        # Komentarz został opublikowany.
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Utworzenie obiektu Comment, ale jeszcze nie zapisujemy go w bazie danych.
                new_comment = comment_form.save(commit=False)
                # Przypisanie komentarza do bieżącego posta.
                new_comment.post = post
                # Zapisanie komentarza w bazie danych.
                new_comment.save()
    else:
        comment_form = CommentForm()
    return render(request,
                  'my_blog/post/detail.html',
                  {'post': post,
                   'comments': comments,
                   'comment_form': comment_form})


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'my_blog/post/list.html'


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id,status='published')
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) zachęca do przeczytania "{}"'.format(cd['name'], cd['email'], post.title)
            message = 'Przeczytaj post "{}" na stronie {}\n\n Komentarz dodany przez {}: {}'.format(post.title, post_url, cd['name'], cd['comments'])
            send_mail(subject, message, 'admin@myblog.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'my_blog/post/share.html', {'post':post,
                                                       'form': form,
                                                       'sent': sent})
