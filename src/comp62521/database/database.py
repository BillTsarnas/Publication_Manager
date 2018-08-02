from comp62521.statistics import average
import itertools
import numpy as np
from xml.sax import handler, make_parser, SAXException

PublicationType = ["Conference Paper", "Journal", "Book", "Book Chapter"]

class Publication:
    CONFERENCE_PAPER = 0
    JOURNAL = 1
    BOOK = 2
    BOOK_CHAPTER = 3

    def __init__(self, pub_type, title, year, authors):
        self.pub_type = pub_type
        self.title = title
        if year:
            self.year = int(year)
        else:
            self.year = -1
        self.authors = authors

class Author:
    def __init__(self, name):
        self.name = name

class Stat:
    STR = ["Mean", "Median", "Mode"]
    FUNC = [average.mean, average.median, average.mode]
    MEAN = 0
    MEDIAN = 1
    MODE = 2

class Database:
    

    def read(self, filename):
        self.publications = []
        self.authors = []
        self.author_idx = {}
        self.min_year = None
        self.max_year = None

        handler = DocumentHandler(self)
        parser = make_parser()
        parser.setContentHandler(handler)
        infile = open(filename, "r")
        valid = True
        try:
            parser.parse(infile)
        except SAXException as e:
            valid = False
            print "Error reading file (" + e.getMessage() + ")"
        infile.close()

        for p in self.publications:
            if self.min_year == None or p.year < self.min_year:
                self.min_year = p.year
            if self.max_year == None or p.year > self.max_year:
                self.max_year = p.year

        return valid

    def get_all_authors(self):
        return self.author_idx.keys()

    def get_coauthor_data(self, start_year, end_year, pub_type):
        coauthors = {}
        for p in self.publications:
            if ((start_year == None or p.year >= start_year) and
                (end_year == None or p.year <= end_year) and
                (pub_type == 4 or pub_type == p.pub_type)):
                for a in p.authors:
                    for a2 in p.authors:
                        if a != a2:
                            try:
                                coauthors[a].add(a2)
                            except KeyError:
                                coauthors[a] = set([a2])
        def display(db, coauthors, author_id):
            return "%s (%d)" % (db.authors[author_id].name, len(coauthors[author_id]))

        header = ("Author", "Co-Authors")
        data = []
        for a in coauthors:
            data.append([ display(self, coauthors, a),
                ", ".join([
                    display(self, coauthors, ca) for ca in coauthors[a] ]) ])

        return (header, data)

    def get_average_authors_per_publication(self, av):
        header = ("Conference Paper", "Journal", "Book", "Book Chapter", "All Publications")

        auth_per_pub = [[], [], [], []]

        for p in self.publications:
            auth_per_pub[p.pub_type].append(len(p.authors))

        func = Stat.FUNC[av]

        data = [ func(auth_per_pub[i]) for i in np.arange(4) ] + [ func(list(itertools.chain(*auth_per_pub))) ]
        return (header, data)

    def get_average_publications_per_author(self, av):
        header = ("Conference Paper", "Journal", "Book", "Book Chapter", "All Publications")

        pub_per_auth = np.zeros((len(self.authors), 4))

        for p in self.publications:
            for a in p.authors:
                pub_per_auth[a, p.pub_type] += 1

        func = Stat.FUNC[av]

        data = [ func(pub_per_auth[:, i]) for i in np.arange(4) ] + [ func(pub_per_auth.sum(axis=1)) ]
        return (header, data)

    def get_average_publications_in_a_year(self, av):
        header = ("Conference Paper",
            "Journal", "Book", "Book Chapter", "All Publications")

        ystats = np.zeros((int(self.max_year) - int(self.min_year) + 1, 4))

        for p in self.publications:
            ystats[p.year - self.min_year][p.pub_type] += 1

        func = Stat.FUNC[av]

        data = [ func(ystats[:, i]) for i in np.arange(4) ] + [ func(ystats.sum(axis=1)) ]
        return (header, data)

    def get_average_authors_in_a_year(self, av):
        header = ("Conference Paper",
            "Journal", "Book", "Book Chapter", "All Publications")

        yauth = [ [set(), set(), set(), set(), set()] for _ in range(int(self.min_year), int(self.max_year) + 1) ]

        for p in self.publications:
            for a in p.authors:
                yauth[p.year - self.min_year][p.pub_type].add(a)
                yauth[p.year - self.min_year][4].add(a)

        ystats = np.array([ [ len(S) for S in y ] for y in yauth ])

        func = Stat.FUNC[av]

        data = [ func(ystats[:, i]) for i in np.arange(5) ]
        return (header, data)

    def get_publication_summary_average(self, av):
        header = ("Details", "Conference Paper",
            "Journal", "Book", "Book Chapter", "All Publications")

        pub_per_auth = np.zeros((len(self.authors), 4))
        auth_per_pub = [[], [], [], []]

        for p in self.publications:
            auth_per_pub[p.pub_type].append(len(p.authors))
            for a in p.authors:
                pub_per_auth[a, p.pub_type] += 1

        name = Stat.STR[av]
        func = Stat.FUNC[av]

        data = [
            [name + " authors per publication"]
                + [ func(auth_per_pub[i]) for i in np.arange(4) ]
                + [ func(list(itertools.chain(*auth_per_pub))) ],
            [name + " publications per author"]
                + [ func(pub_per_auth[:, i]) for i in np.arange(4) ]
                + [ func(pub_per_auth.sum(axis=1)) ] ]
        return (header, data)

    def get_publication_summary(self):
        header = ("Details", "Conference Paper",
            "Journal", "Book", "Book Chapter", "Total")

        plist = [0, 0, 0, 0]
        alist = [set(), set(), set(), set()]

        for p in self.publications:
            plist[p.pub_type] += 1
            for a in p.authors:
                alist[p.pub_type].add(a)
        # create union of all authors
        ua = alist[0] | alist[1] | alist[2] | alist[3]

        data = [
            ["Number of publications"] + plist + [sum(plist)],
            ["Number of authors"] + [ len(a) for a in alist ] + [len(ua)] ]
        return (header, data)

    def get_average_authors_per_publication_by_author(self, av):
        header = ("Author", "Number of conference papers",
            "Number of journals", "Number of books",
            "Number of book chapers", "All publications")

        astats = [ [[], [], [], []] for _ in range(len(self.authors)) ]
        for p in self.publications:
            for a in p.authors:
                astats[a][p.pub_type].append(len(p.authors))

        func = Stat.FUNC[av]

        data = [ [self.authors[i].name]
            + [ func(L) for L in astats[i] ]
            + [ func(list(itertools.chain(*astats[i]))) ]
            for i in range(len(astats)) ]
        return (header, data)


    def get_publications_by_author(self):
        header = ("Author", "Number of conference papers",
            "Number of journals", "Number of books",
            "Number of book chapers", "Total", "Number of first author", "Number of last author", "sole author")

        astats = [ [0, 0, 0, 0, 0, 0, 0] for _ in range(len(self.authors)) ]
        for p in self.publications:
            for a in p.authors:
                astats[a][p.pub_type] += 1
                if a == p.authors[0]:
                    astats[a][4] += 1
                if a == p.authors[len(p.authors)-1]:
                    astats[a][5] += 1
                if a == p.authors[0] and len(p.authors) == 1:
                    astats[a][6] += 1 
                    astats[a][4] = astats[a][4] - 1
                    astats[a][5] = astats[a][5] - 1           
        data = [ [self.authors[i].name] + astats[i][0:4] + [sum(astats[i][0:4])] + astats[i][4:7]
            for i in range(len(astats))]
        return (header, data)

    def get_coauthor_chart(self, author_name):
        header = ("Author", "Number of conference papers",
            "Number of journals", "Number of books",
            "Number of book chapers", "overall number of publications", "Number of first author", "Number of last author", "Number of co-authors")
        data = []
        i = 0
        all_publications = self.get_publications_by_author()
        for y in all_publications[1]:
             if author_name.lower() in y[0].lower():
                   i = i + 1
        if i == 0:
             return("Author    not    found  !", "")       
        else:
             for x in all_publications[1]:
                  if author_name.lower() in x[0].lower():
                       name = x[0]
                       info = [name]
                       data.append(info)
             return ("", data)
  
    def get_coauthor_name(self, author_name):
        name_list = []
        coauthors = set()
        for a in self.authors:
            name_list.append(a.name)
        if author_name in name_list:
            b = name_list.index(author_name)
            for p in self.publications:
                if b not in p.authors:
                    continue
                for a in p.authors:
                    coauthors.add(name_list[a])
            if author_name in coauthors:
                coauthors.remove(author_name)
        return coauthors

    def get_coauthor_choose_name(self):
        name_list = []
        for a in self.authors:
            name_list.append(a.name) 
        return name_list

    def get_author_search(self, author_name):
        header = ("Author", "Number of conference papers",
            "Number of journals", "Number of books",
            "Number of book chapers", "overall number of publications", "Number of first author", "Number of last author", "Number of co-authors")
        data = []
        i = 0
        all_publications = self.get_publications_by_author()
        for y in all_publications[1]:
             if author_name.lower() in y[0].lower():
                   i = i + 1
        if i == 0:
             return("Author    not    found  !", [])
        elif i == 1:
             for x in all_publications[1]:
                  if author_name.lower() in x[0].lower():
                       name = x[0]
                       header, data = self.click_author(name)
             return (header, data)
        else:
             for x in all_publications[1]:
                  if author_name.lower() in x[0].lower():
                       name = x[0]
                       info = [name]
                       data.append(info)
             return ("", data)

    def click_author(self, author_name):
        header = ("Details", "overall","journal articles", "conference papers", "books", "book chapters")
        stats =[ [0, 0, 0, 0] for _ in range(0, 5)]
        title = [ [0] for _ in range(0, 4)]
        journal_data = self.get_Journal_first_last_sole()[1]
        conference_data = self.get_ConferencePaper_first_last_sole()[1]
        book_data = self.get_Book_first_last_sole()[1]
        bookchapter_data = self.get_BookChapter_first_last_sole()[1]

        pub_data = self.get_publications_by_author()[1]
        for x in pub_data:
            if author_name == x[0]:
                pub_list = [x[2], x[1], x[3], x[4]]
        stats[0][0:4] = pub_list

        coauthors = len(self.get_coauthor_details(author_name)) - 1

        for x in journal_data:
            if author_name == x[0]:
                Journal = x[1:4]
        for x in conference_data:
            if author_name == x[0]:
                Conference = x[1:4]
        for x in book_data:
            if author_name == x[0]:
                Book = x[1:4]
        for x in bookchapter_data:
            if author_name == x[0]:
                Bookchapter = x[1:4]
        stats[1][0] = Journal[0]
        stats[2][0] = Journal[1]
        stats[3][0] = Journal[2]
        
        stats[1][1] = Conference[0]
        stats[2][1] = Conference[1]
        stats[3][1] = Conference[2]
        
        stats[1][2] = Book[0]
        stats[2][2] = Book[1]
        stats[3][2] = Book[2]
        
        stats[1][3] = Bookchapter[0]
        stats[2][3] = Bookchapter[1]
        stats[3][3] = Bookchapter[2]

        title[0][0] = "Number of publications"
        title[1][0] = "Number of times first author"
        title[2][0] = "Number of times last author"
        title[3][0] = "Number of times sole author"

        data = [ [title[i][0]] + [sum(stats[i][0:4])] + stats[i][0:4]
            for i in range(0, 4)] + [['Number of co-authors', coauthors]] + [['author name', author_name]]
        return (header, data)

    def get_Journal_first_last_sole(self):
        article = 1
        header = ("Author", 
             "Number of first author", "Number of last author", "sole author")
        astats = [[0, 0, 0] for _ in range(len(self.authors))]
        for p in self.publications:
          if p.pub_type == 1:
            for a in p.authors:
                if a == p.authors[0] :
                    astats[a][0] += 1
                if a == p.authors[len(p.authors)-1] :
                    astats[a][1] += 1
                if a == p.authors[0] and len(p.authors) == 1 :
                    astats[a][2] += 1
                    astats[a][0] = astats[a][0] - 1
                    astats[a][1] = astats[a][1] - 1
        data = [ [self.authors[i].name] + astats[i][0:3]
             for i in range(len(astats))]
        return (header, data)

    def get_Book_first_last_sole(self):
        header = ("Author",
              "Number of first author", "Number of last author", "sole author")
        astats = [ [0, 0, 0 ] for _ in range(len(self.authors)) ] 
        for p in self.publications:
          if p.pub_type == 2:
            for a in p.authors:
                if a == p.authors[0]:
                    astats[a][0] += 1
                if a == p.authors[len(p.authors)-1]:
                    astats[a][1] += 1
                if a == p.authors[0] and len(p.authors) == 1:
                    astats[a][2] += 1
                    astats[a][0] = astats[a][0] - 1
                    astats[a][1] = astats[a][1] - 1
        data = [ [self.authors[i].name] + astats[i][0:3]
            for i in range(len(astats))]
        return (header, data)
    
    def get_BookChapter_first_last_sole(self):
        header = ("Author", "Number of first author", 
              "Number of last author", "sole author")
        astats = [ [0, 0, 0 ] for _ in range(len(self.authors)) ] 
        for p in self.publications:
          if p.pub_type == 3:
            for a in p.authors:
                if a == p.authors[0]:
                    astats[a][0] += 1
                if a == p.authors[len(p.authors)-1]:
                    astats[a][1] += 1
                if a == p.authors[0] and len(p.authors) == 1:
                    astats[a][2] += 1
                    astats[a][0] = astats[a][0] - 1
                    astats[a][1] = astats[a][1] - 1
        data = [ [self.authors[i].name] + astats[i][0:3]
            for i in range(len(astats))]
        return (header, data)
        

    def get_ConferencePaper_first_last_sole(self):
        header = ("Author", 
              "Number of first author", "Number of last author", "sole author")
        astats = [ [0, 0, 0 ] for _ in range(len(self.authors)) ] 
        for p in self.publications:
          if p.pub_type == 0:
            for a in p.authors:
                if a == p.authors[0]:
                    astats[a][0] += 1
                if a == p.authors[len(p.authors)-1]:
                    astats[a][1] += 1
                if a == p.authors[0] and len(p.authors) == 1:
                    astats[a][2] += 1
                    astats[a][0] = astats[a][0] - 1
                    astats[a][1] = astats[a][1] - 1
        data = [ [self.authors[i].name] + astats[i][0:3]
            for i in range(len(astats))]
        return (header, data)

    def get_none_first_last_sole(self):
        data = ['']
        #return ('Please   choose   a   publication   type  !', [])
    
    def get_average_authors_per_publication_by_year(self, av):
        header = ("Year", "Conference papers",
            "Journals", "Books",
            "Book chapers", "All publications")

        ystats = {}
        for p in self.publications:
            try:
                ystats[p.year][p.pub_type].append(len(p.authors))
            except KeyError:
                ystats[p.year] = [[], [], [], []]
                ystats[p.year][p.pub_type].append(len(p.authors))

        func = Stat.FUNC[av]

        data = [ [y]
            + [ func(L) for L in ystats[y] ]
            + [ func(list(itertools.chain(*ystats[y]))) ]
            for y in ystats ]
        return (header, data)

    def get_publications_by_year(self):
        header = ("Year", "Number of conference papers",
            "Number of journals", "Number of books",
            "Number of book chapers", "Total")

        ystats = {}
        for p in self.publications:
            try:
                ystats[p.year][p.pub_type] += 1
            except KeyError:
                ystats[p.year] = [0, 0, 0, 0]
                ystats[p.year][p.pub_type] += 1

        data = [ [y] + ystats[y] + [sum(ystats[y])] for y in ystats ]
        return (header, data)

    def get_average_publications_per_author_by_year(self, av):
        header = ("Year", "Conference papers",
            "Journals", "Books",
            "Book chapers", "All publications")

        ystats = {}
        for p in self.publications:
            try:
                s = ystats[p.year]
            except KeyError:
                s = np.zeros((len(self.authors), 4))
                ystats[p.year] = s
            for a in p.authors:
                s[a][p.pub_type] += 1

        func = Stat.FUNC[av]

        data = [ [y]
            + [ func(ystats[y][:, i]) for i in np.arange(4) ]
            + [ func(ystats[y].sum(axis=1)) ]
            for y in ystats ]
        return (header, data)

    def get_author_totals_by_year(self):
        header = ("Year", "Number of conference papers",
            "Number of journals", "Number of books",
            "Number of book chapers", "Total")

        ystats = {}
        for p in self.publications:
            try:
                s = ystats[p.year][p.pub_type]
            except KeyError:
                ystats[p.year] = [set(), set(), set(), set()]
                s = ystats[p.year][p.pub_type]
            for a in p.authors:
                s.add(a)
        data = [ [y] + [len(s) for s in ystats[y]] + [len(ystats[y][0] | ystats[y][1] | ystats[y][2] | ystats[y][3])]
            for y in ystats ]
        return (header, data)

    def add_publication(self, pub_type, title, year, authors):
        if year == None or len(authors) == 0:
            print "Warning: excluding publication due to missing information"
            print "    Publication type:", PublicationType[pub_type]
            print "    Title:", title
            print "    Year:", year
            print "    Authors:", ",".join(authors)
            return
        if title == None:
            print "Warning: adding publication with missing title [ %s %s (%s) ]" % (PublicationType[pub_type], year, ",".join(authors))
        idlist = []
        for a in authors:
            try:
                idlist.append(self.author_idx[a])
            except KeyError:
                a_id = len(self.authors)
                self.author_idx[a] = a_id
                idlist.append(a_id)
                self.authors.append(Author(a))
        self.publications.append(
            Publication(pub_type, title, year, idlist))
        if (len(self.publications) % 100000) == 0:
            print "Adding publication number %d (number of authors is %d)" % (len(self.publications), len(self.authors))

        if self.min_year == None or year < self.min_year:
            self.min_year = year
        if self.max_year == None or year > self.max_year:
            self.max_year = year

    def _get_collaborations(self, author_id, include_self):
        data = {}
        for p in self.publications:
            if author_id in p.authors:
                for a in p.authors:
                    try:
                        data[a] += 1
                    except KeyError:
                        data[a] = 1
        if not include_self:
            del data[author_id]
        return data

    def get_coauthor_details(self, name):
        author_id = self.author_idx[name]
        data = self._get_collaborations(author_id, True)
        return [ (self.authors[key].name, data[key])
            for key in data ]

    def get_network_data(self):
        na = len(self.authors)

        nodes = [ [self.authors[i].name, -1] for i in range(na) ]
        links = set()
        for a in range(na):
            collab = self._get_collaborations(a, False)
            nodes[a][1] = len(collab)
            for a2 in collab:
                if a < a2:
                    links.add((a, a2))
        return (nodes, links)

    def get_authors_separation(self, author1, author2):
        author1 = str(author1)
        author2 = str(author2)
        Header = ("Author1", "Author2", "Degrees of separation")
        nodes, links = self.get_network_data()
        na = len(self.authors)
        author_id1 = self.author_idx[author1]
        author_id2 = self.author_idx[author2]
        separations = [author1]
        list_unused = []
        for a in range(na):
            if a == author_id1:
                separations.append(0)
            else:
                separations.append('X')
                list_unused.append(a)
        degree = 0
        list_flag = True
        list_index = list_unused[:]
        while (list_flag):
            list_start = list_unused[:]
            author_connection = []
            for Author in range(1, na + 1):
                if separations[Author] != 'X':
                    Author_id = Author - 1
                    author_connection.append(Author_id)
            for Author_id2 in author_connection:
                for author_unused in list_index:
                    if Author_id2 < author_unused:
                        index = (Author_id2, author_unused)
                    else:
                        index = (author_unused, Author_id2)
                    if index in links:
                        separations[author_unused + 1] = degree
                        list_unused.remove(author_unused)
                list_index = list_unused[:]
            degree = degree + 1
            if list_unused == list_start or list_unused == []:
                list_flag = False
        separation = separations[author_id2 + 1]
        data = [author1, author2, separation]
        return (Header, data)

