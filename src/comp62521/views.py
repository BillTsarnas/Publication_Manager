from comp62521 import app
from database import database
from flask import (render_template, request)
from operator import itemgetter
import json
from flask import Response

sorted_before = [False, False, False, False, False, False, False, False, False]
cooth_sorted_before = [False, False]
def sort_col(inp, num_col):
    global sorted_before
    if sorted_before[num_col]:
        sorted_before[num_col] = False
        return sorted(inp, key=itemgetter(int(num_col)))
    else:
        sorted_before[num_col] = True
        return sorted(inp, key=itemgetter(int(num_col)), reverse=True)

def sort_by_sur(tmp, num_col):
    global sorted_before
    app.debug = True
    #sort by sur only if the first col is clicked
    if num_col == 0:
        for auth in tmp:
            full_name = auth[0].split()
            if full_name[-1].startswith('('):
                full_name.pop()
            if full_name[-1].isdigit():
                full_name[-2] = full_name[-2] + " " + full_name[-1]
                full_name.pop()
            auth.insert(0,full_name[-1])
        y = sort_col(tmp, 0)
        for auth in y:
            auth.pop(0)
    else:
        y = sort_col(tmp, num_col)
    return y

def sort_by_precedence(inp, author):

    gl_exactNstart_match, gl_substr_match, gl_no_match = [],[],inp

    for i in range(-1,2):
        print '!!!!!!!!!!' + str(i)
        exact_match, start_match, substr_match, no_match = [],[],[],[]
        auth_key = author.lower()
        for auth in gl_no_match:
            full_name_raw = auth[0].split()
            if i == -1:
                full_name_raw = [' '.join(full_name_raw[:-1]), full_name_raw[-1]]
            elif i == 0:
                full_name_raw = auth[0].split()
            elif i == 1:
                full_name_raw = [full_name_raw[0],' '.join(full_name_raw[1:-1]),full_name_raw[-1]]

            full_name = auth[0].lower().split()

            if full_name[i] == auth_key:
                exact_match.append(full_name_raw)
	    elif full_name[i].startswith(auth_key):
                start_match.append(full_name_raw)
            elif auth_key in full_name[i]:
                substr_match.append(full_name_raw)
            else:
                no_match.append(full_name_raw)

	if(i==-1):
	    y=0
	elif(i==0 or i==1):
	    y=-1
        exact_match = sorted(exact_match, key=itemgetter(i,y, 1))
        start_match = sorted(start_match, key=itemgetter(i,y, 1))
        substr_match = sorted(substr_match, key=itemgetter(i,y, 1))

        exact_match1, start_match1, substr_match1, no_match1 = [],[],[],[]
        for auth in exact_match:
            exact_match1.append([' '.join(auth)])
        for auth in start_match:
            start_match1.append([' '.join(auth)])
        for auth in substr_match:
            substr_match1.append([' '.join(auth)])
        for auth in no_match:
            no_match1.append([' '.join(auth)])

        gl_exactNstart_match += exact_match1  + start_match1
        gl_substr_match += substr_match1
        gl_no_match = no_match1[:]

    return gl_exactNstart_match + gl_substr_match + gl_no_match

def format_data(data):
    fmt = "%.2f"
    result = []
    for item in data:
        if type(item) is list:
            result.append(", ".join([ (fmt % i).rstrip('0').rstrip('.') for i in item ]))
        else:
            result.append((fmt % item).rstrip('0').rstrip('.'))
    return result

