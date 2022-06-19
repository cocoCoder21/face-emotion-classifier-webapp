import cv2
import numpy as np
from mtcnn.mtcnn import MTCNN
import tensorflow as tf
import matplotlib.pyplot as plt


# This class is responsible for processing the image input and predicting its emotion.

class VideoCapture(object):
    def __init__(self):
        # self.video = cv2.VideoCapture(0)
        self.detector = MTCNN(scale_factor=0.1)
        self.img_size = (48, 48)
        self.model = tf.keras.models.load_model('FaceEmotionModel.h5')
        self.emotions_lists_text = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

    def __del__(self):
        pass
        # self.video.release()

    # This is resposible ofr labelling the score attained from the image prediction, and providing the emotion label for it.
    def emotion_analysis(self, emotions_objects):
        tmp_obj = []
        for i in emotions_objects:
            a = i * 100
            print("ROUNDED: ", np.round(a, 4))
            if np.round(a, 4) <= 0.0:
                tmp_obj.append(0.0001)
            else:
                tmp_obj.append(a)
        current_emotion = np.amax(tmp_obj)
        emotion_idx = np.where(tmp_obj == current_emotion)
        emotion_text = self.emotions_lists_text[emotion_idx[0][0]]
        classified_obj = {'emotion': emotion_text, 'accuracy': np.round(current_emotion, 3)}
        return emotion_text, tmp_obj, classified_obj

    # This is for processing the dimension of the image
    def get_frame(self):
        ret, frame = self.video.read()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = self.detector.detect_faces(rgb)
        scores = []

        for face in faces:
            try:
                x, y, w, h = face['box']
                keypoints = face['keypoints']
                roi = rgb[y: y + h, x: x + w]  #
                data = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)
                data = cv2.resize(data, self.img_size) / 255.  # resize imge and flatten
                data = tf.keras.preprocessing.image.img_to_array(data)
                data = np.expand_dims(data, axis=0)
                scores = self.model.predict(data)[0]
                text_return = self.emotion_analysis(scores)
                text = "{}".format(text_return)
                cv2.rectangle(img=frame, pt1=(x, y), pt2=(x + w, y + h), color=(0, 0, 255), thickness=2)  #
                cv2.putText(frame, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                cv2.circle(frame, (keypoints['left_eye']), 2, (0, 155, 255), 2)
                cv2.circle(frame, (keypoints['right_eye']), 2, (0, 155, 255), 2)
                cv2.circle(frame, (keypoints['nose']), 2, (0, 155, 255), 2)
                cv2.circle(frame, (keypoints['mouth_left']), 2, (0, 155, 255), 2)
                cv2.circle(frame, (keypoints['mouth_right']), 2, (0, 155, 255), 2)

            except Exception as e:
                print(e)
                print(roi.shape)

        jpeg = cv2.imencode('.jpg', frame)
        return ret, jpeg.tobytes()

    # This is for predicting the image
    def predict_image(self, img):
        # rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = img
        faces = self.detector.detect_faces(img)
        emotions_array = []  # {'face': fds ,'emotion': array()}
        for face in faces:

            try:
                x, y, w, h = face['box']
                keypoints = face['keypoints']
                roi = img[y: y + h, x: x + w]  #
                data = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)
                data = cv2.resize(data, self.img_size) / 255.  # resize imge and flatten

                # get the image of roi
                img_arr = roi
                img_data = tf.keras.preprocessing.image.array_to_img(img_arr)
                data = tf.keras.preprocessing.image.img_to_array(data)
                data = np.expand_dims(data, axis=0)
                scores = self.model.predict(data)[0]
                # scores = scores.tolist()
                text_return, percentage_scores, classified_obj = self.emotion_analysis(scores)
                text = "{}".format(text_return)
                cv2.rectangle(img=img, pt1=(x, y), pt2=(x + w, y + h), color=(0, 255, 0), thickness=2)  #
                cv2.putText(img, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
                cv2.circle(img, (keypoints['left_eye']), 2, (0, 155, 255), 2)
                cv2.circle(img, (keypoints['right_eye']), 2, (0, 155, 255), 2)
                cv2.circle(img, (keypoints['nose']), 2, (0, 155, 255), 2)
                cv2.circle(img, (keypoints['mouth_left']), 2, (0, 155, 255), 2)
                cv2.circle(img, (keypoints['mouth_right']), 2, (0, 155, 255), 2)
                faces_obj = {'face-img': img_data, 'face-prediction': classified_obj,
                             'scores': np.round(percentage_scores, 4)}
                emotions_array.append(faces_obj)

            except Exception as e:
                print(e)
                print(roi.shape)
        array_img = tf.keras.preprocessing.image.array_to_img(img)
        return array_img, len(faces), emotions_array
