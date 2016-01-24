from flask import Flask, render_template, request, session, redirect, url_for, Markup
import module

app = Flask(__name__)

@app.route("/",methods=['GET','POST'])
def home():
    if 'logged' not in session:
        session['logged']=False
    if request.method=="GET":
        if (session['logged']):
            username = session['username']
            firewood = module.getFirewood(username)
            essays = module.getEssayLinks(username)
            e = ''
            for item in essays:
                if (module.getNewEdits(item) >= 1):
                    e = 'Your essay has been edited!'
            return render_template("home.html",s=session,f=firewood,error=e)
        else:
            firewood=0
            return render_template("home.html",s=session,f=firewood)
    if request.method=="POST":
        button = request.form['button']
        if (button=="Login"):
            username = request.form['username']
            password = request.form['password']
            if (module.authenticate(username,password)):
                session['logged']=True
                session['username'] = username
                firewood = module.getFirewood(session['logged'])
                return render_template("home.html",s=session,f=firewood)
            else:
                return render_template('home.html',s=session,error='Incorrect username or password')
        if (button=="Signup"):
            username = request.form['username']
            password = request.form['password']
            if module.newUser(username,password):
                session['logged']=True
                session['username'] = username
                return render_template('home.html',s=session,error='You have successfully created an account!')
            else:
                return render_template('home.html',s=session,error='Invalid username or password')
        if (button=="Submit"):
            link = request.form['link']
            '''
            title = request.form['title']
            description = request.form['description']
            essay = request.form['essay']
            wordCount = str(module.wordCounter(essay))
            
            if (module.addEssay(title,session['logged'],module.wordCounter(essay),description,essay)):
            '''
            if (module.addEssay(session['username'],link)):
                username = session['username']
                firewood = module.getFirewood(username)
                newFirewood = firewood - 10
                if (firewood >= 10):
                    if (module.setFirewood(username,newFirewood)):
                        module.setToEdit(username,module.getRandomEssay(username))
                        return render_template('home.html',s=session,error='Essay successfully submitted!')
                else:
                    return render_template('home.html',s=session,error='Not enough firewood!')
            else:
                return render_template('home.html',s=session,error='Error with submitting essay')
        if (button=="Logout"):
            session['logged'] = False
            session['username'] = None
            return render_template('home.html')

#When a user clicks a button to logout, direct them here, log them out and redirect them
@app.route('/logout',methods=['GET','POST'])
def logout():
    session['logged'] = False
    return redirect('/')

@app.route('/youressays',methods=['GET','POST'])
def youressays():
    if request.method=="GET":
        essays = module.getEssayLinks(session['username'])
        return render_template('youressays.html',e=essays,allEssays=True)
    if request.method=="POST":
        button = request.form['button']
        if (button == '0' or button == '1' or button == '2' or button == '3' or button == '4' or button == '5'):
            essay = request.form['submit']
            editor = module.getEditor(essay)
            oldFirewood = module.getFirewood(editor)
            payment = int(button)
            if (module.setFirewood(editor,oldFirewood+payment)):
                module.setNewEdits(essay,0)
                return render_template('home.html',s=session,error='Thank you for rating the edit!')
            else:
                return render_template('home.html',s=session,error='Something went wrong while rating the edit :(')
        else:
            rate = False
            if (module.getNewEdits(button) == 1):
                rate = True
            return render_template('youressays.html',essay=button,allEssays=False,r=rate)
         
@app.route('/edit',methods=['GET','POST'])
def edit():
    if request.method=="GET":
        if (session['logged']):
            essay = module.getToEdit(session['username'])
        else:
            essay = ''
        if (essay == ''):
            return render_template('editothers.html',box=False)
        else:
            return render_template('editothers.html',e=essay,box=True)
    if request.method=="POST":
        button = request.form['button']
        if (button=="Submit"):
            username = session['username']
            essay = module.getToEdit(username)
            edited = module.getTimesEdited(essay) + 1
            if (module.setTimesEdited(essay,edited)):
                firewood = module.getFirewood(username)
                newFirewood = firewood + 5
                module.setFirewood(username,newFirewood)
                oldEdits = module.getNewEdits(essay)
                module.setNewEdits(essay,oldEdits+1)
                module.setToEdit(session['username'],'')
                return render_template('home.html',s=session,error='Thank you for editing the essay! You have earned 5 firewood!')
            else:
                return render_template('home.html',s=session,error='Something went wrong while trying to submit the essay edits :(')

app.secret_key="Don't tell anyone!"

@app.route('/browse',methods=['GET','POST'])
def browse():
    if request.method=="GET":
        username = session['username']
        essays = module.getAllEssayLinks(username)
        return render_template('browse.html',e=essays,browsing=True)
    if request.method=="POST":
        button = request.form['button']
        return render_template('browse.html',e=button,browsing=False)


if __name__=="__main__":
    app.debug = True
    app.run('0.0.0.0', port=8000)
