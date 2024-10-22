from datetime import timedelta
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render
from django.http import HttpResponse
from .models import Employee, Attendance, LeaveRequest, ContactRequest, Notification
import datetime


# Create your views here.
def index(request):
    return HttpResponse("ようこそ")


def login(request):
    if request.method == "POST":
        empid = request.POST.get('empid')
        emppasswd = request.POST.get('emppasswd')

        if not empid or not emppasswd:
            messages.error(request, "IDまたはパスワードを入力してください")
            return render(request, 'login.html')

        try:
            employee = Employee.objects.get(empid=empid)
        except Employee.DoesNotExist:
            messages.error(request, "利用者IDが違います")
            return render(request, 'login.html')

        if employee.emppasswd == emppasswd:
            request.session['empid'] = employee.empid
            if employee.role == 5:
                return render(request, 'admin/home.html')
            else:
                return render(request, 'attendance_departure.html',{'employee': employee})
        else:
            messages.error(request, "パスワードが違います")
            return render(request, 'login.html')

    return render(request, 'login.html')


def logout(request): # ユーザーをログアウト
    request.session.flush()  # セッションをクリア
    return redirect('login')


def registration(request):
    if request.method == 'GET':
        employee = Employee.objects.all()
        return render(request, 'admin/emp_registration.html', {'employee': employee})

    if request.method == 'POST':
        empid = request.POST.get('empid')
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        emppasswd = request.POST.get('emppasswd')
        role = request.POST.get('role')
        department = request.POST.get('department')
        hire_date = request.POST.get('hire_date')

        # チェックリスト
        required_fields = [empid, fname, lname, email, emppasswd, role, department, hire_date]
        print(required_fields)
        if not all(required_fields):
            print(request, '全ての項目を入力してください。')
        elif Employee.objects.filter(empid=empid).exists():
            print(request, 'このIDはすでに登録してあります。')
        else:
            employee = Employee(
                empid=empid, fname=fname,
                lname=lname, email=email,
                emppasswd=emppasswd,
                role=role, department=department,
                hire_date=hire_date
            )
            employee.save()
            print(employee.empid)
            print(request, '従業員が登録されました。')
            return render(request,'Registration_end.html')

    return render(request, 'admin/emp_registration.html')


# 出勤
def clock_in(request):
    if 'empid' not in request.session:
        return redirect('login')  # ログインしていない場合はリダイレクト
    employee = get_object_or_404(Employee, empid=request.POST.get('empid'))
    if request.method == 'POST':
        today = timezone.now().date()

        # 出勤情報を取得または作成
        attendance = Attendance(empid_id=request.POST.get('empid'), date=today)

        if not attendance.clock_in_time:
            attendance.clock_in_time = datetime.datetime.now()
            attendance.save()
            message = "出勤時間を記録しました。"
        else:
            message = "すでに出勤時間が記録されています。"

        return render(request, 'attendance_departure.html', {'message': message, 'employee': employee})


# 退勤
def clock_out(request):
    if 'empid' not in request.session:
        return redirect('login')  # ログインしていない場合はリダイレクト
    employee = get_object_or_404(Employee, empid=request.POST.get('empid'))
    if request.method == 'POST':
        today = timezone.now().date()

        attendance = Attendance.objects.filter(empid=request.POST.get('empid'), date=today).first()

        if not attendance:
            message = '出勤記録がありません'
        else:
            if not attendance.clock_out_time:
                attendance.clock_out_time = datetime.datetime.now()
                attendance.save()
                message = "退勤時間を記録しました。"
            else:
                message = "すでに退勤時間が記録されています。"

        return render(request, 'attendance_departure.html', {'message': message, 'employee': employee})


# 休憩入
def break_in(request):
    if 'empid' not in request.session:
        return redirect('login')  # ログインしていない場合はリダイレクト
    employee = get_object_or_404(Employee, empid=request.POST.get('empid'))
    if request.method == 'POST':
        today = timezone.now().date()

        attendance = Attendance.objects.filter(empid=request.POST.get('empid'), date=today).first()

        if not attendance.break_in_time:
            attendance.break_in_time = datetime.datetime.now()
            attendance.save()
            message = "休憩開始時間を記録しました。"
        else:
            message = "出勤記録がないか、すでに休憩開始時間が記録されています。"

        return render(request, 'attendance_departure.html', {'message': message, 'employee': employee})


