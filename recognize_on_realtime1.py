import glob
import os
from datetime import datetime
import face_recognition
import pickle
import cv2
import tqdm
from send_mail import send_mail
import stat

def rmtree(top):
    for root, dirs, files in os.walk(top, topdown=False):
        for name in files:
            filename = os.path.join(root, name)
            os.chmod(filename, stat.S_IWUSR)
            os.remove(filename)
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(top)


if __name__ == '__main__':
    stream = cv2.VideoCapture(0)
    print("[INFO] Loading FaceData...")
    face_data = pickle.loads(open('face_data/face_data.pkl', "rb").read())
    save_path = 'output/recording_' + datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.mp4'
    print('[INFO] Processing Video...')
    frame_array = []
    ret = True
    unknown_found = False
    t1 = datetime.now()
    first_time = True
    while ret:
        t2 = datetime.now()
        ret, frame = stream.read()
        frame = cv2.resize(frame, (720, 480))
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        r = frame.shape[1] / float(rgb.shape[1])
        boxes = face_recognition.face_locations(rgb, model='hog')
        encodings = face_recognition.face_encodings(rgb, boxes)
        names = []
        for encoding in encodings:
            matches = face_recognition.compare_faces(face_data["face_data"],
                                                     encoding)
            name = "Unknown"

            if True in matches:
                matched_ids = [i for (i, b) in enumerate(matches) if b]
                counts = {}
                for i in matched_ids:
                    name = face_data["face_name"][i]
                    counts[name] = counts.get(name, 0) + 1

                name = max(counts, key=counts.get)

            names.append(name)

        for ((top, right, bottom, left), name) in zip(boxes, names):
            top = int(top * r)
            right = int(right * r)
            bottom = int(bottom * r)
            left = int(left * r)

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            y = top - 15 if top - 15 > 15 else top + 15
            cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
            if name == 'Unknown':
                if not os.path.isdir('.tmp'):
                    os.mkdir('.tmp')
                uk_img = frame[top:bottom, left:right]
                file_name = str('.tmp/'+datetime.now().strftime("%Y_%m_%d_%H_%M_%S")) + '.jpg'
                cv2.imwrite(file_name, uk_img)
                unknown_found = True
        frame_array.append(frame)
        cv2.imshow("Frame", frame)
        time_diff = t2 - t1
        time_diff_in_sec = time_diff.days * 24 * 60 * 60 + time_diff.seconds
        if unknown_found and time_diff_in_sec > 5:
            send_mail(glob.glob('.tmp/*.jpg'))
            unknown_found = False
            first_time = False
            t1 = datetime.now()
            print(time_diff_in_sec)
        key = cv2.waitKey(24) & 0xFF
        if key == ord("q"):
            os.system('rmdir /S /Q "{}"'.format('.tmp'))
            break

    print('[INFO] Saving Video')
    out = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*'MP4V'), 24.0, (720, 480))

    for i in tqdm.tqdm(range(len(frame_array)), desc='Encoding Frame'):
        out.write(frame_array[i])
    out.release()
