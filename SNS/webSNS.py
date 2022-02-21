from flask import Flask,request,render_template,session,redirect
from werkzeug.security import generate_password_hash as gph
from werkzeug.security import check_password_hash as cph
from datetime import timedelta
import sqlite3 as sql
import secrets
import html
import datetime

dbname="test.db"

#サービススタート
app = Flask(__name__)

#セッション
#シークレットキー
app.secret_key=secrets.token_urlsafe(16)
#60分間セッションを維持
app.permanent_session_lifetime=timedelta(minutes=60)

#共通画面
@app.route("/")
def non():
    return redirect("login")

#新規登録
@app.route("/new",methods=["GET","POST"])
def new():
    if request.method=="GET":
        return render_template("new.html")
    elif request.method=="POST":
        email=str(request.form["email"])
        name=str(request.form["name"])
        passw=str(request.form["passw"])
        hn=str(request.form["hn"])
        conn=sql.connect(dbname,check_same_thread=False)
        cur=conn.cursor()
        cur.execute("SELECT user_id FROM user WHERE email=?",(email,))
        data=[]
        for row in cur:
            data.append(row[0])
        conn.close()
        if len(data)>0:
            return render_template("new.html")
        target="@"
        idx=email.find(target)
        user_id=email[:idx]
        passw=gph(passw)
        conn=sql.connect(dbname,check_same_thread=False)
        cur=conn.cursor()
        cur.execute("INSERT INTO user (user_id,name,hn,email,pass,time) VALUES (?,?,?,?,?,?)",(user_id,name,hn,email,passw,str(datetime.datetime.today())))
        conn.commit()
        conn.close()
        conn=sql.connect(dbname,check_same_thread=False)
        cur=conn.cursor()
        cur.execute("INSERT INTO prof (user_id) VALUES (?)",(user_id,))
        conn.commit()
        conn.close()
        session["user_id"]=user_id
        session["hn"]=hn
        return redirect("home")

#ログイン画面
@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="GET":
        return render_template("login.html") 
    elif request.method=="POST":
        email=str(request.form["email"])
        passw=str(request.form["pass"])
        conn=sql.connect(dbname,check_same_thread=False)
        cur=conn.cursor()
        cur.execute("SELECT user_id,pass,hn FROM user WHERE email=?",(email,))
        data=[]
        for row in cur:
            data.append(row[0])
            data.append(row[1])
            data.append(row[2])
        conn.close()
        if len(data)==0:
            return render_template("loginmiss.html")
        if cph(data[1],html.escape(passw)):
            session["user_id"]=data[0]
            session["hn"]=data[2]
            return redirect("home")
        else:
            return render_template("loginmiss.html")

