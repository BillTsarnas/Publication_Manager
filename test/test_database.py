from os import path
import unittest

from comp62521.database import database
from comp62521.views import sort_col, sort_by_sur, sort_by_precedence 

class TestDatabase(unittest.TestCase):

    def setUp(self):
        dir, _ = path.split(__file__)
        self.data_dir = path.join(dir, "..", "data")

    def test_read(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        self.assertEqual(len(db.publications), 1)

    def test_read_invalid_xml(self):
        db = database.Database()
        self.assertFalse(db.read(path.join(self.data_dir, "invalid_xml_file.xml")))

    def test_read_missing_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "missing_year.xml")))
        self.assertEqual(len(db.publications), 0)

    def test_read_missing_title(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "missing_title.xml")))
        # publications with missing titles should be added
        self.assertEqual(len(db.publications), 1)

    def test_get_average_authors_per_publication(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "sprint-2-acceptance-1.xml")))
        _, data = db.get_average_authors_per_publication(database.Stat.MEAN)
        self.assertAlmostEqual(data[0], 2.3, places=1)
        _, data = db.get_average_authors_per_publication(database.Stat.MEDIAN)
        self.assertAlmostEqual(data[0], 2, places=1)
        _, data = db.get_average_authors_per_publication(database.Stat.MODE)
        self.assertEqual(data[0], [2])

    def test_get_average_publications_per_author(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "sprint-2-acceptance-2.xml")))
        _, data = db.get_average_publications_per_author(database.Stat.MEAN)
        self.assertAlmostEqual(data[0], 1.5, places=1)
        _, data = db.get_average_publications_per_author(database.Stat.MEDIAN)
        self.assertAlmostEqual(data[0], 1.5, places=1)
        _, data = db.get_average_publications_per_author(database.Stat.MODE)
        self.assertEqual(data[0], [0, 1, 2, 3])

    def test_get_average_publications_in_a_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "sprint-2-acceptance-3.xml")))
        _, data = db.get_average_publications_in_a_year(database.Stat.MEAN)
        self.assertAlmostEqual(data[0], 2.5, places=1)
        _, data = db.get_average_publications_in_a_year(database.Stat.MEDIAN)
        self.assertAlmostEqual(data[0], 3, places=1)
        _, data = db.get_average_publications_in_a_year(database.Stat.MODE)
        self.assertEqual(data[0], [3])

    def test_get_average_authors_in_a_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "sprint-2-acceptance-4.xml")))
        _, data = db.get_average_authors_in_a_year(database.Stat.MEAN)
        self.assertAlmostEqual(data[0], 2.8, places=1)
        _, data = db.get_average_authors_in_a_year(database.Stat.MEDIAN)
        self.assertAlmostEqual(data[0], 3, places=1)
        _, data = db.get_average_authors_in_a_year(database.Stat.MODE)
        self.assertEqual(data[0], [0, 2, 4, 5])
        # additional test for union of authors
        self.assertEqual(data[-1], [0, 2, 4, 5])

    def test_get_publication_summary(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        header, data = db.get_publication_summary()
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data[0]), 6,
            "incorrect number of columns in data")
        self.assertEqual(len(data), 2,
            "incorrect number of rows in data")
        self.assertEqual(data[0][1], 1,
            "incorrect number of publications for conference papers")
        self.assertEqual(data[1][1], 2,
            "incorrect number of authors for conference papers")

    def test_get_average_authors_per_publication_by_author(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "three-authors-and-three-publications.xml")))
        header, data = db.get_average_authors_per_publication_by_author(database.Stat.MEAN)
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data), 3,
            "incorrect average of number of conference papers")
        self.assertEqual(data[0][1], 1.5,
            "incorrect mean journals for author1")
        self.assertEqual(data[1][1], 2,
            "incorrect mean journals for author2")
        self.assertEqual(data[2][1], 1,
            "incorrect mean journals for author3")

    def test_get_publications_by_author(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        header, data = db.get_publications_by_author()
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data), 2,
            "incorrect number of authors")
        self.assertEqual(data[0][5], 1,
            "incorrect total")
        self.assertEqual(data[0][6], 1,
            "incorrect number of first appear")
        self.assertEqual(data[0][7], 0,
            "incorrect number of last appear")
        self.assertEqual(data[0][8], 0,
            "incorrect sole number")

    def test_get_average_publications_per_author_by_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        header, data = db.get_average_publications_per_author_by_year(database.Stat.MEAN)
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data), 1,
            "incorrect number of rows")
        self.assertEqual(data[0][0], 9999,
            "incorrect year in result")

    def test_get_publications_by_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        header, data = db.get_publications_by_year()
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data), 1,
            "incorrect number of rows")
        self.assertEqual(data[0][0], 9999,
            "incorrect year in result")

    def test_get_author_totals_by_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        header, data = db.get_author_totals_by_year()
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data), 1,
            "incorrect number of rows")
        self.assertEqual(data[0][0], 9999,
            "incorrect year in result")
        self.assertEqual(data[0][1], 2,
            "incorrect number of authors in result")

    def test_get_collaborations(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "three-authors-and-three-publications.xml")))
        data = db.author_idx
        author_id = data['author1']
        result = db._get_collaborations(author_id,True)
        result2 = db._get_collaborations(author_id,False)
        self.assertEqual(result,{0: 2, 1: 1})
        self.assertEqual(result2,{1:1})

    def test_get_coauthor_details(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "three-authors-and-three-publications.xml")))
        data = db.get_all_authors()
        result = db.get_coauthor_details(data[1])
        self.assertEqual(result, [('author1',1),('author2',1)])

    def test_get_network_data(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "three-authors-and-three-publications.xml")))
        data = db.get_network_data()
        self.assertEqual(data,([['author1', 1], ['author2', 1], ['author3', 0]], set([(0, 1)])))

    def test_get_all_authors(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "three-authors-and-three-publications.xml")))
        data = db.get_all_authors()
        self.assertEqual(data, ['author1', 'author2', 'author3'])

    def test_get_coauthor_data(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "three-authors-and-three-publications.xml")))
        start_year = db.min_year
        end_year = db.max_year
        pub_type = db.publications[0].pub_type
        _, data = db.get_coauthor_data(start_year, end_year, pub_type)
        self.assertEqual(data, [['author1 (1)', 'author2 (1)'], ['author2 (1)', 'author1 (1)']])

    def test_get_publication_summary_average(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "three-authors-and-three-publications.xml")))
        _, data = db.get_publication_summary_average(database.Stat.MEAN)
        self.assertEqual(data[0][3], 0)

    def test_get_publication_summary_average2(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "three-authors-and-three-publications.xml")))
        _, data = db.get_publication_summary_average(database.Stat.MEDIAN)
        self.assertEqual(data[0][3], 0)

    def test_get_publication_summary_average3(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "missing_year.xml")))
        _, data = db.get_publication_summary_average(database.Stat.MODE)
        self.assertEqual(data[0][1], [])

    def test_get_average_authors_per_publication_by_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "three-authors-and-three-publications.xml")))
        _, data = db.get_average_authors_per_publication_by_year(database.Stat.MEAN)
        self.assertEqual(data, [[9999, 1.3333333333333333, 0, 0, 0, 1.3333333333333333]])

    def test_get_average_authors_per_publication_by_year2(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "publications_small_sample.xml")))
        _, data = db.get_average_authors_per_publication_by_year(database.Stat.MEAN)
        self.assertEqual(data[1][1], 0)

    def test_publications_by_author22(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "dblp_curated_sample.xml")))
        db.get_publications_by_author()

    def test_get_author_search(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "dblp_curated_sample.xml")))
        data = db.get_author_search('stefano ceri')
        self.assertEqual(data, (('Details', 'overall', 'journal articles', 'conference papers', 'books', 'book chapters'), [['Number of publications', 218, 94, 100, 6, 18], ['Number of times first author', 78, 43, 28, 3, 4], ['Number of times last author', 25, 10, 10, 0, 5], ['Number of times sole author', 8, 0, 7, 0, 1], ['Number of co-authors', 230], ['author name', 'Stefano Ceri']	]))
     
        #when an author is not found, a proper message should be returned
        data = db.get_author_search('zxzxzxzxzx')
        self.assertEqual(data, ("Author    not    found  !", []))

        #when the search functions return more than one matches, a list of names ONLY should be returned
        data = db.get_author_search('sat')
        self.assertEqual(data, ("",[[u'Fabio Casati'], [u'Ulrike Sattler'], [u'Uli Sattler'], [u'Satya Sanket Sahoo'], [u'Chisato Yamasaki']]))

    def test_sort_by_precedence(self):
        db = database.Database()
        db.read(path.join(self.data_dir, "precedence_test.xml"))
        inp = db.get_author_search('sam')[1]
        data = sort_by_precedence(inp, 'sam')
        self.assertEqual(data,[[u'Alice Sam'], [u'Brian Sam'], [u'Alice Sammer'], [u'Brian Sammer'], [u'Alice Samming'], [u'Brian Samming'], [u'Sam Alice'], [u'Sam Brian'], [u'Samuel Alice'], [u'Samuel Brian'], [u'Brian Sam Alice'], [u'Alice Sam Brian'], [u'Alice Esam'], [u'Brian Esam']]
	)

    def test_sort(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "sort_test_file.xml")))
        inp = db.get_publications_by_author()[1]
        data = sort_col(inp,0)

        #First click in a column should do descending
        self.assertEqual(data,
                         [[u'Zachary G. Ives', 0, 0, 1, 0, 1, 0, 1, 0],[u'Stefano Ceri', 0, 0, 2, 1, 3, 2, 0, 0],[u'Shamkant B. Navathe', 0, 0, 1, 0, 1, 0, 1, 0], 		[u'Raghu Ramakrishnan', 0, 0, 0, 1, 1, 0, 1, 0], [u'Piero Fraternali', 0, 0, 1, 0, 1, 0, 1, 0],
	[u'Carlo Batini', 0, 0, 1, 0, 1, 1, 0, 0], [u'AnHai Doan', 0, 0, 1, 0, 1, 1, 0, 0], [u'Alon Y. Halevy', 0, 0, 1, 0, 1, 0, 0, 0]]
	)

        #sort again by the same column. Toggling to descending
        data = sort_col(inp,0)
        self.assertEqual(data,
	[[u'Alon Y. Halevy', 0, 0, 1, 0, 1, 0, 0, 0], [u'AnHai Doan', 0, 0, 1, 0, 1, 1, 0, 0], [u'Carlo Batini', 0, 0, 1, 0, 1, 1, 0, 0],
	[u'Piero Fraternali', 0, 0, 1, 0, 1, 0, 1, 0], [u'Raghu Ramakrishnan', 0, 0, 0, 1, 1, 0, 1, 0],
	[u'Shamkant B. Navathe', 0, 0, 1, 0, 1, 0, 1, 0], [u'Stefano Ceri', 0, 0, 2, 1, 3, 2, 0, 0], [u'Zachary G. Ives', 0, 0, 1, 0, 1, 0, 1, 0]]
	)

        #sort by another column
        data = sort_col(inp,5)
        self.assertEqual(data,
	[[u'Stefano Ceri', 0, 0, 2, 1, 3, 2, 0, 0], [u'Piero Fraternali', 0, 0, 1, 0, 1, 0, 1, 0], [u'Carlo Batini', 0, 0, 1, 0, 1, 1, 0, 0],
	[u'Shamkant B. Navathe', 0, 0, 1, 0, 1, 0, 1, 0], [u'Raghu Ramakrishnan', 0, 0, 0, 1, 1, 0, 1, 0],
	[u'AnHai Doan', 0, 0, 1, 0, 1, 1, 0, 0], [u'Alon Y. Halevy', 0, 0, 1, 0, 1, 0, 0, 0], [u'Zachary G. Ives', 0, 0, 1, 0, 1, 0, 1, 0]]
	)

        #sort by surname only - a new function sort_by_sur is created
        data = sort_by_sur(inp,0)
        self.assertEqual(data,
	[[u'Raghu Ramakrishnan', 0, 0, 0, 1, 1, 0, 1, 0], [u'Shamkant B. Navathe', 0, 0, 1, 0, 1, 0, 1, 0],[u'Zachary G. Ives', 0, 0, 1, 0, 1, 0, 1, 0], 	[u'Alon Y. Halevy', 0, 0, 1, 0, 1, 0, 0, 0], [u'Piero Fraternali', 0, 0, 1, 0, 1, 0, 1, 0], [u'AnHai Doan', 0, 0, 1, 0, 1, 1, 0, 0],
	[u'Stefano Ceri', 0, 0, 2, 1, 3, 2, 0, 0], [u'Carlo Batini', 0, 0, 1, 0, 1, 1, 0, 0]]
	)

        #Duplicate author name contain a number. This should not be considered while sorting
        db.read(path.join(self.data_dir, "sort_test_file2.xml"))
        inp = db.get_publications_by_author()[1]

        data = sort_by_sur(inp,0)
        self.assertEqual(data,
	[[u'Alvaro A. A. Fernandes', 1, 0, 0, 0, 1, 0, 0, 0], [u'Carole A. Goble', 1, 0, 0, 0, 1, 0, 0, 0], [u'Tony Griffiths', 1, 0, 0, 0, 1, 1, 0, 0], 	[u'Bo Huang 0001', 1, 0, 0, 0, 1, 0, 0, 0], [u'Olga Krebs', 1, 0, 0, 0, 1, 0, 0, 0], [u'Keith T. Mason', 1, 0, 0, 0, 1, 0, 0, 0],
 	[u'Wolfgang Mller 0001', 1, 0, 0, 0, 1, 0, 1, 0], [u'Quyen Nguyen', 1, 0, 0, 0, 1, 0, 0, 0], [u'Stuart Owen', 1, 0, 0, 0, 1, 0, 0, 0],
	[u'Norman W. Paton', 1, 0, 0, 0, 1, 0, 0, 0], [u'Katherine Wolstencroft', 1, 0, 0, 0, 1, 1, 0, 0],
	[u'Michael F. Worboys', 1, 0, 0, 0, 1, 0, 1, 0]]
	)

        #In co-author page, every author name is accompanied in a value in paretheses. this should not be considered while sorting
        start_year, end_year, pub_type = 1800, 2020, 4
        inp = db.get_coauthor_data(start_year, end_year, pub_type)[1]
        data = sort_by_sur(inp,0)
        self.assertEqual(data,
	[[u'Michael F. Worboys (5)', u'Norman W. Paton (5), Keith T. Mason (5), Bo Huang 0001 (5), Tony Griffiths (5), Alvaro A. A. Fernandes (5)'], [u'Katherine Wolstencroft (5)', u'Stuart Owen (5), Carole A. Goble (5), Quyen Nguyen (5), Olga Krebs (5), Wolfgang Mller 0001 (5)'], [u'Norman W. Paton (5)', u'Keith T. Mason (5), Bo Huang 0001 (5), Michael F. Worboys (5), Tony Griffiths (5), Alvaro A. A. Fernandes (5)'], [u'Stuart Owen (5)', u'Katherine Wolstencroft (5), Carole A. Goble (5), Quyen Nguyen (5), Olga Krebs (5), Wolfgang Mller 0001 (5)'], [u'Quyen Nguyen (5)', u'Katherine Wolstencroft (5), Stuart Owen (5), Carole A. Goble (5), Olga Krebs (5), Wolfgang Mller 0001 (5)'], [u'Wolfgang Mller 0001 (5)', u'Katherine Wolstencroft (5), Stuart Owen (5), Carole A. Goble (5), Quyen Nguyen (5), Olga Krebs (5)'], [u'Keith T. Mason (5)', u'Norman W. Paton (5), Bo Huang 0001 (5), Michael F. Worboys (5), Tony Griffiths (5), Alvaro A. A. Fernandes (5)'], [u'Olga Krebs (5)', u'Katherine Wolstencroft (5), Stuart Owen (5), Carole A. Goble (5), Quyen Nguyen (5), Wolfgang Mller 0001 (5)'], [u'Bo Huang 0001 (5)', u'Norman W. Paton (5), Keith T. Mason (5), Michael F. Worboys (5), Tony Griffiths (5), Alvaro A. A. Fernandes (5)'], [u'Tony Griffiths (5)', u'Norman W. Paton (5), Keith T. Mason (5), Bo Huang 0001 (5), Michael F. Worboys (5), Alvaro A. A. Fernandes (5)'], [u'Carole A. Goble (5)', u'Katherine Wolstencroft (5), Stuart Owen (5), Quyen Nguyen (5), Olga Krebs (5), Wolfgang Mller 0001 (5)'], [u'Alvaro A. A. Fernandes (5)', u'Norman W. Paton (5), Keith T. Mason (5), Bo Huang 0001 (5), Michael F. Worboys (5), Tony Griffiths (5)']]
	)

    def test_click_author(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "dblp_curated_sample.xml")))
        data = db.click_author('Stefano Ceri')
        self.assertEqual(data, (('Details', 'overall', 'journal articles', 'conference papers', 'books', 'book chapters'), [['Number of publications', 218, 94, 100, 6, 18], ['Number of times first author', 78, 43, 28, 3, 4], ['Number of times last author', 25, 10, 10, 0, 5], ['Number of times sole author', 8, 0, 7, 0, 1], ['Number of co-authors', 230], ['author name', 'Stefano Ceri']]))

    def test_get_Journal_first_last_sole(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "publications_small_sample.xml")))
        _, data = db.get_Journal_first_last_sole()
        self.assertEqual(data[3], ['Carole A. Goble', 1, 0, 0])
    def test_get_Book_first_last_sole(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "publications_small_sample.xml")))
        _, data = db.get_Book_first_last_sole()
        self.assertEqual(data[6], ['Stefano Ceri', 1, 0, 0])
    def test_get_ConferencePaper_first_last_sole(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "publications_small_sample.xml")))
        _, data = db.get_ConferencePaper_first_last_sole()
        self.assertEqual(data[0], ['Sean Bechhofer', 1, 0, 0])
    def test_get_BookChapter_first_last_sole(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "publications_small_sample.xml")))
        _, data = db.get_BookChapter_first_last_sole()
        self.assertEqual(data[6], ['Stefano Ceri', 1, 0, 0])
    def test_get_none_first_last_sole(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "publications_small_sample.xml")))
        data = db.get_none_first_last_sole()
        self.assertEqual(data,('Please   choose   a   publication   type  !', []))
if __name__ == '__main__':
    unittest.main()
