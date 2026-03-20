from django.shortcuts import render
from django.http import HttpResponse
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from collections import Counter
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader


def home(request):

    notes_text = ""
    important_sentences = []
    summary_text = ""
    concepts = []

    if request.method == "POST":

        notes_text = request.POST.get("notes", "")

        # PDF Upload Handling
        if 'pdf_file' in request.FILES and request.FILES['pdf_file']:

            pdf_file = request.FILES['pdf_file']
            reader = PdfReader(pdf_file)

            notes_text = ""

            for page in reader.pages:
                text = page.extract_text()
                if text:
                    notes_text += text

        # PROCESS ONLY IF TEXT EXISTS
        if notes_text.strip():

            sentences = sent_tokenize(notes_text)
            words = word_tokenize(notes_text.lower())

            stop_words = set(stopwords.words("english"))

            filtered_words = []

            for word in words:
                if word.isalnum() and word not in stop_words:
                    filtered_words.append(word)

            word_freq = Counter(filtered_words)

            # Concepts
            concepts = [word for word, freq in word_freq.most_common(5)]

            # Sentence scoring
            sentence_scores = {}

            for sentence in sentences:
                for word in word_tokenize(sentence.lower()):
                    if word in word_freq:
                        if sentence not in sentence_scores:
                            sentence_scores[sentence] = word_freq[word]
                        else:
                            sentence_scores[sentence] += word_freq[word]

            important_sentences = sorted(
                sentence_scores,
                key=sentence_scores.get,
                reverse=True
            )[:3]

            summary_text = " ".join(important_sentences)

    return render(request, "home.html", {
        "notes": notes_text,
        "points": important_sentences,
        "summary": summary_text,
        "concepts": concepts
    })


# PDF DOWNLOAD FUNCTION
def download_pdf(request):

    summary = request.GET.get("summary", "")

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="learnlens_summary.pdf"'

    p = canvas.Canvas(response)

    p.setFont("Helvetica", 12)

    y = 800

    for line in summary.split("."):
        if line.strip():
            p.drawString(50, y, line.strip())
            y -= 20

    p.save()

    return response