@app.route("/averages")
def showAverages():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset":dataset, "id":"averages"}
    args['title'] = "Averaged Data"
    tables = []
    headers = ["Average", "Conference Paper", "Journal", "Book", "Book Chapter", "All Publications"]
    averages = [ database.Stat.MEAN, database.Stat.MEDIAN, database.Stat.MODE ]
    tables.append({
        "id":1,
        "title":"Average Authors per Publication",
        "header":headers,
        "rows":[
                [ database.Stat.STR[i] ]
                + format_data(db.get_average_authors_per_publication(i)[1])
                for i in averages ] })
    tables.append({
        "id":2,
        "title":"Average Publications per Author",
        "header":headers,
        "rows":[
                [ database.Stat.STR[i] ]
                + format_data(db.get_average_publications_per_author(i)[1])
                for i in averages ] })
    tables.append({
        "id":3,
        "title":"Average Publications in a Year",
        "header":headers,
        "rows":[
                [ database.Stat.STR[i] ]
                + format_data(db.get_average_publications_in_a_year(i)[1])
                for i in averages ] })
    tables.append({
        "id":4,
        "title":"Average Authors in a Year",
        "header":headers,
        "rows":[
                [ database.Stat.STR[i] ]
                + format_data(db.get_average_authors_in_a_year(i)[1])
                for i in averages ] })

    args['tables'] = tables
    return render_template("averages.html", args=args)

@app.route("/coauthors")
def showCoAuthors():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    PUB_TYPES = ["Conference Papers", "Journals", "Books", "Book Chapters", "All Publications"]
    args = {"dataset":dataset, "id":"coauthors"}
    args["title"] = "Co-Authors"

    start_year = db.min_year
    if "start_year" in request.args:
        start_year = int(request.args.get("start_year"))

    end_year = db.max_year
    if "end_year" in request.args:
        end_year = int(request.args.get("end_year"))

    pub_type = 4
    if "pub_type" in request.args:
        pub_type = int(request.args.get("pub_type"))

    num_col = request.args.get('num_col')
    if num_col != None:
        y1 = db.get_coauthor_data(start_year, end_year, pub_type)[0]
        y2 = sort_by_sur(db.get_coauthor_data(start_year, end_year, pub_type)[1], int(num_col))
        args["data"] = (y1,y2)
    else:
        args["data"] = db.get_coauthor_data(start_year, end_year, pub_type)
    
    args["start_year"] = start_year
    args["end_year"] = end_year
    args["pub_type"] = pub_type
    args["min_year"] = db.min_year
    args["max_year"] = db.max_year
    args["start_year"] = start_year
    args["end_year"] = end_year
    args["pub_str"] = PUB_TYPES[pub_type]
    return render_template("coauthors.html", args=args)

@app.route("/")
def showStatisticsMenu():
    dataset = app.config['DATASET']
    args = {"dataset":dataset}
    global sorted_before
    sorted_before = [False, False, False, False, False, False, False, False, False]
    return render_template('statistics.html', args=args)

@app.route("/firstlastsole")
def show_first_last_sole():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    PUB_TYPES = ["Conference Papers", "Journals", "Books", "Book Chapters"]
    args = {"dataset":dataset, "id":"firstlastsole"}
    args["title"] = "Display first last and sole author in different publication type"
    inproceedings = 0
    article = 1
    book = 2
    incollection = 3

    pub_type = 4
    if "pub_type" in request.args:
        pub_type = int(request.args.get("pub_type"))
    if pub_type == 0:
        args["data"] = db.get_ConferencePaper_first_last_sole() 
        args['pub_type'] = pub_type
    if pub_type == 1:  
        args["data"] = db.get_Journal_first_last_sole()  
        args['pub_type'] = pub_type 
    if pub_type == 2:    
        args["data"] = db.get_Book_first_last_sole()
        args['pub_type'] = pub_type
    if pub_type == 3:
        args["data"] = db.get_BookChapter_first_last_sole()
        args['pub_type'] = pub_type
    if pub_type == 4:
        args["data"] = db.get_none_first_last_sole()
        args['pub_type'] = pub_type
    return render_template('firstlastsole.html', args=args)

@app.route("/AuthorStatus")
def showauthorStatus():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset":dataset, "id":"AuthorStatus"}
    
    
    Author_name=''
    Author_name = request.args.get('author')
    args["data"] = db.click_author(Author_name)
    args['title'] = "Statistics for: " + args['data'][1][-1][1]
    args['author'] = args['data'][1][-1][1]
    args['data'][1].pop()

    return render_template("AuthorStatus.html", args=args)

