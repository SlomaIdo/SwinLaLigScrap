#TODO: #2 Move all the functions to separate function file.
#TODO: #3 Putting this all together, create a flow to scrape the competitions, disciplines and results.
#TODO: #4 debug and test the code, via a whole run.
#TODO: #5 Push to SQLite database.


import requests
from bs4 import BeautifulSoup

class CompetitionScraper():
    
    """This Class is used to scrape the competitions from the ISR main website.
    The class is initialized with the url of the competitions page.
    The class has a method get_competition_names which returns a list of dictionaries
    with the competition name, link and tabindex.
    ...
    Attributes
    ----------
    url : str

    """
    def __init__(self, url:str)-> None:
        """Initializes the class with the url of the competitions page.

        Args:
            url (str): Accepts the url of the competitions page.
        """
        self.url = url
        self.page = requests.get(url, cookies={'_culture':'en-US'})
        self.soup = BeautifulSoup(self.page.content, 'html.parser')
        
    
    def get_competition_names(self)-> str:
        """This method scrapes the competition names, links and tabindex 
        from the competitions page.

        Parameters:
            None

        Returns:
            List: List of dictionaries with the competition name, link and tabindex.
        """
        competitions_td = self.soup.find_all('td', {"class": "rr c-name"})
        list_of_competitions = []
        for i in competitions_td:
            comp_dict = \
                {'competition_name': i.text,
                'competition_link': i.find('a')['href'],
                'competition_tabindex': i.find('a')['tabindex']
                }
            list_of_competitions.append(comp_dict)
        return list_of_competitions

class SingleCompPage():
    """Single Competition Class
    ...    
    """
    def __init__(self, url:str) -> None:
        """Single Competition Page class is used to scrape the information from a single competition page.

        Args:
            url (str): url of a single competition page.
        """
        self.url = url
        self.page = requests.get(url, cookies={'_culture':'en-US'})
        self.soup = BeautifulSoup(self.page.content, 'html.parser')
    
    def get_competition_info(self) -> str:
        """
        Returns:
            list: list of links of heats and results.
        """
        competition_info = list(set([i['src'] for i in self.soup.find_all('iframe')]))
        return competition_info

#url = 'https://isr.org.il/competitions.asp?cYear=2024&cMonth=0&cType=1&cMode=0&isFinish=true'
#test = CompetitionScraper(url)
#list_of_comp = test.get_competition_names()
#list_of_comp

#comp_url = 'https://isr.org.il/comp.asp?compID=454'
#test = SingleCompPage(comp_url).get_competition_info()
#test

class AthleticsDisciplines():
    
    def __init__(self, url:str) -> None:
        self.url = url
        self.page = requests.get(url, cookies={'_culture':'en-US'})
        self.soup = BeautifulSoup(self.page.content, 'html.parser')
    
    def extract_main_table(self) -> str:
        """Extract the main table in a single competition page.

        Raises:
            ValueError: If the number of columns in the table does not match the number of headers.

        Returns:
            list: list of dictionaries with the competition details.
        """
        requests.post('https://loglig.com:2053/Common/SetCulture?lang=en')
        main_table = self.soup.find_all('table', {"class": "table res-table"})
        main_table_columns = main_table[0].find('tr', {"class": "disciplines-title"})        
        #Only 7 headers are needed. 
        main_table_columns = tuple([i.text for i in main_table_columns.find_all('th')])
        main_table_columns = main_table_columns[0:7]        
        rows_of_table = main_table[0].find_all('tr')
        comp_rows = []
        for row in rows_of_table:
            text_ls = [j.text for j in row.find_all('td')]
            if len(text_ls) == 0: 
                continue            
            #remove all \n from list elements
            text_ls = [item.replace('\n', '') for item in text_ls]
            text_ls = text_ls[0:7]
            # find the reults link
            link = row.find_all('a',{"class": "btn btn-primary resultsModal button-with-spinner"})
            if len(link) > 0:
                results_link = link[0]['href']
            else:
                results_link = None

            if len(text_ls) == 7 and len(main_table_columns) == 7:
                row_dict = dict(zip(main_table_columns, text_ls))
            else:
                raise ValueError('The number of columns in the table does not\
                                  match the number of headers.')
            if results_link is not None:
                row_dict['results_link'] = results_link
            else:
                row_dict['results_link'] = None
            comp_rows.append(row_dict)
        return comp_rows


url = 'https://loglig.com:2053/LeagueTable/AthleticsDisciplines/9453'
test = AthleticsDisciplines(url)
comp_details = test.extract_main_table()
comp_details

class AthleticsDisciplineResults():
    """Class for extracting the results table in a single discipline page.
    """
        
    def __init__(self, url:str) -> None:
        self.url = url
        self.page = requests.get(url, cookies={'_culture':'en-US'})
        self.soup = BeautifulSoup(self.page.content, 'html.parser')
        
    def extract_results_table(self) -> str:
        """Extract the results table in a single competition page.
    
            Raises:
                ValueError: If the number of columns in the table does not match the number of headers.
    
            Returns:
                list: list of dictionaries with the competition results.
        """
        results_table = self.soup.find_all('table', {"class": "table res-table"})
        main_table_columns = results_table[0].find('tr', {"class": "disciplines-title"})        
            #Only 8 headers are needed.
            # Parsing the main table columns.
        main_table_columns = tuple([i.text for i in main_table_columns.find_all('th')])

        rows_of_table = results_table[0].find_all('tr')
        comp_rows = []
        table_first_row = None
        for row in rows_of_table:
            text_ls = [j.text for j in row.find_all('td')]
            if len(text_ls) == 0: 
                continue            
                #remove all \n from list elements
            text_ls = [item.replace('\n', '') for item in text_ls]
            text_ls = [item.rstrip() for item in text_ls]
            text_ls = text_ls[0:8]
               
            if len(text_ls) == 8 and len(main_table_columns) == 8:
                row_dict = dict(zip(main_table_columns, text_ls))
            elif text_ls[0] == 'Direct Finals':
                table_first_row = text_ls[0]
                continue
            else:
                raise ValueError('The number of columns in the table does not\
                                      match the number of headers.')
            row_dict['table_first_row'] = table_first_row
            comp_rows.append(row_dict)
        return comp_rows
            

#url = 'https://loglig.com:2053/LeagueTable/AthleticsDisciplineResults/41422'
#test = AthleticsDisciplineResults(url)
#comp_details = test.extract_results_table()
#comp_details
