from flask import Flask, render_template, Response, request
import requests
from flask_wtf.csrf import CSRFProtect
from flask_ngrok import run_with_ngrok
from VideoCapture import VideoCapture
import matplotlib.pyplot as plt
from PIL import Image
import base64
import cv2
import os
import io


# This is responsible to provide protection for the website, especially when the user input something.
csrf = CSRFProtect()

app = Flask(__name__)
csrf.init_app(app)

app.config["MAX_CONTENT_LENGTH"] = 3024 * 3024
app.config["UPLOAD_EXTENSIONS"] = ['.jpg', '.png']


@app.route('/')
def Home():
    return render_template('/sample.html',
                           is_uploaded=False,
                           img_path='',
                           img_size='',
                           img_filename='',
                           img_width=0,
                           img_height=0,
                           img_upload_isvalid=False,
                           predicted_image='',
                           is_predicted=False,
                           is_error=False,
                           is_error_msg=''
                           )


def gen(cam):
    while True:
        ret, frame = cam.get_frame()

        if not ret:
            break

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame
               + b'\r\n\r\n')


@csrf.exempt
@app.route('/video_capture')
def video_capture():
    return Response(
        gen(VideoCapture()),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


def PIL_bytes(objects):
    objects = objects
    for obj in objects:
        face = obj['face-img']
        buffered = io.BytesIO()
        buffered.seek(0)
        face = face.resize((150, 150))
        face.save(buffered, format="JPEG")
        face_string_encoded = base64.b64encode(buffered.getvalue())
        face_string = face_string_encoded.decode('utf-8')
        obj['face-img'] = face_string
    return objects


@csrf.exempt
@app.route('/predict_capture', methods=["POST"])
def predict_capture():
    if request.method == 'POST':
        base64_str = request.form['img_predict_name']
        # img = Image.open(io.BytesIO(base64.decodebytes(bytes(base64_str, "utf-8"))))
        # img.save('my-image.jpeg')
        img = plt.imread(io.BytesIO(base64.decodebytes(bytes(base64_str, "utf-8"))), 0)
        cap = VideoCapture()
        predicted_image, num_faces, list_faces = cap.predict_image(img)
        # predicted_image.save('helloworld.jpg')
        list_faces_string = PIL_bytes(list_faces)
        buffered = io.BytesIO()
        predicted_image = predicted_image.resize((400, 400))
        predicted_image.save(buffered, format="JPEG")
        image_string_encoded = base64.b64encode(buffered.getvalue())
        image_string = image_string_encoded.decode('utf-8')
        if num_faces > 0:
            return render_template('sample.html',
                                   is_uploaded=True,
                                   predicted_image=image_string,
                                   is_predicted=True,
                                   is_error=False,
                                   list_emotions=list_faces_string
                                   )
        else:
            msg = "-Theres no Face/s detected in that image. Please upload image that fit to the critera"
            return render_template('sample.html',
                                   is_uploaded=False,
                                   img_path='',
                                   img_size='',
                                   img_filename='',
                                   img_width=0,
                                   img_height=0,
                                   img_upload_isvalid=False,
                                   predicted_image='',
                                   is_predicted=False,
                                   is_error=True,
                                   is_error_msg=msg
                                   )
            # @app.route('/destroy_uploaded',methods=['POST'])
            # def destroy_uploaded():
            #     if request.method == 'POST':
            #         req = request.get_json()
            #         cloudinary.uploader.destroy(req['public_id'])
            #         res = make_response(jsonify({"message": "OKKK"}), 200)
            #
            print(img)


#         return res

# This route is responsible for accepting the POST request of the user, as well as the processing of the image.
@csrf.exempt
@app.route('/fetch_upload', methods=['POST'])
def fetch_upload():
    isValid = False
    image_IO = None
    id = request.args.get('second')

    if request.method == 'POST':
        try:
            img = request.files['img-file']
            img_size = len(img.read())
            img.seek(0)
            image_string_encoded = base64.b64encode(img.read())
            image_string = image_string_encoded.decode('utf-8')
            img.seek(0)
            imgIO = io.BytesIO(img.stream.read())
            imgIO.seek(0)
            image_IO = Image.open(imgIO)
            image_IO = image_IO.convert('RGB')
            img_width = image_IO.size[0]
            img_height = image_IO.size[1]
            buffered = io.BytesIO()
            buffered.seek(0)
            image_IO.save(buffered, format="JPEG")
            image_string_encoded = base64.b64encode(buffered.getvalue())
            image_string = image_string_encoded.decode('utf-8')
            imgIO.seek(0)
            # set img display screen to resize the display
            imgIO_display = image_IO
            buffered2 = io.BytesIO()
            buffered2.seek(0)
            imgIO_display = imgIO_display.resize((400, 400))
            imgIO_display.save(buffered2, format="JPEG")
            img_display_string_encoded = base64.b64encode(buffered2.getvalue())
            img_display_string = img_display_string_encoded.decode('utf-8')
            imgIO_display.seek(0)

            if int(img_width) > 500 and int(img_height) > 500:
                isValid = True
            return render_template('sample.html',
                                   is_uploaded=True, id=id,
                                   img_display=img_display_string,
                                   img_path=image_string,
                                   encoded_img=image_string_encoded,
                                   img_size=img_size,
                                   img_filename=img.filename,
                                   img_width=img_width,
                                   img_height=img_height,
                                   img_upload_isvalid=isValid,
                                   predicted_image='',
                                   is_predicted=False,
                                   is_error=False
                                   )
        except OSError as e:
            msg = "Invalid Image - " + str(e)
            return render_template('sample.html',
                                   is_uploaded=False, id=id,
                                   img_path='',
                                   img_size='',
                                   img_filename='',
                                   img_width=0,
                                   img_height=0,
                                   img_upload_isvalid=False,
                                   predicted_image='',
                                   is_predicted=False,
                                   is_error=True,
                                   is_error_msg=msg
                                   )



#
# # This route is responsible for accepting the POST request of the user, as well as the processing of the image.
# @csrf.exempt
# @app.route('/webcam_upload', methods=['POST'])
# def webcam_upload():
#     print("I'M A POST REQUEST INSIDE FLASK!")
#     isValid = False
#     image_IO = None
#     id = request.args.get('second')
#
#     if request.method == 'POST':
#         try:
#             # data_url = request.args.get('image')  # here parse the data_url out http://xxxxx/?image={dataURL}
#             # content = data_url.split(';')[1]
#             # image_encoded = content.split(',')[1]
#             # body = base64.decodebytes(image_encoded.encode('utf-8'))
#
#             img = request.files['img-file']
#             img_size = len(img.read())
#             img.seek(0)
#             image_string_encoded = base64.b64encode(img.read())
#             image_string = image_string_encoded.decode('utf-8')
#             img.seek(0)
#             imgIO = io.BytesIO(img.stream.read())
#             imgIO.seek(0)
#             image_IO = Image.open(imgIO)
#             img_width = image_IO.size[0]
#             img_height = image_IO.size[1]
#             buffered = io.BytesIO()
#             buffered.seek(0)
#             image_IO.save(buffered, format="JPEG")
#             image_string_encoded = base64.b64encode(buffered.getvalue())
#             image_string = image_string_encoded.decode('utf-8')
#             imgIO.seek(0)
#             # set img display screen to resize the display
#             imgIO_display = image_IO
#             buffered2 = io.BytesIO()
#             buffered2.seek(0)
#             imgIO_display = imgIO_display.resize((400, 400))
#             imgIO_display.save(buffered2, format="JPEG")
#             img_display_string_encoded = base64.b64encode(buffered2.getvalue())
#             img_display_string = img_display_string_encoded.decode('utf-8')
#             imgIO_display.seek(0)
#
#             if int(img_width) > 500 and int(img_height) > 500:
#                 isValid = True
#             return render_template('sample.html',
#                                    is_uploaded=True, id=id,
#                                    img_display=img_display_string,
#                                    img_path=image_string,
#                                    encoded_img=image_string_encoded,
#                                    img_size=img_size,
#                                    img_filename=img.filename,
#                                    img_width=img_width,
#                                    img_height=img_height,
#                                    img_upload_isvalid=isValid,
#                                    predicted_image='',
#                                    is_predicted=False,
#                                    is_error=False
#                                    )
#         except OSError as e:
#             msg = "Invalid Image - " + str(e)
#             return render_template('sample.html',
#                                    is_uploaded=False, id=id,
#                                    img_path='',
#                                    img_size='',
#                                    img_filename='',
#                                    img_width=0,
#                                    img_height=0,
#                                    img_upload_isvalid=False,
#                                    predicted_image='',
#                                    is_predicted=False,
#                                    is_error=True,
#                                    is_error_msg=msg
#                                    )


@app.errorhandler(413)
def request_entity_too_large(error):
    msg = "File Too Large - " + str(error)
    return render_template('sample.html',
                           is_uploaded=False, id=id,
                           img_path='',
                           img_size='',
                           img_filename='',
                           img_width=0,
                           img_height=0,
                           img_upload_isvalid=False,
                           predicted_image='',
                           is_predicted=False,
                           is_error=True,
                           is_error_msg=msg
                           )


@app.errorhandler(404)
def request_entity_too_large(error):
    msg = str(error)
    return render_template('sample.html',
                           is_uploaded=False, id=id,
                           img_path='',
                           img_size='',
                           img_filename='',
                           img_width=0,
                           img_height=0,
                           img_upload_isvalid=False,
                           predicted_image='',
                           is_predicted=False,
                           is_error=True,
                           is_error_msg=msg
                           )


if __name__ == '__main__':
    app.run()

# Run the web applicaion using "python app.py"