#プロフィールページ
@app.route("/home")
def home():
    if "user_id" in session:
        if (request.args.get("user_id") is None) or str(request.args.get("user_id"))==session["user_id"]:#自分
            conn=sql.connect(dbname,check_same_thread=False)
            cur=conn.cursor()
            cur.execute("SELECT greet,url,birth,loc FROM prof where user_id=?",(session["user_id"],))
            greet=""
            url=""
            birth=""
            loc=""
            for row in cur:
                greet="" if row[0]==None else row[0]
                url="" if row[1]==None else row[1]
                birth="" if row[2]==None else row[2]
                loc="" if row[3]==None else row[3]
            conn.close()
            edit="<a href=\"prof\">プロフィールを編集</a>"
            #print(data)
            dm=html.escape(session["user_id"])
            return render_template("home.html",dm=dm,user_id=html.escape(session["user_id"]),user_name=html.escape(session["hn"]+"@"+session["user_id"]),greet=html.escape(greet),url=html.escape(url),birth=html.escape(birth),loc=html.escape(loc),edit=edit)
        else:#他人
            conn=sql.connect(dbname,check_same_thread=False)
            cur=conn.cursor()
            cur.execute("SELECT greet,url,birth,loc FROM prof where user_id=?",(request.args.get("user_id"),))
            greet=""
            url=""
            birth=""
            loc=""
            for row in cur:
                greet="" if row[0]==None else row[0]
                url="" if row[1]==None else row[1]
                birth="" if row[2]==None else row[2]
                loc="" if row[3]==None else row[3]
            conn.close()
            conn=sql.connect(dbname,check_same_thread=False)
            cur=conn.cursor()
            cur.execute("SELECT hn FROM user WHERE user_id=?",(request.args.get("user_id"),))
            name=""
            for row in cur:
                name=row[0]
            conn.close()
            if (request.args.get("src") is not None) and (request.args.get("dst") is not None):
                conn=sql.connect(dbname,check_same_thread=False)
                cur=conn.cursor()
                cur.execute("SELECT follow_id FROM follow WHERE src_id=? AND dst_id=?",(request.args.get("src"),request.args.get("dst")))
                data=[]
                for row in cur:
                    data.append(row[0])
                conn.close()
                if len(data)>0:
                    conn=sql.connect(dbname,check_same_thread=False)
                    cur=conn.cursor()
                    cur.execute("DELETE FROM follow WHERE src_id=? AND dst_id=?",(request.args.get("src"),request.args.get("dst")))
                    conn.commit()
                    conn.close()
                else:
                    conn=sql.connect(dbname,check_same_thread=False)
                    cur=conn.cursor()
                    cur.execute("INSERT INTO follow (src_id,dst_id) VALUES (?,?)",(request.args.get("src"),request.args.get("dst")))
                    conn.commit()
                    conn.close()
            conn=sql.connect(dbname,check_same_thread=False)
            cur=conn.cursor()
            cur.execute("SELECT follow_id FROM follow WHERE src_id=? AND dst_id=?",(session["user_id"],request.args.get("user_id")))
            data=[]
            for row in cur:
                data.append(row[0])
            conn.close()
            if len(data)>0:
                fol="フォローを外す"
            else:
                fol="フォローする"    
            edit="<a href=\"home?user_id="+html.escape(request.args.get("user_id"))+"&src="+html.escape(session["user_id"])+"&dst="+html.escape(request.args.get("user_id"))+"\">"+fol+"</a>"
            dm=html.escape(request.args.get("user_id"))
            return render_template("home.html",dm=dm,user_id=html.escape(request.args.get("user_id")),user_name=html.escape(name+"@"+request.args.get("user_id")),greet=html.escape(greet),url=html.escape(url),birth=html.escape(birth),loc=html.escape(loc),edit=edit)
    else:
        return redirect("login")

#プロフィール編集
@app.route("/prof",methods=["GET","POST"])
def prof():
    if "user_id" in session:
        if request.method=="GET":
            token=secrets.token_hex()
            session["prof"]=token
            conn=sql.connect(dbname,check_same_thread=False)
            cur=conn.cursor()
            cur.execute("SELECT greet,url,birth,loc FROM prof WHERE user_id=?",(session["user_id"],))
            greet=""
            url=""
            birth=""
            loc=""
            for row in cur:
                greet=row[0]
                url=row[1]
                birth=row[2]
                loc=row[3]
            conn.close()
            return render_template("prof.html",token=html.escape(token),greet=html.escape(greet),url=html.escape(url),birth=html.escape(birth),loc=html.escape(loc))
        elif request.method=="POST":
            if session["prof"]==request.form["prof"]:
                greet=request.form["greet"]
                url=request.form["url"]
                birth=request.form["birth"]
                loc=request.form["loc"]
                conn=sql.connect(dbname,check_same_thread=False)
                cur=conn.cursor()
                cur.execute("SELECT user_id FROM prof WHERE user_id=?",(session["user_id"],))
                data=[]
                for row in cur:
                    data.append(row[0])
                if len(data)>0:
                    conn=sql.connect(dbname,check_same_thread=False)
                    cur=conn.cursor()
                    cur.execute("UPDATE prof SET greet=?,url=?,birth=?,loc=? WHERE user_id=?",(greet,url,birth,loc,session["user_id"]))
                    conn.commit()
                    conn.close()
                else:
                    conn=sql.connect(dbname,check_same_thread=False)
                    cur=conn.cursor()
                    cur.execute("INSERT INTO prof (greet,url,birth,loc,user_id) VALUES(?,?,?,?,?)",(greet,url,birth,loc,session["user_id"]))
                    conn.commit()
                    conn.close()
                return redirect("home")
            else:
                return redirect("home")
    else:
        return redirect("login")

