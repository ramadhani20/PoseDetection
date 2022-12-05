import math
import cv2
import numpy as np
from time import time
import mediapipe as mp
import matplotlib.pyplot as plt

# Inisialisasi kelas pose mediapipe.
mp_pose = mp.solutions.pose

# Menyiapkan fungsi Pose.
pose = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.3, model_complexity=2)

# Inisialisasi kelas menggambar mediapipe, berguna untuk anotasi.
mp_drawing = mp.solutions.drawing_utils 

def detectPose(image, pose, display=True):
    '''
   Fungsi ini melakukan deteksi pose pada gambar.
     Argumen:
         image: Gambar input dengan orang terkemuka yang posenya perlu dideteksi.
         pose: Fungsi pengaturan pose yang diperlukan untuk melakukan deteksi pose.
         display: Nilai boolean yang jika disetel ke true fungsi menampilkan gambar input asli, gambar yang dihasilkan,
                  dan pose landmark dalam plot 3D dan tidak menghasilkan apa-apa.
     Pengembalian:
         output_image: Gambar input dengan landmark pose yang terdeteksi digambar.
         landmark: Daftar landmark yang terdeteksi diubah menjadi skala aslinya.
    '''
    
    # Buat salinan gambar input.
    output_image = image.copy()
    
    # Ubah gambar dari BGR menjadi format RGB.
    imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Lakukan Deteksi Pose.
    results = pose.process(imageRGB)
    
    # Ambil tinggi dan lebar gambar input.
    height, width, _ = image.shape
    
    # Inisialisasi daftar untuk menyimpan tengara yang terdeteksi.
    landmarks = []
    
    # Periksa apakah ada landmark yang terdeteksi
    if results.pose_landmarks:
    
        # Gambarlah landmark Pose pada gambar keluaran.
        mp_drawing.draw_landmarks(image=output_image, landmark_list=results.pose_landmarks,
                                  connections=mp_pose.POSE_CONNECTIONS)
        
        # Ulangi pada landmark yang terdeteksi.
        for landmark in results.pose_landmarks.landmark:
            
            # Tambahkan tengara ke dalam daftar.
            landmarks.append((int(landmark.x * width), int(landmark.y * height),
                                  (landmark.z * width)))
    
    # Periksa apakah gambar input asli dan gambar yang dihasilkan ditentukan untuk ditampilkan.
    if display:
    
        # Menampilkan gambar input asli dan gambar yang dihasilkan.
        plt.figure(figsize=[22,22])
        plt.subplot(121);plt.imshow(image[:,:,::-1]);plt.title("Original Image");plt.axis('off');
        plt.subplot(122);plt.imshow(output_image[:,:,::-1]);plt.title("Output Image");plt.axis('off');
        
        # Juga Plot landmark Pose dalam 3D.
        mp_drawing.plot_landmarks(results.pose_world_landmarks, mp_pose.POSE_CONNECTIONS)
        
    # Jika tidak
    else:
        
        # Kembalikan gambar keluaran dan tengara yang ditemukan.
        return output_image, landmarks

# Atur fungsi Pose untuk video.
pose_video = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, model_complexity=1)

# Inisialisasi objek VideoCapture untuk membaca dari webcam.
video = cv2.VideoCapture(1)

# Buat jendela bernama untuk tujuan mengubah ukuran
cv2.namedWindow('Pose Detection', cv2.WINDOW_NORMAL)


# Inisialisasi objek VideoCapture untuk membaca dari video yang disimpan dalam disk.
# video = cv2.VideoCapture('media/running.mp4')

# Setel ukuran kamera video
video.set(3,1280)
video.set(4,960)

# Inisialisasi variabel untuk menyimpan waktu dari frame sebelumnya.
time1 = 0

# Ulangi hingga video berhasil diakses.
while video.isOpened():
    
    # Membaca sebuah bingkai.
    ok, frame = video.read()
    
    # Periksa apakah bingkai tidak terbaca dengan benar.
    if not ok:
        
        # Putuskan lingkarannya.
        break
    
    # Balikkan bingkai secara horizontal untuk visualisasi alami (tampilan selfie).
    frame = cv2.flip(frame, 1)
    
    # Dapatkan lebar dan tinggi bingkai
    frame_height, frame_width, _ =  frame.shape
    
    # Ubah ukuran bingkai sambil menjaga rasio aspek.
    frame = cv2.resize(frame, (int(frame_width * (640 / frame_height)), 640))
    
    # Lakukan deteksi landmark Pose.
    frame, _ = detectPose(frame, pose_video, display=False)
    
    # Atur waktu untuk frame ini ke waktu saat ini.
    time2 = time()
    
    # Periksa apakah perbedaan antara waktu bingkai sebelumnya dan ini > 0 untuk menghindari pembagian dengan nol.
    if (time2 - time1) > 0:
    
        # Hitung jumlah frame per detik.
        frames_per_second = 1.0 / (time2 - time1)
        
        # Tulis jumlah frame per detik yang dihitung pada frame.
        cv2.putText(frame, 'FPS: {}'.format(int(frames_per_second)), (10, 30),cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 3)
    
    # Perbarui waktu bingkai sebelumnya ke waktu bingkai ini.
    # Karena frame ini akan menjadi frame sebelumnya pada iterasi berikutnya.
    time1 = time2
    
    # Tampilkan bingkai.
    cv2.imshow('Pose Detection', frame)
    
    # Tunggu sampai tombol ditekan
    # Ambil kode ASCII dari tombol yang ditekan
    k = cv2.waitKey(1) & 0xFF
    
    # Periksa apakah 'ESC' ditekan.
    if(k == 27):
        
        # 
        break