@app.route("/searchfunction")
def showsearchresults():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset":dataset, "id":"searchfunction"}
    args['title'] = "Search Author"
    args['author_suggest'] = False
    
    author = ''
    if "author" in request.args:
        author = request.args.get("author")
        args['data'] = db.get_author_search(author)
        if len(args['data'][1]) > 1 and len(args['data'][1][0]) == 1:
            args['author_suggest'] = True
            tmp = db.get_author_search(author)
            args['data'] = (tmp[0],sort_by_precedence(tmp[1], author))
            args['author'] = author
        elif (len(args['data'][1]) > 1 and len(args['data'][1][0]) != 1):
            args['author'] = args['data'][1][-1][1]
            args['data'][1].pop()
        else:
            args['author'] = author
    if 'author' not in request.args:
        args['data'] = ['']
    return render_template("searchfunction.html", args=args)

@app.route("/Author_Status")
def show_author_Status():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset":dataset, "id":"Author_Status"}
    
    Author_name=''
    Author_name = request.args.get('author')
    args["author"] = Author_name
    coauthors = db.get_coauthor_name(Author_name)
    args["data"] = [{"name": name, "x":300, "y": 250} for name in coauthors]
    args["data"].append({"name": Author_name, "x":300, "y": 250})
    args["data"] = json.dumps(args["data"])
    args["links"] = json.dumps([{"source": Author_name, "target": name} for name in coauthors])
    return render_template("Author_Status.html", args=args)

@app.route("/chartcoauthor")
def chart_coauthor():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset":dataset, "id":"chartcoauthor"}
    args['title'] = "Please click or input author's name to get the research network"
    
    author = ''
    
    if "author" in request.args:
        author = request.args.get("author")
        args['data'] = db.get_coauthor_chart(author)
        if len(args['data'][1]) >= 1 :
            args['author_suggest'] = True
            tmp = db.get_coauthor_chart(author)
            args['data'] = (tmp[0],sort_by_precedence(tmp[1], author))
        args['author'] = author
    if 'author' not in request.args:
        args['data'] = db.get_coauthor_choose_name()
    
    return render_template("chartcoauthor.html", args=args)

@app.route("/statisticsdetails/<status>")
def showPublicationSummary(status):
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset":dataset, "id":status}

    args['author_click'] = False
    
    num_col = request.args.get('num_col')

    if (status == "publication_summary"):
        args["title"] = "Publication Summary"
        if num_col != None:
            y1 = db.get_publication_summary()[0]
            y2 = sort_col(db.get_publication_summary()[1], int(num_col))
            args["data"] = (y1,y2)
        else:
            args["data"] = db.get_publication_summary()

    if (status == "publication_author"):

        args['author_click'] = True

        args["title"] = "Author Publication"
        if num_col != None:
            y1 = db.get_publications_by_author()[0]
            y2 = sort_by_sur(db.get_publications_by_author()[1], int(num_col))
            args["data"] = (y1,y2)
        else:
            args["data"] = db.get_publications_by_author()

    if (status == "publication_year"):
        args["title"] = "Publication by Year"
        if num_col != None:
            y1 = db.get_publications_by_year()[0]
            y2 = sort_col(db.get_publications_by_year()[1], int(num_col))
            args["data"] = (y1,y2)
        else:
            args["data"] = db.get_publications_by_year()

    if (status == "author_year"):
        args["title"] = "Author by Year"
        if num_col != None:
            y1 = db.get_author_totals_by_year()[0]
            y2 = sort_col(db.get_author_totals_by_year()[1], int(num_col))
            args["data"] = (y1,y2)
        else:
            args["data"] = db.get_author_totals_by_year()
        

    return render_template('statistics_details.html', args=args)

@app.route("/Separation",methods=["GET"])
def authorSeparation():
    db = app.config['DATABASE']
    author1 = request.args.get("name1")
    author2 = request.args.get("name2")
    res = json.dumps(db.get_authors_separation(author1,author2))
    return Response(
        response=res,
        mimetype="application/json",
        status=200
    )

@app.route('/authors_separation_page')
def author_separation_show():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset": dataset}
    args["title"] = "Please input two authors' name and click submit to calculate the degrees of separation"
    args["data"] = db.get_publications_by_author()
    return render_template("authors_separation.html",args=args)