# 休憩戻
def break_out(request):
    if 'empid' not in request.session:
        return redirect('login')  # ログインしていない場合はリダイレクト
    employee = get_object_or_404(Employee, empid=request.POST.get('empid'))
    if request.method == 'POST':
        today = timezone.now().date()

        attendance = Attendance.objects.filter(empid=request.POST.get('empid'), date=today).first()

        if not attendance.break_out_time:
            attendance.break_out_time = datetime.datetime.now()
            attendance.save()
            message = "休憩終了時間を記録しました。"
        else:
            message = "出勤記録がないか、すでに休憩終了時間が記録されています。"

        return render(request, 'attendance_departure.html', {'message': message, 'employee': employee})


def employee_worktime(request):
    if 'empid' not in request.session:
        return redirect('login')  # ログインしていない場合はリダイレクト
    employee = Employee.objects.get(empid=request.GET.get('empid'))
    if request.method == 'GET':
        today = timezone.now().date()

        # 今日の勤務時間を集計
        attendance_today = Attendance.objects.filter(empid=request.GET.get('empid'), date=today).first()
        total_hours_today = timedelta()

        if attendance_today.clock_in_time and attendance_today.clock_out_time:
            total_hours_today = (attendance_today.clock_out_time - attendance_today.clock_in_time)

        # 今月の勤務時間を集計
        first_day_of_month = today.replace(day=1)
        attendance_this_month = Attendance.objects.filter(empid_id=request.GET.get('empid'), date__gte=first_day_of_month)
        total_hours_month = timedelta()

        for attendance in attendance_this_month:
            if attendance.clock_in_time and attendance.clock_out_time:
                total_hours_month += (attendance.clock_out_time - attendance.clock_in_time)

        context = {
            'employee': employee,
            'total_hours_today': total_hours_today,
            'total_hours_month': total_hours_month,
        }

        return render(request, 'employee_worktime.html', context)
    return render(request, 'employee_worktime.html', {'employee': employee})


def admin_worktime_empsearch(request):
    if 'empid' not in request.session:
        return redirect('login')  # ログインしていない場合はリダイレクト
    # 管理者（roleが5）でない場合はリダイレクト
    if 'empid' in request.session:
        empcheck = Employee.objects.get(empid=request.session.get('empid'))
        if empcheck.role == 5:
            if request.method == 'GET':
                e = Employee.objects.all()
                return render(request, 'admin/worktime_aggregation.html', {'employee': e})
            elif request.method == 'POST':
                empid = request.POST.get('empid')
                if empid:
                    e = Employee.objects.filter(empid=empid)
                    total_hours_month = timedelta()
                    today = timezone.now().date()
                    first_day_of_month = today.replace(day=1)
                    attendance_this_month = Attendance.objects.filter(empid=request.GET.get('empid'), date__gte=first_day_of_month)
                    for attendance in attendance_this_month:
                        if attendance.clock_in_time and attendance.clock_out_time:
                            total_hours_month += (attendance.clock_out_time - attendance.clock_in_time)
                    return render(request, 'admin/worktime_aggregation.html', {'employee': e,'employee_worktime': total_hours_month,})
                else:
                    message = "指定されたIDを持つ従業員は存在しません。"

                return render(request, 'admin/worktime_aggregation.html', {'message': message})
            return render(request, 'admin/worktime_aggregation.html')
        else:
            return redirect('login')
    else:
        return redirect('login')


def admin_worktime_aggregation(request):
    if 'empid' not in request.session:
        return redirect('login')  # ログインしていない場合はリダイレクト
    # 管理者（roleが5）でない場合はリダイレクト
    if 'empid' in request.session:
        empcheck = Employee.objects.get(empid=request.session.get('empid'))
        if empcheck.role == 5:
            if request.method == 'POST':
                today = timezone.now().date()
                employee = Employee.objects.all()

                total_hours_month = timedelta()
                # 従業員ごとの今月の勤務時間を集計
                for e in employee:
                    first_day_of_month = today.replace(day=1)
                    attendance_this_month = Attendance.objects.filter(empid=request.GET.get('empid'), date__gte=first_day_of_month)

                    for attendance in attendance_this_month:
                        if attendance.clock_in_time and attendance.clock_out_time:
                            total_hours_month += (attendance.clock_out_time - attendance.clock_in_time)

                context = {
                    'employee': employee,
                    'employee_worktime': total_hours_month,
                }
                return render(request, 'admin/worktime_aggregation.html',  context)

    return render(request, 'admin/worktime_aggregation.html')


