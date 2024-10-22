from django.utils import timezone  # timezoneをインポート

from django.db import models


# Create your models here.
class Employee(models.Model):
    empid = models.CharField(max_length=8, primary_key=True)  # 自動生成される従業員ID
    fname = models.CharField(max_length=50)      # 名
    lname = models.CharField(max_length=50)       # 姓
    email = models.EmailField(unique=True)      # メールアドレス（ユニーク）
    emppasswd = models.CharField(max_length=256, default='password')    # パスワード
    role = models.IntegerField()       # 役職
    department = models.CharField(max_length=100)     # 部署
    hire_date = models.DateField()                    # 入社日


class Attendance(models.Model):
    Attendance_id = models.AutoField(primary_key=True)
    empid = models.ForeignKey(Employee, on_delete=models.CASCADE)    # 従業員に対する外部キー
    clock_in_time = models.DateTimeField()  # 出勤時間
    clock_out_time = models.DateTimeField(null=True, blank=True)  # 退勤時間 # 退勤時間はまだ設定されていない可能性がある
    break_in_time = models.DateTimeField(null=True, blank=True)  # 休憩開始時間
    break_out_time = models.DateTimeField(null=True, blank=True)  # 休憩終了時間
    date = models.DateField()   # 日付
    created_at = models.DateTimeField(auto_now_add=True)    # レコード作成日時
    updated_at = models.DateTimeField(auto_now=True)    # レコード更新日時


class ContactRequest(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)  # 従業員への外部キー
    request_type = models.CharField(max_length=50)  # リクエストの種類（出勤時間修正、退勤時間修正など）
    message = models.TextField()  # リクエストのメッセージ
    created_at = models.DateTimeField(auto_now_add=True)  # 作成日時
    status = models.CharField(max_length=20, default='申請中')  # ステータス（申請中、承認、却下）


class LeaveRequest(models.Model):
    Leave_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE)  # 従業員に対する外部キー
    leave_type = models.CharField(max_length=20)  # 休暇の種類（例: 有給、特別休暇）
    start_date = models.DateField()  # 休暇の開始日
    end_date = models.DateField()  # 休暇の終了日
    reason = models.TextField()  # 休暇の理由

    # 追加部分: 休暇申請の状態を表すフィールド
    status = models.CharField(
        max_length=20,
        choices=[('pending', '承認待ち'), ('approved', '承認済み'), ('rejected', '却下')],  # 状態の選択肢
        default='pending'  # 初期値は「承認待ち」
    )

    created_at = models.DateTimeField(auto_now_add=True)  # 申請作成日時


class Notification(models.Model):
    sender = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, related_name='sent_notifications')  # 通知の送信者
    recipient = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name='received_notifications')  # 通知の受信者
    message = models.TextField()  # 通知のメッセージ内容
    created_at = models.DateTimeField(default=timezone.now)  # 通知が送信された日時



