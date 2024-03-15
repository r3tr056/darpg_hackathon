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

# @only_authenticated_user
def portal(request):
    return render(request, "home.html", {})

def chatbot(request):
    return render(request, "chatbot.html", {})

def landing(request):
    return render(request, "landing.html", {})

def process_grievance_report():
    pass

def report(request):
    return render(request, "reports/report.html", {})

@only_authenticated_user
def portal(request):
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