class DocumentHandler(handler.ContentHandler):
    TITLE_TAGS = [ "sub", "sup", "i", "tt", "ref" ]
    PUB_TYPE = {
        "inproceedings":Publication.CONFERENCE_PAPER,
        "article":Publication.JOURNAL,
        "book":Publication.BOOK,
        "incollection":Publication.BOOK_CHAPTER }

    def __init__(self, db):
        self.tag = None
        self.chrs = ""
        self.clearData()
        self.db = db

    def clearData(self):
        self.pub_type = None
        self.authors = []
        self.year = None
        self.title = None

    def startDocument(self):
        pass

    def endDocument(self):
        pass

    def startElement(self, name, attrs):
        if name in self.TITLE_TAGS:
            return
        if name in DocumentHandler.PUB_TYPE.keys():
            self.pub_type = DocumentHandler.PUB_TYPE[name]
        self.tag = name
        self.chrs = ""

    def endElement(self, name):
        if self.pub_type == None:
            return
        if name in self.TITLE_TAGS:
            return
        d = self.chrs.strip()
        if self.tag == "author":
            self.authors.append(d)
        elif self.tag == "title":
            self.title = d
        elif self.tag == "year":
            self.year = int(d)
        elif name in DocumentHandler.PUB_TYPE.keys():
            self.db.add_publication(
                self.pub_type,
                self.title,
                self.year,
                self.authors)
            self.clearData()
        self.tag = None
        self.chrs = ""

    def characters(self, chrs):
        if self.pub_type != None:
            self.chrs += chrs
