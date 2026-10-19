import flet as ft
import yt_dlp
import os
import threading

def main(page: ft.Page):
    page.title = "دانلودر همه‌کاره"
    page.theme_mode = ft.ThemeMode.DARK
    page.rtl = True  # راست‌چین کردن محیط برنامه برای زبان فارسی
    page.padding = 20
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # مسیر ذخیره در پوشه دانلودهای اندروید
    def get_download_path():
        android_path = "/storage/emulated/0/Download"
        if os.path.exists(android_path):
            return android_path
        return os.path.expanduser("~/Downloads")

    # المان‌های رابط کاربری
    title_text = ft.Text("دانلودر ویدیو و موزیک", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_400)
    
    url_input = ft.TextField(
        label="لینک ویدیو (یوتیوب، اینستاگرام، آپارات و...)",
        hint_text="https://...",
        width=310,
        border_radius=12,
        prefix_icon=ft.icons.LINK
    )

    format_Type = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="video", label="ویدیو (MP4)"),
            ft.Radio(value="audio", label="فقط صدا (M4A)"),
        ], alignment=ft.MainAxisAlignment.CENTER),
        value="video"
    )

    progress_bar = ft.ProgressBar(width=320, value=0, visible=False, color=ft.colors.GREEN_400)
    status_text = ft.Text("آماده برای دانلود", size=14, color=ft.colors.GREY_400)

    # تابع به‌روزرسانی نوار پیشرفت
    def progress_hook(d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded = d.get('downloaded_bytes', 0)
            if total:
                percent = downloaded / total
                progress_bar.value = percent
                status_text.value = f"در حال دانلود... {int(percent * 100)}%"
                status_text.color = ft.colors.BLUE_300
                page.update()
        elif d['status'] == 'finished':
            status_text.value = "در حال ذخیره‌سازی فایل..."
            status_text.color = ft.colors.ORANGE_300
            page.update()

    # تابع اصلی دانلود در پس‌زمینه (همراه با تشخیص هوشمند نیم‌بها)
    def download_worker(url, mode):
        save_path = get_download_path()
        
        # لیست سایت‌های داخلی برای دانلود مستقیم و نیم‌بها
        iranian_domains = ['aparat.com', 'telewebion.com', 'tamasha.com', 'namasha.com', '.ir']
        is_internal = any(domain in url.lower() for domain in iranian_domains)

        if mode == "audio":
            ydl_opts = {
                'format': 'bestaudio[ext=m4a]/bestaudio/best',
                'outtmpl': f'{save_path}/%(title)s.%(ext)s',
                'progress_hooks': [progress_hook],
                'noplaylist': True,
            }
        else:
            ydl_opts = {
                'format': 'best[ext=mp4]/best',
                'outtmpl': f'{save_path}/%(title)s.%(ext)s',
                'progress_hooks': [progress_hook],
                'noplaylist': True,
            }

        # اگر سایت ایرانی بود، پروکسی را نادیده بگیر تا نیم‌بها حساب شود
        if is_internal:
            ydl_opts['proxy'] = ""

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            status_text.value = "✅ دانلود تمام شد! (ذخیره در پوشه Download گوشی)"
            status_text.color = ft.colors.GREEN_400
        except Exception as ex:
            status_text.value = "❌ خطا: مطمئن شوید فیلترشکن روشن است یا لینک معتبر است."
            status_text.color = ft.colors.RED_400
        finally:
            download_btn.disabled = False
            progress_bar.visible = False
            page.update()

    # رویداد کلیک روی دکمه دانلود
    def start_download(e):
        url = url_input.value.strip()
        if not url:
            status_text.value = "⚠️ لطفاً ابتدا لینک را وارد کنید!"
            status_text.color = ft.colors.AMBER_400
            page.update()
            return

        download_btn.disabled = True
        progress_bar.visible = True
        progress_bar.value = None
        status_text.value = "در حال دریافت اطلاعات ویدیو..."
        status_text.color = ft.colors.WHITE
        page.update()

        threading.Thread(target=download_worker, args=(url, format_Type.value), daemon=True).start()

    # دکمه جایگذاری از کلیپ‌بورد
    def paste_link(e):
        clipboard_text = page.get_clipboard()
        if clipboard_text:
            url_input.value = clipboard_text
            page.update()

    paste_btn = ft.IconButton(
        icon=ft.icons.CONTENT_PASTE,
        tooltip="جایگذاری لینک",
        on_click=paste_link
    )

    download_btn = ft.ElevatedButton(
        text="شروع دانلود",
        icon=ft.icons.DOWNLOAD_ROUNDED,
        style=ft.ButtonStyle(
            bgcolor=ft.colors.GREEN_600,
            color=ft.colors.WHITE,
            padding=15,
        ),
        width=250,
        on_click=start_download
    )

    # چیدمان صفحه
    page.add(
        ft.Column(
            [
                ft.Icon(ft.icons.CLOUD_DOWNLOAD_ROUNDED, size=70, color=ft.colors.BLUE_400),
                title_text,
                ft.Container(height=15),
                ft.Row([url_input, paste_btn], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=5),
                format_Type,
                ft.Container(height=15),
                progress_bar,
                status_text,
                ft.Container(height=15),
                download_btn,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )

ft.app(target=main)
