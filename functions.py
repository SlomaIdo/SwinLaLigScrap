from bs4 import BeautifulSoup
import requests
import re

accepted_rudolph = ["50 Freestyle","100 Freestyle","200 Freestyle","400 Freestyle",
                        "800 Freestyle","1500 Freestyle","50 Breaststroke",
                        "100 Breaststroke","200 Breaststroke","50 Butterfly",
                        "100 Butterfly","200 Butterfly","50 Backstroke","100 Backstroke",
                        "200 Backstroke","200 Medley","400 Medley"]


def extract_athletics_discipline(soup:BeautifulSoup, n:int=7)-> list:
    """Extract the main table in a single competition page.

    Args:
        soup (BeautifulSoup): BeautifulSoup object of the single competition page.
        n (int): The number of columns in the table.

    Raises:
        ValueError: if the number of columns in the table does not match the number of headers.
    Returns:
        list: List of Dicts with the table rows.
    """

    main_table = soup.find_all('table', {"class": "table res-table"})
    main_table_columns = main_table[0].find('tr', {"class": "disciplines-title"})        
    #Only 7 headers are needed. 
    main_table_columns = tuple([i.text for i in main_table_columns.find_all('th')])
    main_table_columns = main_table_columns[0:n]
    # Problem is that we want to get only the first level of table rows.
    #TODO: #7 How to handle when there is a Category minimum standard? like in: https://isr.org.il/comp.asp?compID=475
    #rows_of_table = main_table[0].find_all('tr')
    rows_of_table = main_table[0].tbody.find_all('tr', recursive=False)
    comp_rows = []
    for row in rows_of_table:
        #text_ls = [j.text for j in row.find_all('td')]
        text_ls = [j.text for j in row.find_all('td',recursive=False)]
        if len(text_ls) == 0: 
            continue            
        #remove all \n from list elements
        text_ls = [item.replace('\n', '') for item in text_ls]        
        text_ls = [item.strip() for item in text_ls]
        text_ls = text_ls[0:n]
        # find the reults link
        link = row.find_all('a',{"class": "btn btn-primary resultsModal button-with-spinner"})
        if len(link) > 0:
            results_link = link[0]['href']
        else:
            results_link = None
        try:
            if len(text_ls) == n and len(main_table_columns) == n:
                row_dict = dict(zip(main_table_columns, text_ls))
            else:
                raise ValueError('The number of columns in the table does not\
                                     match the number of headers.')
        except ValueError as e:
            print(f"Error: {e}")
            pass
        if results_link is not None:
            row_dict['results_link'] = results_link
        else:
            row_dict['results_link'] = None
        comp_rows.append(row_dict)
    return comp_rows    

def extract_athletics_discipline_results(soup:BeautifulSoup, n:int=8)-> list:
    """Extract the results table in a single competition page.

    Args:
        soup (BeautifulSoup): BeautifulSoup object of the single competition page.
        n (int, optional): The number of columns in the table. Defaults to 8.

    Raises:
        ValueError: if the number of columns in the table does not match the number of headers.

    Returns:
        list: List of Dicts with the table rows.
    """
    results_table = soup.find_all('table', {"class": "table res-table"})
    if len(results_table) == 0:
        return []
    main_table_columns = results_table[0].find('tr', {"class": "disciplines-title"})        
    #Only 8 headers are needed.
    # Parsing the main table columns.
    main_table_columns = tuple([i.text for i in main_table_columns.find_all('th')])
    main_table_columns = main_table_columns[0:n]

    rows_of_table = results_table[0].find_all('tr')
    comp_rows = []
    table_first_row = None
    for row in rows_of_table:
        text_ls = [j.text for j in row.find_all('td')]
        if len(text_ls) == 0: 
            continue            
        
        #remove all \n from list elements
        text_ls = [item.replace('\n', '') for item in text_ls]
        text_ls = [item.replace('\r', '') for item in text_ls]
        text_ls = [item.strip() for item in text_ls]
        text_ls = text_ls[0:n]
               
        if (len(text_ls) == n and len(main_table_columns) == n) or \
            (len(text_ls) == len(main_table_columns)):
            row_dict = dict(zip(main_table_columns, text_ls))
        elif text_ls[0] == 'Direct Finals' or \
                text_ls[0] == 'Preliminary' or \
                text_ls[0] == 'Qualifications' or \
                text_ls[0] == 'Finals' or \
                text_ls[0] == 'Semifinals':
            table_first_row = text_ls[0]
            continue
        else:
            #TODO: #8 How to handle relay, when multiple swimmers are in the same row?
            raise ValueError('The number of columns in the table does not\
                                match the number of headers.')
        row_dict['table_first_row'] = table_first_row
        comp_rows.append(row_dict)
    return comp_rows

def Rudolph(year:int, gender:str, age:str, event:str, result:str) -> int:
    """Rudolph is a function that returns a string with the results of a swimmer.
    from https://bswimmer.org/rudolph/

    Args:
        year (int): The year of the competition
        gender (str): 
        """
    headers = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0'
    base_url = "https://bswimmer.org/rudolph/Rudolph.php?year={}&gender={}&age={}&event={}&result={}"
    #payload = {
    #   'year': year,
    #    'gender': gender,
    #    'age': age,
    #    'event': event,
    #    'results': results
    #}
    # replac space to %20 in event
    event = event.replace(' ', '%20')
    #replace : to %3A in result
    if re.search(pattern='[0-9]{2}:[0-9]{2}.[0-9]{2}', string=result) is None:
        return None
    else:
        result = result.replace(':', '%3A')
        result = '00%3A' + result
    try:
        bswim_url = base_url.format(year, gender, age, event, result)
        page = requests.get(bswim_url, headers={'User-Agent': headers})
        soup = BeautifulSoup(page.text, 'html.parser')
        return int(soup.text)
    except Exception as e:
        print(f"Error: {e}")
        return None

def replace_event_to_Rudolph(str):
    """_summary_

    Args:
        str (_type_): _description_

    Returns:
        _type_: _description_
    """

    accepted_rudolph = ["50 Freestyle","100 Freestyle","200 Freestyle","400 Freestyle",
                        "800 Freestyle","1500 Freestyle","50 Breaststroke",
                        "100 Breaststroke","200 Breaststroke","50 Butterfly",
                        "100 Butterfly","200 Butterfly","50 Backstroke","100 Backstroke",
                        "200 Backstroke","200 Medley","400 Medley"]
    
    # remove the m under the digits    
    str = re.sub(r'(?<=\d)m', '', str)
    # remove the Individual from the string
    str = re.sub(r'Individual ', '', str)    
    # remove multiple spaces to one space
    str = re.sub(r'\s+', ' ', str)
    if re.search(pattern='relay', string=str,flags=re.IGNORECASE):        
        return False
    elif re.search(pattern='100 Medley', string=str,flags=re.IGNORECASE):
        return False
    elif str not in accepted_rudolph:
        return False
    else:
        return str