from django.shortcuts import render, redirect, get_object_or_404
from .models import Review,Comment
from .forms import ReviewForm,CommentForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

# Create your views here.
def review_list(request):
    reviews = Review.objects.all().order_by('-pk')
    context = {
        'reviews': reviews
    }
    return render(request, 'community/review_list.html',context)


def detail(request, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    comment_form = CommentForm()
    context = {
        'review':review,
        'comment_form' : comment_form
    }
    return render(request, 'community/review_detail.html', context)

@login_required
def create(request):
    if request.method == "POST":
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.user = request.user
            review.save()
            return redirect('community:review_list')
    else:
        review_form = ReviewForm()
    context = {
        'review_form' : review_form
    }
    return render(request,'community/form.html',context)


@login_required
def update(request, review_pk):
    if request.user.is_authenticated:
        review = get_object_or_404(Review, pk=review_pk)
        if review.user != request.user:
            return redirect('community:detail', review.pk)
        else :
            if request.method == "POST":
                review_form = ReviewForm(request.POST, instance=review)
                if review_form.is_valid():
                    updated = review_form.save()
                    return redirect('community:detail', updated.pk)
            else :
                review_form = ReviewForm(instance=review)
            context = {
                'review_form' : review_form
            }
            return render(request,'community/form.html', context)
    else:
        return redirect('accounts:login')


@login_required
@require_POST
def delete(request, review_pk):
    if request.user.is_authenticated:
        review = get_object_or_404(Review, pk=review_pk)
        if review.user != request.user:
            return redirect('community:detail', review.pk)
        else:
            if request.method == "POST":
                review = get_object_or_404(Review, pk=review_pk)
                review.delete()
                return redirect('community:review_list')
            else :
                return redirect('community:detail', review.pk)

    else:
        return redirect('accounts:login')

@login_required
def comment_create(request, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.review = review
            comment.user = request.user
            comment.save()
        return redirect('community:detail', review.pk)



@require_POST
def comment_delete(request, review_pk, comment_pk):
    if request.user.is_authenticated:
        if request.method == "POST":
            comment = get_object_or_404(Comment, pk=comment_pk)
            if comment.user == request.user:
                comment.delete()
        return redirect('community:detail', review_pk)
    else :
        return redirect('accounts:login')