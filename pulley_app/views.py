from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .forms import SignupForm, LoginForm,PasswordChangeForm
from .models import CustomUser,profile
import cv2
from ultralytics import YOLO  # pyright: ignore[reportMissingImports]
import os
import math
import numpy as np
from django.contrib import messages
import matplotlib.pyplot as plt
from math import sqrt
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from pulley_app.forms import ImageUploadForm,ProfileForm
import os
from .models import PulleyDetection
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password
import time
import threading
from django.http import StreamingHttpResponse, JsonResponse
from django.utils import timezone
from django.conf import settings
from pathlib import Path
import json
from .models import DetectionRecord
# Create your views here.
# yolo_camera.py



def main_view(request):
    return render(request, 'pulley_app/railways.html')


def railway_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        return render(request, 'pulley_app/buttons2.html')
def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            # user = CustomUser.objects.create_user(
            #     email=form.cleaned_data['email'],
            #     username=form.cleaned_data['username'],
            #     employee_id=form.cleaned_data['employee_id'],
            #     password=form.cleaned_data['password']
            # )
            # user = form.save(commit=False)
            form.save()
            # messages.success(request, "Signup successful! Please log in.")
            return redirect('login')
        else:
            # messages.error(request, "Please correct the errors below.")
            # print("form.errors",form.errors)
            pass
    else:
        form = SignupForm()
    return render(request, 'pulley_app/signup.html',{'form': form})


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        # print("email,password",email,password)
        # ✅ Authenticate using email
        user = authenticate(request, email=email, password=password)
        # print("useremailakdjfkj",user,email)
        if user is not None:
            login(request, user)
            # messages.success(request, "Login successful!")
            return redirect('railway')  # redirect where you want
        else:
            messages.error(request, "Invalid email or password")
      
    return render(request, 'pulley_app/login.html')


# def logout_view(request):
#     if request.method == 'POST':
#         # Only logout when form is submitted (Yes button clicked)
#         logout(request)
#         return redirect('login')
#     else:
#         # Show confirmation page on GET request
#         return render(request, 'pulley_app/logout.html')
def logout_view(request):
    logout(request)
    return redirect('login')

def change_password_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Password changed successfully!")
            # return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'pulley_app/changepassword.html', {'form': form})

def profile_form_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile created successfully!")
            return redirect('profile')
    else:
        form = ProfileForm()
    return render(request, 'pulley_app/profile_form.html', {'form': form})

def profile_view(request):
    if request.user.is_authenticated:
        profile_data =profile.objects.get(user=request.user)
        
    return render(request, 'pulley_app/profile2.html',{'profile': profile_data})
def all_data_view(request):
    detectections = PulleyDetection.objects.all().order_by('-id')
    return render(request, 'pulley_app/list_olddata.html', {'detections': detectections})


def result_data_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    detections = PulleyDetection.objects.filter(user=request.user).order_by('-created_at')
    # print(detections)
    return render(request, 'pulley_app/list_olddata.html', {'detections': detections})

def all_data_view_for_camera(request):
    detectections = DetectionRecord.objects.all().order_by('-id')
    return render(request, 'pulley_app/data_camera.html', {'detections': detectections})

def result_data_view_for_camera(request):
    if not request.user.is_authenticated:
        return redirect('login')
    detections = DetectionRecord.objects.filter(user=request.user).order_by('-created_at')
    # print(detections)
    return render(request, 'pulley_app/data_camera.html', {'detections': detections})

def demo_video_view(request):
    return render(request, 'pulley_app/demovideo.html')