#フォロー
@app.route("/follow")
def follow():
    if "user_id" in session:
        user_id=""
        if request.args.get("user_id") is not None:
            user_id=request.args.get("user_id")
        else:
            user_id=session["user_id"]
        conn=sql.connect(dbname,check_same_thread=False)
        cur=conn.cursor()
        cur.execute("SELECT dst_id FROM follow WHERE src_id=?",(user_id,))
        data=[]
        tmp=[]
        for row in cur:
            cur2=conn.cursor()
            cur2.execute("SELECT hn FROM user WHERE user_id=?",(row[0],))
            for col in cur2:
                tmp.append(col[0])
            cur2.execute("SELECT greet FROM prof WHERE user_id=?",(row[0],))
            i=0
            for col in cur2:
                i=1
                tmp.append(col[0])
            if i==0:
                tmp.append(" ")
            tmp.append(row[0])
            data.append(tmp)
            tmp=[]
        conn.close()
        res=""
        for i in range(len(data)):
            res=res+"\t<tr><td>ハンドルネーム</td><td><a href=\"home?user_id="+html.escape(data[i][2])+"\">"+html.escape(data[i][0])+"</td><td><a href=\"dm?user_id="+html.escape(data[i][2])+"\">DM</a></td></tr>\n"
            res=res+"\t<tr><td colspan=\"3\"><pre>"+html.escape(data[i][1])+"</pre></td></tr>\n"
        return render_template("follow.html",user_id=html.escape(user_id),res=res)
    else:
        return redirect("login")

#フォワー
@app.route("/follower")
def follower():
    if "user_id" in session:
        user_id=""
        if request.args.get("user_id") is not None:
            user_id=request.args.get("user_id")
        else:
            user_id=session["user_id"]
        conn=sql.connect(dbname,check_same_thread=False)
        cur=conn.cursor()
        cur.execute("SELECT src_id FROM follow WHERE dst_id=?",(user_id,))
        data=[]
        tmp=[]
        for row in cur:
            cur2=conn.cursor()
            cur2.execute("SELECT hn FROM user WHERE user_id=?",(row[0],))
            for col in cur2:
                tmp.append(col[0])
            cur2.execute("SELECT greet FROM prof WHERE user_id=?",(row[0],))
            i=0
            for col in cur2:
                i=1
                tmp.append(col[0])
            if i==0:
                tmp.append(" ")
            tmp.append(row[0])
            data.append(tmp)
            tmp=[]
        conn.close()
        res=""
        for i in range(len(data)):
            res=res+"\t<tr><td>ハンドルネーム</td><td><a href=\"home?user_id="+html.escape(data[i][2])+"\">"+html.escape(data[i][0])+"</td><td><a href=\"dm?user_id="+html.escape(data[i][2])+"\">DM</a></td></tr>\n"
            res=res+"\t<tr><td colspan=\"3\"><pre>"+html.escape(data[i][1])+"</pre></td></tr>\n"
        return render_template("follower.html",user_id=html.escape(user_id),res=res)
    else:
        return redirect("login")    

#ユーザ探し
@app.route("/find")
def find():
    if "user_id" in session:
        data=[]
        tmp=[]
        conn=sql.connect(dbname,check_same_thread=False)
        cur=conn.cursor()
        if request.args.get("key") is None:#キーワードが無い時
            cur.execute("SELECT greet,user_id FROM prof")
        else:#キーワードがある時
            key=request.args.get("key")
            cur.execute("SELECT greet,user_id FROM prof WHERE greet like ? OR user_id like ? OR loc like ?",("%"+key+"%","%"+key+"%","%"+key+"%"))
        for row in cur:
            tmp.append("" if row[0]==None else row[0])
            tmp.append(row[1])
            cur2=conn.cursor()
            cur2.execute("SELECT hn FROM user WHERE user_id=?",(row[1],))
            for col in cur2:
                tmp.append(tmp.append(col[0]))
            data.append(tmp)
            tmp=[]
        res=""
        for i in range(len(data)):
            res=res+"\t<tr><td>ハンドルネーム</td><td><a href=\"home?user_id="+html.escape(data[i][1])+"\">"+html.escape(data[i][2])+"</td><td><a href=\"dm?user_id="+html.escape(data[i][1])+"\">DM</a></td></tr>\n"
            res=res+"\t<tr><td colspan=\"3\"><pre>"+html.escape(data[i][0])+"</pre></td></tr>\n"
        return render_template("find.html",res=res)
    else:
        return redirect("login")