def leave_application(request):
    if 'empid' not in request.session:
        return redirect('login')  # ログインしていない場合はリダイレクト
    if request.method == 'POST':
        leave_type = request.POST.get('leave_type')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason')

        if not all([leave_type, start_date, end_date, reason]):
            message = '全ての項目を入力してください。'
            return render(request, 'leave_application.html', {'message': message})
        else:
            LeaveRequest.objects.create(
                employee=Employee.objects.get(empid=request.session['empid']),
                leave_type=leave_type,
                start_date=start_date,
                end_date=end_date,
                reason=reason
            )
            message = '休暇申請を送信しました。'
            return render(request,'leave_status.html', {'message': message})

    return render(request, 'leave_application.html')


def leave_status(request):
    if request.method == 'GET':
        employee = Employee.objects.get(employee_id=request.session['empid'])
        leave_request = LeaveRequest.objects.filter(employee_id=request.GET.get('empid'))

    return render(request, 'leave_status.html', {'leave_request': leave_request, 'employee':employee})


def manage_leaves(request):
    # ログインしているのが管理者かどうかをチェック
    if request.session.get('empid'):
        employee = get_object_or_404(Employee, empid=request.session['empid'])
        if employee.role != 5:  # 管理者か確認
            return redirect('login')

    # 承認待ちの申請を取得
    pending_leaves = LeaveRequest.objects.filter(status='pending').order_by('created_at')
    return render(request, 'admin/manage_leaves.html', {'pending_leaves': pending_leaves})


def approve_leave(request, leave_id):
    leave = get_object_or_404(LeaveRequest, pk=leave_id)
    leave.status = 'approved'
    leave.save()
    return redirect('manage_leaves')


def reject_leave(request, leave_id):
    leave = get_object_or_404(LeaveRequest, pk=leave_id)
    leave.status = 'rejected'
    leave.save()
    return redirect('manage_leaves')


def request_contact(request):
    if request.method == "POST":
        employee_id = request.session.get('empid')
        employee = get_object_or_404(Employee, pk=employee_id)
        request_type = request.POST.get('request_type')
        message = request.POST.get('message')

        # ContactRequestオブジェクトを作成して保存
        contact_request = ContactRequest(
            employee=employee,
            request_type=request_type,
            message=message
        )
        contact_request.save()
        messages.success(request, "リクエストが送信されました。")
        return redirect('attendance_departure')  # 適切なリダイレクト先に変更してください

    return render(request, 'request_contact.html')


def admin_contact_request(request):
    contact_request = ContactRequest.objects.all()
    return render(request, 'admin/contact_request.html', {'contact_request': contact_request})


def approve_contact_request(request, request_id):
    contact_request = get_object_or_404(ContactRequest, pk=request_id)
    contact_request.status = '承認'
    contact_request.save()
    messages.success(request, "リクエストが承認されました。")
    return redirect('admin_contact_requests')


def reject_contact_request(request, request_id):
    contact_request = get_object_or_404(ContactRequest, pk=request_id)
    contact_request.status = '却下'
    contact_request.save()
    messages.success(request, "リクエストが却下されました。")
    return redirect('admin_contact_requests')


# 通知を作成するビュー
def create_notification(request):
    if request.method == "POST":
        recipient_id = request.POST.get('recipient_id')
        message = request.POST.get('message')

        if recipient_id and message:
            try:
                recipient = Employee.objects.get(empid=recipient_id)
                sender = Employee.objects.get(empid=request.session['empid'])
                Notification.objects.create(sender=sender, recipient=recipient, message=message, created_at=timezone.now())
                messages.success(request, "通知を送信しました。")
            except Employee.DoesNotExist:
                messages.error(request, "指定された従業員が見つかりません。")
        else:
            messages.error(request, "全ての項目を入力してください。")

    return redirect('admin/home')


# 受信した通知を表示するビュー
def view_notification(request):
    if 'empid' not in request.session:
        return redirect('login')

    employee = Employee.objects.get(empid=request.session['empid'])
    notification = employee.received_notifications.all().order_by('-created_at')

    return render(request, 'admin/notification.html', {'notification': notification})


def attendance_date(request):
    attendance = Attendance.objects.get(patid=request.POST['patid'])
    attendance_record = Attendance.objects.filter(employee=attendance).order_by('date')

    return render(request, 'Attendance_date.html', {'attendance_record': attendance_record, 'attendance': attendance})