def detect_pulleys(request):
    # Initialize outputs to avoid UnboundLocalError in non-POST or early-exit paths
    out_path = None
    info_lines = []
    result_url = None
    # result_image_url = None
    # distances = []
    if request.method == "POST":
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_file = form.cleaned_data["image"]
            print("image_file",image_file)
            MODEL_PATH = "C://Users//Dell Pc//Desktop//Yolo2//PulleyDetector//ai//runs//detect//yolov11m-custom//weights//best.pt"
            uploads_storage = FileSystemStorage(
                location=os.path.join(settings.MEDIA_ROOT, 'uploads'),
                base_url=settings.MEDIA_URL + 'uploads/'
            )
            results_storage = FileSystemStorage(
                location=os.path.join(settings.MEDIA_ROOT, 'results'),
                base_url=settings.MEDIA_URL + 'results/'
            )
            filename = uploads_storage.save(image_file.name, image_file)
            IMAGE_PATH = uploads_storage.path(filename)
            # IMAGE_PATH = "D://yolo_model_trian//1.jpg"  # change to your image path
            MM_PER_PIXEL = 1.0  # set your real-world scale (millimeters per pixel)
            # Thermal compensation defaults (total first->third distance)
            BASE_TEMPERATURE_C = 35.0
            STANDARD_TOTAL_DISTANCE_MM = 1300.0  # reference "standard" used for loss computation (1300 - total)
            TEMPERATURE_SENSITIVITY_MM_PER_C = 0.5  # legacy fallback if HTL missing
            HTL_COEFFICIENT = 0.017  # multiplier for HTL-based adjustment
            HTL_MIN = 200.0
            HTL_MAX = 800.0
            # Take temperature from user input; fallback to default if missing
            temp_raw = form.cleaned_data.get("temperature")
            CURRENT_TEMPERATURE_C = float(temp_raw) if temp_raw is not None else 35.0  # °C
            htl_raw = form.cleaned_data.get("htl")
            htl_value = float(htl_raw) if htl_raw is not None else None
            if htl_value is None:
                raise ValueError("HTL value is required.")
            htl_value = float(htl_value)
            if not (HTL_MIN <= htl_value <= HTL_MAX):
                raise ValueError(f"HTL value must be between {HTL_MIN} and {HTL_MAX}.")

            # Chart-based values for total distance X (1->3) vs temperature (°C).
            # Fill this with rows from your chart (Temp row → corresponding total X in mm).
            # If exact temperature isn't present, we will interpolate between surrounding keys.
            # Example starter data (edit/extend these according to your table):
            TEMP_TO_TOTAL_DISTANCE_MM = {
                10.0: 1385.0,
                15.0: 1368.0,
                20.0: 1351.0,
                21.0: 1348.0,
                22.0: 1344.0,
                23.0: 1341.0,
                24.0: 1337.0,
                25.0: 1334.0,
                26.0: 1331.0,
                27.0: 1327.0,
                28.0: 1324.0,
                29.0: 1320.0,
                30.0: 1317.0,
                31.0: 1314.0,
                32.0: 1310.0,
                33.0: 1307.0,
                34.0: 1303.0,
                35.0: 1300.0,
                36.0: 1297.0,
                37.0: 1293.0,
                38.0: 1290.0,
                39.0: 1286.0,
                40.0: 1283.0,
                41.0: 1280.0,
                42.0: 1276.0,
                43.0: 1273.0,
                44.0: 1269.0,
                45.0: 1266.0,
                50.0: 1249.0,
            }

            # Ratio assumptions for a 3:1 pulley layout (first->second, second->third)
            DISTANCE_RATIO_12 = 0.75
            DISTANCE_RATIO_23 = 0.25
            # NUMBERING_SIDE = "left"  # choose "left" (default) or "right" to start numbering from that side


            model = YOLO(MODEL_PATH)

            results = model.predict(source=IMAGE_PATH, save=True, verbose=False)
            if not results:
                raise RuntimeError("No results returned by the model.")

            result = results[0]
            if result.boxes is None or len(result.boxes) == 0:
                raise RuntimeError("No detections found in the image.")

            names = result.names if hasattr(result, "names") else model.names
            boxes = result.boxes
            cls_indices = boxes.cls.cpu().numpy().astype(int)
            xyxy = boxes.xyxy.cpu().numpy()

            # Collect pulley centers
            pulley_points = []
            for i, c in enumerate(cls_indices):
                label = names.get(int(c), str(c)) if isinstance(names, dict) else names[int(c)]
                if str(label).lower() == "pulley":
                    x1, y1, x2, y2 = xyxy[i]
                    cx = (x1 + x2) / 2.0
                    cy = (y1 + y2) / 2.0
                    pulley_points.append((cx, cy))

            if len(pulley_points) < 2:
                raise RuntimeError("Found fewer than 2 pulleys. Need at least 2 to compute distance.")

            # Sort left-to-right to define first, second, third
            pulley_points.sort(key=lambda p: p[0])
            p1 = pulley_points[0] if len(pulley_points) >= 1 else None
            p2 = pulley_points[1] if len(pulley_points) >= 2 else None
            p3 = pulley_points[2] if len(pulley_points) >= 3 else None

            # Load image for drawing
            img = cv2.imread(IMAGE_PATH)
            if img is None:
                raise RuntimeError(f"Failed to load image: {IMAGE_PATH}")

            # Draw points
            for (cx, cy) in pulley_points:
                cv2.circle(img, (int(cx), int(cy)), 6, (0, 255, 0), -1)
            # Draw pulley indices (1, 2, 3) next to centers
            for idx, (cx, cy) in enumerate(pulley_points, start=1):
                cv2.putText(
                    img,
                    f"{idx}",
                    (int(cx) + 8, int(cy) - 8),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (0, 255, 255),
                    2,
                    cv2.LINE_AA
                )

            def pixel_distance(p1, p2):
                return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

            def _chart_total_distance(temp_c):
                """
                Return chart-based total distance X for temperature (with linear interpolation).
                If the chart has no data, return None.
                """
                if not TEMP_TO_TOTAL_DISTANCE_MM:
                    return None
                # Exact hit
                if temp_c in TEMP_TO_TOTAL_DISTANCE_MM:
                    return float(TEMP_TO_TOTAL_DISTANCE_MM[temp_c])
                # Find neighbors for interpolation
                keys = sorted(TEMP_TO_TOTAL_DISTANCE_MM.keys())
                if temp_c <= keys[0]:
                    return float(TEMP_TO_TOTAL_DISTANCE_MM[keys[0]])
                if temp_c >= keys[-1]:
                    return float(TEMP_TO_TOTAL_DISTANCE_MM[keys[-1]])
                lower = None
                upper = None
                for k in keys:
                    if k < temp_c:
                        lower = k
                    elif k > temp_c:
                        upper = k
                        break
                if lower is None or upper is None:
                    return None
                x0 = lower
                y0 = float(TEMP_TO_TOTAL_DISTANCE_MM[lower])
                x1 = upper
                y1 = float(TEMP_TO_TOTAL_DISTANCE_MM[upper])
                ratio = (temp_c - x0) / (x1 - x0)
                return y0 + ratio * (y1 - y0)

            def expected_total_distance_for_temperature(temp_c, htl=None):
                """
                Compute expected total pulley distance (1->3) in mm for the given temperature.
                Priority: use HTL-based formula. If unavailable, use chart values, otherwise linear fallback.
                """
                if htl is not None:
                    delta_t = temp_c - BASE_TEMPERATURE_C
                    adjustment = (htl * HTL_COEFFICIENT) * abs(delta_t)
                    if delta_t > 0:
                        return STANDARD_TOTAL_DISTANCE_MM - adjustment
                    if delta_t < 0:
                        return STANDARD_TOTAL_DISTANCE_MM + adjustment
                    return STANDARD_TOTAL_DISTANCE_MM

                chart_value = _chart_total_distance(temp_c)
                if chart_value is not None:
                    return chart_value
                delta_t = temp_c - BASE_TEMPERATURE_C
                return STANDARD_TOTAL_DISTANCE_MM - TEMPERATURE_SENSITIVITY_MM_PER_C * delta_t

            def temperature_from_total_distance(distance_mm):
                """
                Estimate temperature (°C) from a measured total pulley distance 1->3.
                """
                delta_d = STANDARD_TOTAL_DISTANCE_MM - distance_mm
                return BASE_TEMPERATURE_C + (delta_d / TEMPERATURE_SENSITIVITY_MM_PER_C)

            def split_total_distance(distance_mm):
                """
                Split total 1->3 distance into 1->2 and 2->3 spans using configured ratios.
                """
                return (
                    distance_mm * DISTANCE_RATIO_12,
                    distance_mm * DISTANCE_RATIO_23
                )

            dist12_mm = None
            dist23_mm = None

            # Compute and draw 1->2
            if p1 is not None and p2 is not None:
                d_px = pixel_distance(p1, p2)
                dist12_mm = 1.6*d_px * MM_PER_PIXEL
                cv2.line(img, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), (0, 0, 255), 2)
                mid12 = (int((p1[0] + p2[0]) / 2), int((p1[1] + p2[1]) / 2))
                cv2.putText(img, f"{dist12_mm:.2f} mm", mid12, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)

            # Compute and draw 2->3
            total_distance_mm = None

            if p2 is not None and p3 is not None:
                d_px = pixel_distance(p2, p3)
                dist23_mm = 1.6*d_px * MM_PER_PIXEL
                cv2.line(img, (int(p2[0]), int(p2[1])), (int(p3[0]), int(p3[1])), (255, 0, 0), 2)
                mid23 = (int((p2[0] + p3[0]) / 2), int((p2[1] + p3[1]) / 2))
                cv2.putText(img, f"{dist23_mm:.2f} mm", mid23, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2, cv2.LINE_AA)

            if dist12_mm is not None and dist23_mm is not None:
                total_distance_mm = dist12_mm + dist23_mm

            expected_total_db = None
            loss_mm_db = None

            if total_distance_mm is not None and TEMPERATURE_SENSITIVITY_MM_PER_C > 0 and p1 is not None and p3 is not None:
                expected_total = expected_total_distance_for_temperature(CURRENT_TEMPERATURE_C, htl_value)
                expected_dist12, expected_dist23 = split_total_distance(expected_total)
                estimated_temp = temperature_from_total_distance(total_distance_mm)
                loss_mm = expected_total - total_distance_mm
                expected_total_db = expected_total
                loss_mm_db = loss_mm
                info_lines = [
                    f"Temperature: {CURRENT_TEMPERATURE_C:.1f} °C",
                    f"HTL (L/2): {htl_value:.1f}",
                    f"Pulley 1->Pulley 2: {dist12_mm:.3f} mm",
                    f"Pulley 2->Pulley 3: {dist23_mm:.3f} mm",
                    f"Total distance (1->3): {total_distance_mm:.3f} mm",
                    f"Expected @ {CURRENT_TEMPERATURE_C:.1f} °C (HTL {htl_value:.1f}): {expected_total:.3f} mm",
                    f"Expected 1->2: {expected_dist12:.3f} mm | 2->3: {expected_dist23:.3f} mm",
                    f"Loss vs expected:{CURRENT_TEMPERATURE_C:.1f} °C: {expected_total:.3f} mm - {total_distance_mm:.3f} mm = {loss_mm:.3f} mm",
                    # f"Estimated temperature: {estimated_temp:.2f} C"
                ]
                text_y = int(min(p1[1], p3[1]) - 10)
                for line in info_lines:
                    cv2.putText(
                        img,
                        line,
                        (int((p1[0] + p3[0]) / 2 - 160), max(text_y, 30)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (255, 0, 0),
                        2,
                        cv2.LINE_AA
                    )
                    text_y -= 25

            # Save annotated image under results folder using uploaded filename as base
            uploaded_root, uploaded_ext = os.path.splitext(filename)
            result_filename = f"{uploaded_root}_output{uploaded_ext}"
            out_path = results_storage.path(result_filename)
            print(f"DEBUG: Saving image to: {out_path}")
            cv2.imwrite(out_path, img)
            # Verify file was saved
            if os.path.exists(out_path):
                print(f"DEBUG: Image saved successfully at: {out_path}")
            else:
                print(f"DEBUG: ERROR - Image file not found at: {out_path}")
            # Public URL for template rendering
            result_url = results_storage.url(result_filename)
            print(f"DEBUG: Result image URL: {result_url}")
            print(f"DEBUG: Full URL would be: {request.build_absolute_uri(result_url)}")
            # cv2.imshow("output",img)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()

            # Print distances
            print(f"HTL (L/2) value: {htl_value:.1f}")
            if dist12_mm is not None:
                print(f"Distance first->second pulley: {dist12_mm:.3f} mm (scale {MM_PER_PIXEL} mm/px)")
            if dist23_mm is not None:
                print(f"Distance second->third pulley: {dist23_mm:.3f} mm (scale {MM_PER_PIXEL} mm/px)")
            if total_distance_mm is not None and TEMPERATURE_SENSITIVITY_MM_PER_C > 0:
                expected_total = expected_total_distance_for_temperature(CURRENT_TEMPERATURE_C, htl_value)
                expected_dist12, expected_dist23 = split_total_distance(expected_total)
                estimated_temp = temperature_from_total_distance(total_distance_mm)
                loss_mm = expected_total - total_distance_mm
                print(f"Expected total distance (1->3) at {CURRENT_TEMPERATURE_C:.1f} °C with HTL {htl_value:.1f}: {expected_total:.3f} mm")
                print(f"Expected split: 1->2 = {expected_dist12:.3f} mm, 2->3 = {expected_dist23:.3f} mm")
                print(f"Measured total distance (1->3): {total_distance_mm:.3f} mm")
                print(f"Loss vs expected:{CURRENT_TEMPERATURE_C:.1f} °C: {expected_total:.3f} mm - {total_distance_mm:.3f} mm = {loss_mm:.3f} mm")
                # print(f"Estimated temperature from measured total: {estimated_temp:.3f} °C")
            if len(pulley_points) < 3:
                print("Only two pulleys detected; third-to-second distance not computed.")
            print(f"Annotated image saved to: {out_path}")

            # Save to model
            try:
                distance_summary = ""
                if dist12_mm is not None:
                    distance_summary += f"Pulley 1->2: {dist12_mm:.3f} mm | "
                if dist23_mm is not None:
                    distance_summary += f"Pulley 2->3: {dist23_mm:.3f} mm | "
                if total_distance_mm is not None:
                    distance_summary += f"Total: {total_distance_mm:.3f} mm | "
                if expected_total_db is not None:
                    distance_summary += (
                        f"Standard (HTL {htl_value:.0f}) @ {CURRENT_TEMPERATURE_C:.1f}°C: {expected_total_db:.3f} mm | "
                        f"Diff: {loss_mm_db:.3f} mm"
                    )
                distance_summary = distance_summary.rstrip(" | ")

                PulleyDetection.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    uploaded_image=f"uploads/{filename}",
                    result_image=f"results/{result_filename}",
                    temperature_c=CURRENT_TEMPERATURE_C,
                    htl_value=htl_value,
                    dist_p1_p2=dist12_mm,
                    dist_p2_p3=dist23_mm,
                    total_distance=total_distance_mm,
                    expected_total=expected_total_db,
                    loss_mm=loss_mm_db,
                    distances=distance_summary
                )
            except Exception as e:
                print(f"Warning: failed to save PulleyDetection record: {e}")
    else:
        form = ImageUploadForm()

    return render(request, "pulley_app/upload.html", {
        "form": form,
        "result_image_url": result_url,
        "distances": info_lines,
    })