# Lepaskan objek VideoCapture.
video.release()

# Tutup jendela.
cv2.destroyAllWindows()

def calculateAngle(landmark1, landmark2, landmark3):
    '''
   Fungsi ini menghitung sudut antara tiga landmark yang berbeda.
     Argumen:
         landmark1: Landmark pertama yang berisi koordinat x,y dan z.
         landmark2: Landmark kedua yang berisi koordinat x,y dan z.
         landmark3: Landmark ketiga yang berisi koordinat x,y dan z.
     Pengembalian:
         angle: Sudut yang dihitung antara tiga landmark.

    '''

    # Dapatkan koordinat landmark yang diperlukan.
    x1, y1, _ = landmark1
    x2, y2, _ = landmark2
    x3, y3, _ = landmark3

    # Hitunglah sudut antara ketiga titik tersebut
    angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))
    
    # Periksa apakah sudutnya kurang dari nol.
    if angle < 0:

        # Tambahkan 360 ke sudut yang ditemukan.
        angle += 360
    
    # Kembalikan sudut yang dihitung.
    return angle

    # Hitunglah sudut antara ketiga landmark tersebut.
angle = calculateAngle((558, 326, 0), (642, 333, 0), (718, 321, 0))

# Display the calculated angle.
print(f'Sudut yang dihitung adalah {angle}')
def classifyPose(landmarks, output_image, display=False):
    '''
   Fungsi ini mengklasifikasikan pose yoga tergantung pada sudut berbagai sendi tubuh.
     Argumen:
         landmark: Daftar landmark yang terdeteksi dari orang yang posenya perlu diklasifikasikan.
         output_image: Gambar orang dengan landmark pose yang terdeteksi yang digambar.
         display: Nilai boolean yang jika disetel ke true fungsi menampilkan gambar yang dihasilkan dengan label pose
         tertulis di atasnya dan tidak mengembalikan apa pun.
     Pengembalian:
         output_image: Gambar dengan penanda pose yang terdeteksi digambar dan label pose ditulis.
         label: Label pose rahasia dari orang di output_image.

    '''
    
    # Inisialisasi label pose. Tidak diketahui pada tahap ini.
    label = 'Pose Tidak Ada'

    # Tentukan warna (Merah) dengan label yang akan ditulis pada gambar
    color = (0, 0, 255)
    
    # Hitung sudut yang diperlukan.
    #----------------------------------------------------------------------------------------------------------------
    
    # Dapatkan sudut antara titik bahu, siku, dan pergelangan tangan kiri.
    left_elbow_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
                                      landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value],
                                      landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value])
    
    # Dapatkan sudut antara titik bahu, siku, dan pergelangan tangan kanan.
    right_elbow_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
                                       landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value],
                                       landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value])   
    
    # Dapatkan sudut antara titik siku, bahu, dan pinggul kiri.
    left_shoulder_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value],
                                         landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
                                         landmarks[mp_pose.PoseLandmark.LEFT_HIP.value])

    # Dapatkan sudut antara titik pinggul, bahu, dan siku kanan.
    right_shoulder_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value],
                                          landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
                                          landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value])

    # Dapatkan sudut antara titik pinggul, lutut, dan pergelangan kaki kiri.
    left_knee_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.LEFT_HIP.value],
                                     landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value],
                                     landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value])

    # Dapatkan sudut antara titik pinggul, lutut, dan pergelangan kaki kanan
    right_knee_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value],
                                      landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value],
                                      landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value])
    
    #----------------------------------------------------------------------------------------------------------------
    
    # Periksa apakah itu pose warrior II atau pose T.
    # Adapun keduanya, kedua lengan harus lurus dan bahu harus pada sudut tertentu.
    #----------------------------------------------------------------------------------------------------------------
    
    # Periksa apakah kedua lengan lurus.
    if left_elbow_angle > 165 and left_elbow_angle < 195 and right_elbow_angle > 165 and right_elbow_angle < 195:

        # Periksa apakah bahu berada pada sudut yang diperlukan.
        if left_shoulder_angle > 80 and left_shoulder_angle < 110 and right_shoulder_angle > 80 and right_shoulder_angle < 110:

    # Periksa apakah itu pose warrior II
    #----------------------------------------------------------------------------------------------------------------

            # Periksa apakah satu kaki lurus.
            if left_knee_angle > 165 and left_knee_angle < 195 or right_knee_angle > 165 and right_knee_angle < 195:

                # Periksa apakah kaki lainnya ditekuk pada sudut yang diperlukan.
                if left_knee_angle > 90 and left_knee_angle < 120 or right_knee_angle > 90 and right_knee_angle < 120:

                    # Tentukan label posenya yaitu pose Warrior II.
                    label = 'Warrior II Pose' 
                        
    #----------------------------------------------------------------------------------------------------------------
    
    # Periksa apakah itu pose T
    #----------------------------------------------------------------------------------------------------------------
    
            # Periksa apakah kedua kaki lurus
            if left_knee_angle > 160 and left_knee_angle < 195 and right_knee_angle > 160 and right_knee_angle < 195:

                # Tentukan label posenya yaitu pose pohon.
                label = 'T Pose'

    #----------------------------------------------------------------------------------------------------------------
    
    # Periksa apakah itu pose pohon.
    #----------------------------------------------------------------------------------------------------------------
    
    # Periksa apakah satu kaki lurus
    if left_knee_angle > 165 and left_knee_angle < 195 or right_knee_angle > 165 and right_knee_angle < 195:

        # Periksa apakah kaki lainnya ditekuk pada sudut yang diperlukan.
        if left_knee_angle > 315 and left_knee_angle < 335 or right_knee_angle > 25 and right_knee_angle < 45:

            # Tentukan label posenya yaitu pose pohon.
            label = 'Tree Pose'
                
    #----------------------------------------------------------------------------------------------------------------
    
    # Periksa apakah posenya berhasil diklasifikasikan
    if label != 'Unknown Pose':
        
        # Perbarui warna (menjadi hijau) dengan label yang akan ditulis pada gambar.
        color = (0, 255, 0)  
    
    # Tulis label pada gambar keluaran.
    cv2.putText(output_image, label, (10, 30),cv2.FONT_HERSHEY_PLAIN, 2, color, 2)
    
    # Periksa apakah gambar yang dihasilkan ditentukan untuk ditampilkan.
    if display:
    
        # Menampilkan gambar yang dihasilkan.
        plt.figure(figsize=[10,10])
        plt.imshow(output_image[:,:,::-1]);plt.title("Output Image");plt.axis('off');
        
    else:
        
        # Kembalikan gambar keluaran dan label rahasia.
        return output_image, label