#TL

#DM相手
@app.route("/dmfind")
def dmfind():
    if "user_id" in session:
        data=[]
        tmp=[]
        conn=sql.connect(dbname,check_same_thread=False)
        cur=conn.cursor()
        if request.args.get("key") is None:#キーワードが無い時
            cur.execute("SELECT greet,user_id FROM prof")
        else:#キーワードがある時
            key=request.args.get("key")
            cur.execute("SELECT greet,user_id FROM prof WHERE greet like ? OR user_id like ? OR loc like ?",("%"+key+"%","%"+key+"%","%"+key+"%"))
        for row in cur:
            tmp.append("" if row[0]==None else row[0])
            tmp.append(row[1])
            cur2=conn.cursor()
            cur2.execute("SELECT hn FROM user WHERE user_id=?",(row[1],))
            for col in cur2:
                tmp.append(tmp.append(col[0]))
            data.append(tmp)
            tmp=[]
        res=""
        for i in range(len(data)):
            res=res+"\t<tr><td>ハンドルネーム</td><td><a href=\"dm?user_id="+html.escape(data[i][1])+"\">"+html.escape(data[i][2])+"</td></tr>\n"
            res=res+"\t<tr><td colspan=\"2\"><pre>"+html.escape(data[i][0])+"</pre></td></tr>\n"
        return render_template("dmfind.html",res=res)
    else:
        return redirect("login")

#DM
@app.route("/dm",methods=["GET","POST"])
def dm():
    if "user_id" in session:
        if request.method=="GET":
            if request.args.get("user_id") is None:
                return redirect("dmfind")
            token=secrets.token_hex()
            session["dm"]=token
            user_id=request.args.get("user_id")
            conn=sql.connect(dbname,check_same_thread=False)
            cur=conn.cursor()
            cur.execute("SELECT src_id,dst_id,msg,time FROM dm WHERE src_id=? AND dst_id=? OR src_id=? AND dst_id=?",(session["user_id"],user_id,user_id,session["user_id"]))
            src=[]
            src_hn=[]
            dst=[]
            dst_hn=[]
            msg=[]
            time=[]
            for row in cur:
                src.append(row[0])
                dst.append(row[1])
                msg.append(row[2])
                time.append(row[3])
                cur2=conn.cursor()
                cur2.execute("SELECT hn FROM user WHERE user_id=?",(row[0],))
                for col in cur2:
                    src_hn.append(col[0])
                cur2.execute("SELECT hn FROM user WHERE user_id=?",(row[1],))
                for col in cur2:
                    dst_hn.append(col[0])
            conn.close()
            res=""
            for i in range(len(src_hn)):
                if src_hn[i]==session["hn"]:
                    res=res+"<tr><td></td><td bgcolor=#00FF00><pre>"+html.escape(msg[i])+"</pre></td><td bgcolor=#00FF00>"+html.escape(src_hn[i])+"</td></tr>"
                    res=res+"<tr><td></td><td colspan=\"2\" align=\"right\" bgcolor=#00FF00>"+str(time)[2:21]+"</td></tr>"
                else:
                    res=res+"<tr><td>"+html.escape(src_hn[i])+"</td><td><pre>"+html.escape(msg[i])+"</pre></td><td></td></tr>"
                    res=res+"<tr><td colspan=\"2\" align=\"left\">"+str(time)[2:21]+"</td><td></td></tr>"
            return render_template("dm.html",res=res,token=token,src_id=session["user_id"],dst_id=user_id)
        elif request.method=="POST":
            if session["dm"]==request.form["dm"]:
                token=secrets.token_hex()
                session["dm"]=token
                user_id=request.form["dst_id"]
                conn=sql.connect(dbname,check_same_thread=False)
                cur=conn.cursor()
                cur.execute("INSERT INTO dm (src_id,dst_id,msg,time) VALUES (?,?,?,?)",(session["user_id"],user_id,request.form["text"],str(datetime.datetime.today())))
                conn.commit()
                conn.close()
                conn=sql.connect(dbname,check_same_thread=False)
                cur=conn.cursor()
                cur.execute("SELECT src_id,dst_id,msg,time FROM dm WHERE src_id=? AND dst_id=? OR src_id=? AND dst_id=?",(session["user_id"],user_id,user_id,session["user_id"]))
                src=[]
                src_hn=[]
                dst=[]
                dst_hn=[]
                msg=[]
                time=[]
                for row in cur:
                    src.append(row[0])
                    dst.append(row[1])
                    msg.append(row[2])
                    time.append(row[3])
                    cur2=conn.cursor()
                    cur2.execute("SELECT hn FROM user WHERE user_id=?",(row[0],))
                    for col in cur2:
                        src_hn.append(col[0])
                    cur2.execute("SELECT hn FROM user WHERE user_id=?",(row[1],))
                    for col in cur2:
                        dst_hn.append(col[0])
                conn.close()
                res=""
                for i in range(len(src_hn)):
                    if src_hn[i]==session["hn"]:
                        res=res+"<tr><td></td><td bgcolor=#00FF00><pre>"+html.escape(msg[i])+"</pre></td><td bgcolor=#00FF00>"+html.escape(src_hn[i])+"</td></tr>"
                        res=res+"<tr><td></td><td colspan=\"2\" align=\"right\" bgcolor=#00FF00>"+str(time)[2:21]+"</td></tr>"
                    else:
                        res=res+"<tr><td>"+html.escape(src_hn[i])+"</td><td><pre>"+html.escape(msg[i])+"</pre></td><td></td></tr>"
                        res=res+"<tr><td colspan=\"2\" align=\"left\">"+str(time)[2:21]+"</td><td></td></tr>"
                return render_template("dm.html",res=res,token=token,src_id=session["user_id"],dst_id=user_id)
            else:
                return redirect("dmfind")
    else:
        return redirect("login")

