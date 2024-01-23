from crypt import methods
from fileinput import filename
from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import FileField, validators
from flask_uploads import configure_uploads, IMAGES, UploadSet
from PIL import Image, ImageDraw, ImageFont
import PIL
import os
import sys
import face_recognition
from datetime import datetime

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret123'
app.config['UPLOADED_IMAGES_DEST'] = 'static/uploads/findfacesimage/'

images = UploadSet('images', IMAGES)
configure_uploads(app, images)


class FindFaceForm(FlaskForm):
    image = FileField('image')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/findfaces/', methods=['GET', 'POST'])
def findfaces():
    form = FindFaceForm()

    if request.method == 'POST' and form.validate():

        # Create folder with folder name = timestamp to store the pulled faces:
        datenow = datetime.now()
        date_time = datenow.strftime("%Y%m%d%H%M%S%p")
        print(date_time)
        folder_name = "filename"+date_time
        parent_dir = "static/uploads/findfacesimage/"
        path = os.path.join(parent_dir, folder_name)
        os.makedirs(path)
        image_path = parent_dir+folder_name
        # format: static/uploads/findfacesimage/filename20220424213140PM

        # Save image uploaded with filename = image file name
        ogirinal_filename = images.save(form.image.data)

        # Load the image just stored and detect the coordinates of each face (face_recognition) --> (top,right,bottom,left)
        ogirinal_image = face_recognition.load_image_file(
            './static/uploads/findfacesimage/'+ogirinal_filename)
        face_locations = face_recognition.face_locations(ogirinal_image)

        # Count number of people in the image:
        num_of_people = len(face_locations)

        # Create an empty array to store face file name. E.g. [(89, 79, 132, 36), (94, 429, 137, 386)]
        img_array = []

        # Pull and save each face in the image into static/uploads/pullfaces folder:
        for face_location in face_locations:

            top, right, bottom, left = face_location

            face_image = ogirinal_image[top:bottom, left:right]

            pil_image = Image.fromarray(face_image)
            # pil_image.show()

            pil_image.save(f"{image_path}/{top, right, bottom, left}.png")

            img_array.append(face_location)

        return render_template('findfacesresult.html', ogirinal_filename=ogirinal_filename, num_of_people=num_of_people, folder_name=folder_name, img_array=img_array)

    return render_template('findfaces.html', form=form)


@app.route('/display/<ogirinal_filename>')
def display_image(ogirinal_filename):
    return redirect(url_for('static', filename='uploads/findfacesimage/' + ogirinal_filename))


@app.route('/identify/', methods=['GET', 'POST'])
def identify():
    form = FindFaceForm()

    if request.method == 'POST' and form.validate():

        # Save image uploaded with filename = image file name
        ogirinal_filename = images.save(form.image.data)

        image_of_bill = face_recognition.load_image_file(
            './img/known/Bill Gates.jpg')
        bill_face_encoding = face_recognition.face_encodings(image_of_bill)[0]

        image_of_steve = face_recognition.load_image_file(
            './img/known/Steve Jobs.jpg')
        steve_face_encoding = face_recognition.face_encodings(image_of_steve)[
            0]

        image_of_obama = face_recognition.load_image_file(
            './img/known/Barack Obama.jpg')
        obama_face_encoding = face_recognition.face_encodings(image_of_obama)[
            0]

        image_of_trump = face_recognition.load_image_file(
            './img/known/Donald Trump.jpg')
        trump_face_encoding = face_recognition.face_encodings(image_of_trump)[
            0]

        # Create array of encodings and names
        known_face_encodings = [
            bill_face_encoding,
            steve_face_encoding,
            obama_face_encoding,
            trump_face_encoding
        ]

        known_face_names = [
            "Bill Gates",
            "Steve Jobs",
            "Barack Obama",
            "Donald Trump"
        ]

        # Load test image to find faces in
        test_image = face_recognition.load_image_file(
            './static/uploads/findfacesimage/'+ogirinal_filename)

        # Find faces in test image
        face_locations = face_recognition.face_locations(test_image)
        face_encodings = face_recognition.face_encodings(
            test_image, face_locations)

        # Convert to PIL format
        pil_image = Image.fromarray(test_image)

        # Create a ImageDraw instance
        draw = ImageDraw.Draw(pil_image)

        # Loop through faces in the test image
        for(top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(
                known_face_encodings, face_encoding)

            name = "Unknown"

            # If match:
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]

            # Draw the box:
            draw.rectangle(((left, top), (right, bottom)), outline=(0, 0, 0))

            # Draw label:
            text_width, text_height = draw.textsize(name)
            print(text_width)
            print(text_height)
            font = ImageFont.truetype("./static/font/arial.ttf", size=25)
            draw.rectangle(((left, bottom - text_height - 35),
                            (right, bottom)), fill=(0, 0, 0), outline=(0, 0, 0))
            draw.text((left+6, bottom - text_height - 25),
                      name, fill=(255, 255, 255, 255), font=font)

        del draw

        # Save image:
        pil_image.save(f'static/uploads/identifyface/' +
                       ogirinal_filename+'_identify.png')

        return render_template('identifyresult.html', ogirinal_filename=ogirinal_filename)

    return render_template('identify.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
