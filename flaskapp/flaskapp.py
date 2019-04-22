
import cgi,cgitb,wave
import glob
from Model import evaluate
import os, glob, time, operator
from flask import Flask, Response,render_template
from flask import request
from flask_jsglue import JSGlue
app = Flask(__name__,template_folder='view')
jsglue = JSGlue(app)
@app.route('/')
def hello_world():
  return render_template("index.html")
if __name__ == '__main__':
   app.run()

@app.route('/record', methods=["GET", "POST"])
def record():
    if request.method =='POST':
        scene = request.form["scene"]
        print("TEST"+ scene)
        return render_template("record.html", scene = scene)
@app.route('/realRecord', methods=["GET", "POST"])
def realRecord():
    return render_template("realRecord.html")
# @app.route('/result', methods=["GET", "POST"])
# def result():
#     resultPath= request.args.get("resultPath")
#     return render_template("result.html", resultPath = resultPath)
@app.route("/saveAudio", methods=['GET','POST'])
def hello2():
    if request.method =='POST':
        #form = cgi.FieldStorage()
        fname = request.files['audio_data'].filename 
        blob = request.files['audio_data']

        returnV="";       
        returnR="";


        path = '/home/ubuntu/flaskapp/static/audio/*'
        list_of_files = glob.glob(path) # * means all if need specific format then *.csv
        sorted_files = sorted(list_of_files, key=os.path.getctime)


        print("TESTING2: "+sorted_files[-1])

        audio = open('/home/ubuntu/flaskapp/static/audio/'+"real_"+fname+'.wav', 'wb')
        audio.write(blob.read())

        returnV = 'audio/'+"real_"+fname+'.wav'
        returnR = '/home/ubuntu/flaskapp/static/audio/'+"real_"+fname+'.wav'

        print("TESTING1:" + returnR)

        #evaluate(sorted_files[-1],returnR)
        resultFile, score, mono, tony = evaluate(sorted_files[-1],returnR)

        f = open(resultFile)
        text = f.read()
        f.close()
        f=open(resultFile,'w')
        f.write("time,pitch,volume\n")
        f.write(text)
        f.close()
        filename = os.path.basename(resultFile)
        resultFile = 'RealResult/' + filename
        print("resultFILE "+resultFile)

        score = int(score*100)
        print(score)
 
        return render_template('/result.html', path = returnV, resultPath = resultFile, score=score,mono=mono, tony=tony)


       
@app.route("/saveBase", methods=['GET','POST'])
def base():
    if request.method =='POST':
        fname = request.files['audio_data'].filename 
        blob = request.files['audio_data']
        returnV="";       
        returnR="";
        audio = open('/home/ubuntu/flaskapp/static/audio/'+"base_"+fname+'.wav', 'wb')
        audio.write(blob.read())
        returnV = '/audio/'+"base_"+fname+'.wav'
        returnB = '/home/ubuntu/flaskapp/static/audio/'+"base_"+fname+'.wav'
        print("HELLO TESTING")
        return render_template("realRecord.html")

# if __name__ == '__main__':
#   app.run()
