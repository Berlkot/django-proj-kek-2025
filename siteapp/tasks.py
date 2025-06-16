# siteapp/tasks.py
from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

from .models import Advertisement, AdStatus, User
from datetime import timedelta

@shared_task
def archive_old_advertisements() -> str:
    """
    Архивирует объявления, которые находятся в завершенном статусе
    более 30 дней.
    
    Завершенные статусы: "Найдено владельцем", "Передано владельцу", "В архиве".
    """
    try:
        archive_status, _ = AdStatus.objects.get_or_create(name="В архиве")
        # Статусы, после которых можно архивировать
        completed_statuses = AdStatus.objects.filter(
            name__in=["Найдено владельцем", "Передано владельцу"]
        )
        
        # Дата, раньше которой объявления считаются старыми
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        # Находим объявления для архивации
        ads_to_archive = Advertisement.objects.filter(
            status__in=completed_statuses,
            publication_date__lt=thirty_days_ago
        )
        
        count = ads_to_archive.count()
        if count > 0:
            ads_to_archive.update(status=archive_status)
            result = f"Successfully archived {count} old advertisements."
        else:
            result = "No old advertisements to archive."
            
        print(result)
        return result
    except AdStatus.DoesNotExist:
        error_msg = "Error: Could not find required AdStatus objects."
        print(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        print(error_msg)
        return error_msg


@shared_task
def send_weekly_digest() -> str:
    """
    Отправляет еженедельный дайджест администраторам сайта.
    """
    try:
        # Находим всех администраторов
        admins = User.objects.filter(is_staff=True)
        admin_emails = [admin.email for admin in admins if admin.email]

        if not admin_emails:
            return "No admin users with emails found to send digest."

        # Собираем статистику за последнюю неделю
        one_week_ago = timezone.now() - timedelta(weeks=1)
        new_ads_count = Advertisement.objects.filter(publication_date__gte=one_week_ago).count()
        new_users_count = User.objects.filter(date_joined__gte=one_week_ago).count()
        
        context = {
            'new_ads_count': new_ads_count,
            'new_users_count': new_users_count,
            'report_date': timezone.now().strftime('%d.%m.%Y'),
        }

        # Рендерим HTML-шаблон письма
        html_message = render_to_string('emails/weekly_digest.html', context)
        
        send_mail(
            subject='Еженедельный отчет по сайту "СпасиЗверя"',
            message=f"Новых объявлений: {new_ads_count}. Новых пользователей: {new_users_count}.", # Plain text fallback
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=admin_emails,
            html_message=html_message, # HTML-версия письма
            fail_silently=False,
        )
        
        result = f"Weekly digest sent to {len(admin_emails)} admins."
        print(result)
        return result

    except Exception as e:
        error_msg = f"Failed to send weekly digest: {e}"
        print(error_msg)
        return error_msg