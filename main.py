import cv2
import mediapipe as mp
import numpy as np
import serial
import time

"""
GiTam Ver. 2^3 - Sistem za razbudjivanje pospanog vozaca

Prije pokretanja programa potrebno je uraditi sljedece stvari!
- Ukucati u terminal sljedece komande:
    pip install pyserial
    pip install numpy
    pip install mediapipe
- Staviti u (1) port na kojem ce da slusa Arduino.
- Poslati sketch na Arduino sa Arduino IDE (Bez ovoga nece nista raditi).

Za gasenje prozora sa kamerom pritisnuti ESC.
"""

# Postavljanje konekcije sa Arduinom (1)
arduino = serial.Serial('/dev/tty.usbmodem111101', 9600)  # Prvi parametar je izlazni port za Arduino, na racunaru korisnika
time.sleep(2)

# Hvala Mediapipe inzinjerima za ovaj code koji sljedi

# Mediapipe mesh za facu
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1)

# EAR
EAR_THRESHOLD = 0.2
POSPAN_FRAMES = 15
frame_counter = 0
status = "budan"

# Mediapipe index brojevi
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

def calculate_EAR(eye, landmarks, image_width, image_height):
    def _p(index):
        x = int(landmarks[index].x * image_width)
        y = int(landmarks[index].y * image_height)
        return np.array([x, y])

    p1 = _p(eye[1])
    p2 = _p(eye[2])
    p3 = _p(eye[5])
    p4 = _p(eye[4])
    p0 = _p(eye[0])
    p3 = _p(eye[3])

    vertical = np.linalg.norm(p2 - p4)
    horizontal = np.linalg.norm(p0 - p3)

    ear = vertical / horizontal
    return ear

def send_to_arduino(poruka):
    arduino.write((poruka + "\n").encode())
    print(f"[Poruka za Arduino] {poruka}")

# Upaliti kameru
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    h, w = frame.shape[:2]
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(frame_rgb)

    if results.multi_face_landmarks:
        landmarks = results.multi_face_landmarks[0].landmark

        left_ear = calculate_EAR(LEFT_EYE, landmarks, w, h)
        right_ear = calculate_EAR(RIGHT_EYE, landmarks, w, h)
        avg_ear = (left_ear + right_ear) / 2.0

        # Drowsiness check
        if avg_ear < EAR_THRESHOLD:
            frame_counter += 1
            if frame_counter >= POSPAN_FRAMES and status != "pospan":
                send_to_arduino("pospan")
                status = "pospan"
        else:
            if status != "budan":
                send_to_arduino("budan")
                status = "budan"
            frame_counter = 0

        # Ispis informacija na ekran
        cv2.putText(frame, f"EAR: {avg_ear:.2f}", (30, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(frame, f"Status: {status}", (30, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

    cv2.imshow("Detekcija pospanosti", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # Pritisnuti ESC da se ugasi prozor
        break

cap.release()
cv2.destroyAllWindows()
send_to_arduino("budan")
arduino.close()
