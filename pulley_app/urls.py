from django.urls import path
from django.contrib.auth.views import PasswordResetView,PasswordResetDoneView,PasswordResetConfirmView,PasswordResetCompleteView
from . import views

urlpatterns = [
    path("image/", views.detect_pulleys, name="detect_pulleys"),
   
    path('', views.main_view, name='main'),
    path('railway/', views.railway_view, name='railway'),
    path('result_data/', views.result_data_view, name='result_data'),
    path('old_data/', views.all_data_view, name='old_data'),
     path('result_data_camera/', views.result_data_view_for_camera, name='result_data_camera'),
    path('all_data_camera/', views.all_data_view_for_camera, name='all_data_camera'),
    path('profile/', views.profile_view, name='profile'),
    path('profile_form/', views.profile_form_view, name='profile_form'),
    path('bookings/', views.bookings_view, name='bookings'),
    path('services/', views.services_view, name='services'),
    path('support/', views.support_view, name='support'),
    path('employee/', views.count_user, name='employee'),
    # Password management URLs
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('reset_password/', PasswordResetView.as_view(template_name="pulley_app/resetpassword.html"), name='reset_password'),
    path('reset_password/done/', PasswordResetDoneView.as_view(template_name="pulley_app/passwordrestdone.html"), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name="pulley_app/passwordconfirmation.html"), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(template_name="pulley_app/passwordcomplete.html"), name='password_reset_complete'),  

    path('calculator/', views.calculator_view, name='calculator'),
    path('calculator-buttons/', views.calculator_buttons_view, name='calculator_buttons'),
    path('pulley-calculator/', views.pulley_calculator_views, name='pulley_calculator'),
    path('employees/', views.employees_view, name='employees'),
    path('choose-database/', views.chooes_your_database_view, name='choose_database'),
    # path('detect-video/', views.detect_pulleys_video, name='detect_video'),
    # path('demo-video/', views.demo_video_view, name='demo_video'),
    
    
    # path("yolo_camera/", views.yolo_camera, name="yolo_camera"),
    # path("video_stream/", views.video_stream, name="video_stream"),
    # path("detection_results/", views.detection_results, name="detection_results"),
    # path("stop_camera/", views.stop_camera, name="stop_camera"),
    # path("", views.index, name="index"),
    path("yolo_camera/", views.yolo_camera, name="yolo_camera"),
    path("video_stream/", views.video_stream, name="video_stream"),
    path("detection_results/",views.detection_results, name="detection_results"),
    path("request_capture/", views.request_capture, name="request_capture"),
    path("stop_camera/", views.stop_camera, name="stop_camera"),
    path("", views.index, name="index"),
]