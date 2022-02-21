import sqlite3 as sql
import datetime
from werkzeug.security import generate_password_hash as gph
dbname="test.db"
conn=sql.connect(dbname,timeout=1,check_same_thread=False)
cur=conn.cursor()
#cur.execute("CREATE TABLE prof(prof_id integer primary key autoincrement,user_id text NOT NULL,greet text,url text,birth text,loc text)")
#cur.execute("UPDATE user SET pass=? WHERE email='aaa@gmail.com'",(gph("aaa"),))
cur.execute("SELECT * FROM prof")
for row in cur:
    print(row)
#cur.execute("CREATE TABLE user(user_id text primary key,name text NOT NULL,hn text NOT NULL,email text NOT NULL,pass text NOT NULL,time text NOT NULL)")
#cur.execute("CREATE TABLE follow(follow_id integer primary key autoincrement,src_id text NOT NULL,dst_id text NOT NULL)")
#cur.execute("CREATE TABLE tl(ti_id integer primary key autoincrement,user_id text NOT NULL,msg text,time text NOT NULL)")
#cur.execute("CREATE TABLE dm(dm_id integer primary key autoincrement,src_id text NOT NULL,dst_id text NOT NULL,msg text NOT NULL,time text NOT NULL)")

#cur.execute("CREATE TABLE users(user_id integer primary key autoincrement,user_name text NOT NULL,pass text NOT NULL,perm integer NOT NULL,room text NOT NULL,num text,tick text,time text NOT NULL,loca text,tel text)")
#cur.execute("CREATE TABLE carte(carte_id integer primary key autoincrement,doc_id integer NOT NULL,pati_id integer NOT NULL,cont text NOT NULL)")
#cur.execute("CREATE TABLE pati(state_id integer primary key autoincrement,pati_id integer NOT NULL,temp real NOT NULL,press_max integer NOT NULL,press_min integer NOT NULL,spo2 integer NOT NULL,eat integer NOT NULL)")
#cur.execute("CREATE TABLE msgdoc(title_id integer primary key autoincrement,doc_id integer NOT NULL,pati_id integer NOT NULL,title text NOT NULL,msg text NOT NULL)")
#cur.execute("CREATE TABLE act(act_id integer primary key autoincrement,user_id integer NOT NULL,pati_id integer NOT NULL,title text NOT NULL,cont text NOT NULL)")
#cur.execute("CREATE TABLE call(call_id integer primary key autoincrement,nur_id integer NOT NULL,pati_id integer NOT NULL,call_cont text NOT NULL,act_cont text NOT NULL)")
#cur.execute("CREATE TABLE chro(chro_id integer primary key autoincrement,pati_id integer NOT NULL,cont text NOT NULL)")
#cur.execute("CREATE TABLE med(med_id integer primary key autoincrement,pati_id integer NOT NULL,med text NOT NULL)")
#cur.execute("CREATE TABLE msgnur(meg_id integer primary key autoincrement,nurse_id integer NOT NULL,title text NOT NULL,msg text NOT NULL)")
#cur.execute("CREATE TABLE test(test_id integer primary key autoincrement,user_id integer NOT NULL,pati_id integer NOT NULL,result text NOT NULL,time text NOT NULL)")
#cur.execute("CREATE TABLE ret(ret_id integer primary key autoincrement,doc_id integer NOT NULL,pati_id integer NOT NULL,day text NOT NULL,money integer NOT NULL)")
#cur.execute("ALTER TABLE ret ADD COLUMN time text")
#t=(str(datetime.datetime.today()))
#cur.execute("UPDATE pati SET time=? WHERE time is '' or time is null",(str(datetime.datetime.today()),))
#cur.execute("select * from chro")
#conn.commit()

#cur.execute("SELECT * FROM users WHERE mail=?","aaa@gmail.com")
#cur.execute("SELECT * FROM pati")
#cur.execute("DELETE FROM act WHERE act_id=2")
#cur.execute("PRAGMA table_info('msgdoc')")
#cur.execute("SELECT user_name FROM users WHERE user_id=?",(1,))
#for row in cur:
#    print(row)
conn.commit()
conn.close()