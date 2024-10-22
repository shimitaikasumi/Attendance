from django.urls import path
from . import views
urlpatterns = [
    path('', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('registration/', views.registration, name='registration'),
    path('attendance_date/', views.attendance_date, name='attendance_date'),
    path('clock_in/', views.clock_in, name='clock_in'),
    path('clock_out/', views.clock_out, name='clock_out'),
    path('break_in/', views.break_in, name='break_in'),
    path('break_out/', views.break_out, name='break_out'),
    path('employee_worktime/', views.employee_worktime, name='employee_worktime'),
    path('leave_application/', views.leave_application, name='leave_application'),
    path('leave_status/', views.leave_status, name='leave_status'),
    path('manage_leaves/', views.manage_leaves, name='manage_leaves'),
    path('approve_leave/<int:leave_id>/', views.approve_leave, name='approve_leave'),
    path('reject_leave/<int:leave_id>/', views.reject_leave, name='reject_leave'),
    # 従業員側
    path('request_contact/', views.request_contact, name='request_contact'),
    # 管理者側
    path('admin_contact_request/', views.admin_contact_request, name='admin_contact_requests'),
    path('admin_worktime_aggregation/', views.admin_worktime_aggregation, name='admin_worktime_aggregation'),
    path('approve_contact_request/<int:request_id>/', views.approve_contact_request, name='approve_contact_request'),
    path('reject_contactrequest/<int:request_id>/', views.reject_contact_request, name='reject_contact_request'),
    path('create_notification/', views.create_notification, name='create_notification'),
    path('view_notification/', views.view_notification, name='view_notification'),
    path('admin_worktime_empsearch/', views.admin_worktime_empsearch, name='admin_worktime_empsearch'),
]