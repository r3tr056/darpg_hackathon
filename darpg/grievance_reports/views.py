from reportlab.pdfgen import canvas

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from django.urls import reverse

from authentication.decorators import only_authenticated_user, redirect_authenticated_user, reviewer_required
from .forms import GrievanceReportForm
from .models import GrievanceReport

blog = {
    'category':'Railways Customer Service',
    'category_code': '1225',
    'title': 'Unavailability of Reserved Seating on Train XYZ - Booking ID: 123456789',
    'username': 'satymevsingh',
    'time': '2024-01-15 00:00:19',
    'content': """I am writing to express my dissatisfaction with the recent experience I encountered while traveling on Train XYZ from Station A to Station B on March 12, 2024. Despite having made a reservation with Booking ID 123456789, I faced significant inconvenience due to the unavailability of reserved seating.

Upon boarding the train at Station A, I proceeded to locate my assigned seat as per the reservation confirmation. However, upon reaching the designated coach and seat, I was dismayed to find that another passenger was occupying the same seat, claiming to have a valid reservation. Despite presenting my ticket and booking details, the situation escalated into a dispute with the other passenger, causing unnecessary delay and discomfort.

Moreover, upon seeking assistance from the onboard staff, I was informed that there were no alternative seats available in the coach, forcing me to stand for a considerable duration of the journey. This not only caused physical discomfort but also posed safety concerns, particularly during peak travel hours.

I find this situation unacceptable and would like to bring it to your attention for immediate resolution. As a paying customer, I expect the railway service to honor reservations and ensure the availability of adequate seating capacity to accommodate passengers as per the booking arrangements. The failure to do so not only reflects poorly on the service quality but also undermines the trust and confidence of passengers in the reliability of the railway system.

I kindly request that appropriate measures be taken to address this issue and prevent similar incidents from occurring in the future. This may include conducting thorough checks to ensure accurate seating allocation, implementing effective communication channels between passengers and staff, and enhancing the capacity management system to avoid overbooking situations.

I trust that you will give prompt attention to this matter and provide a satisfactory resolution at the earliest convenience. Your prompt action in this regard would be greatly appreciated.

Thank you for your attention to this grievance, and I look forward to a favorable response.

""",
}

def portal(request):
    return render(request, "portal_home.html", {})

def chatbot(request):
    return render(request, "chatbot.html", {})

def landing(request):
    return render(request, "landing.html", {})

def process_grievance_report():
    pass

def report(request):
    return render(request, "reports/report.html", {'blog': blog})

@only_authenticated_user
def _portal(request):
    if request.is_reviewer():
        pending_reports = GrievanceReport.object.filter(reviewer=request.user, status=GrievanceReport.PENDING)
        completed_reports = GrievanceReport.objects.filter(reviewer=request.user, status=GrievanceReport.COMPLETED)
    else:
        pending_reports = GrievanceReport.objects.filter(submitter=request.user, status=GrievanceReport.PENDING)
        completed_reports = GrievanceReport.objects.filter(submitter=request.user, status=GrievanceReport.COMPLETED)

    page_data = {
        'username': request.user.username,
        'profile_picture': request.user.profile_picture,
        'bio': request.user.bio,
        'score': request.user.score,
        'role': 'Reviewer' if request.user.is_reviewer() else 'Submitter',
        'pending_reports': pending_reports,
        'completed_reports': completed_reports
    }

    return render(request, 'portal_home.html', {'data': page_data})

@only_authenticated_user
def report_detail(request, report_id):
    if request.is_reviewer():
        report = get_object_or_404(GrievanceReport, id=report_id, reviewer=request.user)
    else:
        report = get_object_or_404(GrievanceReport, id=report_id, submitter=request.user)
    return render(request, 'reports/report.html', {'report': report})

@only_authenticated_user
def submit_grievance(request):
    if request.method == 'POST':
        form = GrievanceReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.submitter = request.user
            report.save()
            # Process the report for topic modelling and routing suggestions
            process_grievance_report(request)
            return redirect('report_list')
    else:
        form = GrievanceReportForm()
    return render(request, 'reports/submit_grievance.html', {'form': form})

def delete_report(request, report_id):
    if request.method == 'POST':
        if request.user.is_authenticated:
            report = get_object_or_404(GrievanceReport, id=report_id, submitter=request.user)
            report.delete()
            return redirect('portal')
        return render(request, 'delete_report_confirmation.html', {'report': report})

@reviewer_required
def share_report(request, report_id):
    report = get_object_or_404(GrievanceReport, id=report_id)
    if request.method == 'POST':
        recipient_email = request.POST.get('recipient_email')
        subject = f"Shared report : {report.title}"
        
        report_html = render_to_string('report_pdf_template.html', {'report': report})

        response = HttpResponse(content_type="application/pdf")
        response['Content-Disposition'] = f'attachment; filename="{report.title}.pdf"'

        p = canvas.Canvas(response)
        p.drawString(100, 800, "Report Title: " + report.title)
        p.drawString(100, 780, "Report Content: " + report.subject_content)
        p.showPage()
        p.save()

        report_url = request.build_absolute_uri(reverse('report_details', kwargs={'id': report_id}))

        email_body = f"Please find the shared report attached.\n\nYou can also view the report online: {report_url}"

        email = EmailMessage(subject, email_body, settings.DEFAULT_FROM_EMAIL, [recipient_email])
        email.attach(f"{report.title}.pdf", response.getvalue(), 'application/pdf')
        email.send()

        return redirect('report_detail', report_id=report_id)
    return render(request, 'share_report.html', {'report': report})