# Atur fungsi Pose untuk video.
pose_video = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, model_complexity=1)
# def to_pixel_coords(relative_coords):
#             return tuple(round(coord * dimension) for coord, dimension in zip(relative_coords, SCREEN_DIMENSIONS))

# Inisialisasi objek VideoCapture untuk membaca dari webcam.
camera_video = cv2.VideoCapture(0)
camera_video.set(3,1280)
camera_video.set(4,960)

# Inisialisasi jendela yang dapat diubah ukurannya.
cv2.namedWindow('Pose Classification', cv2.WINDOW_NORMAL)

# Ulangi hingga webcam berhasil diakses.
while camera_video.isOpened():
    
    # Membaca sebuah bingkai.
    ok, frame = camera_video.read()
    
    # Periksa apakah bingkai tidak terbaca dengan benar.
    if not ok:
        
        # Lanjutkan ke iterasi berikutnya untuk membaca frame berikutnya dan mengabaikan frame kamera yang kosong.
        continue
    
    # Balikkan bingkai secara horizontal untuk visualisasi alami (tampilan selfie).
    frame = cv2.flip(frame, 1)
    
    # Dapatkan lebar dan tinggi bingkai
    frame_height, frame_width, _ =  frame.shape
    
    # Ubah ukuran bingkai sambil menjaga rasio aspek.
    frame = cv2.resize(frame, (int(frame_width * (640 / frame_height)), 640))
    
    # Lakukan deteksi landmark Pose.
    frame, landmarks = detectPose(frame, pose_video, display=False)
    
    # Periksa apakah tengara terdeteksi.
    if landmarks:
        
        # Lakukan Klasifikasi Pose.
        frame, _ = classifyPose(landmarks, frame, display=False)
    
    # Tampilkan bingkai.
    cv2.imshow('Pose Classification', frame)
    
    # Tunggu hingga tombol ditekan. 
    # Ambil kode ASCII dari tombol yang ditekan
    k = cv2.waitKey(1) & 0xFF
    
    # Periksa apakah 'ESC' ditekan.
    if(k == 27):
        
        # Putuskan lingkarannya.
        break

# Lepaskan objek VideoCapture dan tutup jendela.
camera_video.release()
cv2.destroyAllWindows()
