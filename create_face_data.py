import face_recognition
import pickle
import cv2
import os
import glob
import tqdm



data_path = glob.glob('dataset/*')
save_path = 'face_data'
if not os.path.isdir(save_path):
    os.mkdir(save_path)
data_path.sort()

face_data = []
face_name = []

for face in data_path:
    img_list = glob.glob(face + '/*')
    for i in tqdm.tqdm(range(len(img_list)), desc='[INFO] Processing '+face.split('/')[-1]):
        image = cv2.imread(img_list[i])
        image = cv2.resize(image, (720, 480))
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb, model='hog')
        encodings = face_recognition.face_encodings(rgb, boxes)

        for encoding in encodings:
            face_data.append(encoding)
            face_name.append(face.split('/')[-1])

print("[INFO] Saving Face Data...")
data = {"face_data": face_data, "face_name": face_name}
f = open(save_path+'/face_data.pkl', "wb")
f.write(pickle.dumps(data))
f.close()
