# 0422 Django Project3 README

> 2인 1조 Project - CRUD, AUTH(login, signup ,logout), 1:N(comment)

### 구현 과정

1. 구조 잡기

* 프로젝트명 : django_pjt3
* 앱명 : accounts, community

* accounts 필수
  * templates
    * signup.html(회원가입 화면)
    * login.html(로그인 화면)
  * urls.py
* community 필수
  * templates
    * form.html(글쓰기, 수정하기)
    * review_list.html(index화면, 게시글 리스트)
    * review_detail.html(상세보기, 수정, 삭제, 댓글기능,댓삭)
  * forms.py (댓글폼CommentForm, 게시물폼ReviewyForm)
  * urls.py

---

2. model 설정

```python
from django.conf import settings #추가

class Review(models.Model):
    ...명세대로
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) #추가

class Comment(models.Model):
    content = models.TextField()
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
```

3. Form

* forms.py 주의사항

```python
#forms.py
#글쓰기 Form에서 user_id가 같이 입력되도록 뜨므로 forms.py에 fields를 사용자 지정으로 바꾼다.
class ReviewForm(...)
	...
    fields = ['title','movie_title',,'rank','content']로
```

4. Admin

```python
admin.site.register(Review,Comment)
```

5. URL

   명세대로

6. View & Template 필수조건

   * Navbar 조건 -`if request.resolver_match.url_name == ?` 사용
     * 사용자 인증 여부 관계x(무조건 고정) - Home버튼(전체리뷰목록조회), 새 리뷰 작성 페이지
     * 사용자 인증 x - 로그인 페이지, 회원가입페이지 링크
     * 사용자 인증 0 - 로그아웃



     * accounts app
    
       * 신규 사용자 생성(회원가입)
         * 이미 인증된 사용자 `is_authenticated` 사용 - 전체리뷰목록 페이지로 redirect
         * `UserCreationForm`사용
       * 기존 사용자 인증(로그인)
         * 이미 인증되어있는 사용자- 전체 리뷰 목록 페이지로 redirect
         * ` AuthenticationForm`  사용
    
       * POST 유효성 검사  `is_valid`를 사용
       * 404에러 `get_object_or_404` 사용
    
       * 사용자==작성자 `if review.user == request.user` 사용
    
     ```python
     #accounts/views.py
    
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
     ```
    
     * community app
       * 이미 인증된 사용자 `is_authenticated` 사용 - 전체리뷰목록 페이지로 redirect
       * 데이터 검증, 404에러 페이지 동일
    
     ```python
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
     ```





* 페어프로젝트 하면서 느낀 점:

  * 혼자 하기 보다는 협업하면서 서로 질문도 하고 의견도 나눌 수 있어서 좋았다.
  * 협업은 소통이 중요하다.
  * 같이 하면서 문제가 생기면 함께 해결하면서 나도 배울 수 있는게 좋았다.
  * 다른 사람의 스타일을 볼 수 있는게 참고가 된다.
  * 같이 해주신 병준님 수고 많으셨고 감사드린다는 점





* 어려웠던 점

  * create에서 처음에 모델 정의에 user부터 넣고서 CRUD기능을 구현하려고 했더니 user가 NULL이 되어 integrity룰에 어긋났다.

  -> 해결 :  user를 위해 로그인 폼과 기능들을 넣어주고, @login_required을 추가하여 예외를 방지.

  * update를 하니까 글이 새로 작성되어버리는 문제가 발생.

  -> 해결 : form.html에서 action 주소가 create로 되어 있었다.

  * 게시글 delete가 되지 않음

  -> delete의 버튼이 POST가 아니라 get방식이었다.



* 우리조 게시판만의 강점

1. `{{ review.title}} [{{review.comment_set.count}}]`를 사용하여 제목 옆에 댓글 수를 표시.
2. 자신의 댓글이 아니면 삭제 버튼이 없다.
3. 자신의 게시글이 아니면 수정, 삭제 버튼이 없다.
4. 로그아웃 상태이면 댓글 작성 안되고 오직 글 조회만 가능하다.