# Global storage for detection results (thread-safe with locks)
detection_data = {
    'dist12': None,
    'dist23': None,
    'total': None,
    'points': [],
    'confidences': [],
    'expected_total': None,
    'expected_dist12': None,
    'expected_dist23': None,
    'loss_mm': None,
    'pulley_count': 0,
    'frame_available': False,
    'last_update': None,
    'latest_frame': None
}
detection_lock = threading.Lock()
camera_cap = None
camera_running = False

def bookings_view(request):
        if not request.user.is_authenticated:
            return redirect('login')
        else:
            return render(request,'pulley_app/bookings.html')
        # response = render(request, 'pulley_app/bookings.html')
        # response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        # response['Pragma'] = 'no-cache'
        # response['Expires'] = '0'
        # return response

def services_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    response = render(request, 'pulley_app/services.html')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

def support_view(request):
    """Support and Settings page - requires login"""
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'pulley_app/support.html')

def calculator_view(request):
    """Calculator page - requires login"""
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'pulley_app/calculator.html')
def calculator_buttons_view(request):
    """Calculator Buttons page - requires login"""
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'pulley_app/calcbuttons.html')
def pulley_calculator_views(request):
    return render(request, 'pulley_app/pulley_calculator.html')
def employees_view(request):
    """Employee management page - requires login and staff access"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Get all users/employees
    employees = CustomUser.objects.all().order_by('-date_joined')
    
    # Count active users
    active_count = CustomUser.objects.filter(is_active=True).count()
    
    context = {
        'employees': employees,
        'active_count': active_count,
    }
    
    return render(request, 'pulley_app/employees.html', context)

def chooes_your_database_view(request):
    return render(request, 'pulley_app/buttonimg.html')

#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888


#second sections------------------------------------------------------------------------------
CAPTURE_SUBDIR = Path("best_captures")
MEDIA_ROOT = Path(getattr(settings, "MEDIA_ROOT", Path(settings.BASE_DIR) / "media"))
BEST_CAPTURE_DIR = MEDIA_ROOT / CAPTURE_SUBDIR


def _default_detection_state():
    return {
        'dist12': None,
        'dist23': None,
        'total': None,
        'points': [],
        'confidences': [],
        'expected_total': None,
        'expected_dist12': None,
        'expected_dist23': None,
        'loss_mm': None,
        'pulley_count': 0,
        'frame_available': False,
        'last_update': None,
        'latest_frame': None,
        'capture_complete': False,
        'capture_image_path': None,
    }


# Global storage for detection results (thread-safe with locks)
detection_data = _default_detection_state()
detection_lock = threading.Lock()
camera_cap = None
camera_running = False


def reset_detection_state():
    """Return detection storage to its initial blank state."""
    with detection_lock:
        detection_data.clear()
        detection_data.update(_default_detection_state())

def stop_camera_feed():
    """Stop and release the camera safely."""
    global camera_cap, camera_running
    with detection_lock:
        camera_running = False
        if camera_cap is not None:
            try:
                camera_cap.release()
            except Exception:
                pass
            camera_cap = None

def save_detection_frame(frame):
    """Persist an annotated frame to disk and return the media-relative path."""
    if frame is None:
        return None
    try:
        BEST_CAPTURE_DIR.mkdir(parents=True, exist_ok=True)
        filename = f"detection_{int(time.time())}.jpg"
        file_path = BEST_CAPTURE_DIR / filename
        cv2.imwrite(str(file_path), frame)
        return (CAPTURE_SUBDIR / filename).as_posix()
    except Exception as exc:
        print(f"Error saving detection frame: {exc}")
        return None










# optonal second part of project-----------------------------------------------------------------------------------------
# yolo_camera.py
CAPTURE_SUBDIR = Path("best_captures")
MEDIA_ROOT = Path(getattr(settings, "MEDIA_ROOT", Path(settings.BASE_DIR) / "media"))
BEST_CAPTURE_DIR = MEDIA_ROOT / CAPTURE_SUBDIR
REFERENCE_LABELS = ("poll", "pole", "counter weight")
MODEL_PATH = Path("C://Users//Dell Pc//Desktop//new railway//myvideodetectections//ai//runs//detect//yolov11m-custom//weights//best.pt")
_yolo_model = None
_model_lock = threading.Lock()


def _default_detection_state():
    return {
        'dist12': None,
        'dist23': None,
        'total': None,
        'points': [],
        'confidences': [],
        'segments': [],
        'expected_total': None,
        'expected_dist12': None,
        'expected_dist23': None,
        'loss_mm': None,
        'pulley_count': 0,
        'frame_available': False,
        'last_update': None,
        'latest_frame': None,
        'capture_complete': False,
        'capture_image_path': None,
        'capture_requested': False,
    }


# Global storage for detection results (thread-safe with locks)
detection_data = _default_detection_state()
detection_lock = threading.Lock()
camera_cap = None
camera_running = False


def reset_detection_state():
    """Return detection storage to its initial blank state."""
    with detection_lock:
        detection_data.clear()
        detection_data.update(_default_detection_state())


def stop_camera_feed():
    """Stop and release the camera safely."""
    global camera_cap, camera_running
    with detection_lock:
        camera_running = False
        if camera_cap is not None:
            try:
                camera_cap.release()
            except Exception:
                pass
            camera_cap = None


def _get_yolo_model():
    global _yolo_model
    with _model_lock:
        if _yolo_model is None:
            _yolo_model = YOLO(str(MODEL_PATH))
    return _yolo_model


def save_detection_frame(frame):
    """Persist an annotated frame to disk and return the media-relative path."""
    if frame is None:
        return None
    try:
        BEST_CAPTURE_DIR.mkdir(parents=True, exist_ok=True)
        filename = f"detection_{int(time.time())}.jpg"
        file_path = BEST_CAPTURE_DIR / filename
        cv2.imwrite(str(file_path), frame)
        return (CAPTURE_SUBDIR / filename).as_posix()
    except Exception as exc:
        print(f"Error saving detection frame: {exc}")
        return None

def index(request):
    return render(request, 'index.html')

def yolo_camera(request):
    if request.GET.get('restart') == '1':
        stop_camera_feed()
        existing_thread = getattr(yolo_camera, "_detection_thread", None)
        if existing_thread and existing_thread.is_alive():
            try:
                existing_thread.join(timeout=0.5)
            except Exception:
                pass
        reset_detection_state()
        yolo_camera._detection_thread = None

    MM_PER_PIXEL = 1.0  # update with your calibration value
    CONF_THRES = 0.25
    IOU_THRES = 0.45
    IMAGE_SZ = 640

    # Thermal / expected distance configuration
    BASE_TEMPERATURE_C = 35.0
    STANDARD_TOTAL_DISTANCE_MM = 1300.0
    TEMPERATURE_SENSITIVITY_MM_PER_C = 0.5
    CURRENT_TEMPERATURE_C = 31.0  # update with actual measurement

    # Ratio assumptions for a 3:1 pulley layout (first->second, second->third)
    DISTANCE_RATIO_12 = 0.75
    DISTANCE_RATIO_23 = 0.25

    # Chart lookup for expected total distance (1->3) vs temperature
    TEMP_TO_TOTAL_DISTANCE_MM = {
        10.0: 1385.0,
        15.0: 1368.0,
        20.0: 1351.0,
        21.0: 1348.0,
        22.0: 1344.0,
        23.0: 1341.0,
        24.0: 1337.0,
        25.0: 1334.0,
        26.0: 1331.0,
        27.0: 1327.0,
        28.0: 1324.0,
        29.0: 1320.0,
        30.0: 1317.0,
        31.0: 1314.0,
        32.0: 1310.0,
        33.0: 1307.0,
        34.0: 1303.0,
        35.0: 1300.0,
        36.0: 1297.0,
        37.0: 1293.0,
        38.0: 1290.0,
        39.0: 1286.0,
        40.0: 1283.0,
        41.0: 1280.0,
        42.0: 1276.0,
        43.0: 1273.0,
        44.0: 1269.0,
        45.0: 1266.0,
        50.0: 1249.0,
    }


    def _collect_label_centers(result, label_names):
        names = result.names if hasattr(result, "names") else result.model.names
        if result.boxes is None or len(result.boxes) == 0:
            return [], []
        boxes = result.boxes
        cls_indices = boxes.cls.cpu().numpy().astype(int)
        xyxy = boxes.xyxy.cpu().numpy()
        conf = boxes.conf.cpu().numpy() if hasattr(boxes, "conf") else None
        target_names = {label.lower() for label in label_names}
        points = []
        confidences = []
        for i, c in enumerate(cls_indices):
            if conf is not None and conf[i] < CONF_THRES:
                continue
            label = names.get(int(c), str(c)) if isinstance(names, dict) else names[int(c)]
            if str(label).lower() in target_names:
                x1, y1, x2, y2 = xyxy[i]
                cx = (x1 + x2) / 2.0
                cy = (y1 + y2) / 2.0
                points.append((cx, cy))
                confidences.append(float(conf[i]) if conf is not None else 1.0)
        return points, confidences

    def _select_reference_point(result):
        ref_points, ref_confidences = _collect_label_centers(result, REFERENCE_LABELS)
        if not ref_points:
            return None
        best_idx = max(range(len(ref_points)), key=lambda idx: ref_confidences[idx] if idx < len(ref_confidences) else 0.0)
        return ref_points[best_idx]

    def _order_points(points, confidences, reference_point):
        if not points:
            return points, confidences
        if reference_point is None:
            order = sorted(range(len(points)), key=lambda idx: points[idx][0])
        else:
            order = sorted(
                range(len(points)),
                key=lambda idx: math.hypot(points[idx][0] - reference_point[0], points[idx][1] - reference_point[1])
            )
        ordered_points = [points[idx] for idx in order]
        ordered_confidences = [confidences[idx] for idx in order]
        return ordered_points, ordered_confidences

    def get_pulley_centers(result):
        reference_point = _select_reference_point(result)
        points, confidences = _collect_label_centers(result, ("pulley",))
        points, confidences = _order_points(points, confidences, reference_point)
        return points, confidences, reference_point


    def pixel_distance(p1, p2):
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


    def _chart_total_distance(temp_c):
        if not TEMP_TO_TOTAL_DISTANCE_MM:
            return None
        if temp_c in TEMP_TO_TOTAL_DISTANCE_MM:
            return float(TEMP_TO_TOTAL_DISTANCE_MM[temp_c])
        keys = sorted(TEMP_TO_TOTAL_DISTANCE_MM.keys())
        if temp_c <= keys[0]:
            return float(TEMP_TO_TOTAL_DISTANCE_MM[keys[0]])
        if temp_c >= keys[-1]:
            return float(TEMP_TO_TOTAL_DISTANCE_MM[keys[-1]])
        lower = None
        upper = None
        for k in keys:
            if k < temp_c:
                lower = k
            elif k > temp_c:
                upper = k
                break
        if lower is None or upper is None:
            return None
        x0 = lower
        y0 = float(TEMP_TO_TOTAL_DISTANCE_MM[lower])
        x1 = upper
        y1 = float(TEMP_TO_TOTAL_DISTANCE_MM[upper])
        ratio = (temp_c - x0) / (x1 - x0)
        return y0 + ratio * (y1 - y0)

    def expected_total_distance_for_temperature(temp_c):
        chart_value = _chart_total_distance(temp_c)
        if chart_value is not None:
            return chart_value
        delta_t = temp_c - BASE_TEMPERATURE_C
        return STANDARD_TOTAL_DISTANCE_MM - TEMPERATURE_SENSITIVITY_MM_PER_C * delta_t


    def split_total_distance(distance_mm):
        return (
            distance_mm * DISTANCE_RATIO_12,
            distance_mm * DISTANCE_RATIO_23,
        )

    def annotate_frame(frame, result):
        annotated = frame.copy()
        points, confidences, reference_point = get_pulley_centers(result)
        boxes = result.boxes
        if boxes is not None:
            cls_indices = boxes.cls.cpu().numpy().astype(int)
            xyxy = boxes.xyxy.cpu().numpy()
            conf = boxes.conf.cpu().numpy() if hasattr(boxes, "conf") else None
            names = result.names if hasattr(result, "names") else result.model.names
            for i, c in enumerate(cls_indices):
                if conf is not None and conf[i] < CONF_THRES:
                    continue
                label = names.get(int(c), str(c)) if isinstance(names, dict) else names[int(c)]
                if str(label).lower() != "pulley":
                    continue
                x1, y1, x2, y2 = map(int, xyxy[i])
                cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
                conf_text = f"{conf[i]:.2f}" if conf is not None else "1.00"
                cv2.putText(annotated, conf_text, (x1, y1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2, cv2.LINE_AA)
        if reference_point is not None:
            ref_x, ref_y = int(reference_point[0]), int(reference_point[1])
            cv2.circle(annotated, (ref_x, ref_y), 10, (0, 165, 255), 2)
            cv2.putText(annotated, "Poll", (ref_x + 10, ref_y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2, cv2.LINE_AA)
        for idx, (cx, cy) in enumerate(points):
            cv2.circle(annotated, (int(cx), int(cy)), 8, (0, 255, 0), -1)
            cv2.circle(annotated, (int(cx), int(cy)), 12, (0, 255, 0), 2)
            label_text = f"P{idx + 1}"
            if idx < len(confidences):
                label_text += f" ({confidences[idx]:.2f})"
            cv2.putText(annotated, label_text, (int(cx) + 15, int(cy)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv2.LINE_AA)

        dist12 = None
        dist23 = None
        total = None
        segment_distances = []
        text_y = 30

        color_palette = [
            (0, 0, 255),
            (255, 0, 0),
            (0, 255, 255),
            (255, 0, 255),
            (0, 255, 0),
        ]

        if len(points) >= 2:
            for idx in range(len(points) - 1):
                p_start = points[idx]
                p_end = points[idx + 1]
                segment_distance = pixel_distance(p_start, p_end) * MM_PER_PIXEL
                segment_distance=segment_distance*2.2
                segment_distances.append(segment_distance)
                print("-----------segment_distance-----------:", segment_distance)
                color = color_palette[idx % len(color_palette)]
                cv2.line(annotated, (int(p_start[0]), int(p_start[1])), (int(p_end[0]), int(p_end[1])), color, 2)
                midpoint = (int((p_start[0] + p_end[0]) / 2), int((p_start[1] + p_end[1]) / 2))
                cv2.putText(annotated, f"{segment_distance:.2f} mm", midpoint,
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2, cv2.LINE_AA)
                cv2.putText(annotated, f"P{idx + 1}->P{idx + 2}: {segment_distance:.2f} mm", (10, text_y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2, cv2.LINE_AA)
                text_y += 28

            total = sum(segment_distances)
            print("-----------------total---------",total)
            if total is not None:
                cv2.putText(annotated, f"P1->P{len(points)} total: {total:.2f} mm", (10, text_y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2, cv2.LINE_AA)
                text_y += 28
                if TEMPERATURE_SENSITIVITY_MM_PER_C > 0:
                    expected_total = expected_total_distance_for_temperature(CURRENT_TEMPERATURE_C)
                    delta = total - expected_total
                    delta_color = (0, 255, 0) if delta >= 0 else (0, 0, 255)
                    cv2.putText(annotated, f"Δ vs standard: {delta:+.2f} mm", (10, text_y),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, delta_color, 2, cv2.LINE_AA)

            if segment_distances:
                dist12 = segment_distances[0]
                print("-----------dist12-----------:", dist12)
            if len(segment_distances) >= 2:
                dist23 = segment_distances[1]
                print("-----------dist23-----------:", dist23)

        height = annotated.shape[0]
        cv2.putText(annotated, f"Scale: {MM_PER_PIXEL:.3f} mm/px",
                    (10, height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2, cv2.LINE_AA)

        return annotated, dist12, dist23, total, points, confidences, segment_distances


    def print_measurements(dist12, dist23, total):
        if dist12 is None and dist23 is None:
            print("No pulley detctions found.")
            return

        if dist12 is not None:
            print(f"Distance first->second pulley: {dist12:.3f} mm (scale {MM_PER_PIXEL} mm/px)")
        if dist23 is not None:
            print(f"Distance second->third pulley: {dist23:.3f} mm (scale {MM_PER_PIXEL} mm/px)")

        if total is not None and TEMPERATURE_SENSITIVITY_MM_PER_C > 0:
            expected_total = expected_total_distance_for_temperature(CURRENT_TEMPERATURE_C)
            expected_dist12, expected_dist23 = split_total_distance(expected_total)
            loss_mm = expected_total - total
            print(f"Expected total distance (1->3) at {CURRENT_TEMPERATURE_C:.1f} °C: {expected_total:.3f} mm")
            print(f"Expected split: 1->2 = {expected_dist12:.3f} mm, 2->3 = {expected_dist23:.3f} mm")
            print(f"Measured total distance (1->3): {total:.3f} mm")
            print(f"Loss vs expected:{CURRENT_TEMPERATURE_C:.1f} °C: {expected_total:.3f} mm - {total:.3f} mm = {loss_mm:.3f} mm")
        elif dist12 is not None and dist23 is None:
            print("Only two pulleys detected; third-to-second distance not computed.")


    def main():
        global camera_cap, camera_running, detection_data, detection_lock
        
        model = _get_yolo_model()
        camera_cap = cv2.VideoCapture(0)
        camera_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        camera_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        # Optimize camera buffer size
        camera_cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        if not camera_cap.isOpened():
            print("Error: Could not open camera.")
            camera_running = False
            return

        camera_running = True
        print("Camera started. Detection running smoothly...")
        last_print_time = 0
        last_save_time = 0
        frame_counter = 0
        # Process every 3rd frame to reduce load (can adjust based on performance)
        PROCESS_EVERY_N_FRAMES = 3
        # Save to database every 2 seconds
        SAVE_INTERVAL_SECONDS = 2.0

        while camera_running:
            ret, frame = camera_cap.read()
            if not ret:
                print("Error: Failed to read frame from camera.")
                break
            
            frame_counter += 1
            # Skip frames to reduce processing load
            should_process = (frame_counter == 1) or (frame_counter % PROCESS_EVERY_N_FRAMES == 0)
            
            if should_process:
                # Run inference without saving frames to disk for faster startup
                results = model.predict(
                    source=frame,
                    save=True,
                    verbose=False,
                    conf=CONF_THRES,
                    iou=IOU_THRES,
                    imgsz=IMAGE_SZ,
                    agnostic_nms=False
                )
            else:
                # Use previous results or skip annotation
                results = None
                with detection_lock:
                    detection_data['latest_frame'] = frame.copy()
                    detection_data['frame_available'] = True
                    detection_data['last_update'] = time.time()

            if should_process and results:
                annotated_frame, dist12, dist23, total, points, confidences, segments = annotate_frame(frame, results[0])
                
                # Store results in shared dictionary
                with detection_lock:
                    detection_data['capture_complete'] = False
                    detection_data['dist12'] = dist12
                    detection_data['dist23'] = dist23
                    detection_data['total'] = total
                    detection_data['points'] = points
                    detection_data['confidences'] = confidences
                    detection_data['segments'] = segments
                    detection_data['pulley_count'] = len(points)
                    detection_data['frame_available'] = True
                    detection_data['last_update'] = time.time()
                    
                    if total is not None and TEMPERATURE_SENSITIVITY_MM_PER_C > 0:
                        expected_total = expected_total_distance_for_temperature(CURRENT_TEMPERATURE_C)
                        expected_dist12, expected_dist23 = split_total_distance(expected_total)
                        loss_mm = expected_total - total
                        detection_data['expected_total'] = expected_total
                        detection_data['expected_dist12'] = expected_dist12
                        detection_data['expected_dist23'] = expected_dist23
                        detection_data['loss_mm'] = loss_mm
                    else:
                        detection_data['expected_total'] = None
                        detection_data['expected_dist12'] = None
                        detection_data['expected_dist23'] = None
                        detection_data['loss_mm'] = None
                    
                    # Store the latest annotated frame for streaming
                    detection_data['latest_frame'] = annotated_frame

                current_time = time.time()
                with detection_lock:
                    capture_requested = detection_data.get('capture_requested', False)
                
                # Save to database only when user has requested capture and we have full detection
                has_full_detection = (
                    len(points) >= 3 and
                    dist12 is not None and
                    dist23 is not None and
                    total is not None
                )
                
                if (
                    capture_requested
                    and has_full_detection
                    and current_time - last_save_time >= SAVE_INTERVAL_SECONDS
                ):
                    try:
                        points_json = json.dumps([[float(p[0]), float(p[1])] for p in points]) if points else None
                        image_relative_path = save_detection_frame(annotated_frame)
                        DetectionRecord.objects.create(
                            dist12=dist12,
                            dist23=dist23,
                            total=total,
                            expected_total=detection_data.get('expected_total'),
                            expected_dist12=detection_data.get('expected_dist12'),
                            expected_dist23=detection_data.get('expected_dist23'),
                            loss_mm=detection_data.get('loss_mm'),
                            pulley_count=len(points),
                            temperature_c=CURRENT_TEMPERATURE_C,
                            points_json=points_json,
                            image_path=image_relative_path,
                        )
                        last_save_time = current_time
                        with detection_lock:
                            detection_data['capture_complete'] = True
                            detection_data['capture_image_path'] = image_relative_path
                            detection_data['capture_requested'] = False
                        print(f"Data saved to database at {timezone.now()} - full 3-pulley detection captured. Stopping camera...")
                        camera_running = False
                        break
                    except Exception as e:
                        print(f"Error saving to database: {e}")
                
                if current_time - last_print_time > 1.0 and (dist12 is not None or dist23 is not None):
                    print("-" * 60)
                    print_measurements(dist12, dist23, total)
                    last_print_time = current_time
            else:
                # Use previous annotated frame if available for smoother streaming
                with detection_lock:
                    if detection_data.get('latest_frame') is not None:
                        annotated_frame = detection_data['latest_frame'].copy()
                    else:
                        # If no previous frame, use current frame
                        annotated_frame = frame
                        if not detection_data.get('frame_available'):
                            detection_data['capture_complete'] = False
                            detection_data['pulley_count'] = 0
                            detection_data['dist12'] = None
                            detection_data['dist23'] = None
                            detection_data['total'] = None
                            detection_data['points'] = []

        if camera_cap:
            camera_cap.release()
        camera_running = False
        print("Camera stopped.")


    detection_thread = getattr(yolo_camera, "_detection_thread", None)
    if detection_thread is None or not detection_thread.is_alive():
        detection_thread = threading.Thread(target=main, daemon=True)
        detection_thread.start()
        yolo_camera._detection_thread = detection_thread

    return render(request, 'pulley_app/camera.html')

def video_stream(request):
    """Stream video frames as MJPEG"""
    def generate_frames():
        global detection_data, detection_lock, camera_running
        
        while True:
            with detection_lock:
                capture_complete = detection_data.get('capture_complete', False)
                frame_available = detection_data.get('frame_available', False)
                latest_frame = detection_data.get('latest_frame')
                camera_active = camera_running
            
            if camera_active and frame_available and latest_frame is not None:
                try:
                    frame = latest_frame.copy()
                except:
                    frame = np.zeros((480, 640, 3), dtype=np.uint8)
            else:
                # Return black frame with status text if no frame available
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                status_text = "Waiting for camera..." if not capture_complete else "Capture complete. Camera stopped."
                cv2.putText(frame, status_text, (80, 240), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
            
            # Encode frame as JPEG with optimized quality for smoother streaming
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
            if ret:
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            # Slightly slower frame rate for smoother operation
            time.sleep(0.04)  # ~25 FPS for better stability
    
    return StreamingHttpResponse(generate_frames(), content_type='multipart/x-mixed-replace; boundary=frame')

def detection_results(request):
    """API endpoint to get detection results"""
    global detection_data, detection_lock
    
    with detection_lock:
        # Convert numpy arrays/tuples to lists for JSON serialization
        points = detection_data.get('points', [])
        confidences = detection_data.get('confidences', [])
        segments = detection_data.get('segments', [])
        
        # Convert points to list of lists (handles tuples, numpy arrays, etc.)
        points_list = []
        if points:
            for p in points:
                try:
                    points_list.append([float(p[0]), float(p[1])])
                except (TypeError, IndexError):
                    pass
        
        confidences_list = [float(c) for c in confidences] if confidences else []
        segments_list = [float(s) for s in segments] if segments else []
        
        data = {
            'dist12': detection_data.get('dist12'),
            'dist23': detection_data.get('dist23'),
            'total': detection_data.get('total'),
            'pulley_count': detection_data.get('pulley_count', 0),
            'expected_total': detection_data.get('expected_total'),
            'expected_dist12': detection_data.get('expected_dist12'),
            'expected_dist23': detection_data.get('expected_dist23'),
            'loss_mm': detection_data.get('loss_mm'),
            'points': points_list,
            'confidences': confidences_list,
            'segments': segments_list,
            'last_update': detection_data.get('last_update'),
            'camera_running': camera_running,
            'capture_complete': detection_data.get('capture_complete', False),
            'capture_image_path': detection_data.get('capture_image_path'),
            'capture_requested': detection_data.get('capture_requested', False),
        }
    
    return JsonResponse(data)

def stop_camera(request):
    """API endpoint to stop the camera"""
    global camera_running, camera_cap, detection_lock
    
    with detection_lock:
        camera_running = False
        if camera_cap is not None:
            camera_cap.release()
            camera_cap = None
        detection_data['capture_complete'] = False
        detection_data['capture_requested'] = False
    
    # Get final detection results
    with detection_lock:
        # Convert numpy arrays/tuples to lists for JSON serialization
        points = detection_data.get('points', [])
        confidences = detection_data.get('confidences', [])
        segments = detection_data.get('segments', [])
        
        # Convert points to list of lists (handles tuples, numpy arrays, etc.)
        points_list = []
        if points:
            for p in points:
                try:
                    points_list.append([float(p[0]), float(p[1])])
                except (TypeError, IndexError):
                    pass
        
        confidences_list = [float(c) for c in confidences] if confidences else []
        segments_list = [float(s) for s in segments] if segments else []
        
        data = {
            'dist12': detection_data.get('dist12'),
            'dist23': detection_data.get('dist23'),
            'total': detection_data.get('total'),
            'pulley_count': detection_data.get('pulley_count', 0),
            'expected_total': detection_data.get('expected_total'),
            'expected_dist12': detection_data.get('expected_dist12'),
            'expected_dist23': detection_data.get('expected_dist23'),
            'loss_mm': detection_data.get('loss_mm'),
            'points': points_list,
            'confidences': confidences_list,
            'segments': segments_list,
            'last_update': detection_data.get('last_update'),
            'camera_running': False,
            'capture_complete': detection_data.get('capture_complete', False),
            'capture_image_path': detection_data.get('capture_image_path'),
            'capture_requested': detection_data.get('capture_requested', False),
            'success': True
        }
    
    return JsonResponse(data)
# Config (mirrors predict.py / video.py)


def request_capture(request):
    """Flag that the next full detection should be saved"""
    global detection_data, detection_lock
    with detection_lock:
        detection_data['capture_requested'] = True
        detection_data['capture_complete'] = False
    return JsonResponse({'capture_requested': True})