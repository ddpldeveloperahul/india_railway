from django.shortcuts import render

# Create your views here.
import cv2
import numpy as np
import matplotlib.pyplot as plt
from math import sqrt
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from .forms import ImageUploadForm
import os
from rest_framework import viewsets
from .models import Image_database
from .serializers import DatasetSerializer

class DatasetViewSet(viewsets.ModelViewSet):
    queryset = Image_database.objects.all()
    serializer_class = DatasetSerializer

def detect_pulleys(request):
    result_image_url = None
    distances = []

    if request.method == "POST":
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_file = form.cleaned_data["image"]
            fs = FileSystemStorage()
            filename = fs.save(image_file.name, image_file)
            image_path = fs.path(filename)

            img = cv2.imread(image_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray = cv2.medianBlur(gray, 5)

            edges = cv2.Canny(gray, 80, 180)
            gray = cv2.addWeighted(gray, 0.8, edges, 0.2, 0)

            circles = cv2.HoughCircles(
                gray,
                cv2.HOUGH_GRADIENT,
                dp=1.2,
                minDist=100,
                param1=100,
                param2=40,
                minRadius=35,
                maxRadius=90
            )

            centers = []
            radii = []

            if circles is not None:
                circles = np.round(circles[0, :]).astype(np.int32)
                mean_y = np.mean(circles[:, 1])
                for (x, y, r) in circles:
                    if abs(y - mean_y) < 40:
                        centers.append((x, y))
                        radii.append(r)
                        cv2.circle(img, (x, y), r, (255, 0, 0), 2)
                        cv2.circle(img, (x, y), 3, (0, 0, 255), -1)

                centers = sorted(centers, key=lambda x: x[0])

                for i in range(len(centers) - 1):
                    x1, y1 = centers[i]
                    x2, y2 = centers[i + 1]
                    distance = float(sqrt((float(x2) - float(x1)) ** 2 + (float(y2) - float(y1)) ** 2))
                    distances.append(f"Distance between Pulley {i + 1} and Pulley {i + 2}: {distance:.2f} pixels")
                    cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    midx, midy = (x1 + x2) // 2, (y1 + y2) // 2
                    cv2.putText(img, f"{distance:.1f}px", (midx - 30, midy - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

                result_filename = f"result_{filename}"
                result_path = os.path.join(fs.location, result_filename)
                cv2.imwrite(result_path, img)
                result_image_url = fs.url(result_filename)

    else:
        form = ImageUploadForm()

    return render(request, "pulley_app/index.html", {
        "form": form,
        "result_image_url": result_image_url,
        "distances": distances,
    })