#dm_ajax
@app.route("/dm_ajax")
def dm_ajax():
    conn=sql.connect(dbname,check_same_thread=False)
    cur=conn.cursor()
    src_id=request.args.get("src_id")
    dst_id=request.args.get("dst_id")
    cur.execute("SELECT src_id,dst_id,msg,time FROM dm WHERE src_id=? AND dst_id=? OR src_id=? AND dst_id=?",(src_id,dst_id,dst_id,src_id))
    src=[]
    src_hn=[]
    dst=[]
    dst_hn=[]
    msg=[]
    time=[]
    for row in cur:
        src.append(row[0])
        dst.append(row[1])
        msg.append(row[2])
        time.append(row[3])
        cur2=conn.cursor()
        cur2.execute("SELECT hn FROM user WHERE user_id=?",(row[0],))
        for col in cur2:
            src_hn.append(col[0])
        cur2.execute("SELECT hn FROM user WHERE user_id=?",(row[1],))
        for col in cur2:
            dst_hn.append(col[0])
    conn.close()
    res="<table align=\"center\">"
    for i in range(len(src_hn)):
        if src_hn[i]==session["hn"]:
            res=res+"<tr><td></td><td bgcolor=#00FF00><pre>"+html.escape(msg[i])+"</pre></td><td bgcolor=#00FF00>"+html.escape(src_hn[i])+"</td></tr>"
            res=res+"<tr><td></td><td colspan=\"2\" align=\"right\" bgcolor=#00FF00>"+str(time)[2:21]+"</td></tr>"
        else:
            res=res+"<tr><td>"+html.escape(src_hn[i])+"</td><td><pre>"+html.escape(msg[i])+"</pre></td><td></td></tr>"
            res=res+"<tr><td colspan=\"2\" align=\"left\">"+str(time)[2:21]+"</td><td></td></tr>"
    res=res+"</table>"
    return res
        
#掲示板(

#クリックジャッキング
@app.after_request
def apply_caching(response):
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0")
