from django.urls import path
from django.contrib.auth import views as auth_views

from . import views 

urlpatterns = [
	
	path('', views.loginPage, name="login"),
	path('register', views.registerPage, name="register"),
	path('logout', views.logoutUser, name="logout"),

	path('home', views.home, name="home"),
	path('about', views.about, name="about"),
	path('search_stock', views.searchPage, name="search_stock"),
	path('add_stock', views.add_stock, name="add_stock"),
	path('delete_stock/<stock_name>', views.delete_stock, name="delete_stock"),

	path('reset_password', 
		auth_views.PasswordResetView.as_view(template_name="password_reset.html"), 
		name="reset_password"),

	path('reset_password_sent', 
		auth_views.PasswordResetDoneView.as_view(template_name="password_reset_sent.html"),
		 name="password_reset_done"),
	
	path('reset/<uidb64>/<token>', 
		auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_form.html"), 
		name="password_reset_confirm"),

	path('reset_password_complete', 
		auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_done.html"), 
		name="password_reset_complete"),
]